import api from './client';

// Auth
export const authQueries = {
  login: (username, password) => api.post('/api/auth/login', { username, password }),
  register: (data) => api.post('/api/auth/register', data),
  logout: () => api.post('/api/auth/logout'),
  me: () => api.get('/api/auth/me'),
};

// User profile
export const userQueries = {
  getMe: () => api.get('/api/users/me'),
  updateMe: (data) => api.put('/api/users/me', data),
  changePassword: (data) => api.post('/api/users/change-password', data),
};

// Workout
export const workoutQueries = {
  getPlan: () => api.get('/api/workout/plan'),
  getDay: (weekday) => api.get(`/api/workout/day/${encodeURIComponent(weekday)}`),
  addExercise: (weekday, exerciseId) =>
    api.post(`/api/workout/day/${encodeURIComponent(weekday)}/exercises`, { exercise_id: exerciseId }),
  updateExercise: (weekday, assignmentId, data) =>
    api.put(`/api/workout/day/${encodeURIComponent(weekday)}/exercises/${assignmentId}`, data),
  removeExercise: (weekday, assignmentId) =>
    api.delete(`/api/workout/day/${encodeURIComponent(weekday)}/exercises/${assignmentId}`),
  reorder: (weekday, exercises) =>
    api.put(`/api/workout/day/${encodeURIComponent(weekday)}/order`, { exercises }),
};

// Dashboard
export const dashboardQueries = {
  getDashboard: () => api.get('/api/dashboard'),
};

// Calendar
export const calendarQueries = {
  getCalendar: () => api.get('/api/calendar/'),
};

// Exercises
export const exerciseQueries = {
  list: (params = {}) => api.get('/api/exercises', { params }),
  get: (id) => api.get(`/api/exercises/${id}`),
  muscleGroups: () => api.get('/api/exercises/muscle-groups'),
  create: (data) => api.post('/api/exercises', data),
  update: (id, data) => api.put(`/api/exercises/${id}`, data),
  delete: (id) => api.delete(`/api/exercises/${id}`),
};

// Admin
export const adminQueries = {
  listUsers: (params = {}) => api.get('/api/admin/users', { params }),
  getUser: (id) => api.get(`/api/admin/users/${id}`),
  changeRole: (id, role) => api.put(`/api/admin/users/${id}/role`, null, { params: { role } }),
  deleteUser: (id) => api.delete(`/api/admin/users/${id}`),
  listExercises: (params = {}) => api.get('/api/admin/exercises', { params }),
  createExercise: (data) => api.post('/api/admin/exercises', data),
  updateExercise: (id, data) => api.put(`/api/admin/exercises/${id}`, data),
  deleteExercise: (id) => api.delete(`/api/admin/exercises/${id}`),
};
