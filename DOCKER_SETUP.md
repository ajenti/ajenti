# Docker Setup Guide for Ajenti 3 Development

This guide will help you set up Ajenti 3 using Docker for development purposes.

> **⚠️ Important Note**: This Docker setup is intended **strictly for development purposes only**. 
> Containerizing Ajenti is **not recommended for production environments** as Ajenti is designed to 
> directly access and manage Linux server resources. Containerization would limit Ajenti's capabilities 
> to manage the host system effectively.

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Node.js and Yarn (for frontend development)
- At least 2GB of free RAM
- Port 8001 available (or modify the port in docker-compose.yml)

## Quick Start

### 1. Start the Backend Container

```bash
# Build and start the container
docker-compose up --build -d

# Check if the container is running
docker ps

# View logs
docker logs ajenti-ajenti-3-development-backend-1 -f
```

The backend will be available at `http://localhost:8001`

### 2. Build the Frontend (Required for Development)

The Docker container runs the backend, but you need to build the frontend separately:

#### Build ngx-ajenti library (required first):
```bash
cd plugins-new/ngx-ajenti
yarn install
yarn run build
```

#### Build and run the core plugin (shell):
```bash
cd plugins-new/core/frontend
yarn install
ln -nsf ../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core
cp proxy.conf.template.json proxy.conf.json
yarn start
```

The frontend will be available at `http://localhost:4200`

#### Build additional plugins (e.g., dashboard):
```bash
cd plugins-new/dashboard/frontend
yarn install
ln -nsf ../../../ngx-ajenti/dist/ngx-ajenti node_modules/@ngx-ajenti/core
cp proxy.conf.template.json proxy.conf.json
# Edit angular.json to use a different port if needed (e.g., 4201)
yarn start
```

## Container Configuration

### Ports
- **8001**: Backend API (mapped from container port 8000)
- **4200+**: Frontend development servers (not containerized)

### Volumes
The following directories are mounted into the container:
- `./.container/etc/` → `/etc/ajenti/` (configuration files)
- `./.container/config/` → `/root/.config/` (user configuration)
- `./` → `/opt/ajenti/backend/` (source code with hot reload)

## Useful Docker Commands

### View Container Logs
```bash
docker logs ajenti-ajenti-3-development-backend-1 -f
```

### Stop the Container
```bash
docker-compose down
```

### Restart the Container
```bash
docker-compose restart
```

### Execute Commands Inside Container
```bash
docker exec -it ajenti-ajenti-3-development-backend-1 /bin/bash
```

### Rebuild Container (after Dockerfile changes)
```bash
docker-compose up --build -d
```

## Accessing Ajenti

1. **Backend API**: `http://localhost:8001`
2. **Frontend (Development)**: `http://localhost:4200` (after building frontend)
3. **Default Login**: Autologin is enabled in development mode (root user)

## Troubleshooting

### Port Already in Use
If you see an error about port 8001 being in use:

1. Check what's using the port:
   ```bash
   lsof -i :8001  # Linux/Mac
   netstat -ano | findstr :8001  # Windows
   ```

2. Either stop the conflicting service or change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "8002:8000"  # Use 8002 instead
   ```

### Frontend 404 Errors
If you see 404 errors for JavaScript/CSS files, you need to build the frontend:
- Follow the "Build the Frontend" section above
- Make sure ngx-ajenti is built first
- Ensure the proxy.conf.json is configured correctly

### Container Won't Start
```bash
# Check container status
docker ps -a

# View detailed logs
docker logs ajenti-ajenti-3-development-backend-1

# Remove and recreate
docker-compose down
docker-compose up --build -d
```

### Permission Issues
The container runs as root. If you encounter permission issues with mounted volumes:
```bash
# On Linux/Mac, you may need to adjust permissions
sudo chown -R $USER:$USER ./.container/
```

## Development Workflow

1. **Backend Changes**: 
   - Edit Python files in the workspace
   - Changes are reflected immediately (volume mount)
   - Watch logs: `docker logs ajenti-ajenti-3-development-backend-1 -f`

2. **Frontend Changes**:
   - Edit TypeScript/Angular files
   - Frontend dev server auto-reloads (if using `--watch`)
   - Keep `yarn start` running in separate terminal

3. **Adding New Plugins**:
   - Follow the plugin development guide
   - Build ngx-ajenti first
   - Set up plugin frontend as described in ManualFrontendSetup.md

## Production Deployment

**Do not use this Docker setup for production!** 

For production deployment:
- Install Ajenti directly on the host system
- Follow the official installation guide: https://docs.ajenti.org/
- Use the provided installation script or package manager

## Additional Resources

- [Official Documentation](https://docs.ajenti.org/)
- [Plugin Development Guide](https://docs.ajenti.org/en/latest/dev/intro.html)
- [Manual Frontend Setup](ManualFrontendSetup.md)
- [GitHub Repository](https://github.com/ajenti/ajenti)

## Configuration Files

### Default Configuration Location
- Config: `/etc/ajenti/config.yml` (inside container)
- Users: `/etc/ajenti/users.yml`
- SMTP: `/etc/ajenti/smtp.yml`
- TFA: `/etc/ajenti/tfa.yml`

These files are mounted from `./.container/etc/` on your host system.

## Container Details

- **Base Image**: Ubuntu 22.04
- **Python Version**: 3.10.12
- **Entrypoint**: `make rundev` (development mode with autologin)
- **Working Directory**: `/opt/ajenti/backend`

## Next Steps

After setup:
1. Access the backend API at `http://localhost:8001`
2. Build and run the frontend at `http://localhost:4200`
3. Start developing plugins or core features
4. Refer to ManualFrontendSetup.md for detailed frontend setup
5. Check the official docs for plugin development

---

**Happy coding! 🚀**
