# SMDR - Social Media Data Repository

A Django-based web application for managing social media data with a modern UI built using Tailwind CSS.

## Features

- User authentication and authorization
- Social authentication (Google)
- Email verification
- Profile management
- Modern UI with Tailwind CSS
- Responsive design
- Secure password management

## Tech Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL
- **Frontend**: 
  - Tailwind CSS
  - Alpine.js
- **Authentication**: django-allauth
- **Production Server**: Gunicorn + Nginx

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Nginx

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smdr
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Node.js dependencies:
```bash
npm install
```

5. Create a `.env` file in the project root with the following variables:
```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgres://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

6. Set up the database:
```bash
python manage.py migrate
```

7. Build Tailwind CSS:
```bash
npm run build:prod
```

8. Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Development

1. Start the development server:
```bash
bash scripts/dev.sh
```

2. For production deployment:
```bash
bash scripts/manage_gunicorn.sh start
```

## Project Structure

```
smdr/
├── smdrproject/          # Main project settings
├── smdr/                 # Main application
├── static/              # Static files
│   ├── css/            # CSS source files
│   └── js/             # JavaScript files
├── staticfiles/         # Collected static files
├── templates/           # HTML templates
├── scripts/            # Management scripts
└── venv/               # Virtual environment
```

## Available Scripts

- `scripts/dev.sh`: Development environment setup
- `scripts/manage_gunicorn.sh`: Gunicorn process management
- `scripts/backup.sh`: Create project backups
- `scripts/cleanup.sh`: Clean up development artifacts
- `scripts/start_servers.sh`: Start all production servers (nginx, gunicorn, django)
- `scripts/manage_users.sh`: User account management

## Server Management

The application uses a systemd service for automatic startup and management:

### Systemd Service
The `smdr.service` is installed in `/etc/systemd/system/` and provides:
- Automatic startup on system boot
- Service monitoring and automatic restart
- Centralized logging via syslog
- Proper service dependencies

### Managing the Service
```bash
# Start the service
sudo systemctl start smdr

# Stop the service
sudo systemctl stop smdr

# Check status
sudo systemctl status smdr

# View logs
sudo journalctl -u smdr

# Enable automatic startup
sudo systemctl enable smdr

# Disable automatic startup
sudo systemctl disable smdr
```

### Manual Server Management
For manual server management, use:
```bash
# Start all servers
./scripts/start_servers.sh

# Check server status
sudo systemctl status nginx
ps aux | grep gunicorn
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.

## Acknowledgments

- Django Framework
- Tailwind CSS
- django-allauth
- All contributors and maintainers

# SMDR Project

## Management Scripts

The project includes several management scripts in the `scripts/` directory:

### Core Management Scripts
- `manage_prod.sh` - Production environment management (services, backups, deployments)
- `manage_dev.sh` - Development environment management (server, migrations, builds)

### System Scripts
- `set_timezone.sh` - Server timezone configuration
- `cleanup.sh` - System maintenance and cleanup tasks
- `setup_site.py` - Initial site configuration

### Usage Examples

#### Development Environment
```bash
# Start development server
./scripts/manage_dev.sh runserver

# Setup development environment
./scripts/manage_dev.sh setup

# Create database migrations
./scripts/manage_dev.sh makemigrations

# Apply migrations
./scripts/manage_dev.sh migrate

# Build static files
./scripts/manage_dev.sh build
```

#### Production Environment
```bash
# Restart all services
./scripts/manage_prod.sh restart

# Reload services gracefully
./scripts/manage_prod.sh reload

# Check service status
./scripts/manage_prod.sh status

# View logs
./scripts/manage_prod.sh logs

# Create database backup
./scripts/manage_prod.sh backup_db
```

For detailed change management procedures, see [CHANGES.md](CHANGES.md).
