import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { userQueries } from '../api/queries';

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [form, setForm] = useState({
    username: user?.username || '',
    age: user?.age ?? '',
    height: user?.height ?? '',
    weight: user?.weight ?? '',
  });
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setSaving(true);

    const updateData = {};
    if (form.username && form.username !== user?.username) {
      updateData.username = form.username;
    }
    if (form.age !== '' && String(form.age) !== String(user?.age ?? '')) {
      updateData.age = parseInt(form.age, 10);
    }
    if (form.height !== '' && String(form.height) !== String(user?.height ?? '')) {
      updateData.height = parseInt(form.height, 10);
    }
    if (form.weight !== '' && String(form.weight) !== String(user?.weight ?? '')) {
      updateData.weight = parseInt(form.weight, 10);
    }

    try {
      await userQueries.updateMe(updateData);
      setSuccess('Profile updated successfully.');
      // Refresh user data from context
      const res = await userQueries.getMe();
      // Note: parent component manages user state; we rely on the success message
    } catch (err) {
      const msg = err.response?.data?.detail || 'Update failed.';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!currentPassword) {
      setError('Please enter your current password.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }
    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters.');
      return;
    }

    setChangingPassword(true);
    try {
      await userQueries.changePassword({ current_password: currentPassword, new_password: newPassword });
      setSuccess('Password changed successfully. Please log in with your new password.');
      // Clear password fields
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      // Trigger logout so user must re-login with new password
      setTimeout(() => { logout(); }, 1500);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Password change failed.';
      setError(msg);
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      <div className="settings-section card">
        <h2>Profile</h2>
        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <div className="form-group">
            <label className="form-label" htmlFor="settings-username">Username</label>
            <input
              id="settings-username"
              className="form-input"
              type="text"
              value={form.username}
              onChange={handleChange('username')}
              placeholder="Username"
              minLength={3}
              maxLength={50}
            />
            <p className="form-hint">Your unique username. Can be changed once.</p>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-age">Age</label>
            <input
              id="settings-age"
              className="form-input"
              type="number"
              value={form.age}
              onChange={handleChange('age')}
              placeholder="Age"
              min={1}
              max={150}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-height">Height (cm)</label>
            <input
              id="settings-height"
              className="form-input"
              type="number"
              value={form.height}
              onChange={handleChange('height')}
              placeholder="Height in cm"
              min={50}
              max={300}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-weight">Weight (kg)</label>
            <input
              id="settings-weight"
              className="form-input"
              type="number"
              value={form.weight}
              onChange={handleChange('weight')}
              placeholder="Weight in kg"
              min={10}
              max={500}
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Profile Changes'}
          </button>
        </form>
      </div>

      <div className="settings-section card">
        <h2>Change Password</h2>
        <form onSubmit={handleChangePassword}>
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <div className="form-group">
            <label className="form-label" htmlFor="settings-current-password">Current Password</label>
            <input
              id="settings-current-password"
              className="form-input"
              type="password"
              value={currentPassword}
              onChange={e => setCurrentPassword(e.target.value)}
              placeholder="Enter current password"
              autoComplete="current-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-new-password">New Password</label>
            <input
              id="settings-new-password"
              className="form-input"
              type="password"
              value={newPassword}
              onChange={e => setNewPassword(e.target.value)}
              placeholder="Enter new password (min 6 characters)"
              minLength={6}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-confirm-password">Confirm New Password</label>
            <input
              id="settings-confirm-password"
              className="form-input"
              type="password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="Re-enter new password"
              autoComplete="new-password"
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={changingPassword}>
            {changingPassword ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>

      <div className="settings-section card">
        <h2>Danger Zone</h2>
        <p className="settings-warning">Once you logout, you will need your credentials to log back in.</p>
        <button className="btn btn-danger" onClick={logout}>Logout</button>
      </div>
    </div>
  );
}
