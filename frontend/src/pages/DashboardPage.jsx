import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { workoutQueries } from '../api/queries';

const WEEKDAY_FULL = [
  'Sunday', 'Monday', 'Tuesday', 'Wednesday',
  'Thursday', 'Friday', 'Saturday',
];

export default function DashboardPage() {
  const { user } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const res = await workoutQueries.getPlan();
        setPlan(res.data);
      } catch (err) {
        setError('Could not load your workout plan.');
      } finally {
        setLoading(false);
      }
    };
    fetchPlan();
  }, []);

  const today = new Date();
  const todayWeekday = WEEKDAY_FULL[today.getDay()];
  const todayDateStr = today.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const todayDay = plan?.days?.find(d => d.weekday === todayWeekday);
  const todayExercises = todayDay?.exercises || [];
  const isRestDay = todayExercises.length === 0;

  const getGreeting = () => {
    const hour = today.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) {
    return <div className="loading-state">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <section className="dashboard-greeting card">
        <h1>{getGreeting()}, {user?.username || 'User'}!</h1>
        <p className="greeting-date">{todayDateStr}</p>
      </section>

      <section className="dashboard-profile card">
        <h2>Your Profile</h2>
        <div className="profile-grid">
          <div className="profile-item">
            <span className="profile-label">Username</span>
            <span className="profile-value">{user?.username}</span>
          </div>
          {user?.age && (
            <div className="profile-item">
              <span className="profile-label">Age</span>
              <span className="profile-value">{user.age} years</span>
            </div>
          )}
          {user?.height && (
            <div className="profile-item">
              <span className="profile-label">Height</span>
              <span className="profile-value">{user.height} cm</span>
            </div>
          )}
          {user?.weight && (
            <div className="profile-item">
              <span className="profile-label">Weight</span>
              <span className="profile-value">{user.weight} kg</span>
            </div>
          )}
          <div className="profile-item">
            <span className="profile-label">Role</span>
            <span className="profile-value">{user?.role}</span>
          </div>
        </div>
      </section>

      <section className="dashboard-today card">
        <h2>Today: {todayWeekday}</h2>
        {error && <div className="alert alert-error">{error}</div>}
        {isRestDay ? (
          <div className="rest-day-message">
            <div className="rest-day-icon">💪</div>
            <h3>Today is a rest day</h3>
            <p>You have no exercises scheduled for today. Recover and come back tomorrow.</p>
            <a href="/workout" className="btn btn-secondary">Plan your workout</a>
          </div>
        ) : (
          <div className="today-exercises">
            <h3>Exercises for today</h3>
            <ul className="exercise-list">
              {todayExercises.map(ex => (
                <li key={ex.id} className="exercise-item">
                  <span className="exercise-name">
                    {/* Exercise name comes from the exercise detail; we store only id.
                        In V1 we show the ID; the real name requires a join.
                        The frontend will fetch exercise names separately if needed.
                        For now we show a placeholder — the backend returns exercise_id. */}
                    Exercise #{ex.exercise_id}
                  </span>
                  <span className="exercise-order">Order: {ex.display_order}</span>
                </li>
              ))}
            </ul>
            <a href="/workout" className="btn btn-primary">Manage Today's Workout</a>
          </div>
        )}
      </section>
    </div>
  );
}
