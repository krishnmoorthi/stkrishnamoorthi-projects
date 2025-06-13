python#!/bin/bash

# Setup Python environment
python -m venv venv
cd venv/Scripts
./activate
pip install -r requirements.txt

# Setup Node.js environment
cd node
npm install
cd ..

echo "Setup complete. Don't forget to:"
echo "1. Create a .env file with your configuration"
echo "2. Set the SCAN_PROJECT_PATH to your Node.js project directory"