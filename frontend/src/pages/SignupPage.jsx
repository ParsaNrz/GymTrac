import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState('');
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await signup({
        username,
        password,
        age: age ? parseInt(age, 10) : null,
        height: height ? parseInt(height, 10) : null,
        weight: weight ? parseInt(weight, 10) : null,
      });
      setSuccess(true);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Signup failed';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card card">
          <h1 className="auth-title">Account Created</h1>
          <p className="auth-subtitle">You can now log in to GymTrac.</p>
          <Link to="/login" className="btn btn-primary">Go to Login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1 className="auth-title">Sign Up</h1>
        <p className="auth-subtitle">Create your GymTrac account</p>
        <form onSubmit={handleSubmit}>
          {error && <div className="alert alert-error">{error}</div>}
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="form-input"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Choose a username"
              autoComplete="username"
              required
              minLength={3}
              maxLength={50}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input
              id="password"
              className="form-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Choose a password"
              autoComplete="new-password"
              required
              minLength={6}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="age">Age (optional)</label>
            <input
              id="age"
              className="form-input"
              type="number"
              value={age}
              onChange={e => setAge(e.target.value)}
              placeholder="e.g. 25"
              min={1}
              max={150}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="height">Height in cm (optional)</label>
            <input
              id="height"
              className="form-input"
              type="number"
              value={height}
              onChange={e => setHeight(e.target.value)}
              placeholder="e.g. 175"
              min={50}
              max={300}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="weight">Weight in kg (optional)</label>
            <input
              id="weight"
              className="form-input"
              type="number"
              value={weight}
              onChange={e => setWeight(e.target.value)}
              placeholder="e.g. 75"
              min={10}
              max={500}
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
