import asyncio
from playwright.async_api import async_playwright
import aiohttp
import json
import logging
import traceback
from sys import stdout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=stdout
)
logger = logging.getLogger(__name__)

# ANSI color codes
NEON_CYAN = '\033[1;96m'  # Bright cyan
RESET_COLOR = '\033[0m'

# Force enable ANSI colors for Windows
import os
os.system('')  # Enable ANSI escape sequences

class WebEnabledLLM:
    def __init__(self, model_name="deepseek-r1:14b", headless=True):
        self.model_name = model_name
        self.headless = headless
        self.ollama_url = "http://localhost:11434/api/generate"
        logger.info(f"Initializing WebEnabledLLM with model: {model_name}, headless: {headless}")

    async def search_web(self, query, num_results=3):
        """Search the web using Playwright."""
        logger.info(f"Starting web search for query: {query}")
        results = []
        async with async_playwright() as p:
            logger.info("Launching browser")
            browser = await p.chromium.launch(headless=self.headless, args=["--disable-blink-features=AutomationControlled"])
            try:
                context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36', viewport={"width":1280, "height":800})
                page = await context.new_page()
                
                logger.info("Navigating to Google")
                await page.goto('https://www.google.com/?hl=en')
                logger.info("Waiting for network idle")
                await page.wait_for_load_state('networkidle')
                logger.info(f"Current page URL: {page.url}")

                # Handle consent popup
                logger.info("Checking for consent popup")
                consent_button = await page.query_selector('button:has-text("I agree")')
                if consent_button:
                    logger.info("Found consent button, clicking it")
                    await consent_button.click()
                    await asyncio.sleep(2)  # Wait for page update

                # Robust selector for search input
                search_selectors = [
                    'input[name="q"]', 
                    'input[aria-label="Search"]', 
                    '#lst-ib',
                    '#APjFqb'
                ]
                
                logger.info("Attempting to find search input")
                for selector in search_selectors:
                    try:
                        logger.info(f"Trying selector: {selector}")
                        await page.wait_for_selector(selector, timeout=10000)
                        search_input = await page.query_selector(selector)
                        if search_input:
                            logger.info(f"Found search input with selector: {selector}")
                            await search_input.fill(query)
                            logger.info("Filled search input, pressing Enter")
                            await search_input.press('Enter')
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} not found: {str(e)}")
                else:
                    logger.error("No valid search input found. Taking screenshot for debugging.")
                    await page.screenshot(path='debug_search_input.png')
                    raise Exception("Failed to find search input")

                logger.info("Waiting for search results")
                await page.wait_for_selector('#search')
                # Wait for the page to settle after search
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)  # Give JavaScript time to render
                logger.info("Found search results container")
                search_results = await page.query_selector_all('div.g:not(.g-blk)')
                logger.info(f"Found {len(search_results)} total results")

                for result in search_results[:num_results]:
                    logger.debug("Processing a search result")
                    title = await result.query_selector('h3')
                    link = await result.query_selector('a[href^="http"]')
                    snippet_elem = await result.query_selector('div[style*="webkit-line-clamp"]')
                    
                    if title and link and snippet_elem:
                        title_text = await title.inner_text()
                        link_href = await link.get_attribute('href')
                        snippet_text = await snippet_elem.inner_text()
                        # Only add if we have meaningful content
                        if len(title_text.strip()) > 0 and len(snippet_text.strip()) > 0:
                            logger.debug(f"Found title: {title_text}")
                            logger.debug(f"Found link: {link_href}")
                            logger.debug(f"Found snippet: {snippet_text}")
                            logger.info(f"Adding result: {title_text[:50]}...")
                            results.append({
                                'title': title_text,
                                'link': link_href,
                                'snippet': snippet_text
                            })
                    else:
                        logger.debug(f"Missing elements - title: {bool(title)}, link: {bool(link)}, snippet: {bool(snippet_elem)}")
                        if title or link or snippet_elem:
                            logger.info("Taking screenshot of partial result for debugging")
                            await page.screenshot(path='debug_partial_result.png')
            except Exception as e:
                logger.error(f"Error during web search: {str(e)}")
                logger.debug(f"Detailed error: {traceback.format_exc()}")
            finally:
                await browser.close()
        logger.info(f"Search completed with {len(results)} results")
        return results

    async def query_with_web_search(self, user_query, search_results_count=3):
        """Query the model with web search results as context."""
        logger.info(f"Processing query with web search: {user_query}")
        
        search_results = await self.search_web(user_query, search_results_count)
        context = "No search results were found. I'll try to answer based on my model knowledge." if not search_results else "\n".join(
            [f"{i+1}. {result['title']}\n   {result['snippet']}\n   Source: {result['link']}" for i, result in enumerate(search_results)]
        )
        
        prompt = f"{context}\n\nBased on these results, please answer the following question: {user_query}\n\nFirst, think through the answer step by step (enclosed in <think></think> tags), then provide a concise final response."
        logger.debug(f"Generated prompt length: {len(prompt)} characters")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True
                }) as response:
                    if response.status == 200:
                        in_thinking = False
                        buffer = ""
                        
                        # Process the stream
                        async for line in response.content:
                            try:
                                chunk = json.loads(line)
                                if chunk.get("done", False):
                                    logger.info("Successfully completed response from Ollama")
                                    logger.debug(f"Total tokens: {chunk.get('eval_count', 0)}")
                                    if in_thinking:  # Ensure we reset color if we end in thinking mode
                                        print(RESET_COLOR, end="", flush=True)
                                    print()  # New line after completion
                                    break

                                token = chunk.get("response", "")
                                if not token:
                                    continue

                                buffer += token
                                
                                # Check for thinking tags in buffer
                                while "<think>" in buffer or "</think>" in buffer:
                                    if "<think>" in buffer and not in_thinking:
                                        think_pos = buffer.find("<think>")
                                        # Print text before <think>
                                        print(buffer[:think_pos], end="", flush=True)
                                        print(NEON_CYAN, end="", flush=True)
                                        buffer = buffer[think_pos + len("<think>"):]
                                        in_thinking = True
                                    elif "</think>" in buffer and in_thinking:
                                        think_pos = buffer.find("</think>")
                                        # Print text before </think>
                                        print(buffer[:think_pos], end="", flush=True)
                                        print(RESET_COLOR, end="", flush=True)
                                        buffer = buffer[think_pos + len("</think>"):]
                                        in_thinking = False
                                    else:
                                        break

                                # Print remaining buffer with current color state
                                print(buffer, end="", flush=True)
                                buffer = ""
                                
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to decode JSON from chunk: {line}")
                                continue
                            
                    else:
                        raise Exception(f"HTTP error {response.status}")
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection error to Ollama API: {str(e)}")
            return "Error: Could not connect to Ollama. Is the service running?"
        except Exception as e:
            logger.error(f"Unexpected error querying Ollama: {str(e)}")
            logger.debug(f"Detailed error: {traceback.format_exc()}")
            return f"Error querying the model: {str(e)}"

async def main():
    try:
        llm = WebEnabledLLM("deepseek-r1:14b", headless=True)
        while True:
            user_input = input("\nEnter your question (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                logger.info("User requested to quit")
                break
            print("\nSearching and processing...")
            await llm.query_with_web_search(user_input)  # Don't print response, it's streamed
    except KeyboardInterrupt:
        logger.info("Application terminated by user (KeyboardInterrupt)")

if __name__ == "__main__":
    asyncio.run(main())