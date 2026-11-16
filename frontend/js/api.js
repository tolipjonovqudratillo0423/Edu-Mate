/**
 * EduMate — API Client Layer
 * Connects frontend UI to Django REST Framework backend.
 */

(function () {
  'use strict';

  const API_BASE_URL = window.EDUMATE_API_BASE_URL || 'http://127.0.0.1:8000';
  const ACCESS_KEY = 'edumate_access_token';
  const REFRESH_KEY = 'edumate_refresh_token';

  let isRefreshing = false;
  let refreshQueue = [];

  function getAccessToken() {
    return localStorage.getItem(ACCESS_KEY);
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }

  function setTokens(access, refresh) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  }

  function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  function isAuthenticated() {
    return !!getAccessToken();
  }

  async function request(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers || {})
    };

    const token = getAccessToken();
    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
      response = await fetch(url, {
        ...options,
        headers
      });
    } catch (networkError) {
      console.error('[API Network Error]', networkError);
      throw new Error('Network error. Please check if the EduMate backend server is running.');
    }

    // Handle token refresh on 401
    if (response.status === 401 && getRefreshToken() && !options._isRetry) {
      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const newTokens = await refreshAuthToken();
          isRefreshing = false;
          refreshQueue.forEach((cb) => cb(newTokens.access));
          refreshQueue = [];
        } catch (refreshErr) {
          isRefreshing = false;
          refreshQueue = [];
          clearTokens();
          if (window.EduData && window.EduData.reset) window.EduData.reset();
          window.location.hash = '#/login';
          if (window.showToast) window.showToast('Session expired. Please sign in again.', 'danger', 'alert-circle');
          throw new Error('Session expired. Please sign in again.');
        }
      }

      return new Promise((resolve, reject) => {
        refreshQueue.push((newAccess) => {
          options._isRetry = true;
          options.headers = {
            ...headers,
            Authorization: `Bearer ${newAccess}`
          };
          request(endpoint, options).then(resolve).catch(reject);
        });
      });
    }

    if (response.status === 204) {
      return { status: true, data: null };
    }

    let data;
    try {
      data = await response.json();
    } catch (e) {
      data = null;
    }

    if (!response.ok) {
      let errMsg = 'Request failed';
      if (data && data.message) {
        errMsg = data.message;
      } else if (data && typeof data === 'object') {
        const firstKey = Object.keys(data)[0];
        if (firstKey) {
          const val = data[firstKey];
          errMsg = Array.isArray(val) ? val[0] : String(val);
        }
      }
      const err = new Error(errMsg);
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  }

  async function refreshAuthToken() {
    const refresh = getRefreshToken();
    if (!refresh) throw new Error('No refresh token');

    const res = await fetch(`${API_BASE_URL}/auth/refresh-token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh })
    });

    if (!res.ok) throw new Error('Refresh failed');
    const json = await res.json();
    const tokens = json.data && json.data.tokens ? json.data.tokens : json.data || {};
    setTokens(tokens.access, tokens.refresh || refresh);
    return tokens;
  }

  // Public API methods
  window.EduApi = {
    getBaseUrl() {
      return API_BASE_URL;
    },
    getAccessToken,
    setTokens,
    clearTokens,
    isAuthenticated,
    request,

    // Authentication
    async login(email, password) {
      const res = await request('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      if (res.data && res.data.tokens) {
        setTokens(res.data.tokens.access, res.data.tokens.refresh);
      }
      return res.data;
    },

    async register(email, firstName, lastName, password) {
      return await request('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({
          email,
          first_name: firstName,
          last_name: lastName,
          password: password,
          password2: password
        })
      });
    },

    async logout() {
      try {
        const refresh = getRefreshToken();
        if (refresh) {
          await request('/auth/logout/', {
            method: 'POST',
            body: JSON.stringify({ refresh })
          });
        }
      } catch (e) {
        console.warn('Backend logout warning:', e);
      } finally {
        clearTokens();
      }
    },

    // User & Profile
    async getAboutMe() {
      const res = await request('/users/about-me/');
      return res.data;
    },

    async getProfile() {
      try {
        const res = await request('/users/profile/');
        return res.data;
      } catch (err) {
        // If profile doesn't exist yet, return null
        if (err.status === 400 || err.status === 404) return null;
        throw err;
      }
    },

    async createProfile(profileData) {
      const res = await request('/users/profile/', {
        method: 'POST',
        body: JSON.stringify(profileData)
      });
      return res.data;
    },

    async updateProfile(profileData) {
      const res = await request('/users/profile/', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });
      return res.data;
    },

    // Catalog Tracks
    async getTracks() {
      try {
        const res = await request('/tracks/');
        return res.data || [];
      } catch (e) {
        return [
          { id: 1, slug: 'ielts-speaking', name: 'IELTS Speaking', category: 'exam' },
          { id: 2, slug: 'ielts-writing', name: 'IELTS Writing', category: 'exam' },
          { id: 3, slug: 'sat-math', name: 'SAT Math', category: 'exam' },
          { id: 4, slug: 'python', name: 'Python', category: 'tech' }
        ];
      }
    },

    // Goals
    async getGoals() {
      const res = await request('/goals/');
      return res.data || [];
    },

    async createGoal(goalData) {
      const res = await request('/goals/', {
        method: 'POST',
        body: JSON.stringify(goalData)
      });
      return res.data;
    },

    async saveGoalFromForm({ trackName, current, target, deadline, weeklyHours }) {
      const tracks = await this.getTracks();
      const track = tracks.find((item) => item.name === trackName || item.slug === trackName.toLowerCase().replace(/[^a-z0-9]+/g, '-'));
      if (!track) throw new Error(`Study track not found: ${trackName}`);
      const currentScore = Number((current.match(/[\d.]+/) || [])[0]) || 1;
      const targetScore = Number((target.match(/[\d.]+/) || [])[0]) || 5;
      const sat = /sat/i.test(trackName);
      const level = (score) => sat ? (score < 1000 ? 1 : score < 1200 ? 2 : score < 1350 ? 3 : score < 1500 ? 4 : 5) : (score <= 4.5 ? 1 : score <= 5.5 ? 2 : score <= 6.5 ? 3 : score <= 7.5 ? 4 : 5);
      const month = deadline.match(/^([A-Za-z]+)\s+(\d{4})$/);
      let isoDeadline = deadline;
      if (month) {
        const date = new Date(`${month[1]} 1, ${month[2]}`);
        if (!Number.isNaN(date.getTime())) isoDeadline = new Date(date.getFullYear(), date.getMonth() + 1, 0).toISOString().slice(0, 10);
      }
      return this.createGoal({ track: track.id, current_level: level(currentScore), target_level: level(targetScore), current_score: currentScore, target_score: targetScore, deadline: isoDeadline, weekly_hours: weeklyHours });
    },

    async updateGoal(goalId, goalData) {
      const res = await request(`/goals/${goalId}/`, {
        method: 'PATCH',
        body: JSON.stringify(goalData)
      });
      return res.data;
    },

    async deleteGoal(goalId) {
      return await request(`/goals/${goalId}/`, {
        method: 'DELETE'
      });
    },

    // Availability
    async getAvailability() {
      const res = await request('/availability/');
      return res.data || [];
    },

    async createSlot(weekday, slot) {
      const res = await request('/availability/', {
        method: 'POST',
        body: JSON.stringify({ weekday, slot })
      });
      return res.data;
    },

    async deleteSlot(slotId) {
      return await request(`/availability/${slotId}/`, {
        method: 'DELETE'
      });
    },

    async saveAvailabilitySchedule(selectedMap) {
      // Diff current slots against selectedMap
      const current = await this.getAvailability();
      const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

      // Delete unselected slots
      for (const item of current) {
        const dayStr = DAYS[item.weekday];
        const key = `${dayStr}-${item.slot}`;
        if (!selectedMap[key]) {
          await this.deleteSlot(item.id);
        }
      }

      // Add newly selected slots
      for (let w = 0; w < 7; w++) {
        const dayStr = DAYS[w];
        for (const slotName of ['morning', 'afternoon', 'evening']) {
          const key = `${dayStr}-${slotName}`;
          if (selectedMap[key]) {
            const alreadyExists = current.some((c) => c.weekday === w && c.slot === slotName);
            if (!alreadyExists) {
              await this.createSlot(w, slotName);
            }
          }
        }
      }

      return await this.getAvailability();
    },

    // Partners
    async getPartners(trackId) {
      const res = await request(`/partners/?track=${trackId}`);
      return res.data || { max_score: 0, results: [] };
    },

    // Match Requests
    async getIncomingRequests() {
      const res = await request('/match-requests/?box=received');
      return res.data || [];
    },

    async getOutgoingRequests() {
      const res = await request('/match-requests/?box=sent');
      return res.data || [];
    },

    async sendMatchRequest(toUserId, trackId, message) {
      const res = await request('/match-requests/', {
        method: 'POST',
        body: JSON.stringify({
          to_user: toUserId,
          track: trackId,
          message: message || ''
        })
      });
      return res.data;
    },

    async updateMatchRequestStatus(requestId, status) {
      if (status === 'cancelled') status = 'canceled';
      const res = await request(`/match-requests/${requestId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ status })
      });
      return res.data;
    },

    normalizeRequestStatus(status) { return status === 'canceled' ? 'cancelled' : status; },

    // Mates (Active pairs)
    async getMates(statusFilter = 'active') {
      const res = await request(`/mates/?status=${statusFilter}`);
      return res.data || [];
    },

    async endMate(matchId) {
      const res = await request(`/mates/${matchId}/`, {
        method: 'DELETE'
      });
      return res.data;
    }
  };
})();
