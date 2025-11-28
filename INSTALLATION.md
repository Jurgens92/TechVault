# TechVault Ubuntu 24.04 Installation Guide

This guide provides instructions for installing TechVault on a fresh Ubuntu 24.04 server.

## Prerequisites

- Fresh Ubuntu 24.04 installation
- Root or sudo access
- Internet connection
- At least 2GB RAM
- 10GB free disk space

## Quick Installation

**100% Automated - Zero Interaction Required!**

The installation script is fully automated and requires no user input. Simply run:

```bash
wget https://raw.githubusercontent.com/Jurgens92/TechVault/main/install.sh
sudo bash install.sh
```

Or if you've already cloned the repository:

```bash
cd TechVault
sudo bash install.sh
```

The script will automatically:
- Install all dependencies
- Set up the database with secure credentials
- Build and deploy the application
- Create a default admin account
- Configure everything to run on port 80

### Default Admin Credentials

After installation, you can immediately login with:

- **Email**: `admin@techvault.local`
- **Password**: `TechVault2024!`

**⚠️ IMPORTANT**: Change the admin password immediately after first login!

## What the Install Script Does

The installation script performs the following steps automatically:

1. **System Update**: Updates all system packages
2. **Dependency Installation**:
   - Python 3.12
   - PostgreSQL (database)
   - Node.js 20.x (LTS)
   - Nginx (web server)
   - Build tools and libraries
3. **Database Setup**: Creates PostgreSQL database and user with secure credentials
4. **Application Setup**:
   - Clones TechVault from GitHub
   - Sets up Python virtual environment
   - Installs backend dependencies
   - Builds frontend production bundle
5. **Configuration**:
   - Generates secure SECRET_KEY
   - Creates environment files
   - Runs database migrations
   - Creates admin superuser
6. **Service Setup**:
   - Creates systemd service for Django backend
   - Configures Nginx to serve on port 80
   - Enables auto-start on boot
7. **Deployment**: Starts all services and verifies they're running

## Post-Installation

After successful installation, TechVault is immediately ready to use:

1. **Access the Application**: Open `http://your-server-ip` in your browser
2. **Login with default credentials**:
   - Email: `admin@techvault.local`
   - Password: `TechVault2024!`
3. **Change your password**: Go to your profile settings and update the password
4. **Admin Panel**: Access at `http://your-server-ip/admin`

All installation credentials are saved in `/opt/techvault/installation_credentials.txt`

## Default Locations

- **Installation Directory**: `/opt/techvault`
- **Backend Code**: `/opt/techvault/backend`
- **Frontend Build**: `/opt/techvault/frontend/dist`
- **Backend Environment**: `/opt/techvault/backend/.env`
- **Credentials File**: `/opt/techvault/installation_credentials.txt`

## Service Management

### Backend Service

```bash
# View status
sudo systemctl status techvault-backend

# Start service
sudo systemctl start techvault-backend

# Stop service
sudo systemctl stop techvault-backend

# Restart service
sudo systemctl restart techvault-backend

# View logs
sudo journalctl -u techvault-backend -f
```

### Nginx Web Server

```bash
# View status
sudo systemctl status nginx

# Restart
sudo systemctl restart nginx

# Test configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log
```

## Updating TechVault

### Automated Update (Recommended)

**100% Automated - Zero interaction required!**

To update TechVault to the latest version, simply run:

```bash
cd /opt/techvault
sudo bash update.sh
```

Or download and run directly:

```bash
wget https://raw.githubusercontent.com/Jurgens92/TechVault/main/update.sh
sudo bash update.sh
```

The update script will automatically:
- Create a backup of your current installation and database
- Pull the latest code from GitHub
- Update all dependencies (backend and frontend)
- Run database migrations
- Rebuild the frontend
- Collect static files
- Restart all services
- Verify everything is working

**Backup Location**: `/opt/techvault_backups/techvault_backup_TIMESTAMP/`

The script creates a timestamped backup before updating. If something goes wrong, you can restore using the generated restore script:

```bash
sudo bash /opt/techvault_backups/techvault_backup_TIMESTAMP/restore_this_backup.sh
```

### Manual Update

If you prefer to update manually:

```bash
cd /opt/techvault

# Backup current installation
sudo cp -r /opt/techvault /opt/techvault.backup.$(date +%s)

# Pull latest changes
sudo git pull origin main

# Update backend
cd backend
sudo su -c "source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput"

# Update frontend
cd ../frontend
sudo npm install
sudo npm run build

# Restart services
sudo systemctl restart techvault-backend
sudo systemctl restart nginx
```

## Troubleshooting

### Backend Not Starting

Check the logs:
```bash
sudo journalctl -u techvault-backend -n 100
```

Common issues:
- Database connection problems: Check PostgreSQL is running
- Missing dependencies: Reinstall with `pip install -r requirements.txt`
- Port 8000 in use: Check for other services using `sudo lsof -i :8000`

### Nginx Issues

Test configuration:
```bash
sudo nginx -t
```

Check logs:
```bash
sudo tail -f /var/log/nginx/error.log
```

### Database Connection Issues

Test PostgreSQL:
```bash
sudo -u postgres psql -d techvault -c "SELECT version();"
```

Reset database password (if needed):
```bash
sudo -u postgres psql -c "ALTER USER techvault WITH PASSWORD 'new_password';"
```

Then update `/opt/techvault/backend/.env` with the new password.

### Can't Access on Port 80

Check if Nginx is running:
```bash
sudo systemctl status nginx
```

Check firewall (if enabled):
```bash
sudo ufw status
sudo ufw allow 80/tcp
```

Verify Nginx is listening on port 80:
```bash
sudo netstat -tlnp | grep :80
```

## SSL/HTTPS Setup (Optional)

To enable HTTPS with Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

## Backup and Restore

### Backup Database

```bash
sudo -u postgres pg_dump techvault > techvault_backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
sudo -u postgres psql techvault < techvault_backup_20240101.sql
```

### Backup Uploaded Files

```bash
sudo tar -czf media_backup_$(date +%Y%m%d).tar.gz /opt/techvault/backend/media/
```

## Security Recommendations

1. **Change Default Passwords**: Ensure all default passwords are changed
2. **Enable Firewall**:
   ```bash
   sudo ufw enable
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp  # SSH
   ```
3. **Enable HTTPS**: Use Let's Encrypt (see above)
4. **Regular Updates**: Keep system and application updated
5. **Backup Regularly**: Automate database and file backups
6. **Secure Credentials File**: The file at `/opt/techvault/installation_credentials.txt` contains sensitive information. Secure it:
   ```bash
   sudo chmod 600 /opt/techvault/installation_credentials.txt
   ```

## Performance Tuning

### Gunicorn Workers

Edit `/etc/systemd/system/techvault-backend.service` and adjust workers:
```
--workers 3  # Change based on CPU cores (2-4 x num_cores)
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart techvault-backend
```

### PostgreSQL

For production workloads, tune PostgreSQL settings in `/etc/postgresql/*/main/postgresql.conf`:
- `shared_buffers`: 25% of RAM
- `effective_cache_size`: 50% of RAM
- `maintenance_work_mem`: 64MB - 1GB

## Uninstall

To completely remove TechVault:

```bash
# Stop services
sudo systemctl stop techvault-backend
sudo systemctl disable techvault-backend
sudo systemctl stop nginx

# Remove systemd service
sudo rm /etc/systemd/system/techvault-backend.service
sudo systemctl daemon-reload

# Remove Nginx config
sudo rm /etc/nginx/sites-enabled/techvault
sudo rm /etc/nginx/sites-available/techvault

# Remove application
sudo rm -rf /opt/techvault

# Remove database (optional)
sudo -u postgres psql -c "DROP DATABASE techvault;"
sudo -u postgres psql -c "DROP USER techvault;"
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Jurgens92/TechVault/issues
- Documentation: See README.md

## Manual Installation

If you prefer to install manually without the script, follow these steps:

### 1. Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git curl build-essential libpq-dev python3-dev -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs
```

### 2. Setup Database
```bash
sudo -u postgres psql <<EOF
CREATE USER techvault WITH PASSWORD 'your_secure_password';
CREATE DATABASE techvault OWNER techvault;
GRANT ALL PRIVILEGES ON DATABASE techvault TO techvault;
ALTER USER techvault CREATEDB;
EOF
```

### 3. Clone and Setup Application
```bash
sudo git clone https://github.com/Jurgens92/TechVault.git /opt/techvault
cd /opt/techvault/backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create .env file (see .env.example)
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Build Frontend
```bash
cd /opt/techvault/frontend
npm install
npm run build
```

### 5. Configure Services
Follow the systemd and Nginx configuration steps from the install script.

---

**Built for IT professionals by IT professionals**
