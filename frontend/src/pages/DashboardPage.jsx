import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { dashboardQueries } from '../api/queries';
import { workoutQueries } from '../api/queries';
import { exerciseQueries } from '../api/queries';

const WEEKDAY_FULL = [
  'Sunday', 'Monday', 'Tuesday', 'Wednesday',
  'Thursday', 'Friday', 'Saturday',
];

export default function DashboardPage() {
  const { user: authUser } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [plan, setPlan] = useState(null);
  const [exerciseMap, setExerciseMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, planRes, exRes] = await Promise.all([
          dashboardQueries.getDashboard(),
          workoutQueries.getPlan(),
          exerciseQueries.list(),
        ]);
        setDashboard(dashRes.data);
        setPlan(planRes.data);
        const map = {};
        exRes.data.forEach(ex => { map[ex.id] = ex.name; });
        setExerciseMap(map);
      } catch (err) {
        setError('Could not load dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const today = new Date();
  const todayWeekday = WEEKDAY_FULL[today.getDay()];
  const todayDateStr = today.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  const getGreeting = () => {
    const hour = today.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const todayDay = plan?.days?.find(d => d.weekday === todayWeekday);
  const todayExercises = todayDay?.exercises || [];

  const summary = dashboard?.plan_summary;

  if (loading) {
    return <div className="loading-state">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <section className="dashboard-greeting card">
        <h1>{getGreeting()}, {dashboard?.user?.username || authUser?.username || 'User'}!</h1>
        <p className="greeting-date">{todayDateStr}</p>
      </section>

      <section className="dashboard-profile card">
        <h2>Your Profile</h2>
        <div className="profile-grid">
          <div className="profile-item">
            <span className="profile-label">Username</span>
            <span className="profile-value">{dashboard?.user?.username || '—'}</span>
          </div>
          {dashboard?.user?.age && (
            <div className="profile-item">
              <span className="profile-label">Age</span>
              <span className="profile-value">{dashboard.user.age} years</span>
            </div>
          )}
          {dashboard?.user?.height && (
            <div className="profile-item">
              <span className="profile-label">Height</span>
              <span className="profile-value">{dashboard.user.height} cm</span>
            </div>
          )}
          {dashboard?.user?.weight && (
            <div className="profile-item">
              <span className="profile-label">Weight</span>
              <span className="profile-value">{dashboard.user.weight} kg</span>
            </div>
          )}
          <div className="profile-item">
            <span className="profile-label">Role</span>
            <span className="profile-value">{dashboard?.user?.role || '—'}</span>
          </div>
        </div>
      </section>

      <section className="dashboard-summary card">
        <h2>Workout Plan Summary</h2>
        {summary?.plan_id === null ? (
          <div className="summary-empty">
            <p>No workout plan yet. Head to the <a href="/workout">Workout</a> page to create one.</p>
          </div>
        ) : (
          <div className="summary-stats">
            <div className="summary-stat">
              <span className="summary-value">{summary?.total_days || 0}</span>
              <span className="summary-label">Days planned</span>
            </div>
            <div className="summary-stat">
              <span className="summary-value">{summary?.total_exercises || 0}</span>
              <span className="summary-label">Total exercises</span>
            </div>
            <div className="summary-stat">
              <span className="summary-value">{summary?.today_exercises_count || 0}</span>
              <span className="summary-label">Today's exercises</span>
            </div>
          </div>
        )}
      </section>

      <section className="dashboard-today card">
        <h2>Today: {todayWeekday}</h2>
        {error && <div className="alert alert-error">{error}</div>}
        {summary?.is_rest_day ? (
          <div className="rest-day-message">
            <div className="rest-day-icon">💪</div>
            <h3>Today is a rest day</h3>
            <p>You have no exercises scheduled for today. Recover and come back tomorrow.</p>
            <a href="/workout" className="btn btn-secondary">Plan your workout</a>
          </div>
        ) : todayExercises.length > 0 ? (
          <div className="today-exercises">
            <h3>Exercises for today</h3>
            <ul className="exercise-list">
              {todayExercises.map(ex => {
                const exName = exerciseMap[ex.exercise_id] || `Exercise #${ex.exercise_id}`;
                return (
                  <li key={ex.id} className="exercise-item">
                    <span className="exercise-name">{exName}</span>
                    {ex.sets && ex.reps && (
                      <span className="exercise-meta">{ex.sets} × {ex.reps}</span>
                    )}
                    {ex.notes && (
                      <span className="exercise-notes">{ex.notes}</span>
                    )}
                  </li>
                );
              })}
            </ul>
            <a href="/workout" className="btn btn-primary">Manage Today's Workout</a>
          </div>
        ) : (
          <div className="rest-day-message">
            <p>No exercises for today yet. <a href="/workout">Add some</a>.</p>
          </div>
        )}
      </section>
    </div>
  );
}
