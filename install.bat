@echo off
echo 🚀 Starting Web-Enabled LLM Setup...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    exit /b 1
)

REM Check pip installation
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not installed.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Install Playwright browser
echo 🎭 Installing Playwright browser...
playwright install chromium

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo 🐪 Installing Ollama...
    echo Please download and install Ollama from https://ollama.ai/download/windows
    echo Press any key when Ollama is installed...
    pause >nul
) else (
    echo ✅ Ollama is already installed
)

REM Check if Ollama service is running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
    echo 🚀 Starting Ollama service...
    start "" ollama serve
    timeout /t 5 /nobreak >nul
)

REM Pull the model
echo 🤖 Pulling the DeepSeek model (this may take a while)...
ollama pull deepseek-r1:14b

echo.
echo ✨ Installation complete! ✨
echo.
echo To start using the Web-Enabled LLM:
echo 1. Ensure Ollama is running: ollama serve
echo 2. Activate the virtual environment: venv\Scripts\activate
echo 3. Run the script: python web_search_llm.py
echo.
echo Enjoy! 🎉
echo.

pause 