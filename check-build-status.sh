#!/bin/bash
# Check Ajenti Frontend Build Status

echo "========================================="
echo "Ajenti Frontend Build Status Checker"
echo "========================================="
echo ""

SHELL_BUILD_DIR="/mnt/c/Users/james/OneDrive/Desktop/panels/2/ajenti/plugins-new/shell/resources/build"
NGX_AJENTI_DIST="/mnt/c/Users/james/OneDrive/Desktop/panels/2/ajenti/plugins-new/ngx-ajenti/dist/ngx-ajenti"

# Check ngx-ajenti
echo "1. Checking ngx-ajenti library..."
if [ -d "$NGX_AJENTI_DIST" ]; then
    echo "   ✅ ngx-ajenti is built"
    echo "   Location: $NGX_AJENTI_DIST"
else
    echo "   ❌ ngx-ajenti NOT built"
    echo "   Run: cd plugins-new/ngx-ajenti && yarn run build"
fi

echo ""

# Check shell plugin
echo "2. Checking shell plugin build..."
if [ -d "$SHELL_BUILD_DIR" ]; then
    echo "   ✅ Shell plugin build directory exists"
    
    # Check for required files
    FILES=("main.js" "polyfills.js" "all.vendor.js" "all.css")
    MISSING=()
    
    for file in "${FILES[@]}"; do
        if [ -f "$SHELL_BUILD_DIR/$file" ]; then
            SIZE=$(du -h "$SHELL_BUILD_DIR/$file" | cut -f1)
            echo "   ✅ $file ($SIZE)"
        else
            echo "   ❌ $file - MISSING"
            MISSING+=("$file")
        fi
    done
    
    if [ ${#MISSING[@]} -eq 0 ]; then
        echo ""
        echo "   🎉 All required files are present!"
    else
        echo ""
        echo "   ⚠️  Missing ${#MISSING[@]} file(s). Build may be incomplete."
    fi
else
    echo "   ❌ Shell plugin NOT built"
    echo "   Run: cd plugins-new/shell/frontend && yarn run build"
fi

echo ""
echo "========================================="

# Check if build is currently running
if ps aux | grep -E "ng build|yarn.*build" | grep -v grep > /dev/null; then
    echo "   ⏳ Build process is currently running..."
    echo "   Wait for it to complete or check with: ps aux | grep 'ng build'"
else
    echo "   No active build process detected"
fi

echo "========================================="
