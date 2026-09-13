#!/bin/bash
set -e

PLUGIN_DIR="$HOME/.gemini/config/plugins/supersep"
echo "========================================="
echo "  Installing SuperSep Global Plugin"
echo "========================================="

echo "1. Creating plugin directory: $PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

echo "2. Copying SuperSep files..."
rsync -av --exclude='.venv' --exclude='.git' ./ "$PLUGIN_DIR/"

echo "3. Initializing virtual environment in plugin..."
cd "$PLUGIN_DIR"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

if [ ! -f "$PLUGIN_DIR/.env" ]; then
    cp "$PLUGIN_DIR/.env.example" "$PLUGIN_DIR/.env"
    echo "Created default .env from .env.example. Please update your ROUTER_API_KEY in $PLUGIN_DIR/.env"
fi

echo "========================================="
echo "  SuperSep Installed Successfully!"
echo "  Commands available in any workspace:"
echo "  - /mikirsep <ide / kebutuhan>"
echo "  - /gassep   <task / blueprint>"
echo "  - /commitsep [pesan commit]"
echo "========================================="
