#!/usr/bin/env bash
set -e

echo "====================================================="
echo "   🚀 Setting up Intern-Hunter-AI (2026 Edition) 🚀  "
echo "====================================================="

# Check for Poetry
if ! command -v poetry &> /dev/null
then
    echo "📦 Poetry could not be found. Installing via official installer..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "📦 Installing Python dependencies..."
poetry install

echo "🌐 Installing Playwright browsers..."
poetry run playwright install chromium

echo "📑 Checking system dependencies for WeasyPrint (PDF Generation)..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux detected. Attempting to install required Pango/Cairo libraries..."
    sudo apt-get update && sudo apt-get install -y \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libjpeg-dev \
        libopenjp2-7-dev \
        libffi-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS detected. Checking for Homebrew..."
    if command -v brew &> /dev/null; then
        brew install pango pango libffi
    else
        echo "Please install Homebrew to install WeasyPrint dependencies."
    fi
else
    echo "OS not automatically supported for WeasyPrint system dependencies. Please ensure Pango/Cairo are installed, or use Docker."
fi

echo "📝 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example. Please populate it with your API keys!"
else
    echo "✅ .env file already exists."
fi

echo "📁 Setting up Obsidian Vault structure..."
mkdir -p obsidian_template/Internships/Templates
mkdir -p exports

echo "====================================================="
echo "✅ Setup Complete! Launching InternHunter Interactive Mode..."
echo "====================================================="
mkdir -p ~/.local/bin

cat > ~/.local/bin/intern-hunter << EOF
#!/bin/bash
# === InternHunter Global Wrapper ===
PROJECT_DIR="$(pwd)"

cd "\$PROJECT_DIR" 2>/dev/null || {
    echo "❌ Error: Cannot find InternHunter folder at \$PROJECT_DIR"
    echo "Please update the PROJECT_DIR path in ~/.local/bin/intern-hunter"
    exit 1
}

poetry run intern-hunter "\$@"
EOF

chmod +x ~/.local/bin/intern-hunter

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    export PATH="$HOME/.local/bin:$PATH"
    echo "✅ Added ~/.local/bin to your PATH. Please run 'source ~/.bashrc' or restart your terminal."
fi

echo "🔗 'intern-hunter' command is now available globally!"
echo "====================================================="
poetry run intern-hunter setup


