#!/bin/bash
# Installation script for H5P Transcript Generator V2

set -e  # Exit on error

echo "======================================"
echo "H5P Transcript Generator V2 - Setup"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
if ! pip3 install -r requirements.txt; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Setup .env file
echo "Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file and add your Gemini API key!"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter to open .env in nano editor (or Ctrl+C to skip)..."
    nano .env 2>/dev/null || vi .env 2>/dev/null || echo "Please edit .env manually"
else
    echo "✅ .env file already exists"
fi
echo ""

# Check for template
echo "Checking for H5P template..."
if [ ! -d "templates" ]; then
    mkdir -p templates
    echo "⚠️  Created templates/ directory"
    echo "   Please add your template.zip file to: templates/template.zip"
elif [ ! -f "templates/template.zip" ]; then
    echo "⚠️  Template not found at: templates/template.zip"
    echo "   Please add your H5P template file"
else
    echo "✅ Template found"
fi
echo ""

# Test installation
echo "Testing installation..."
if python3 -c "import streamlit, google.generativeai, dotenv, cv2, PIL" 2>/dev/null; then
    echo "✅ All modules imported successfully"
else
    echo "⚠️  Some modules could not be imported. Please check the error messages above."
fi
echo ""

# Print next steps
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Verify your Gemini API key is set in .env"
echo "2. Ensure templates/template.zip exists"
echo "3. Run the application:"
echo ""
echo "   Streamlit UI:"
echo "   $ streamlit run orchestrator_v2.py"
echo ""
echo "   Command Line:"
echo "   $ python3 cli_generator.py -t transcript.txt -u 'video_url' -n 'Title'"
echo ""
echo "For detailed instructions, see:"
echo "  - README.md (comprehensive guide)"
echo "  - QUICKSTART.md (quick start guide)"
echo ""
echo "Happy generating! 🎉"
