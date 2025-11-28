#!/bin/bash

################################################################################
# TechVault Reconfiguration Script
#
# Use this script to rebuild the frontend after installation
# This is useful if you need to access TechVault from a different IP/domain
#
# Usage: sudo bash reconfigure.sh
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root (use sudo)"
    exit 1
fi

INSTALL_DIR="/opt/techvault"

if [ ! -d "$INSTALL_DIR" ]; then
    log_error "TechVault is not installed at $INSTALL_DIR"
    exit 1
fi

log_info "TechVault Reconfiguration"
echo "========================================"
echo ""
log_info "Current frontend configuration uses relative URLs (works with any IP/domain)"
log_info "This script will rebuild the frontend to ensure it's up to date."
echo ""
log_info "Rebuilding frontend..."

cd "$INSTALL_DIR/frontend"

# Rebuild frontend
npm run build

log_success "Frontend rebuilt successfully"

# Restart services
log_info "Restarting services..."
systemctl restart techvault-backend
systemctl restart nginx

log_success "Services restarted"

echo ""
echo "========================================"
log_success "Reconfiguration complete!"
echo "========================================"
echo ""
log_info "You can now access TechVault from any IP or domain that routes to this server."
echo ""
