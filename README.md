# Web-Enabled LLM with Ollama

![Web-Enabled LLM with Ollama](assets/readme.png)

A Python application that combines web search capabilities with Ollama's LLM to provide informed responses based on current web information.

## Features

- Real-time web search using Playwright
- Integration with Ollama's LLM API
- Streaming token output with colored thinking process
- Robust error handling and logging

## Quick Install

### On macOS/Linux:
```bash
chmod +x install.sh
./install.sh
```

### On Windows:
```bash
install.bat
```

The installation script will:
1. Check for Python and pip
2. Create and activate a virtual environment
3. Install all Python dependencies
4. Install Playwright browser
5. Install Ollama (if not already installed)
6. Pull the required LLM model
7. Start the Ollama service

## Manual Installation

If you prefer to install components manually, follow these steps:

### 1. Ollama Setup

Install Ollama (version >= 0.1.29):
- macOS/Linux: `curl -fsSL https://ollama.ai/install.sh | sh`
- Windows: Download from https://ollama.ai/download/windows

Pull the required model:
```bash
ollama pull deepseek-r1:14b
```

Start the Ollama service:
```bash
ollama serve
```

### 2. Python Environment

Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Install Playwright browser:
```bash
playwright install chromium
```

## Usage

1. Ensure Ollama is running with the deepseek-r1:14b model pulled
2. Run the script:
```bash
python web_search_llm.py
```

3. Enter your questions when prompted. The script will:
   - Search the web for relevant information
   - Process the results through the LLM
   - Display the thinking process in cyan
   - Provide a final response

4. Type 'quit' to exit

## Example

```
Enter your question (or 'quit' to exit): who is TAYLOR.WTF?

Searching and processing...
[Thinking process in cyan]
[Final response in default color]
```

## Troubleshooting

1. If you see "Error: Could not connect to Ollama", ensure:
   - Ollama is installed and running (`ollama serve`)
   - The required model is pulled (`ollama pull deepseek-r1:14b`)

2. If web search fails:
   - Check your internet connection
   - Verify Playwright is properly installed with browsers

3. If the installation script fails:
   - Try the manual installation steps
   - Check system requirements (Python 3.7+, pip)
   - Ensure you have administrative privileges

## Requirements

See `requirements.txt` for Python package dependencies.

## License

MIT License 