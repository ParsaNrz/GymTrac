import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import { calendarQueries } from '../api/queries';

const WEEKDAYS = [
  'Monday', 'Tuesday', 'Wednesday', 'Thursday',
  'Friday', 'Saturday', 'Sunday',
];

const WEEKDAY_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function CalendarPage() {
  const { user } = useAuth();
  const [calendarData, setCalendarData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCalendar = async () => {
      try {
        const res = await calendarQueries.getCalendar();
        setCalendarData(res.data);
      } catch (err) {
        setError('Could not load your workout calendar.');
      } finally {
        setLoading(false);
      }
    };
    fetchCalendar();
  }, []);

  const getDayData = (weekday) => {
    return calendarData?.days?.find(d => d.weekday === weekday);
  };

  const exerciseMap = useMemo(() => {
    const map = {};
    if (calendarData) {
      calendarData.days.forEach(day => {
        day.exercises.forEach(ex => {
          map[ex.exercise_id] = ex.exercise_name;
        });
      });
    }
    return map;
  }, [calendarData]);

  if (loading) {
    return <div className="loading-state">Loading calendar...</div>;
  }

  return (
    <div className="calendar-page">
      <h1>Your Workout Calendar</h1>
      {user && (
        <p className="calendar-subtitle">
          Weekly schedule for <strong>{user.username}</strong>
        </p>
      )}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Weekly schedule */}
      <div className="calendar-week-card card">
        <h2>Weekly Schedule</h2>
        <div className="calendar-week-grid">
          {WEEKDAYS.map(weekday => {
            const dayData = getDayData(weekday);
            const exercises = dayData?.exercises || [];
            const hasWorkout = exercises.length > 0;

            return (
              <div
                key={weekday}
                className={`calendar-week-day card ${hasWorkout ? 'has-workout' : ''}`}
              >
                <div className="calendar-weekday-header">
                  <span className="weekday-name">{weekday}</span>
                  {hasWorkout && (
                    <span className="weekday-badge">
                      {exercises.length} exercise{exercises.length !== 1 ? 's' : ''}
                    </span>
                  )}
                </div>

                {hasWorkout ? (
                  <ul className="calendar-day-exercises">
                    {exercises.map(ex => (
                      <li key={ex.assignment_id} className="calendar-exercise-item">
                        <div className="calendar-exercise-main">
                          <span className="calendar-exercise-name">
                            {ex.exercise_name}
                          </span>
                          {ex.sets && ex.reps && (
                            <span className="calendar-exercise-meta">
                              {ex.sets} × {ex.reps}
                            </span>
                          )}
                          {ex.equipment && (
                            <span className="calendar-exercise-equipment">
                              {ex.equipment}
                            </span>
                          )}
                        </div>
                        {ex.notes && (
                          <p className="calendar-exercise-notes">{ex.notes}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="calendar-rest-day">Rest day</p>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="calendar-legend card">
        <span className="legend-item">
          <span className="legend-dot has-workout-dot"></span>
          Day with exercises
        </span>
        <span className="legend-item">
          <span className="legend-dot rest-day-dot"></span>
          Rest day
        </span>
      </div>
    </div>
  );
}
