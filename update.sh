#!/bin/bash

################################################################################
# TechVault Update Script for Ubuntu 24.04
#
# FULLY AUTOMATED - Zero interaction required!
#
# This script will:
# - Create a backup of the current installation
# - Pull the latest code from GitHub
# - Update backend dependencies
# - Update frontend dependencies
# - Run database migrations
# - Rebuild frontend
# - Collect static files
# - Restart all services
#
# Usage: sudo bash update.sh
#
# The script creates a backup before updating. If something goes wrong,
# you can restore using: sudo bash restore_backup.sh
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

# Configuration
INSTALL_DIR="/opt/techvault"
BACKUP_DIR="/opt/techvault_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/techvault_backup_$TIMESTAMP"

# Check if TechVault is installed
if [ ! -d "$INSTALL_DIR" ]; then
    log_error "TechVault is not installed at $INSTALL_DIR"
    log_info "Please run install.sh first"
    exit 1
fi

# Check if it's a git repository
if [ ! -d "$INSTALL_DIR/.git" ]; then
    log_error "$INSTALL_DIR is not a git repository"
    log_info "Manual installation detected. This script only works with git-based installations."
    exit 1
fi

log_info "Starting TechVault update..."
echo "========================================"

# Create backup directory
log_info "Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Backup current installation
log_info "Creating backup at $BACKUP_PATH..."
cp -r "$INSTALL_DIR" "$BACKUP_PATH"
log_success "Backup created successfully"

# Backup database
log_info "Backing up database..."
if [ -f "$INSTALL_DIR/backend/.env" ]; then
    # Source the environment file to get DB settings
    source <(grep -E '^(ENVIRONMENT|USE_SQLITE|DB_NAME|DB_USER|DB_PASSWORD)=' "$INSTALL_DIR/backend/.env" | sed 's/^/export /')

    # Determine which database is being used
    if [ "$USE_SQLITE" = "1" ] || [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "local" ] || [ "$ENVIRONMENT" = "dev" ] || [ -z "$ENVIRONMENT" ]; then
        # Using SQLite
        if [ -f "$INSTALL_DIR/backend/db.sqlite3" ]; then
            cp "$INSTALL_DIR/backend/db.sqlite3" "$BACKUP_PATH/db.sqlite3"
            log_success "SQLite database backed up to $BACKUP_PATH/db.sqlite3"
        else
            log_warning "SQLite database file not found. Skipping database backup."
        fi
    else
        # Using PostgreSQL
        if [ ! -z "$DB_NAME" ] && [ ! -z "$DB_USER" ]; then
            if PGPASSWORD="$DB_PASSWORD" pg_dump -U "$DB_USER" -h localhost "$DB_NAME" > "$BACKUP_PATH/database_backup.sql" 2>/dev/null; then
                log_success "PostgreSQL database backed up to $BACKUP_PATH/database_backup.sql"
            else
                log_warning "PostgreSQL backup failed. This may be because PostgreSQL is not configured or credentials are incorrect."
            fi
        else
            log_warning "Could not find PostgreSQL credentials. Skipping database backup."
        fi
    fi
else
    log_warning ".env file not found. Skipping database backup."
fi

# Stop services before update
log_info "Stopping TechVault services..."
systemctl stop techvault-backend || log_warning "Backend service not running"

# Update code from GitHub
log_info "Pulling latest code from GitHub..."
cd "$INSTALL_DIR"

# Stash any local changes
git stash save "Auto-stash before update $TIMESTAMP" 2>/dev/null || true

# Fetch and pull latest changes
git fetch origin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
log_info "Updating branch: $CURRENT_BRANCH"
git pull origin "$CURRENT_BRANCH"

log_success "Code updated successfully"

# Update backend
log_info "Updating backend dependencies..."
cd "$INSTALL_DIR/backend"

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install/update dependencies
pip install -r requirements.txt --quiet
pip install gunicorn --quiet

log_success "Backend dependencies updated"

# Run migrations
log_info "Running database migrations..."
python manage.py makemigrations
python manage.py migrate
log_success "Database migrations completed"

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput
log_success "Static files collected"

deactivate

# Update frontend
log_info "Updating frontend..."
cd "$INSTALL_DIR/frontend"

# Update npm packages
log_info "Updating frontend dependencies..."
npm install --quiet
log_success "Frontend dependencies updated"

# Rebuild frontend
log_info "Building frontend..."
npm run build
log_success "Frontend built successfully"

# Restart services
log_info "Restarting services..."
systemctl daemon-reload
systemctl start techvault-backend
systemctl restart nginx

log_success "Services restarted"

# Wait a moment and check service status
sleep 3

# Verify services are running
BACKEND_STATUS="running"
NGINX_STATUS="running"

if ! systemctl is-active --quiet techvault-backend; then
    log_error "Backend service failed to start!"
    BACKEND_STATUS="failed"
else
    log_success "Backend service is running"
fi

if ! systemctl is-active --quiet nginx; then
    log_error "Nginx service failed to start!"
    NGINX_STATUS="failed"
else
    log_success "Nginx service is running"
fi

# Final summary
echo ""
echo "========================================"

if [ "$BACKEND_STATUS" = "running" ] && [ "$NGINX_STATUS" = "running" ]; then
    log_success "TechVault update completed successfully!"
else
    log_error "Update completed with errors!"
    log_warning "Some services failed to start. Check the logs and restore from backup if needed."
fi

echo "========================================"
echo ""

log_info "Update Summary:"
echo "  - Updated: $TIMESTAMP"
echo "  - Branch: $CURRENT_BRANCH"
echo "  - Backup location: $BACKUP_PATH"
echo ""

log_info "Version Information:"
cd "$INSTALL_DIR"
echo "  - Latest commit: $(git log -1 --pretty=format:'%h - %s (%cr)')"
echo ""

log_info "Service Status:"
echo "  - Backend: $BACKEND_STATUS"
echo "  - Nginx: $NGINX_STATUS"
echo ""

log_info "Useful Commands:"
echo "  - View backend logs: journalctl -u techvault-backend -f"
echo "  - View nginx logs: tail -f /var/log/nginx/error.log"
echo "  - Restart backend: systemctl restart techvault-backend"
echo "  - Check status: systemctl status techvault-backend"
echo ""

if [ "$BACKEND_STATUS" != "running" ] || [ "$NGINX_STATUS" != "running" ]; then
    log_warning "Rollback Instructions:"
    echo "  If you need to rollback to the previous version:"
    echo "  1. Run the automatic restore script: sudo bash $BACKUP_PATH/restore_this_backup.sh"
    echo ""
    echo "  Or manually:"
    echo "  1. Stop services: systemctl stop techvault-backend"
    echo "  2. Restore files: rm -rf $INSTALL_DIR && cp -r $BACKUP_PATH $INSTALL_DIR"
    echo "  3. Restart services: systemctl start techvault-backend && systemctl restart nginx"
    echo ""
else
    log_info "Backup Retention:"
    echo "  - Backups are stored in: $BACKUP_DIR"
    echo "  - You can safely delete old backups to save space"
    echo "  - Current backup: $BACKUP_PATH"
    echo ""

    # List all backups
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        echo "  - Total backups: $BACKUP_COUNT"
        if [ "$BACKUP_COUNT" -gt 5 ]; then
            log_warning "You have $BACKUP_COUNT backups. Consider removing old ones to save disk space."
        fi
    fi
fi

echo ""
log_success "Update process finished!"
echo ""

# Create a simple restore script for this backup
cat > "$BACKUP_PATH/restore_this_backup.sh" <<'RESTORE_SCRIPT'
#!/bin/bash

# Quick restore script for this backup
# Usage: sudo bash restore_this_backup.sh

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

BACKUP_PATH="$(dirname "$(readlink -f "$0")")"
INSTALL_DIR="/opt/techvault"

echo "Restoring TechVault from backup..."
echo "Backup: $BACKUP_PATH"
echo ""

# Stop services
systemctl stop techvault-backend || true

# Restore files
echo "Restoring files..."
rm -rf "$INSTALL_DIR"
cp -r "$BACKUP_PATH" "$INSTALL_DIR"

# Restore database if backup exists
if [ -f "$BACKUP_PATH/db.sqlite3" ]; then
    echo "Restoring SQLite database..."
    cp "$BACKUP_PATH/db.sqlite3" "$INSTALL_DIR/backend/db.sqlite3"
elif [ -f "$BACKUP_PATH/database_backup.sql" ]; then
    echo "Restoring PostgreSQL database..."
    source <(grep -E '^(DB_NAME|DB_USER|DB_PASSWORD)=' "$INSTALL_DIR/backend/.env" | sed 's/^/export /')
    PGPASSWORD="$DB_PASSWORD" psql -U "$DB_USER" -h localhost "$DB_NAME" < "$BACKUP_PATH/database_backup.sql"
fi

# Restart services
echo "Restarting services..."
systemctl start techvault-backend
systemctl restart nginx

echo ""
echo "Restore completed!"
echo "TechVault has been restored to the backup from: $(basename $BACKUP_PATH)"
RESTORE_SCRIPT

chmod +x "$BACKUP_PATH/restore_this_backup.sh"
log_info "Quick restore script created: $BACKUP_PATH/restore_this_backup.sh"
