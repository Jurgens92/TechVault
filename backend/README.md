# TechVault Backend

Enterprise-grade IT documentation platform backend built with Django 5, Django REST Framework, and PostgreSQL.

## Tech Stack

- **Framework**: Django 5.0.1
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL
- **Authentication**: Django-allauth + SimpleJWT
- **Social Auth**: GitHub OAuth

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip and virtualenv

## Local Development Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up PostgreSQL Database

```bash
# Install PostgreSQL (if not already installed)
# On macOS:
brew install postgresql@14
brew services start postgresql@14

# On Ubuntu/Debian:
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# On Windows:
# Download and install from https://www.postgresql.org/download/windows/
```

Create the database:

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE techvault;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE techvault TO postgres;

# Exit psql
\q
```

### 4. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=techvault
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Optional: GitHub OAuth (for social login)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/auth/registration/` - Register new user
- `POST /api/auth/login/` - Login with email/password
- `POST /api/auth/logout/` - Logout
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token

### User

- `GET /api/user/profile/` - Get current user profile
- `PUT /api/user/profile/` - Update current user profile

### Admin

- `/admin/` - Django admin interface

## Setting Up GitHub OAuth (Optional)

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the details:
   - Application name: TechVault Local
   - Homepage URL: `http://localhost:5173`
   - Authorization callback URL: `http://localhost:8000/accounts/github/login/callback/`
4. Copy the Client ID and Client Secret
5. Add them to your `.env` file:
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ```
6. Restart the Django server

## Project Structure

```
backend/
├── backend/              # Main project configuration
│   ├── __init__.py
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── core/                # Core app (shared utilities)
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── admin.py
│   └── views.py
├── users/               # User management
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py        # Custom User model
│   ├── serializers.py   # User serializers
│   ├── admin.py         # User admin
│   └── views.py         # User views
├── api/                 # API routes and views
│   ├── __init__.py
│   ├── apps.py
│   ├── urls.py          # API URL configuration
│   └── views.py         # API views
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Testing the API

### Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password1": "securepassword123",
    "password2": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/user/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Common Issues & Troubleshooting

### Database Connection Error

If you get a database connection error:
- Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Verify database credentials in `.env`
- Check if the database exists: `psql -l`

### Migration Issues

If migrations fail:
```bash
# Reset migrations (WARNING: Only for development)
python manage.py migrate --fake api zero
python manage.py migrate --fake users zero
python manage.py migrate --fake core zero
python manage.py migrate
```

### Port Already in Use

If port 8000 is already in use:
```bash
# Run on a different port
python manage.py runserver 8001
```

## Production Deployment Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up proper email backend (replace console backend)
- [ ] Enable HTTPS
- [ ] Configure proper CORS settings
- [ ] Set up database backups
- [ ] Configure static file serving with whitenoise or CDN
- [ ] Set up logging and monitoring
- [ ] Enable GitHub OAuth callback with production URL

## Development Commands

```bash
# Create new Django app
python manage.py startapp appname

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Shell
python manage.py shell
```

## License

Proprietary - TechVault
