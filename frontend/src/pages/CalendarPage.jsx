import { useState, useEffect, useMemo } from 'react';
import { workoutQueries } from '../api/queries';

const WEEKDAY_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const WEEKDAY_FULL = [
  'Sunday', 'Monday', 'Tuesday', 'Wednesday',
  'Thursday', 'Friday', 'Saturday',
];

export default function CalendarPage() {
  const [plan, setPlan] = useState(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null);
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

  const getExercisesForDate = (date) => {
    const weekday = WEEKDAY_FULL[date.getDay()];
    const day = plan?.days?.find(d => d.weekday === weekday);
    return day?.exercises || [];
  };

  const isWorkoutDay = (date) => {
    return getExercisesForDate(date).length > 0;
  };

  const getMonthGrid = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPad = firstDay.getDay();
    const totalDays = lastDay.getDate();
    const days = [];

    // Previous month padding
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startPad - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthLastDay - i),
        isOtherMonth: true,
      });
    }
    // Current month
    for (let d = 1; d <= totalDays; d++) {
      days.push({
        date: new Date(year, month, d),
        isOtherMonth: false,
      });
    }
    // Next month padding to fill the grid
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isOtherMonth: true,
      });
    }
    return days;
  };

  const monthGrid = useMemo(() => getMonthGrid(currentDate), [currentDate]);

  const goToPrev = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNext = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDay(null);
  };

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  if (loading) {
    return <div className="loading-state">Loading calendar...</div>;
  }

  return (
    <div className="calendar-page">
      <h1>Calendar</h1>

      <div className="calendar-header">
        <button className="btn btn-secondary" onClick={goToPrev}>← Prev</button>
        <h2 className="calendar-title">{monthName}</h2>
        <button className="btn btn-secondary" onClick={goToNext}>Next →</button>
        <button className="btn btn-primary" onClick={goToToday}>Today</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="calendar-controls">
        <div className="view-toggle">
          <button className="btn btn-secondary btn-sm active">Monthly</button>
        </div>
      </div>

      <div className="calendar-grid card">
        <div className="calendar-weekdays">
          {WEEKDAY_SHORT.map(d => (
            <div key={d} className="weekday-label">{d}</div>
          ))}
        </div>
        <div className="calendar-days">
          {monthGrid.map(({ date, isOtherMonth }) => {
            const exercises = getExercisesForDate(date);
            const hasWorkout = exercises.length > 0;
            const isSelected = selectedDay?.getTime() === date.getTime();
            const isToday =
              date.getDate() === new Date().getDate() &&
              date.getMonth() === new Date().getMonth() &&
              date.getFullYear() === new Date().getFullYear();

            return (
              <div
                key={date.getTime()}
                className={`calendar-cell ${isOtherMonth ? 'other-month' : ''} ${hasWorkout ? 'has-workout' : ''} ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
                onClick={() => setSelectedDay(date)}
              >
                <span className="cell-date">{date.getDate()}</span>
                {hasWorkout && <span className="workout-indicator">●</span>}
              </div>
            );
          })}
        </div>
      </div>

      {selectedDay && (
        <div className="selected-day-card card">
          <h3>
            {WEEKDAY_FULL[selectedDay.getDay()]}, {selectedDay.toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric',
            })}
          </h3>
          <div className="selected-day-exercises">
            {isWorkoutDay(selectedDay) ? (
              <>
                <h4>Exercises ({getExercisesForDate(selectedDay).length})</h4>
                <ul className="exercise-list">
                  {getExercisesForDate(selectedDay).map(ex => (
                    <li key={ex.id} className="exercise-item">
                      <span className="exercise-name">
                        Exercise #{ex.exercise_id} (order: {ex.display_order})
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="rest-day-message">No exercises scheduled for this day.</p>
            )}
          </div>
          <button
            className="btn btn-secondary"
            onClick={() => setSelectedDay(null)}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
