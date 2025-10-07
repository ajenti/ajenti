#!/bin/bash
# Ajenti 3 Frontend Build Script
# This script builds all necessary frontend components

set -e

echo "========================================"
echo "Ajenti 3 Frontend Build Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGINS_DIR="$SCRIPT_DIR/plugins-new"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js is not installed${NC}"
    echo "Please install Node.js first: https://nodejs.org/"
    exit 1
fi

# Check if Yarn is installed
if ! command -v yarn &> /dev/null; then
    echo -e "${RED}❌ Error: Yarn is not installed${NC}"
    echo "Please install Yarn first: npm install -g yarn"
    exit 1
fi

echo -e "${GREEN}✅ Node.js version: $(node --version)${NC}"
echo -e "${GREEN}✅ Yarn version: $(yarn --version)${NC}"
echo ""

# Step 1: Build ngx-ajenti library
echo "========================================"
echo "Step 1/3: Building ngx-ajenti library"
echo "========================================"
cd "$PLUGINS_DIR/ngx-ajenti"

if [ ! -d "node_modules" ]; then
    echo "Installing ngx-ajenti dependencies..."
    yarn install
else
    echo "Dependencies already installed, skipping..."
fi

echo "Building ngx-ajenti..."
yarn run build

if [ ! -d "dist/ngx-ajenti" ]; then
    echo -e "${RED}❌ Error: ngx-ajenti build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ ngx-ajenti built successfully${NC}"
echo ""

# Step 2: Build shell/core plugin (main UI)
echo "========================================"
echo "Step 2/3: Building shell plugin"
echo "========================================"
cd "$PLUGINS_DIR/shell/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing shell plugin dependencies..."
    yarn install
else
    echo "Dependencies already installed, skipping..."
fi

# Copy ngx-ajenti (use copy instead of symlink for WSL compatibility)
echo "Copying ngx-ajenti library..."
rm -rf node_modules/@ngx-ajenti/core
mkdir -p node_modules/@ngx-ajenti
cp -r "$PLUGINS_DIR/ngx-ajenti/dist/ngx-ajenti" node_modules/@ngx-ajenti/core

# Copy proxy config if it doesn't exist
if [ ! -f "proxy.conf.json" ]; then
    echo "Creating proxy.conf.json..."
    cp proxy.conf.template.json proxy.conf.json
fi

echo "Building shell plugin..."
yarn run build

if [ ! -d "dist" ]; then
    echo -e "${RED}❌ Error: shell plugin build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Shell plugin built successfully${NC}"
echo ""

# Step 3: Build other plugins (optional)
echo "========================================"
echo "Step 3/3: Building additional plugins"
echo "========================================"

ADDITIONAL_PLUGINS=("dashboard" "fstab" "session_list" "traffic")

for plugin in "${ADDITIONAL_PLUGINS[@]}"; do
    if [ -d "$PLUGINS_DIR/$plugin/frontend" ]; then
        echo ""
        echo "Building $plugin plugin..."
        cd "$PLUGINS_DIR/$plugin/frontend"
        
        if [ ! -d "node_modules" ]; then
            echo "Installing $plugin dependencies..."
            yarn install
        fi
        
        # Copy ngx-ajenti (use copy instead of symlink for WSL compatibility)
        rm -rf node_modules/@ngx-ajenti/core
        mkdir -p node_modules/@ngx-ajenti
        cp -r "$PLUGINS_DIR/ngx-ajenti/dist/ngx-ajenti" node_modules/@ngx-ajenti/core
        
        # Copy proxy config if it doesn't exist
        if [ ! -f "proxy.conf.json" ] && [ -f "proxy.conf.template.json" ]; then
            cp proxy.conf.template.json proxy.conf.json
        fi
        
        echo "Building $plugin..."
        yarn run build
        
        if [ -d "dist" ]; then
            echo -e "${GREEN}✅ $plugin built successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  $plugin build failed or no dist folder${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  $plugin frontend not found, skipping...${NC}"
    fi
done

echo ""
echo "========================================"
echo "✅ Frontend Build Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. The backend is already running at: http://localhost:8001"
echo "2. Access Ajenti at: http://localhost:8001"
echo ""
echo "For development with hot reload:"
echo "  cd plugins-new/shell/frontend && yarn start"
echo "  Then access at: http://localhost:4200"
echo ""
