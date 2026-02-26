@echo off
echo ===================================================
echo ^^! Copyright of Automotive Artificial Intelligence (AAI) GmbH ^^!
echo ^^! CORA LEGAL AI (LITE) - WINDOWS INSTALLER ^^!
echo ===================================================

:: --- 1. PYTHON CHECK ---
echo.
echo [1/6] Checking for Python...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [X] Python is not installed or not in your PATH!
    echo.
    echo Windows will now open the Microsoft Store so you can install Python.
    echo Once installed, close the store and run this setup.bat file again.
    echo.
    start ms-windows-store://pdp/?productid=9PJPW5LDXLZ5
    pause
    exit /b 1
) ELSE (
    echo [OK] Python is installed!
)

:: --- 2. PYTHON LIBRARIES ---
echo.
echo [2/6] Installing Python AI Libraries...
python -m pip install -r requirements.txt

:: --- 3. OLLAMA ENGINE CHECK ---
echo.
echo [3/6] Checking for Ollama AI Engine...
ollama --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [X] Ollama is not installed!
    echo.
    echo Opening your browser to download Ollama for Windows...
    start https://ollama.com/download/windows
    echo Please install Ollama, then run this setup.bat file again.
    pause
    exit /b 1
) ELSE (
    echo [OK] Ollama is installed!
)

:: --- 4. QWEN ANALYST MODEL ---
echo.
echo [4/6] Checking Qwen 2.5 Model...
echo (Downloading the AI weights. This may take a few minutes...)
ollama pull qwen2.5

:: --- 5. BUILD THE VECTOR DATABASE ---
echo.
echo [5/6] Building the Local Legal Database (Lite Edition)...
echo This will take about 60 seconds...
python build_lite_index.py

:: --- 6. LAUNCH ---
echo.
echo [6/6] SETUP COMPLETE!
echo Launching Cora AI in your web browser...
python -m streamlit run app.py
pause