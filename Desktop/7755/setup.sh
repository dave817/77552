#!/bin/bash

echo "=================================="
echo "Dating Chatbot Setup Script"
echo "=================================="

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found: $(python3 --version)"
else
    echo "✗ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install pip if not available
if ! python3 -m pip --version &> /dev/null; then
    echo "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt --user

echo ""
echo "=================================="
echo "Setup completed!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run tests: python3 test_api.py"
echo "2. Start server: python3 -m uvicorn backend.main:app --reload"
echo "3. Open browser: http://localhost:8000/ui"
echo ""
