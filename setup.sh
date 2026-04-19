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
echo "✅ Setup Complete!"
echo "To get started:"
echo "  1. Fill in your API keys in the .env file"
echo "  2. Review config/hunter_config.yaml"
echo "  3. Run: poetry shell"
echo "  4. Run: intern-hunter start"
echo "====================================================="
