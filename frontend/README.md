# TechVault Frontend

Modern, responsive React frontend for the TechVault enterprise IT documentation platform.

## Tech Stack

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **UI Components**: shadcn/ui (custom components)
- **Routing**: React Router v6.26+
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Prerequisites

- Node.js 18 or higher
- npm or yarn
- Backend API running on `http://localhost:8000`

## Local Development Setup

### 1. Install Dependencies

```bash
npm install
```

Or if you prefer yarn:

```bash
yarn install
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

The `.env` file should contain:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── ui/             # shadcn/ui components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   ├── Sidebar.tsx     # Navigation sidebar
│   │   ├── DashboardLayout.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx # Authentication context
│   ├── pages/              # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── Dashboard.tsx
│   ├── services/           # API services
│   │   ├── api.ts          # Axios instance with interceptors
│   │   └── auth.ts         # Authentication service
│   ├── types/              # TypeScript types
│   │   └── auth.ts
│   ├── lib/                # Utilities
│   │   └── utils.ts        # cn() helper
│   ├── styles/             # Global styles
│   │   └── index.css       # Tailwind + custom styles
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Entry point
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
├── package.json            # Dependencies
└── README.md               # This file
```

## Features

### Authentication

- Email/password registration and login
- GitHub OAuth integration
- JWT token management with automatic refresh
- Protected routes
- Persistent authentication

### Design System

- Dark theme with blue/slate color scheme
- Professional, enterprise-grade UI
- Fully responsive design
- Custom scrollbars
- Smooth transitions and animations

### Dashboard

- Welcome screen with user information
- Statistics cards for all major entities
- Quick action buttons
- Collapsible sidebar navigation
- Menu items:
  - Dashboard
  - Organizations
  - Locations
  - Contacts
  - Documentation
  - Passwords
  - Configurations
  - Settings
  - Logout

## API Integration

The frontend communicates with the Django backend API through Axios with the following features:

### Automatic Token Management

- Access tokens are automatically attached to requests
- Expired tokens are automatically refreshed
- Failed refresh redirects to login

### API Endpoints Used

```typescript
// Authentication
POST /api/auth/login/          // Login
POST /api/auth/registration/   // Register
POST /api/auth/logout/         // Logout
POST /api/token/refresh/       // Refresh token

// User
GET  /api/user/profile/        // Get user profile
PATCH /api/user/profile/       // Update profile
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Development Tips

### Adding New Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/Sidebar.tsx` (if needed)

### Adding New UI Components

1. Create component in `src/components/ui/`
2. Follow shadcn/ui patterns
3. Use the `cn()` utility for className merging

### Working with API

```typescript
import api from '@/services/api';

// Make authenticated requests
const response = await api.get('/api/endpoint/');
```

### TypeScript Types

Add new types in `src/types/` directory and import using `@/types/...`

## Styling Guide

### Colors

The app uses a custom dark theme with blue accents:

- **Primary**: Blue (`hsl(217.2 91.2% 59.8%)`)
- **Background**: Dark slate (`hsl(222.2 84% 4.9%)`)
- **Foreground**: Light (`hsl(210 40% 98%)`)

### Utility Classes

```css
/* Common patterns */
.premium-card {
  @apply border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10;
}

.glass-effect {
  @apply bg-background/80 backdrop-blur-sm;
}
```

## Building for Production

```bash
# Build the app
npm run build

# Preview the production build locally
npm run preview
```

The build output will be in the `dist/` directory.

## Deployment

### Static Hosting (Vercel, Netlify, etc.)

1. Build the app: `npm run build`
2. Deploy the `dist/` directory
3. Set environment variables in your hosting platform
4. Configure redirects for SPA routing

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:
```bash
npm run dev -- --port 3000
```

### API Connection Issues

1. Ensure backend is running on `http://localhost:8000`
2. Check CORS settings in Django
3. Verify `VITE_API_URL` in `.env`

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure TypeScript compiles: `npm run build`
4. Test thoroughly
5. Submit a pull request

## License

Proprietary - TechVault
