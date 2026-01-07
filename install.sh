#!/bin/bash

################################################################################
# TechVault Installation Script for Ubuntu 24.04
#
# FULLY AUTOMATED - Zero interaction required!
#
# This script will:
# - Install all required dependencies
# - Clone and set up TechVault
# - Configure PostgreSQL database
# - Build and deploy the application
# - Set up Nginx to serve on port 80 (or 443 with HTTPS)
# - Optionally configure HTTPS with Let's Encrypt
# - Create systemd services for auto-start
# - Create default admin account
#
# Usage:
#   Basic: sudo bash install.sh
#   With domain: PUBLIC_DOMAIN=yourdomain.com sudo -E bash install.sh
#   With HTTPS: PUBLIC_DOMAIN=yourdomain.com ENABLE_HTTPS=true ADMIN_EMAIL=admin@yourdomain.com sudo -E bash install.sh
#
# Environment Variables:
#   PUBLIC_DOMAIN - Your domain name or public IP (required for HTTPS)
#   ENABLE_HTTPS - Set to 'true' to enable HTTPS with Let's Encrypt (requires valid domain, not IP)
#   ADMIN_EMAIL - Admin email for Let's Encrypt notifications (recommended for HTTPS)
#
# Default admin credentials:
#   Email: admin@techvault.local
#   Password: TechVault2024!
#   (You should change this after first login!)
################################################################################

set -e  # Exit on any error
export DEBIAN_FRONTEND=noninteractive  # Non-interactive mode

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Check Ubuntu version
log_info "Checking Ubuntu version..."
if ! grep -q "24.04" /etc/os-release; then
    log_warning "This script is designed for Ubuntu 24.04. You are running a different version."
    log_warning "Installation will continue, but some features may not work as expected."
fi

# Configuration
INSTALL_DIR="/opt/techvault"
DB_NAME="techvault"
DB_USER="techvault"
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 64)
ADMIN_PASSWORD="TechVault2024!"
ADMIN_EMAIL="admin@techvault.local"
ADMIN_FIRSTNAME="Admin"
ADMIN_LASTNAME="User"
GITHUB_REPO="https://github.com/Jurgens92/TechVault.git"

# Auto-detect server IP (private)
DETECTED_IP=$(hostname -I | awk '{print $1}')
if [ -z "$DETECTED_IP" ]; then
    DETECTED_IP="localhost"
fi

# Get public IP/domain from environment variable or use detected IP
if [ -z "$PUBLIC_DOMAIN" ]; then
    log_info "Detected private IP: $DETECTED_IP"
    log_warning "If you're accessing this server from outside your network, you need to specify the public IP or domain."
    log_info "You can set it via environment variable: PUBLIC_DOMAIN=your.domain.com sudo -E bash install.sh"
    log_info "Using detected IP: $DETECTED_IP"
    DOMAIN="$DETECTED_IP"
else
    log_info "Using public domain/IP: $PUBLIC_DOMAIN"
    DOMAIN="$PUBLIC_DOMAIN"
fi

# Check if HTTPS should be enabled
USE_HTTPS=false
if [ "$ENABLE_HTTPS" = "true" ]; then
    # Validate that DOMAIN is not an IP address (Let's Encrypt requires a domain)
    if [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "HTTPS requires a valid domain name, not an IP address."
        log_error "Please set PUBLIC_DOMAIN to a domain name that points to this server."
        exit 1
    fi
    log_info "HTTPS will be enabled for domain: $DOMAIN"
    USE_HTTPS=true
else
    log_info "HTTPS not enabled. Set ENABLE_HTTPS=true to enable SSL/TLS."
fi

log_info "Starting TechVault installation..."
echo "========================================"

# Update system
log_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install system dependencies
log_info "Installing system dependencies..."
PACKAGES="python3.12 python3.12-venv python3-pip postgresql postgresql-contrib nginx git curl build-essential libpq-dev python3-dev"

# Add certbot if HTTPS is enabled
if [ "$USE_HTTPS" = "true" ]; then
    log_info "HTTPS enabled - adding certbot to installation"
    PACKAGES="$PACKAGES certbot python3-certbot-nginx"
fi

apt-get install -y $PACKAGES

log_success "System dependencies installed"

# Install Node.js 20.x (LTS)
log_info "Installing Node.js 20.x..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
log_success "Node.js $(node --version) and npm $(npm --version) installed"

# Configure PostgreSQL
log_info "Configuring PostgreSQL database..."
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || log_warning "User $DB_USER already exists"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || log_warning "Database $DB_NAME already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" # For running tests
log_success "PostgreSQL database configured"

# Clone repository
log_info "Cloning TechVault repository..."
if [ -d "$INSTALL_DIR" ]; then
    log_warning "Installation directory already exists. Backing up to ${INSTALL_DIR}.backup"
    mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%s)"
fi

git clone "$GITHUB_REPO" "$INSTALL_DIR"
cd "$INSTALL_DIR"
log_success "Repository cloned to $INSTALL_DIR"

# Set up Python virtual environment
log_info "Setting up Python virtual environment..."
cd "$INSTALL_DIR/backend"
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
log_success "Python dependencies installed"

# Create backend .env file
log_info "Creating backend environment configuration..."
cat > "$INSTALL_DIR/backend/.env" <<EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ENVIRONMENT=production
# Allow all hosts for self-hosted deployments (change if you want to restrict)
ALLOWED_HOSTS=*

# Database
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# CORS - Allow all origins for self-hosted deployments
# The API is protected by authentication, so this is safe
CORS_ALLOW_ALL_ORIGINS=True

# JWT Settings
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
EOF

chmod 600 "$INSTALL_DIR/backend/.env"
log_success "Backend environment configured"

# Run Django migrations
log_info "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
log_success "Database migrations completed"

# Create Django superuser (non-interactive)
log_info "Creating Django superuser..."
DJANGO_SUPERUSER_PASSWORD="$ADMIN_PASSWORD" python manage.py createsuperuser \
    --email "$ADMIN_EMAIL" \
    --first_name "$ADMIN_FIRSTNAME" \
    --last_name "$ADMIN_LASTNAME" \
    --noinput
log_success "Superuser created: $ADMIN_EMAIL"

# Collect static files
log_info "Collecting Django static files..."
python manage.py collectstatic --noinput
log_success "Static files collected"

deactivate

# Set up frontend
log_info "Setting up frontend..."
cd "$INSTALL_DIR/frontend"

# Create frontend .env file
# Set VITE_API_URL to empty string so the frontend uses window.location.origin
# This makes the frontend automatically use the same domain/IP it's accessed from
# allowing the app to work with any domain/IP without rebuilding
cat > "$INSTALL_DIR/frontend/.env" <<EOF
VITE_API_URL=
EOF

log_info "Installing frontend dependencies..."
npm install

log_info "Building frontend..."
npm run build
log_success "Frontend built successfully"

# Create systemd service for backend
log_info "Creating systemd service for Django backend..."
cat > /etc/systemd/system/techvault-backend.service <<EOF
[Unit]
Description=TechVault Django Backend
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/gunicorn backend.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Install gunicorn if not already installed
log_info "Installing gunicorn..."
source "$INSTALL_DIR/backend/venv/bin/activate"
pip install gunicorn
deactivate

# Configure Nginx
log_info "Configuring Nginx..."
cat > /etc/nginx/sites-available/techvault <<'NGINX_EOF'
server {
    listen 80;
    server_name SERVER_NAME_PLACEHOLDER;
    client_max_body_size 100M;

    # Frontend - serve built React app
    location / {
        root INSTALL_DIR_PLACEHOLDER/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Static Files
    location /static/ {
        alias INSTALL_DIR_PLACEHOLDER/backend/staticfiles/;
    }

    # Django Media Files
    location /media/ {
        alias INSTALL_DIR_PLACEHOLDER/backend/media/;
    }
}
NGINX_EOF

# Replace placeholders
sed -i "s|SERVER_NAME_PLACEHOLDER|$DOMAIN|g" /etc/nginx/sites-available/techvault
sed -i "s|INSTALL_DIR_PLACEHOLDER|$INSTALL_DIR|g" /etc/nginx/sites-available/techvault

# Enable Nginx site
ln -sf /etc/nginx/sites-available/techvault /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
log_info "Testing Nginx configuration..."
nginx -t

# Start services before certbot (certbot needs nginx running)
log_info "Starting services..."
systemctl daemon-reload
systemctl enable techvault-backend
systemctl start techvault-backend
systemctl restart nginx

# Configure HTTPS with Let's Encrypt if enabled
if [ "$USE_HTTPS" = "true" ]; then
    log_info "Configuring HTTPS with Let's Encrypt..."
    log_warning "Make sure your domain $DOMAIN points to this server's public IP!"
    log_info "Certbot will automatically configure SSL and set up auto-renewal"

    # Determine admin email for Let's Encrypt
    if [ -z "$ADMIN_EMAIL" ]; then
        CERT_EMAIL="admin@techvault.local"
        log_warning "No ADMIN_EMAIL provided, using default: $CERT_EMAIL"
        log_info "For production, set ADMIN_EMAIL environment variable for Let's Encrypt notifications"
    else
        CERT_EMAIL="$ADMIN_EMAIL"
    fi

    # Run certbot
    log_info "Running certbot for domain: $DOMAIN with email: $CERT_EMAIL"
    certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "$CERT_EMAIL" --redirect

    if [ $? -eq 0 ]; then
        log_success "SSL certificate obtained and configured successfully!"
        log_info "Certbot will automatically renew certificates before they expire"
        PROTOCOL="https"
    else
        log_error "Failed to obtain SSL certificate. Check that:"
        log_error "  1. Domain $DOMAIN points to this server's public IP"
        log_error "  2. Port 80 is accessible from the internet"
        log_error "  3. No firewall is blocking the connection"
        log_warning "Continuing with HTTP only..."
        PROTOCOL="http"
    fi
else
    PROTOCOL="http"
fi

# Restart nginx after certbot modifications
systemctl restart nginx

log_success "Services started and enabled"

# Check service status
sleep 3
if systemctl is-active --quiet techvault-backend; then
    log_success "TechVault backend is running"
else
    log_error "TechVault backend failed to start. Check logs with: journalctl -u techvault-backend -n 50"
fi

if systemctl is-active --quiet nginx; then
    log_success "Nginx is running"
else
    log_error "Nginx failed to start. Check logs with: journalctl -u nginx -n 50"
fi

# Final summary
echo ""
echo "========================================"
log_success "TechVault installation completed!"
echo "========================================"
echo ""
log_info "Installation Summary:"
echo "  - Installation directory: $INSTALL_DIR"
echo "  - Database: PostgreSQL ($DB_NAME)"
echo "  - Application URL: $PROTOCOL://$DOMAIN"
echo "  - Admin panel: $PROTOCOL://$DOMAIN/admin"
if [ "$USE_HTTPS" = "true" ] && [ "$PROTOCOL" = "https" ]; then
    echo "  - HTTPS: Enabled (Let's Encrypt SSL certificate configured)"
    echo "  - Auto-renewal: Enabled (certbot timer running)"
fi
echo ""
log_info "Database Credentials (save these securely):"
echo "  - Database: $DB_NAME"
echo "  - Username: $DB_USER"
echo "  - Password: $DB_PASSWORD"
echo ""
log_info "Admin Account:"
echo "  - Email: $ADMIN_EMAIL"
echo "  - Password: $ADMIN_PASSWORD"
echo "  - ⚠️  IMPORTANT: Change this password after first login!"
echo ""
log_info "Useful Commands:"
echo "  - View backend logs: journalctl -u techvault-backend -f"
echo "  - View nginx logs: tail -f /var/log/nginx/error.log"
echo "  - Restart backend: systemctl restart techvault-backend"
echo "  - Restart nginx: systemctl restart nginx"
echo ""
log_info "Next Steps:"
echo "  1. Open $PROTOCOL://$DOMAIN in your browser"
echo "  2. Log in with:"
echo "     - Email: $ADMIN_EMAIL"
echo "     - Password: $ADMIN_PASSWORD"
echo "  3. Change your admin password immediately!"
if [ "$USE_HTTPS" = "true" ] && [ "$PROTOCOL" = "https" ]; then
    echo "  4. Configure 2FA for enhanced security (see documentation)"
    echo "  5. Start using TechVault!"
else
    echo "  4. Start using TechVault!"
fi
echo ""
log_warning "Important: Save these credentials in a secure location!"
echo ""

# Save credentials to file
CREDENTIALS_FILE="$INSTALL_DIR/installation_credentials.txt"
cat > "$CREDENTIALS_FILE" <<EOF
TechVault Installation Credentials
Generated: $(date)

Application URL: $PROTOCOL://$DOMAIN
Admin Panel: $PROTOCOL://$DOMAIN/admin
$(if [ "$USE_HTTPS" = "true" ] && [ "$PROTOCOL" = "https" ]; then echo "HTTPS: Enabled (Let's Encrypt)"; fi)

Database Credentials:
  Database: $DB_NAME
  Username: $DB_USER
  Password: $DB_PASSWORD

Admin Account:
  Email: $ADMIN_EMAIL
  Password: $ADMIN_PASSWORD
  ⚠️  IMPORTANT: Change this password after first login!

Backend .env location: $INSTALL_DIR/backend/.env
EOF

chmod 600 "$CREDENTIALS_FILE"
echo ""
log_success "All credentials have been saved to: $CREDENTIALS_FILE"
echo ""
