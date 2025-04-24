# Django Project Change Management Guide

This guide outlines the steps to handle different types of changes in the Django project.

## 1. Development Environment Changes

### Model Changes
1. Make changes to models in `models.py`
2. Create migrations:
   ```bash
   ./scripts/manage_dev.sh makemigrations
   ```
3. Apply migrations:
   ```bash
   ./scripts/manage_dev.sh migrate
   ```

### Template Changes
1. Make changes to templates in `templates/` directory
2. Restart development server:
   ```bash
   ./scripts/manage_dev.sh runserver
   ```

### Static Files Changes
1. Make changes to static files (CSS, JS, images)
2. Build static files:
   ```bash
   ./scripts/manage_dev.sh build
   ```

### Form Changes
1. Make changes to forms in `forms.py`
2. Restart development server:
   ```bash
   ./scripts/manage_dev.sh runserver
   ```

## 2. Production Environment Changes

### Model Changes
1. Make changes to models in `models.py`
2. Create migrations:
   ```bash
   ./scripts/manage_dev.sh makemigrations
   ```
3. Apply migrations:
   ```bash
   ./scripts/manage_prod.sh migrate
   ```

### Template Changes
1. Make changes to templates in `templates/` directory
2. Reload services:
   ```bash
   ./scripts/manage_prod.sh reload
   ```

### Static Files Changes
1. Make changes to static files
2. Build and collect static files:
   ```bash
   ./scripts/manage_prod.sh build
   ```

### Tailwind CSS Configuration
1. Tailwind CSS is now properly configured for production use:
   - Removed CDN version from base.html
   - Using PostCSS plugin configuration
   - CSS is built and served through Django's static files system

2. To build Tailwind CSS:
   ```bash
   npm run build
   ```

3. For production builds with minification:
   ```bash
   npm run build:prod
   ```

4. After building Tailwind CSS, collect static files:
   ```bash
   ./scripts/manage_prod.sh build
   ```

### Form Changes
1. Make changes to forms in `forms.py`
2. Reload services:
   ```bash
   ./scripts/manage_prod.sh reload
   ```

## 3. Common Commands

### Development Environment
- Start server: `./scripts/manage_dev.sh runserver`
- Stop server: `./scripts/manage_dev.sh stop`
- Create superuser: `./scripts/manage_dev.sh createsuperuser`
- Open shell: `./scripts/manage_dev.sh shell`
- Full setup: `./scripts/manage_dev.sh setup`

### Production Environment
- Restart services: `./scripts/manage_prod.sh restart`
- Reload services: `./scripts/manage_prod.sh reload`
- Check status: `./scripts/manage_prod.sh status`
- View logs: `./scripts/manage_prod.sh logs`

## 4. Best Practices

1. **Always test changes in development first**
2. **Backup database before migrations**
3. **Use version control for all changes**
4. **Document all model changes**
5. **Clear browser cache after static file changes**
6. **Monitor logs after production changes**

## 5. Troubleshooting

If changes don't appear:
1. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
2. Check logs: `./scripts/manage_prod.sh logs`
3. Verify service status: `./scripts/manage_prod.sh status`
4. Try full restart: `./scripts/manage_prod.sh restart`

## 6. Emergency Procedures

If services fail:
1. Check status: `./scripts/manage_prod.sh status`
2. View logs: `./scripts/manage_prod.sh logs`
3. Restart services: `./scripts/manage_prod.sh restart`
4. If issues persist, contact system administrator

## 7. Server Reboot Procedures

### Before Reboot
1. Check for active users or ongoing processes:
   ```bash
   ./scripts/manage_prod.sh status
   ```
2. Create a backup:
   ```bash
   ./scripts/manage_prod.sh backup_db
   ```

### After Reboot
The systemd service (`smdr.service`) will automatically start all required services in the correct order:
1. Nginx web server
2. Gunicorn application server
3. Django application

To verify the startup:
```bash
# Check systemd service status
sudo systemctl status smdr

# Check individual services
sudo systemctl status nginx
ps aux | grep gunicorn

# View startup logs
sudo journalctl -u smdr
```

### Manual Service Management
If automatic startup fails, you can manually start the services:
```bash
# Start all services
./scripts/start_servers.sh

# Check service status
sudo systemctl status nginx
ps aux | grep gunicorn
```

### Troubleshooting After Reboot
If issues occur after reboot:
1. Check systemd service status: `sudo systemctl status smdr`
2. Review service logs: `sudo journalctl -u smdr`
3. Verify PostgreSQL is running
4. Check file permissions in project directory
5. Ensure virtual environment is accessible
6. Review system logs for any startup errors 