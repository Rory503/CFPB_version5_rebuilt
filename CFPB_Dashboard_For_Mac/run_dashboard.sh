#!/bin/bash
# CFPB Dashboard Launcher for Mac/Linux
# Double-click this file to start the dashboard

echo "=========================================="
echo "CFPB Consumer Complaint Analytics"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing required packages (this may take a few minutes on first run)..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✓ All packages installed"
echo ""
echo "=========================================="
echo "Starting CFPB Dashboard..."
echo "Your browser will open automatically"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start the dashboard
streamlit run web_dashboard.py --server.headless=true

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Dashboard failed to start"
    read -p "Press Enter to exit..."
fi
