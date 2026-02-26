#!/bin/bash

echo "==================================================="
echo "Copyright of Automotive Artificial Intelligence (AAI) GmbH"
echo "⚖️  CORA LEGAL AI (LITE) - AUTOMATED INSTALLER"
echo "==================================================="

# --- 1. PYTHON CHECK & INSTALL ---
echo -e "\n🐍 [1/6] Checking for Python 3..."
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed!"
    echo "⏳ Attempting to trigger Apple's native installer..."
    xcode-select --install
    echo "⚠️  Please complete the Apple installation window that just popped up."
    echo "   Once Python is installed, run this ./setup.sh script again."
    exit 1
else
    echo "✅ Python 3 is installed!"
fi

# --- 2. PIP CHECK ---
echo -e "\n📦 [2/6] Checking Python Package Manager (pip)..."
if ! command -v pip3 &> /dev/null
then
    echo "⚠️ pip3 is missing. Installing pip..."
    python3 -m ensurepip --upgrade
else
    echo "✅ pip is ready!"
fi

# --- 3. PYTHON LIBRARIES ---
echo -e "\n📚 [3/6] Installing Python AI Libraries..."
python3 -m pip install -r requirements.txt

# --- 4. OLLAMA ENGINE ---
echo -e "\n⚙️  [4/6] Checking for Ollama AI Engine..."
if ! command -v ollama &> /dev/null
then
    echo "📥 Ollama not found! Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama is already installed!"
fi

# --- 5. QWEN ANALYST MODEL ---
echo -e "\n🧠 [5/6] Booting AI Engine and checking Qwen 2.5 Model..."
# Silently start the Ollama background app if it isn't running
ollama serve > /dev/null 2>&1 & 
sleep 3 # Give the engine a moment to wake up

echo "⏳ Downloading Qwen 2.5 Analyst Model (This may take a few minutes on the first run)..."
ollama pull qwen2.5

# --- 6. BUILD THE VECTOR DATABASE ---
echo -e "\n🔍 [6/6] Building the Local Legal Database (Lite Edition)..."
echo "This will take about 60 seconds..."
python3 build_lite_index.py

# --- LAUNCH ---
echo -e "\n🎉 SETUP COMPLETE!"
echo "🚀 Launching Cora AI in your web browser..."
python3 -m streamlit run app.py