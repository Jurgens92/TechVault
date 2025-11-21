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

## ✨ Features

### Current (Foundation)

- ✅ User authentication (email/password + GitHub OAuth)
- ✅ JWT token management with auto-refresh
- ✅ Protected routes and authorization
- ✅ Premium dark/blue design language
- ✅ Responsive sidebar navigation
- ✅ Dashboard with user welcome
- ✅ PostgreSQL database
- ✅ Full TypeScript support
- ✅ CORS configuration for local development

### Menu Structure (Placeholders)

- Dashboard
- Organizations
- Locations
- Contacts
- Documentation
- Passwords
- Configurations
- Settings

## 🔧 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd TechVault
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Create PostgreSQL database
createdb techvault

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start backend server
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📚 Documentation

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

## 🚢 Deployment

### Backend (Production Checklist)

- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Generate secure `SECRET_KEY`
- [ ] Set up proper email backend
- [ ] Configure static files serving
- [ ] Set up database backups
- [ ] Enable HTTPS
- [ ] Configure production CORS settings

### Frontend (Production Build)

```bash
cd frontend
npm run build
```

Deploy the `dist/` directory to your hosting platform (Vercel, Netlify, etc.)

## 🛠️ Development Workflow

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Commit with clear messages
5. Create pull request
6. Code review
7. Merge to main

## 📝 Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=techvault
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

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

## 🎯 Roadmap

### Phase 1: Foundation ✅
- User authentication
- Basic dashboard
- Navigation structure

### Phase 2: Core Features (Next)
- Organizations management
- Locations management
- Contacts management

### Phase 3: Documentation
- Document creation and editing
- File attachments
- Search functionality

### Phase 4: Security
- Password vault
- Encrypted storage
- Access controls

### Phase 5: Configuration Management
- Configuration tracking
- Version history
- Change logs

---

**Built with ❤️ for IT professionals**
