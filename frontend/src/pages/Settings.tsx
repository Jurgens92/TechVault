import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Settings as SettingsIcon, User, Mail, Shield, Users, Plus, Edit, Trash2, X } from 'lucide-react';
import { userManagementService, User as UserType, CreateUserData } from '@/services/users';

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<UserType[]>([]);
  const [loading, setLoading] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState<UserType | null>(null);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    is_active: true,
    is_staff: false,
  });

  const isAdmin = user?.is_staff || false;

  useEffect(() => {
    if (isAdmin) {
      loadUsers();
    }
  }, [isAdmin]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const data = await userManagementService.getAllUsers();
      // Ensure data is always an array
      setUsers(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Failed to load users:', err);
      // Reset to empty array on error
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      setLoading(true);
      await userManagementService.createUser(formData as CreateUserData);
      await loadUsers();
      setShowUserModal(false);
      resetForm();
    } catch (err: any) {
      setError(err.response?.data?.email?.[0] || err.response?.data?.detail || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;
    setError('');
    try {
      setLoading(true);
      await userManagementService.updateUser(editingUser.id, {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        is_active: formData.is_active,
        is_staff: formData.is_staff,
      });
      await loadUsers();
      setShowUserModal(false);
      setEditingUser(null);
      resetForm();
    } catch (err: any) {
      setError(err.response?.data?.email?.[0] || err.response?.data?.detail || 'Failed to update user');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      setLoading(true);
      await userManagementService.deleteUser(userId);
      await loadUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    resetForm();
    setEditingUser(null);
    setShowUserModal(true);
  };

  const openEditModal = (userToEdit: UserType) => {
    setFormData({
      email: userToEdit.email,
      first_name: userToEdit.first_name,
      last_name: userToEdit.last_name,
      password: '',
      is_active: userToEdit.is_active,
      is_staff: userToEdit.is_staff,
    });
    setEditingUser(userToEdit);
    setShowUserModal(true);
  };

  const resetForm = () => {
    setFormData({
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      is_active: true,
      is_staff: false,
    });
    setError('');
  };

  const closeModal = () => {
    setShowUserModal(false);
    setEditingUser(null);
    resetForm();
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
            <SettingsIcon className="h-8 w-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>
        </div>
      </div>

      {/* Account Information */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Account Information
          </CardTitle>
          <CardDescription>
            Your account details and profile information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                Email Address
              </label>
              <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-md border border-border">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span>{user?.email}</span>
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">
                Full Name
              </label>
              <div className="flex items-center gap-2 p-3 bg-muted/50 rounded-md border border-border">
                <User className="h-4 w-4 text-muted-foreground" />
                <span>{user?.full_name || 'Not set'}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security
          </CardTitle>
          <CardDescription>
            Manage your security settings and password
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-muted/50 rounded-lg border border-border">
            <p className="text-sm text-muted-foreground">
              Security settings and password management features will be available soon.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* User Management - Admin Only */}
      {isAdmin && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  User Management
                </CardTitle>
                <CardDescription>
                  Manage system users and their permissions
                </CardDescription>
              </div>
              <Button onClick={openCreateModal} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Add User
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading && Array.isArray(users) && users.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading users...
              </div>
            ) : !Array.isArray(users) || users.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No users found
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Name</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Email</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Role</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Joined</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Array.isArray(users) && users.map((u) => (
                      <tr key={u.id} className="border-b border-border hover:bg-muted/50">
                        <td className="py-3 px-4 text-sm">{u.full_name}</td>
                        <td className="py-3 px-4 text-sm">{u.email}</td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${u.is_active ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                            {u.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <span className={`px-2 py-1 rounded text-xs ${u.is_staff ? 'bg-blue-500/10 text-blue-500' : 'bg-gray-500/10 text-gray-500'}`}>
                            {u.is_staff ? 'Admin' : 'User'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {new Date(u.date_joined).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openEditModal(u)}
                              disabled={loading}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteUser(u.id)}
                              disabled={loading || u.id === user?.id}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* User Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{editingUser ? 'Edit User' : 'Create New User'}</CardTitle>
                <Button variant="ghost" size="sm" onClick={closeModal}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser} className="space-y-4">
                {error && (
                  <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">Email</label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="first_name" className="text-sm font-medium">First Name</label>
                  <Input
                    id="first_name"
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="last_name" className="text-sm font-medium">Last Name</label>
                  <Input
                    id="last_name"
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    required
                    disabled={loading}
                  />
                </div>

                {!editingUser && (
                  <div className="space-y-2">
                    <label htmlFor="password" className="text-sm font-medium">Password</label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      required
                      disabled={loading}
                      minLength={8}
                    />
                  </div>
                )}

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      disabled={loading}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Active</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_staff}
                      onChange={(e) => setFormData({ ...formData, is_staff: e.target.checked })}
                      disabled={loading}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Admin</span>
                  </label>
                </div>

                <div className="flex gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={closeModal} disabled={loading} className="flex-1">
                    Cancel
                  </Button>
                  <Button type="submit" disabled={loading} className="flex-1">
                    {loading ? 'Saving...' : editingUser ? 'Update' : 'Create'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Settings;
