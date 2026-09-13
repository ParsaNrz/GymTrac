import { useState, useEffect } from 'react';
import { adminQueries } from '../api/queries';
import { useAuth } from '../context/AuthContext';

export default function AdminPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('users');

  // Users state
  const [users, setUsers] = useState([]);
  const [userLoading, setUserLoading] = useState(true);
  const [userError, setUserError] = useState('');
  const [userSearch, setUserSearch] = useState('');
  const [userPage, setUserPage] = useState(1);
  const [userTotal, setUserTotal] = useState(0);

  // Exercises state
  const [exercises, setExercises] = useState([]);
  const [exLoading, setExLoading] = useState(true);
  const [exError, setExError] = useState('');
  const [exSearch, setExSearch] = useState('');
  const [exFilterGroup, setExFilterGroup] = useState('');
  const [exMuscleGroups, setExMuscleGroups] = useState([]);

  // Admin exercise form
  const [showExForm, setShowExForm] = useState(false);
  const [editingEx, setEditingEx] = useState(null);
  const [exForm, setExForm] = useState({ name: '', primary_muscle_group: '', equipment: '', description: '' });
  const [exFormError, setExFormError] = useState('');
  const [exFormSuccess, setExFormSuccess] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const params = {};
        if (userSearch) params.search = userSearch;
        params.page = userPage;
        params.page_size = 20;
        const res = await adminQueries.listUsers(params);
        setUsers(res.data);
      } catch (err) {
        setUserError('Could not load users.');
      } finally {
        setUserLoading(false);
      }
    };
    fetchUsers();
  }, [userSearch, userPage]);

  useEffect(() => {
    const fetchExercises = async () => {
      try {
        const params = {};
        if (exSearch) params.search = exSearch;
        if (exFilterGroup) params.muscle_group = exFilterGroup;
        const res = await adminQueries.listExercises(params);
        setExercises(res.data);
      } catch (err) {
        setExError('Could not load exercises.');
      } finally {
        setExLoading(false);
      }
    };
    fetchExercises();
  }, [exSearch, exFilterGroup]);

  useEffect(() => {
    const fetchMuscleGroups = async () => {
      try {
        const res = await adminQueries.listExercises({}); // re-use, but we want muscle groups
        // We'll hardcode muscle groups from the known list
        setExMuscleGroups([
          'Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps',
          'Legs', 'Glutes', 'Calves', 'Abs', 'Forearms',
        ]);
      } catch (_) {}
    };
    fetchMuscleGroups();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await adminQueries.changeRole(userId, newRole);
      // Refresh users list
      const params = {};
      if (userSearch) params.search = userSearch;
      params.page = userPage;
      params.page_size = 20;
      const res = await adminQueries.listUsers(params);
      setUsers(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to change role.';
      setUserError(msg);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Delete this user? This cannot be undone.')) return;
    try {
      await adminQueries.deleteUser(userId);
      const params = {};
      if (userSearch) params.search = userSearch;
      params.page = userPage;
      params.page_size = 20;
      const res = await adminQueries.listUsers(params);
      setUsers(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Delete failed.';
      setUserError(msg);
    }
  };

  const loadExerciseForEdit = async (id) => {
    try {
      const res = await adminQueries.listExercises({}); // We need a get-by-id endpoint; reuse admin list and find
      const ex = res.data.find(e => e.id === id);
      if (ex) {
        setEditingEx(id);
        setExForm({
          name: ex.name,
          primary_muscle_group: ex.primary_muscle_group,
          equipment: ex.equipment || '',
          description: ex.description || '',
        });
        setShowExForm(true);
        setExFormError('');
        setExFormSuccess('');
      }
    } catch (err) {
      setExError('Could not load exercise.');
    }
  };

  const handleExSubmit = async (e) => {
    e.preventDefault();
    setExFormError('');
    setExFormSuccess('');
    try {
      if (editingEx) {
        await adminQueries.updateExercise(editingEx, exForm);
        setExFormSuccess('Exercise updated.');
      } else {
        await adminQueries.createExercise(exForm);
        setExFormSuccess('Exercise created.');
      }
      setExForm({ name: '', primary_muscle_group: '', equipment: '', description: '' });
      setEditingEx(null);
      setShowExForm(false);
      // Refresh
      const params = {};
      if (exSearch) params.search = exSearch;
      if (exFilterGroup) params.muscle_group = exFilterGroup;
      const res = await adminQueries.listExercises(params);
      setExercises(res.data);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Operation failed.';
      setExFormError(msg);
    }
  };

  const handleExDelete = async (id) => {
    if (!confirm('Delete this exercise?')) return;
    try {
      await adminQueries.deleteExercise(id);
      const params = {};
      if (exSearch) params.search = exSearch;
      if (exFilterGroup) params.muscle_group = exFilterGroup;
      const res = await adminQueries.listExercises(params);
      setExercises(res.data);
      setExFormSuccess('Exercise deleted.');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Delete failed.';
      setExFormError(msg);
    }
  };

  return (
    <div className="admin-page">
      <h1>Admin Panel</h1>
      <p className="admin-subtitle">Welcome, {user?.username}</p>

      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Users
        </button>
        <button
          className={`admin-tab ${activeTab === 'exercises' ? 'active' : ''}`}
          onClick={() => setActiveTab('exercises')}
        >
          Exercises
        </button>
      </div>

      {activeTab === 'users' && (
        <div className="admin-tab-content">
          <h2>User Management</h2>
          <div className="admin-controls">
            <input
              className="form-input"
              type="text"
              placeholder="Search users..."
              value={userSearch}
              onChange={e => {
                setUserSearch(e.target.value);
                setUserPage(1);
              }}
            />
          </div>
          {userError && <div className="alert alert-error">{userError}</div>}
          {userLoading ? (
            <div className="loading-state">Loading users...</div>
          ) : (
            <div className="admin-table-wrapper card">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Age</th>
                    <th>Height</th>
                    <th>Weight</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td>{u.username}</td>
                      <td>
                        <select
                          className="form-input form-select-sm"
                          value={u.role}
                          onChange={e => handleRoleChange(u.id, e.target.value)}
                        >
                          <option value="user">User</option>
                          <option value="admin">Admin</option>
                        </select>
                      </td>
                      <td>{u.age || '—'}</td>
                      <td>{u.height ? `${u.height} cm` : '—'}</td>
                      <td>{u.weight ? `${u.weight} kg` : '—'}</td>
                      <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      <td>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDeleteUser(u.id)}
                          disabled={u.id === user?.id}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {users.length === 0 && <p className="empty-state">No users found.</p>}
            </div>
          )}
        </div>
      )}

      {activeTab === 'exercises' && (
        <div className="admin-tab-content">
          <h2>Exercise Management</h2>
          <div className="admin-controls">
            <input
              className="form-input"
              type="text"
              placeholder="Search exercises..."
              value={exSearch}
              onChange={e => {
                setExSearch(e.target.value);
              }}
            />
            <select
              className="form-input"
              value={exFilterGroup}
              onChange={e => setExFilterGroup(e.target.value)}
            >
              <option value="">All muscle groups</option>
              {exMuscleGroups.map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={() => {
              setEditingEx(null);
              setExForm({ name: '', primary_muscle_group: '', equipment: '', description: '' });
              setShowExForm(true);
              setExFormError('');
              setExFormSuccess('');
            }}>
              + Add Exercise
            </button>
          </div>
          {exError && <div className="alert alert-error">{exError}</div>}
          {exFormSuccess && <div className="alert alert-success">{exFormSuccess}</div>}
          {exFormError && <div className="alert alert-error">{exFormError}</div>}
          {exLoading ? (
            <div className="loading-state">Loading exercises...</div>
          ) : (
            <div className="admin-table-wrapper card">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Muscle Group</th>
                    <th>Equipment</th>
                    <th>Description</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {exercises.map(ex => (
                    <tr key={ex.id}>
                      <td>{ex.id}</td>
                      <td>{ex.name}</td>
                      <td>{ex.primary_muscle_group}</td>
                      <td>{ex.equipment || '—'}</td>
                      <td className="ex-desc-cell">{ex.description || '—'}</td>
                      <td>
                        <button className="btn btn-secondary btn-sm" onClick={() => loadExerciseForEdit(ex.id)}>
                          Edit
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleExDelete(ex.id)}>
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {exercises.length === 0 && <p className="empty-state">No exercises found.</p>}
            </div>
          )}

          {showExForm && (
            <div className="admin-form-overlay">
              <div className="admin-form-card card">
                <h2>{editingEx ? 'Edit Exercise' : 'Add Exercise'}</h2>
                <form onSubmit={handleExSubmit}>
                  <div className="form-group">
                    <label className="form-label" htmlFor="admin-ex-name">Name</label>
                    <input
                      id="admin-ex-name"
                      className="form-input"
                      type="text"
                      value={exForm.name}
                      onChange={e => setExForm({ ...exForm, name: e.target.value })}
                      placeholder="e.g. Bench Press"
                      required
                      maxLength={100}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="admin-ex-muscle">Primary Muscle Group</label>
                    <select
                      id="admin-ex-muscle"
                      className="form-input"
                      value={exForm.primary_muscle_group}
                      onChange={e => setExForm({ ...exForm, primary_muscle_group: e.target.value })}
                      required
                    >
                      <option value="">Select group</option>
                      {exMuscleGroups.map(g => (
                        <option key={g} value={g}>{g}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="admin-ex-equipment">Equipment (optional)</label>
                    <input
                      id="admin-ex-equipment"
                      className="form-input"
                      type="text"
                      value={exForm.equipment}
                      onChange={e => setExForm({ ...exForm, equipment: e.target.value })}
                      placeholder="e.g. Barbell"
                      maxLength={50}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="admin-ex-desc">Description (optional)</label>
                    <textarea
                      id="admin-ex-desc"
                      className="form-input"
                      rows={3}
                      value={exForm.description}
                      onChange={e => setExForm({ ...exForm, description: e.target.value })}
                      placeholder="Brief description..."
                    />
                  </div>
                  <div className="form-actions">
                    <button className="btn btn-primary" type="submit">
                      {editingEx ? 'Update' : 'Create'}
                    </button>
                    <button className="btn btn-secondary" type="button" onClick={() => {
                      setShowExForm(false);
                      setEditingEx(null);
                      setExFormError('');
                      setExFormSuccess('');
                    }}>
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
