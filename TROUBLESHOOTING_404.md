# Troubleshooting 404 Errors for Frontend Resources

## Problem
You're seeing 404 errors for these files:
```
resources/core/resources/build/polyfills.js
resources/core/resources/build/main.js
all.vendor.js
all.css
```

## Root Cause
The Docker container only runs the Ajenti **backend**. The frontend files need to be built separately using Angular/Node.js.

## Solution: Build the Frontend

### Quick Fix (Automated)
Run the automated build script:
```bash
./build-frontend.sh
```

### Manual Steps

#### Step 1: Build ngx-ajenti Library (Required First)
```bash
cd plugins-new/ngx-ajenti
yarn install
yarn run build
```

**Expected Output:**
- Build should complete successfully
- Files will be in `dist/ngx-ajenti/`
- Takes ~3-5 minutes

#### Step 2: Build Shell Plugin (Main UI)
```bash
cd ../shell/frontend
yarn install

# Create symlink to ngx-ajenti
rm -rf node_modules/@ngx-ajenti/core
mkdir -p node_modules/@ngx-ajenti
ln -nsf ../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core

# Copy proxy configuration
cp proxy.conf.template.json proxy.conf.json

# Build the plugin
yarn run build
```

**Expected Output:**
- Build creates files in `plugins-new/shell/resources/build/`
- Files created:
  - `main.js`
  - `polyfills.js`
  - `all.vendor.js`
  - `all.css`
  - Other compiled assets

#### Step 3: Restart Docker Container (if needed)
```bash
docker-compose restart
```

#### Step 4: Access Ajenti
Navigate to: `http://localhost:8001`

The 404 errors should now be resolved!

## Alternative: Development Mode with Hot Reload

Instead of building for production, you can run in development mode with auto-reload:

```bash
# Terminal 1: Backend (already running in Docker)
docker-compose up -d

# Terminal 2: Frontend development server
cd plugins-new/shell/frontend
yarn start

# Access at http://localhost:4200 (with hot reload)
```

In this mode:
- Changes to TypeScript/Angular files auto-reload
- No need to rebuild after each change
- Perfect for active development

## Verification

### Check if Frontend is Built
```bash
ls -la plugins-new/shell/resources/build/
```

You should see files like:
```
main.js
polyfills.js
all.vendor.js
all.css
```

### Check Backend Logs
```bash
docker logs ajenti-ajenti-3-development-backend-1 -f
```

Look for successful file serving (200 responses instead of 404).

### Test in Browser
Open `http://localhost:8001` and check the browser console.
- No 404 errors = Success!
- UI loads properly = Success!

## Common Issues

### Issue: "Cannot find module '@ngx-ajenti/core'"
**Solution:** Create the symlink:
```bash
cd plugins-new/shell/frontend
ln -nsf ../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core
```

### Issue: "ngx-ajenti dist folder not found"
**Solution:** Build ngx-ajenti first:
```bash
cd plugins-new/ngx-ajenti
yarn run build
```

### Issue: Build fails with peer dependency warnings
**Solution:** These warnings are usually safe to ignore. The build should still complete.

### Issue: Port 4200 already in use
**Solution:** Edit `angular.json` and change the port:
```json
"serve": {
  "options": {
    "port": 4201
  }
}
```

### Issue: Resources still showing 404 after build
**Possible causes:**
1. Build output path is incorrect
2. Docker container needs restart
3. Files weren't copied properly

**Solution:**
```bash
# Verify build output
ls -la plugins-new/shell/resources/build/

# Restart container
docker-compose restart

# Clear browser cache
# Hard refresh: Ctrl+Shift+R (Linux/Windows) or Cmd+Shift+R (Mac)
```

## Build Times

Expected build times on average hardware:
- ngx-ajenti: 3-5 minutes (first time), 30-60 seconds (subsequent)
- shell plugin: 2-4 minutes (first time), 30-60 seconds (subsequent)
- Additional plugins: 1-2 minutes each

## Architecture Overview

```
┌─────────────────────────────────────┐
│   Docker Container (Backend)        │
│                                     │
│   - Python/Ajenti Core              │
│   - REST API                        │
│   - Port: 8000 (mapped to 8001)    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Frontend (Angular/TypeScript)     │
│                                     │
│   Option 1: Production Build        │
│   - Compiled to static files        │
│   - Served by backend              │
│   - Access: http://localhost:8001   │
│                                     │
│   Option 2: Dev Server             │
│   - Hot reload enabled             │
│   - Proxies API to backend         │
│   - Access: http://localhost:4200   │
└─────────────────────────────────────┘
```

## Need More Help?

1. Check the full setup guide: `DOCKER_SETUP.md`
2. View frontend setup details: `ManualFrontendSetup.md`
3. Check container logs: `docker logs ajenti-ajenti-3-development-backend-1 -f`
4. Verify backend is running: `curl -I http://localhost:8001`

## Quick Command Reference

```bash
# Build everything
./build-frontend.sh

# Or step by step:
cd plugins-new/ngx-ajenti && yarn install && yarn run build
cd ../shell/frontend && yarn install && yarn run build

# Development mode
cd plugins-new/shell/frontend && yarn start

# Check Docker status
docker ps
docker logs ajenti-ajenti-3-development-backend-1

# Restart everything
docker-compose restart
```
