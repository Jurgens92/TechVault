import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/DashboardLayout';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import { Organizations } from '@/pages/Organizations';
import { OrganizationDetail } from '@/pages/OrganizationDetail';
import { OrganizationForm } from '@/pages/OrganizationForm';
import { Locations } from '@/pages/Locations';
import { LocationDetail } from '@/pages/LocationDetail';
import { LocationForm } from '@/pages/LocationForm';
import { Contacts } from '@/pages/Contacts';
import { ContactDetail } from '@/pages/ContactDetail';
import { ContactForm } from '@/pages/ContactForm';
import { Documentations } from '@/pages/Documentations';
import { DocumentationDetail } from '@/pages/DocumentationDetail';
import { DocumentationForm } from '@/pages/DocumentationForm';
import { Passwords } from '@/pages/Passwords';
import { PasswordDetail } from '@/pages/PasswordDetail';
import { PasswordForm } from '@/pages/PasswordForm';
import { Configurations } from '@/pages/Configurations';
import { ConfigurationDetail } from '@/pages/ConfigurationDetail';
import { ConfigurationForm } from '@/pages/ConfigurationForm';
import Settings from '@/pages/Settings';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="organizations" element={<Organizations />} />
            <Route path="organizations/:id" element={<OrganizationDetail />} />
            <Route path="organizations/:id/edit" element={<OrganizationForm />} />
            <Route path="organizations/new" element={<OrganizationForm />} />
            <Route path="locations" element={<Locations />} />
            <Route path="locations/:id" element={<LocationDetail />} />
            <Route path="locations/:id/edit" element={<LocationForm />} />
            <Route path="locations/new" element={<LocationForm />} />
            <Route path="contacts" element={<Contacts />} />
            <Route path="contacts/:id" element={<ContactDetail />} />
            <Route path="contacts/:id/edit" element={<ContactForm />} />
            <Route path="contacts/new" element={<ContactForm />} />
            <Route path="documentations" element={<Documentations />} />
            <Route path="documentations/:id" element={<DocumentationDetail />} />
            <Route path="documentations/:id/edit" element={<DocumentationForm />} />
            <Route path="documentations/new" element={<DocumentationForm />} />
            <Route path="passwords" element={<Passwords />} />
            <Route path="passwords/:id" element={<PasswordDetail />} />
            <Route path="passwords/:id/edit" element={<PasswordForm />} />
            <Route path="passwords/new" element={<PasswordForm />} />
            <Route path="configurations" element={<Configurations />} />
            <Route path="configurations/:id" element={<ConfigurationDetail />} />
            <Route path="configurations/:id/edit" element={<ConfigurationForm />} />
            <Route path="configurations/new" element={<ConfigurationForm />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
