# TechVault

**Enterprise-grade IT Documentation Platform**

TechVault is a modern, secure platform for managing IT documentation, similar to ITGlue and Hudu. Built with Django and React, it provides a robust foundation for organizing organizations, locations, contacts, documentation, passwords, and configurations.

## 🏗️ Project Structure

```
TechVault/
├── backend/                 # Django + DRF backend
│   ├── backend/            # Project settings
│   ├── core/               # Core app
│   ├── users/              # User management
│   ├── api/                # API endpoints
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── types/         # TypeScript types
│   │   └── styles/        # Global styles
│   ├── package.json
│   └── README.md
│
└── README.md              # This file
```

## 🚀 Tech Stack

### Backend
- **Framework**: Django 5.0
- **API**: Django REST Framework 3.14
- **Database**: PostgreSQL
- **Authentication**: Django-allauth + SimpleJWT
- **Two-Factor Authentication**: TOTP (Time-based One-Time Password)
- **Security**: HTTPS with Let's Encrypt, Backup codes, Password hashing
- **Social Auth**: GitHub OAuth

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **UI Components**: shadcn/ui
- **Routing**: React Router v6.26+
- **HTTP Client**: Axios with interceptors

## ✨ Features

### Core Management
- **Organizations** - Multi-tenant organization management with full CRUD operations
- **Locations** - Multiple locations per organization with address and contact details
- **Contacts** - Contact management with CSV import/export, software and VoIP assignments
- **Documentation** - Rich documentation system with categories (procedures, configurations, guides, troubleshooting, policies), versioning, and publish/unpublish functionality
- **Password Vault** - Secure password management with categories (account, service, device)
- **Configurations** - System and service configuration tracking (Network, Server, Application, Security, Backup)

### IT Infrastructure Inventory
- **Network Devices** - Comprehensive tracking of firewalls, routers, switches, and WiFi access points with IP/MAC addresses, internet speed, and manufacturer details
- **Servers** - Full server inventory (physical, virtual, cloud, container) with hardware specs, roles, and operating systems
- **Endpoints** - Desktop, laptop, and workstation management with user assignments, hardware details, and operating systems
- **Peripherals** - Track printers, scanners, UPS devices, and NAS storage

### Software & Services
- **Software Management** - License tracking (perpetual, subscription, trial, free) with assignments to contacts and expiry monitoring
- **VoIP Services** - VoIP service tracking (Microsoft Teams, 3CX, Yeastar) with extension assignments and license management
- **Backups** - Backup solution monitoring with status tracking, frequency, retention periods, and last backup dates

### Visualization & Export
- **Infrastructure Diagrams** - Interactive network topology visualization showing the complete IT infrastructure
- **Multi-format Export** - Export diagrams as PNG, PDF, SVG, or JSON
- **Dashboard Statistics** - Overview of all entities with counts and quick access

### Data Management
- **Soft Delete** - All entities support soft delete with full recovery capability
- **Deleted Items Recovery** - Dedicated interface for viewing and restoring soft-deleted items
- **Audit Trail** - Track who created, modified, or deleted items with timestamps
- **CSV Import/Export** - Bulk import and export contacts

### Security & Authentication
- **Email-based Authentication** - Secure registration and login system
- **GitHub OAuth** - Social authentication integration (optional)
- **Two-Factor Authentication (2FA)** - TOTP-based 2FA with QR code setup and backup codes
- **JWT Tokens** - Automatic token refresh for secure API access
- **Rate Limiting** - Brute force protection on authentication endpoints
- **Security Headers** - Production-ready HTTPS enforcement, HSTS, secure cookies

## 📦 Installation

TechVault supports multiple installation methods:

### 🚀 Quick Install (Recommended for Ubuntu 24.04)

One-command deployment on Ubuntu 24.04 servers:

```bash
wget https://raw.githubusercontent.com/Jurgens92/TechVault/main/install.sh
sudo bash install.sh
```

This automated script installs all dependencies, configures the database, deploys the application, and sets up Nginx to serve on port 80.

**Default credentials after installation:**
- Email: `admin@techvault.local`
- Password: `TechVault2024!`

### 🔒 Secure Install with HTTPS (Production)

For production deployments, enable HTTPS with Let's Encrypt:

```bash
PUBLIC_DOMAIN=techvault.yourdomain.com \
ENABLE_HTTPS=true \
ADMIN_EMAIL=admin@yourdomain.com \
sudo -E bash install.sh
```

**Requirements:**
- Valid domain name pointing to your server's public IP
- Ports 80 and 443 open and accessible
- Email address for SSL certificate notifications

This will automatically:
- Obtain and configure SSL certificates from Let's Encrypt
- Set up automatic certificate renewal
- Redirect HTTP to HTTPS
- Configure secure headers

See [SECURITY.md](./SECURITY.md) for detailed security documentation.

### 📚 Complete Installation Guide

For detailed installation instructions, troubleshooting, updating, and manual setup, see [INSTALLATION.md](./INSTALLATION.md).

## 📋 Loading Dummy Data

After installation, you can load sample data for testing and evaluation:

### Quick Start

```bash
cd /opt/techvault/backend
source venv/bin/activate
python manage.py load_dummy_data
```

### Options

**Load dummy data (adds to existing data):**
```bash
python manage.py load_dummy_data
```

**Clear existing data and reload:**
```bash
python manage.py load_dummy_data --clear
```

### Test Users Created

Once loaded, you can log in with these test credentials:

| Email | Password | Role |
|-------|----------|------|
| `admin@techvault.com` | `admin123` | Superuser |
| `john.doe@techvault.com` | `password123` | Regular User |
| `jane.smith@techvault.com` | `password123` | Regular User |
| `bob.johnson@techvault.com` | `password123` | Regular User |

### Sample Data Included

The dummy data loader creates:
- 4 test users
- 5 organizations (Tech Solutions Inc, Digital Innovations Ltd, Cloud Systems Corp, TechGuard MSP, Acme Manufacturing Co)
- 8 locations across organizations
- 25 contacts
- 50+ documentation entries
- 30+ password entries
- Network devices (routers, switches, firewalls)
- Servers (web, database, file servers)
- Peripherals (printers, monitors, etc.)
- Software licenses and assignments
- Backup job records
- Configurations and endpoints

This gives you a realistic test environment to explore TechVault's features!

## 📚 Documentation

- [Installation Guide](./INSTALLATION.md) - Complete installation and setup instructions
- [Security Documentation](./SECURITY.md) - HTTPS and 2FA setup guide
- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)

## 🔐 Security Features

### HTTPS with Let's Encrypt

TechVault supports automatic HTTPS configuration using Let's Encrypt for production deployments:

- **Automatic SSL certificate** generation and renewal
- **HTTP to HTTPS redirect** for secure connections
- **Secure headers** and best practices
- **Free SSL certificates** that auto-renew before expiration

See [SECURITY.md](./SECURITY.md) for detailed HTTPS setup instructions.

### Two-Factor Authentication (2FA)

Protect your account with an additional layer of security:

- **TOTP-based** authentication (Time-based One-Time Passwords)
- Compatible with popular authenticator apps (Google Authenticator, Authy, Microsoft Authenticator, etc.)
- **QR code setup** for easy configuration
- **Backup codes** for account recovery
- Per-user 2FA settings (enable/disable as needed)

**To enable 2FA:**
1. Log in to TechVault
2. Navigate to **2FA Security** in the sidebar
3. Click **Enable 2FA** and follow the setup wizard
4. Save your backup codes in a secure location

See [SECURITY.md](./SECURITY.md) for detailed 2FA documentation and troubleshooting.

## 🔐 Authentication

### Email/Password Registration

1. Navigate to `http://localhost:5173/register`
2. Fill in your details
3. Submit the form
4. You'll be automatically logged in and redirected to the dashboard

### Email/Password Login

1. Navigate to `http://localhost:5173/login`
2. Enter your credentials
3. Submit the form

### GitHub OAuth (Optional)

1. Create a GitHub OAuth App:
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - Homepage URL: `http://localhost:5173`
   - Callback URL: `http://localhost:8000/accounts/github/login/callback/`
2. Copy Client ID and Secret to `backend/.env`:
   ```
   GITHUB_CLIENT_ID=your_client_id
   GITHUB_CLIENT_SECRET=your_client_secret
   ```
3. Restart the Django server
4. Click "GitHub" button on login/register pages

## 🎨 Design Philosophy

TechVault follows a **premium, enterprise-grade design language**:

- **Dark theme** with blue accents for a professional, secure feel
- **Trustworthy** visual hierarchy emphasizing security
- **Modern** interface with smooth transitions
- **Responsive** design that works on all devices
- **Accessible** with proper contrast and focus states

## 📦 API Endpoints

### Authentication & User Management
- `POST /api/auth/registration/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/token/refresh/` - Refresh JWT access token
- `POST /api/token/verify/` - Verify JWT token
- `GET /api/user/profile/` - Get current user profile
- `PATCH /api/user/profile/` - Update user profile

### Two-Factor Authentication
- `GET /api/auth/2fa/status/` - Get 2FA status
- `POST /api/auth/2fa/setup/` - Initialize 2FA setup (get QR code)
- `POST /api/auth/2fa/enable/` - Enable 2FA with TOTP verification
- `POST /api/auth/2fa/disable/` - Disable 2FA
- `POST /api/auth/2fa/verify/` - Verify TOTP token
- `POST /api/auth/2fa/backup-codes/regenerate/` - Regenerate backup codes

### Core Resources (Full REST API)
- `/api/organizations/` - Organizations CRUD
- `/api/locations/` - Locations CRUD
- `/api/contacts/` - Contacts CRUD with CSV import/export
- `/api/documentations/` - Documentation CRUD with versioning
- `/api/passwords/` - Password vault CRUD
- `/api/configurations/` - Configuration CRUD

### IT Infrastructure
- `/api/network-devices/` - Network devices (firewalls, routers, switches, WiFi)
- `/api/servers/` - Server inventory (physical, virtual, cloud, container)
- `/api/endpoint-users/` - Endpoint devices (desktops, laptops, workstations)
- `/api/peripherals/` - Peripherals (printers, scanners, UPS, NAS)

### Software & Services
- `/api/software/` - Software and license management
- `/api/voip/` - VoIP services and assignments
- `/api/backups/` - Backup solutions and monitoring

### Dashboard & Visualization
- `GET /api/dashboard/stats/` - Dashboard statistics for all entities
- `GET /api/diagram/data/` - Infrastructure diagram data

### Admin
- `/admin/` - Django admin interface

All resource endpoints support standard REST operations: `GET` (list/retrieve), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (soft delete)

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test  # To be configured
```

## 🔄 Updating TechVault

**One-command update:**

```bash
cd /opt/techvault
sudo bash update.sh
```

This creates automatic backups and updates all components. See [INSTALLATION.md](./INSTALLATION.md#updating-techvault) for details.

## 🛠️ Development Workflow

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Commit with clear messages
5. Create pull request
6. Code review
7. Merge to main

## 🤝 Contributing

Contributions are welcome! Please follow the development workflow and ensure:

- Code follows project style guidelines
- TypeScript types are properly defined
- Backend includes migrations
- Tests pass
- Documentation is updated

## 📄 License

Proprietary - TechVault

## 🆘 Support

For issues and questions:
- Check the [Backend README](./backend/README.md)
- Check the [Frontend README](./frontend/README.md)
- Review troubleshooting sections
- Open an issue in the repository

---

**Built with ❤️ for IT professionals**
