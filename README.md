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
- **Social Auth**: GitHub OAuth

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **UI Components**: shadcn/ui
- **Routing**: React Router v6.26+
- **HTTP Client**: Axios with interceptors

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

### 👨‍💻 Development Setup

For local development, see [SETUP_GUIDE.md](./SETUP_GUIDE.md).

### 📚 Complete Installation Guide

For detailed installation instructions, troubleshooting, updating, and manual setup, see [INSTALLATION.md](./INSTALLATION.md).

## 📚 Documentation

- [Setup Guide](./SETUP_GUIDE.md) - Comprehensive setup and API documentation
- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)

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

## 🔒 Security Features

- JWT-based authentication with automatic token refresh
- HTTP-only refresh tokens (configurable)
- CORS protection
- Password validation
- Protected API endpoints
- Secure token storage

## 📦 API Endpoints

### Authentication
- `POST /api/auth/registration/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/token/refresh/` - Refresh access token
- `POST /api/token/verify/` - Verify token

### User
- `GET /api/user/profile/` - Get current user profile
- `PATCH /api/user/profile/` - Update user profile

### Admin
- `/admin/` - Django admin interface

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

## 🚀 Updating TechVault

**One-command deployment for Ubuntu 24.04 servers:**

```bash
wget https://raw.githubusercontent.com/Jurgens92/TechVault/main/install.sh
sudo bash install.sh
```

**For public IP/domain access**, set the PUBLIC_DOMAIN variable:

```bash
PUBLIC_DOMAIN=your.domain.com sudo -E bash install.sh
```

This fully automated script will:
- Install all dependencies (Python, Node.js, PostgreSQL, Nginx)
- Set up and configure the database
- Build and deploy both frontend and backend
- Configure Nginx to serve on port 80
- Create systemd services for auto-start
- Generate secure credentials
- Work with any IP/domain (uses relative URLs)

Default admin credentials:
- Email: `admin@techvault.local`
- Password: `TechVault2024!`

For detailed instructions, see [INSTALLATION.md](./INSTALLATION.md)

### Updating TechVault

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
