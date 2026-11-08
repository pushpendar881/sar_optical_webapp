#!/bin/bash

# Unix/Linux/macOS setup script for SAR-to-Optical web app

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/your/seg_cyclegan_project"
    echo ""
    echo "Example: $0 ~/seg_cyclegan_project"
    exit 1
fi

echo "Setting up SAR-to-Optical web app..."
python3 setup.py "$1"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
else
    echo ""
    echo "❌ Setup failed!"
    exit 1
fi