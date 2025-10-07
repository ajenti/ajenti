# Quick Reference: Fixing the 404 Errors

## The Problem You're Seeing
```
resources/core/resources/build/polyfills.js - 404 Not Found
resources/core/resources/build/main.js - 404 Not Found  
all.vendor.js - 404 Not Found
all.css - 404 Not Found
```

## Why This Happens
The Docker container only runs the Python backend. The Angular frontend needs to be built separately.

## ✅ Quick Solution

### Option 1: Automated Build (Recommended)
```bash
./build-frontend.sh
```

Wait 5-10 minutes for the build to complete, then refresh your browser.

### Option 2: Manual Build
```bash
# Step 1: Build ngx-ajenti library (~3-5 min)
cd plugins-new/ngx-ajenti
yarn install
yarn run build

# Step 2: Build shell plugin (~2-4 min)
cd ../shell/frontend
yarn install
rm -rf node_modules/@ngx-ajenti/core
mkdir -p node_modules/@ngx-ajenti
cp -r ../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core
cp proxy.conf.template.json proxy.conf.json
yarn run build

# Step 3: Refresh browser
# Navigate to http://localhost:8001
```

### Option 3: Development Mode (For Active Development)
```bash
# Terminal 1 - Backend already running in Docker
docker-compose up -d

# Terminal 2 - Frontend with hot reload
cd plugins-new/shell/frontend
yarn install
rm -rf node_modules/@ngx-ajenti/core
mkdir -p node_modules/@ngx-ajenti
cp -r ../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core
yarn start

# Access at: http://localhost:4200 (with auto-reload)
```

## Check Build Status
```bash
./check-build-status.sh
```

## Verify It's Fixed
1. Navigate to `http://localhost:8001`
2. Open browser console (F12)
3. No 404 errors = Success! ✅
4. UI loads properly = Success! ✅

## Important Notes

### For WSL/Windows Users
- Use `cp` instead of `ln -s` when linking ngx-ajenti
- Symlinks may not work properly in WSL environments
- The build scripts have been updated to use `cp`

### Build Output Location
The shell plugin builds to:
```
plugins-new/shell/resources/build/
```

This is where Ajenti looks for the frontend files.

## Still Having Issues?

### Check if ngx-ajenti is built:
```bash
ls -la plugins-new/ngx-ajenti/dist/ngx-ajenti/
```
Should show files including `package.json`, `fesm2015`, `fesm2020`, etc.

### Check if shell plugin is built:
```bash
ls -la plugins-new/shell/resources/build/
```
Should show `main.js`, `polyfills.js`, `all.vendor.js`, `all.css`

### View detailed troubleshooting:
```bash
cat TROUBLESHOOTING_404.md
```

### Check Docker logs:
```bash
docker logs ajenti-ajenti-3-development-backend-1 -f
```

Look for 200 responses instead of 404 when accessing resources.

## Timeline
- First time setup: 10-15 minutes (includes yarn install)
- Subsequent builds: 3-5 minutes
- Development mode startup: 2-3 minutes

## Next Steps After Fix
1. ✅ Frontend resources load (no 404s)
2. ✅ Ajenti UI appears
3. ✅ Login as root (autologin enabled in dev mode)
4. Start developing!

---

**Need the full setup guide?** See `DOCKER_SETUP.md`  
**Need troubleshooting help?** See `TROUBLESHOOTING_404.md`
