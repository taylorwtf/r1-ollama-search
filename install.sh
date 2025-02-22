#!/bin/bash

echo "🚀 Starting Web-Enabled LLM Setup..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browser
echo "🎭 Installing Playwright browser..."
playwright install chromium

# Install Ollama if not already installed
if ! command_exists ollama; then
    echo "🐪 Installing Ollama..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service in the background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama service..."
    ollama serve &
    sleep 5  # Wait for Ollama to start
fi

# Pull the model
echo "🤖 Pulling the DeepSeek model (this may take a while)..."
ollama pull deepseek-r1:14b

echo "
✨ Installation complete! ✨

To start using the Web-Enabled LLM:
1. Ensure Ollama is running: ollama serve
2. Activate the virtual environment: source venv/bin/activate
3. Run the script: python web_search_llm.py

Enjoy! 🎉
" 