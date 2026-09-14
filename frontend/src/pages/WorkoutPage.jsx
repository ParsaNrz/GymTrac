import { useState, useEffect } from 'react';
import { workoutQueries } from '../api/queries';
import { exerciseQueries } from '../api/queries';

const WEEKDAYS = [
  'Monday', 'Tuesday', 'Wednesday', 'Thursday',
  'Friday', 'Saturday', 'Sunday',
];

export default function WorkoutPage() {
  const [plan, setPlan] = useState(null);
  const [exercises, setExercises] = useState([]);
  const [muscleGroups, setMuscleGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedDay, setExpandedDay] = useState(null);
  const [addingExercise, setAddingExercise] = useState(null);
  const [addSearch, setAddSearch] = useState('');
  const [filterGroup, setFilterGroup] = useState('');
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [editSets, setEditSets] = useState('');
  const [editReps, setEditReps] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [planRes, exRes, mgRes] = await Promise.all([
          workoutQueries.getPlan(),
          exerciseQueries.list(),
          exerciseQueries.muscleGroups(),
        ]);
        setPlan(planRes.data);
        setExercises(exRes.data);
        setMuscleGroups(mgRes.data);
      } catch (err) {
        setError('Could not load workout data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAddExercise = async (weekday, exerciseId) => {
    try {
      const res = await workoutQueries.addExercise(weekday, exerciseId);
      setPlan(res.data);
      setAddingExercise(null);
      setAddSearch('');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to add exercise';
      setError(msg);
    }
  };

  const handleRemoveExercise = async (weekday, assignmentId) => {
    try {
      await workoutQueries.removeExercise(weekday, assignmentId);
      const res = await workoutQueries.getPlan();
      setPlan(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to remove exercise';
      setError(msg);
    }
  };

  const startEdit = (assignment, weekday) => {
    setEditingAssignment({ assignment, weekday });
    setEditSets(assignment.sets !== null && assignment.sets !== undefined ? assignment.sets : '');
    setEditReps(assignment.reps !== null && assignment.reps !== undefined ? assignment.reps : '');
    setEditNotes(assignment.notes || '');
  };

  const handleSaveEdit = async () => {
    if (!editingAssignment) return;
    const { assignment, weekday } = editingAssignment;
    setSavingEdit(true);
    try {
      const data = {};
      if (editSets !== '') data.sets = parseInt(editSets, 10);
      if (editReps !== '') data.reps = parseInt(editReps, 10);
      if (editNotes !== '') data.notes = editNotes;
      const res = await workoutQueries.updateExercise(weekday, assignment.id, data);
      setPlan(res.data);
      setEditingAssignment(null);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to update exercise';
      setError(msg);
    } finally {
      setSavingEdit(false);
    }
  };

  const getDayExercises = (weekday) => {
    const day = plan?.days?.find(d => d.weekday === weekday);
    return day?.exercises || [];
  };

  const filteredExercises = exercises.filter(e => {
    if (filterGroup && e.primary_muscle_group !== filterGroup) return false;
    if (addSearch && !e.name.toLowerCase().includes(addSearch.toLowerCase())) return false;
    return true;
  });

  if (loading) {
    return <div className="loading-state">Loading workout...</div>;
  }

  return (
    <div className="workout-page">
      <h1>Your Workout Plan</h1>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="workout-grid">
        <div className="workout-days">
          <h2>Weekly Schedule</h2>
          <div className="days-list">
            {WEEKDAYS.map(day => {
              const dayExercises = getDayExercises(day);
              const isExpanded = expandedDay === day;
              return (
                <div key={day} className="day-card card">
                  <button
                    className="day-header"
                    onClick={() => setExpandedDay(isExpanded ? null : day)}
                  >
                    <span className="day-name">{day}</span>
                    <span className="day-count">{dayExercises.length} exercises</span>
                    <span className={`day-toggle ${isExpanded ? 'expanded' : ''}`}>
                      {isExpanded ? '▼' : '▶'}
                    </span>
                  </button>
                  {isExpanded && (
                    <div className="day-content">
                      {dayExercises.length === 0 ? (
                        <p className="day-empty">No exercises assigned. Click "Add Exercise" to add one.</p>
                      ) : (
                        <ul className="day-exercise-list">
                          {dayExercises.map(ex => {
                            const exercise = exercises.find(e => e.id === ex.exercise_id);
                            const isEditing = editingAssignment?.assignment?.id === ex.id;
                            return (
                              <li key={ex.id} className="day-exercise-item">
                                <div className="exercise-header">
                                  <span className="day-exercise-name">
                                    {exercise ? exercise.name : `Exercise #${ex.exercise_id}`}
                                  </span>
                                  {isEditing ? (
                                    <div className="edit-form">
                                      <input
                                        className="form-input form-input-sm"
                                        type="number"
                                        placeholder="Sets"
                                        value={editSets}
                                        onChange={e => setEditSets(e.target.value)}
                                        min={1}
                                        max={100}
                                      />
                                      <input
                                        className="form-input form-input-sm"
                                        type="number"
                                        placeholder="Reps"
                                        value={editReps}
                                        onChange={e => setEditReps(e.target.value)}
                                        min={1}
                                        max={1000}
                                      />
                                      <input
                                        className="form-input form-input-sm"
                                        type="text"
                                        placeholder="Notes"
                                        value={editNotes}
                                        onChange={e => setEditNotes(e.target.value)}
                                        maxLength={500}
                                      />
                                      <button
                                        className="btn btn-primary btn-sm"
                                        onClick={handleSaveEdit}
                                        disabled={savingEdit}
                                      >
                                        {savingEdit ? 'Saving...' : 'Save'}
                                      </button>
                                      <button
                                        className="btn btn-secondary btn-sm"
                                        onClick={() => setEditingAssignment(null)}
                                      >
                                        Cancel
                                      </button>
                                    </div>
                                  ) : (
                                    <div className="exercise-meta">
                                      {ex.sets && ex.reps && (
                                        <span className="exercise-sets-reps">
                                          {ex.sets} × {ex.reps}
                                        </span>
                                      )}
                                      {ex.notes && (
                                        <span className="exercise-notes">{ex.notes}</span>
                                      )}
                                    </div>
                                  )}
                                </div>
                                {!isEditing && (
                                  <div className="exercise-actions">
                                    <button
                                      className="btn btn-secondary btn-sm"
                                      onClick={() => startEdit(ex, day)}
                                    >
                                      Edit
                                    </button>
                                    <button
                                      className="btn btn-danger btn-sm"
                                      onClick={() => handleRemoveExercise(day, ex.id)}
                                    >
                                      Remove
                                    </button>
                                  </div>
                                )}
                              </li>
                            );
                          })}
                        </ul>
                      )}
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => {
                          setAddingExercise(day);
                          setAddSearch('');
                        }}
                      >
                        + Add Exercise
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="workout-sidebar">
          <h2>Exercise Database</h2>
          <div className="exercise-search">
            <input
              className="form-input"
              type="text"
              placeholder="Search exercises..."
              value={addSearch}
              onChange={e => setAddSearch(e.target.value)}
            />
          </div>
          <div className="exercise-filters">
            <label className="form-label">Filter by muscle group:</label>
            <select
              className="form-input"
              value={filterGroup}
              onChange={e => setFilterGroup(e.target.value)}
            >
              <option value="">All groups</option>
              {muscleGroups.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
          <div className="exercise-list-card card">
            <ul className="exercise-db-list">
              {filteredExercises.map(ex => (
                <li key={ex.id} className="exercise-db-item">
                  <div className="exercise-db-info">
                    <span className="exercise-db-name">{ex.name}</span>
                    <span className="exercise-db-meta">
                      {ex.primary_muscle_group}
                      {ex.equipment ? ` • ${ex.equipment}` : ''}
                    </span>
                  </div>
                  {addingExercise && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleAddExercise(addingExercise, ex.id)}
                    >
                      Add to {addingExercise}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
          {addingExercise && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => {
                setAddingExercise(null);
                setAddSearch('');
              }}
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
