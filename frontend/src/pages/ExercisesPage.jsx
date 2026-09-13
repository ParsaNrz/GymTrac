import { useState, useEffect } from 'react';
import { exerciseQueries } from '../api/queries';
import { useAuth } from '../context/AuthContext';

export default function ExercisesPage() {
  const { user } = useAuth();
  const [exercises, setExercises] = useState([]);
  const [muscleGroups, setMuscleGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [filterGroup, setFilterGroup] = useState('');
  const [showAdminForm, setShowAdminForm] = useState(false);
  const [editingExercise, setEditingExercise] = useState(null);
  const [form, setForm] = useState({ name: '', primary_muscle_group: '', equipment: '', description: '' });
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [exRes, mgRes] = await Promise.all([
          exerciseQueries.list(),
          exerciseQueries.muscleGroups(),
        ]);
        setExercises(exRes.data);
        setMuscleGroups(mgRes.data);
      } catch (err) {
        setError('Could not load exercises.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const loadExerciseForEdit = async (id) => {
    try {
      const res = await exerciseQueries.get(id);
      setEditingExercise(id);
      setForm({
        name: res.data.name,
        primary_muscle_group: res.data.primary_muscle_group,
        equipment: res.data.equipment || '',
        description: res.data.description || '',
      });
      setShowAdminForm(true);
      setFormError('');
      setFormSuccess('');
    } catch (err) {
      setError('Could not load exercise details.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    try {
      if (editingExercise) {
        await exerciseQueries.update(editingExercise, form);
        setFormSuccess('Exercise updated.');
      } else {
        await exerciseQueries.create(form);
        setFormSuccess('Exercise created.');
      }
      // Reset form
      setForm({ name: '', primary_muscle_group: '', equipment: '', description: '' });
      setEditingExercise(null);
      // Refresh list
      const res = await exerciseQueries.list({ search, muscle_group: filterGroup });
      setExercises(res.data);
      setShowAdminForm(false);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Operation failed.';
      setFormError(msg);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this exercise?')) return;
    try {
      await exerciseQueries.delete(id);
      const res = await exerciseQueries.list({ search, muscle_group: filterGroup });
      setExercises(res.data);
      setFormSuccess('Exercise deleted.');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Delete failed.';
      setFormError(msg);
    }
  };

  const filteredExercises = exercises.filter(e => {
    if (filterGroup && e.primary_muscle_group !== filterGroup) return false;
    if (search && !e.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  if (loading) {
    return <div className="loading-state">Loading exercises...</div>;
  }

  return (
    <div className="exercises-page">
      <div className="exercises-header">
        <h1>Exercise Database</h1>
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => {
            setEditingExercise(null);
            setForm({ name: '', primary_muscle_group: '', equipment: '', description: '' });
            setShowAdminForm(true);
            setFormError('');
            setFormSuccess('');
          }}>
            + Add Exercise
          </button>
        )}
      </div>

      <div className="exercises-controls">
        <div className="exercise-search">
          <input
            className="form-input"
            type="text"
            placeholder="Search exercises..."
            value={search}
            onChange={e => setSearch(e.target.value)}
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
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {formSuccess && <div className="alert alert-success">{formSuccess}</div>}
      {formError && <div className="alert alert-error">{formError}</div>}

      <div className="exercises-grid">
        {filteredExercises.map(ex => (
          <div key={ex.id} className="exercise-card card">
            <div className="exercise-card-header">
              <h3 className="exercise-card-name">{ex.name}</h3>
              <span className="exercise-card-muscle badge">{ex.primary_muscle_group}</span>
            </div>
            {ex.equipment && (
              <p className="exercise-card-equipment">Equipment: {ex.equipment}</p>
            )}
            {ex.description && (
              <p className="exercise-card-description">{ex.description}</p>
            )}
            {isAdmin && (
              <div className="exercise-card-actions">
                <button className="btn btn-secondary btn-sm" onClick={() => loadExerciseForEdit(ex.id)}>
                  Edit
                </button>
                <button className="btn btn-danger btn-sm" onClick={() => handleDelete(ex.id)}>
                  Delete
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredExercises.length === 0 && !loading && (
        <p className="empty-state">No exercises found.</p>
      )}

      {showAdminForm && (
        <div className="admin-form-overlay">
          <div className="admin-form-card card">
            <h2>{editingExercise ? 'Edit Exercise' : 'Add Exercise'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="ex-name">Name</label>
                <input
                  id="ex-name"
                  className="form-input"
                  type="text"
                  value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })}
                  placeholder="e.g. Bench Press"
                  required
                  maxLength={100}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="ex-muscle">Primary Muscle Group</label>
                <select
                  id="ex-muscle"
                  className="form-input"
                  value={form.primary_muscle_group}
                  onChange={e => setForm({ ...form, primary_muscle_group: e.target.value })}
                  required
                >
                  <option value="">Select a group</option>
                  {muscleGroups.map(g => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="ex-equipment">Equipment (optional)</label>
                <input
                  id="ex-equipment"
                  className="form-input"
                  type="text"
                  value={form.equipment}
                  onChange={e => setForm({ ...form, equipment: e.target.value })}
                  placeholder="e.g. Barbell, Dumbbell, Bodyweight"
                  maxLength={50}
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="ex-desc">Description (optional)</label>
                <textarea
                  id="ex-desc"
                  className="form-input"
                  rows={3}
                  value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })}
                  placeholder="Brief description of the exercise..."
                />
              </div>
              <div className="form-actions">
                <button className="btn btn-primary" type="submit">
                  {editingExercise ? 'Update' : 'Create'}
                </button>
                <button className="btn btn-secondary" type="button" onClick={() => {
                  setShowAdminForm(false);
                  setEditingExercise(null);
                  setFormError('');
                  setFormSuccess('');
                }}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
