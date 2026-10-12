const API_BASE = '/api/v1';

export async function request(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || err.message || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  // Health & Root
  getHealth: () => request('/health'),

  // Dashboard & Analytics
  getDashboardStats: () => request('/analytics/dashboard'),
  getTokenTelemetry: () => request('/analytics/tokens'),
  getExportExcelUrl: () => `${API_BASE}/analytics/export/excel`,
  getExportCsvUrl: () => `${API_BASE}/analytics/export/csv`,

  // Jobs
  getJobs: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/jobs/${q ? '?' + q : ''}`);
  },
  getJob: (id) => request(`/jobs/${id}`),
  createJob: (job) => request('/jobs/', { method: 'POST', body: JSON.stringify(job) }),
  scrapeJobs: (payload) => request('/jobs/scrape', { method: 'POST', body: JSON.stringify(payload) }),
  ingestJob: (url, platform) => request('/jobs/ingest', { method: 'POST', body: JSON.stringify({ url, platform }) }),
  matchJobs: (params = {}) => request('/jobs/match', { method: 'POST', body: JSON.stringify(params) }),
  getJobFitScore: (jobId) => request(`/jobs/${jobId}/fit-score`),

  // Profiles & Memory Bank
  getActiveProfile: () => request('/profiles/active'),
  getProfile: (id) => request(`/profiles/${id}`),
  createProfile: (profile) => request('/profiles/', { method: 'POST', body: JSON.stringify(profile) }),
  updateProfile: (id, profile) => request(`/profiles/${id}`, { method: 'PUT', body: JSON.stringify(profile) }),
  getStories: (candidateId) => request(`/profiles/${candidateId}/stories`),
  createStory: (candidateId, story) => request(`/profiles/${candidateId}/stories`, { method: 'POST', body: JSON.stringify(story) }),
  getQABank: () => request('/profiles/qa-bank/list'),
  addQAEntry: (entry) => request('/profiles/qa-bank', { method: 'POST', body: JSON.stringify(entry) }),

  // Materials & Tailoring
  getMaterialsForJob: (jobId) => request(`/materials/job/${jobId}`),
  tailorResume: (payload) => request('/materials/tailor/resume', { method: 'POST', body: JSON.stringify(payload) }),
  tailorCoverLetter: (payload) => request('/materials/tailor/cover-letter', { method: 'POST', body: JSON.stringify(payload) }),
  compileMaterial: (docId, format) => request(`/materials/${docId}/compile`, { method: 'POST', body: JSON.stringify({ format }) }),
  validateGrounding: (docId) => request(`/materials/${docId}/validate-grounding`, { method: 'POST' }),

  // Review Queue
  getReviewQueue: () => request('/review/queue'),
  getReviewPreview: (appId) => request(`/review/${appId}/preview`),
  reviewAction: (appId, action, notes) =>
    request(`/review/${appId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action, custom_notes: notes }),
    }),
  bulkReviewAction: (application_ids, action) =>
    request('/review/bulk-action', {
      method: 'POST',
      body: JSON.stringify({ application_ids, action }),
    }),

  // Applications
  getApplications: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/applications/${q ? '?' + q : ''}`);
  },
  submitApplication: (appId) => request(`/applications/${appId}/submit`, { method: 'POST' }),
  batchSubmitApplications: () => request('/applications/batch-submit', { method: 'POST' }),

  // Live Execution Runner & Bot
  getExecutionStatus: () => request('/execution/status'),
  startExecution: (config) => request('/execution/start', { method: 'POST', body: JSON.stringify(config) }),
  stopExecution: () => request('/execution/stop', { method: 'POST' }),
  pauseExecution: () => request('/execution/pause', { method: 'POST' }),
  resumeExecution: () => request('/execution/resume', { method: 'POST' }),
  checkSessionHealth: (platform = 'linkedin') => request(`/execution/session/health?platform=${platform}`),
  solveQuestion: (payload) => request('/execution/solve-question', { method: 'POST', body: JSON.stringify(payload) }),
  getExecutionLogs: () => request('/execution/logs'),

  // Providers
  getProviders: () => request('/providers/'),
  getSupportedProviders: () => request('/providers/supported'),
  testProvider: (provider_name, prompt) =>
    request('/providers/test', {
      method: 'POST',
      body: JSON.stringify({ provider_name, prompt }),
    }),

  // Tasks & Queues
  getQueues: () => request('/tasks/queues'),
  getDLQ: () => request('/tasks/dlq'),
  cleanupTasks: () => request('/tasks/cleanup', { method: 'POST' }),
};
