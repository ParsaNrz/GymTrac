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
    password: '',
    confirm_password: '',
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
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
    if (form.age !== '' && form.age !== user?.age) {
      updateData.age = parseInt(form.age, 10);
    }
    if (form.height !== '' && form.height !== user?.height) {
      updateData.height = parseInt(form.height, 10);
    }
    if (form.weight !== '' && form.weight !== user?.weight) {
      updateData.weight = parseInt(form.weight, 10);
    }
    if (form.password) {
      if (form.password !== form.confirm_password) {
        setError('Passwords do not match.');
        setSaving(false);
        return;
      }
      if (form.password.length < 6) {
        setError('Password must be at least 6 characters.');
        setSaving(false);
        return;
      }
      updateData.password = form.password;
    }

    try {
      await userQueries.updateMe(updateData);
      setSuccess('Profile updated successfully.');
      // Clear password fields
      setForm({ ...form, password: '', confirm_password: '' });
    } catch (err) {
      const msg = err.response?.data?.detail || 'Update failed.';
      setError(msg);
    } finally {
      setSaving(false);
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

          <h3>Change Password</h3>
          <div className="form-group">
            <label className="form-label" htmlFor="settings-password">New Password</label>
            <input
              id="settings-password"
              className="form-input"
              type="password"
              value={form.password}
              onChange={handleChange('password')}
              placeholder="Leave blank to keep current password"
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="settings-confirm">Confirm New Password</label>
            <input
              id="settings-confirm"
              className="form-input"
              type="password"
              value={form.confirm_password}
              onChange={handleChange('confirm_password')}
              placeholder="Re-enter new password"
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
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
