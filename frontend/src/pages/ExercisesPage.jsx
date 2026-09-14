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

  const filteredExercises = exercises.filter(e => {
    if (filterGroup && e.primary_muscle_group !== filterGroup) return false;
    if (search && !e.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const grouped = {};
  filteredExercises.forEach(ex => {
    if (!grouped[ex.primary_muscle_group]) {
      grouped[ex.primary_muscle_group] = [];
    }
    grouped[ex.primary_muscle_group].push(ex);
  });

  if (loading) {
    return <div className="loading-state">Loading exercises...</div>;
  }

  return (
    <div className="exercises-page">
      <div className="exercises-header">
        <h1>Exercise Database</h1>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="exercises-controls">
        <div className="exercise-search">
          <input
            className="form-input"
            type="text"
            placeholder="Search exercises by name..."
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

      <div className="exercises-summary">
        <span className="summary-count">
          {filteredExercises.length} exercise{filteredExercises.length !== 1 ? 's' : ''}
          {filterGroup && ` in ${filterGroup}`}
        </span>
      </div>

      {Object.keys(grouped).length > 0 ? (
        Object.entries(grouped).map(([group, exs]) => (
          <section key={group} className="exercise-group card">
            <h2 className="exercise-group-title">{group}</h2>
            <div className="exercise-group-list">
              {exs.map(ex => (
                <div key={ex.id} className="exercise-item">
                  <div className="exercise-item-main">
                    <span className="exercise-name">{ex.name}</span>
                    {ex.equipment && (
                      <span className="exercise-equipment">{ex.equipment}</span>
                    )}
                  </div>
                  {ex.description && (
                    <p className="exercise-description">{ex.description}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
        ))
      ) : (
        <div className="empty-state card">
          <p>No exercises found matching your filters.</p>
        </div>
      )}
    </div>
  );
}
