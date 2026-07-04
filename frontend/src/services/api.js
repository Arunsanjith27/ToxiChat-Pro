const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}, token = null) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map(d => d.msg || d).join(', ')
        : 'Request failed';
    throw new ApiError(message, res.status);
  }
  return data;
}

export const authApi = {
  register: (body) => request('/api/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/login', { method: 'POST', body: JSON.stringify(body) }),
  forgotPassword: (body) => request('/api/auth/forgot-password', { method: 'POST', body: JSON.stringify(body) }),
  resetPassword: (body) => request('/api/auth/reset-password', { method: 'POST', body: JSON.stringify(body) }),
  me: (token) => request('/api/me', {}, token),
};

export const profileApi = {
  update: (body, token) => request('/api/profile', { method: 'PUT', body: JSON.stringify(body) }, token),
  uploadAvatar: (file, token) => {
    const form = new FormData();
    form.append('file', file);
    return request('/api/profile/avatar', { method: 'POST', body: form }, token);
  },
};

export const chatApi = {
  users: (token) => request('/api/users', {}, token),
  messages: (user1, user2, token) => request(`/api/messages/${user1}/${user2}`, {}, token),
  search: (q, token) => request(`/api/search?q=${encodeURIComponent(q)}&limit=20`, {}, token),
  predict: (text, token) => request('/api/predict', { method: 'POST', body: JSON.stringify({ text }) }, token),
  predictEscalation: (text, partner, token) =>
    request('/api/predict/escalation', { method: 'POST', body: JSON.stringify({ text, partner }) }, token),
  rewrite: (text, token) => request('/api/rewrite', { method: 'POST', body: JSON.stringify({ text }) }, token),
  conversationHealth: (partner, token) => request(`/api/conversation/health/${partner}`, {}, token),
};

export const dashboardApi = {
  stats: (token) => request('/api/dashboard/stats', {}, token),
};

export const adminApi = {
  flagged: (token) => request('/api/admin/flagged', {}, token),
  toxicUsers: (token) => request('/api/admin/toxic-users', {}, token),
  users: (token) => request('/api/admin/users', {}, token),
  action: (body, token) => request('/api/admin/action', { method: 'POST', body: JSON.stringify(body) }, token),
  highRiskConversations: (token) => request('/api/admin/analytics/high-risk', {}, token),
  conversationAnalytics: (user1, user2, token) => request(`/api/admin/conversation/${user1}/${user2}`, {}, token),
  analyzeImage: (file, token) => {
    const form = new FormData();
    form.append('file', file);
    return request('/api/image/analyze', { method: 'POST', body: form }, token);
  },
};

export function avatarUrl(path) {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${API_URL}${path}`;
}

export { API_URL, ApiError };
