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
