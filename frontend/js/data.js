/**
 * EduMate — Core Data Store & Models
 * Synchronizes with real Django backend via EduApi when authenticated,
 * and uses isolated EduMockData for in-development features (sessions, reviews).
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'edumate_data_v1';

  // Fallback initial dataset (used offline or when signed out)
  const DEFAULT_DATA = {
    user: {
      id: 1,
      name: 'Madina Azimova',
      avatarInitials: 'MA',
      avatarClass: 'avatar-madina',
      email: 'madina@example.com',
      telegram: '@madina_azimova',
      age: 17,
      ageGroup: '16–17',
      city: 'Tashkent',
      country: 'Uzbekistan',
      bio: 'Targeting IELTS 7.5+ for fall undergraduate admissions. Looking for a daily or 3x/week speaking partner for Part 2 & 3 cue cards and topic discussions.',
      primaryTrack: 'IELTS Speaking',
      currentLevel: 'Band 6.0 (B2)',
      targetLevel: 'Band 7.5 (C1)',
      deadline: 'Dec 2026',
      hoursPerWeek: 6,
      studyStreak: 12,
      totalHours: 38,
      sessionsCompleted: 22,
      activePartnersCount: 2,
      goals: [
        {
          id: 1,
          title: 'IELTS Speaking 7.5 Band',
          track: 'IELTS Speaking',
          track_id: 1,
          currentLevel: 'Band 6.0',
          targetLevel: 'Band 7.5',
          deadline: 'Dec 2026',
          progress: 68,
          hoursDone: 21,
          hoursTotal: 30,
          sessionsCount: 14,
          isPrimary: true
        }
      ],
      weeklyActivity: (window.EduMockData && window.EduMockData.weeklyActivity) || [],
      availability: {
        'Mon-evening': true,
        'Tue-afternoon': true,
        'Tue-evening': true,
        'Wed-evening': true,
        'Thu-evening': true,
        'Fri-afternoon': true,
        'Fri-evening': true,
        'Sat-morning': true,
        'Sat-afternoon': true,
        'Sun-afternoon': true
      },
      privacy: {
        ageGroupOnly: true,
        contactHiddenUntilMatch: true,
        activityVisible: true
      }
    },

    tracks: [
      { id: 1, slug: 'ielts-speaking', name: 'IELTS Speaking', category: 'exam' },
      { id: 2, slug: 'ielts-writing', name: 'IELTS Writing', category: 'exam' },
      { id: 3, slug: 'sat-math', name: 'SAT Math', category: 'exam' },
      { id: 4, slug: 'python', name: 'Python', category: 'tech' }
    ],

    candidates: [],
    incomingRequests: [],
    outgoingRequests: [],
    activePairs: [],
    sessions: (window.EduMockData && window.EduMockData.sessions) || [],
    notifications: (window.EduMockData && window.EduMockData.notifications) || []
  };

  // Safe deep clone
  function clone(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  // Load state from localStorage or fallback
  function loadState() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Ensure mock data for in-development screens is populated
        if (window.EduMockData) {
          if (!parsed.sessions || parsed.sessions.length === 0) parsed.sessions = clone(window.EduMockData.sessions);
          if (!parsed.notifications || parsed.notifications.length === 0) parsed.notifications = clone(window.EduMockData.notifications);
          if (!parsed.user || !parsed.user.weeklyActivity) parsed.user.weeklyActivity = clone(window.EduMockData.weeklyActivity);
        }
        return parsed;
      }
    } catch (e) {
      console.warn('LocalStorage unavailable, running in-memory:', e);
    }
    return clone(DEFAULT_DATA);
  }

  // Save state
  function saveState(s) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
    }
  }

  // State holder
  let state = loadState();

  const LEVEL_MAP = {
    1: 'Beginner (1)',
    2: 'Elementary (2)',
    3: 'Intermediate (3)',
    4: 'Upper Intermediate (4)',
    5: 'Advanced (5)'
  };

  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  /**
   * Refreshes local state from real backend API endpoints
   */
  async function refreshFromBackend() {
    if (!window.EduApi || !window.EduApi.isAuthenticated()) {
      return state;
    }

    try {
      // 1. Tracks
      const tracks = await window.EduApi.getTracks();
      if (tracks && tracks.length > 0) {
        state.tracks = tracks;
      }

      // 2. User info & Profile
      const [aboutMe, profile] = await Promise.all([
        window.EduApi.getAboutMe().catch(() => null),
        window.EduApi.getProfile().catch(() => null)
      ]);

      if (aboutMe) {
        state.user.email = aboutMe.email || state.user.email;
        state.user.telegram = aboutMe.telegram_username ? `@${aboutMe.telegram_username}` : state.user.telegram;
        const fullName = `${aboutMe.first_name || ''} ${aboutMe.last_name || ''}`.trim();
        if (fullName) state.user.name = fullName;
      }

      if (profile) {
        state.user.name = profile.full_name || state.user.name;
        state.user.city = profile.city || state.user.city;
        state.user.bio = profile.bio || state.user.bio;
        state.user.ageGroup = profile.age_group === 'under_18' ? '16–17' : '18+';
        state.user.sessionsCompleted = profile.sessions_completed || 0;
      }

      // Generate avatar initials
      const parts = (state.user.name || 'User').split(' ');
      state.user.avatarInitials = parts.map((p) => p[0]).join('').toUpperCase().slice(0, 2);

      // 3. Goals
      const rawGoals = await window.EduApi.getGoals().catch(() => []);
      state.user.goals = (rawGoals || []).map((g) => ({
        id: g.id,
        title: `${g.track_name} Goal`,
        track: g.track_name,
        track_id: g.track,
        track_slug: g.track_slug,
        currentLevel: LEVEL_MAP[g.current_level] || `Level ${g.current_level}`,
        targetLevel: LEVEL_MAP[g.target_level] || `Level ${g.target_level}`,
        current_level_num: g.current_level,
        target_level_num: g.target_level,
        deadline: g.deadline || '2026',
        weekly_hours: g.weekly_hours || 5,
        progress: 50,
        hoursDone: Math.round((g.weekly_hours || 5) * 2.5),
        hoursTotal: (g.weekly_hours || 5) * 5,
        sessionsCount: 3,
        isPrimary: true
      }));

      if (state.user.goals.length > 0) {
        state.user.primaryTrack = state.user.goals[0].track;
        state.user.currentLevel = state.user.goals[0].currentLevel;
        state.user.targetLevel = state.user.goals[0].targetLevel;
        state.user.hoursPerWeek = state.user.goals[0].weekly_hours;
      }

      // 4. Availability
      const rawAvail = await window.EduApi.getAvailability().catch(() => []);
      const availMap = {};
      (rawAvail || []).forEach((item) => {
        const d = DAYS[item.weekday];
        if (d) availMap[`${d}-${item.slot}`] = true;
      });
      state.user.availability = availMap;

      // 5. Partners (Discovery)
      const activeTrackId = (state.user.goals[0] && state.user.goals[0].track_id) || (state.tracks[0] && state.tracks[0].id) || 1;
      const rawPartners = await window.EduApi.getPartners(activeTrackId).catch(() => []);
      const partnerResults = rawPartners && !Array.isArray(rawPartners) ? rawPartners.results || [] : rawPartners || [];
      const maxScore = rawPartners && !Array.isArray(rawPartners) ? rawPartners.max_score : 0;
      state.candidates = partnerResults.map((p) => {
        const pParts = (p.full_name || 'Student').split(' ');
        const initials = pParts.map((w) => w[0]).join('').toUpperCase().slice(0, 2);
        const availStr = (p.availability || [])
          .map((s) => `${DAYS[s.weekday]} (${s.slot})`)
          .slice(0, 3)
          .join(', ') || 'Flexible evenings';

        const compatPct = maxScore > 0 ? Math.round((p.score / maxScore) * 100) : 0;

        return {
          id: p.id || p.user_id,
          user_id: p.user_id || p.id,
          name: p.full_name,
          ageGroup: p.age_group === 'under_18' ? '16–17' : '18+',
          city: p.city || 'Tashkent',
          avatarClass: 'avatar-nilufar',
          avatarInitials: initials,
          track: p.track_name || p.track,
          track_id: p.track_id || activeTrackId,
          level: (p.goal && LEVEL_MAP[p.goal.current_level]) || 'Intermediate',
          target: (p.goal && LEVEL_MAP[p.goal.target_level]) || 'Advanced',
          compatibility: compatPct,
          goalText: `Targeting ${p.track_name || p.track}. Study ${p.goal ? p.goal.weekly_hours : 5} hrs/week.`,
          tags: [p.track_name || p.track, p.city || 'Tashkent', `${p.score} match score`],
          availability: availStr,
          status: 'none'
        };
      });

      // 6. Match Requests (Incoming & Outgoing)
      const [incoming, outgoing] = await Promise.all([
        window.EduApi.getIncomingRequests().catch(() => []),
        window.EduApi.getOutgoingRequests().catch(() => [])
      ]);

      state.incomingRequests = (incoming || []).map((req) => {
        const name = req.from_user_name || `User #${req.from_user}`;
        const parts = name.split(' ');
        const initials = parts.map((w) => w[0]).join('').toUpperCase().slice(0, 2);
        return {
          id: req.id,
          candidateId: req.from_user,
          name: name,
          avatarClass: 'avatar-nilufar',
          avatarInitials: initials,
          track: req.track_name || 'Study Track',
          compatibility: 92,
          ageGroup: '16–17',
          city: 'Tashkent',
          message: req.message || 'Would love to study and practice together!',
          timeAgo: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Recent',
          status: window.EduApi.normalizeRequestStatus(req.status)
        };
      });

      state.outgoingRequests = (outgoing || []).map((req) => {
        const name = req.to_user_name || `User #${req.to_user}`;
        const parts = name.split(' ');
        const initials = parts.map((w) => w[0]).join('').toUpperCase().slice(0, 2);
        return {
          id: req.id,
          candidateId: req.to_user,
          name: name,
          avatarClass: 'avatar-jasur',
          avatarInitials: initials,
          track: req.track_name || 'Study Track',
          compatibility: 95,
          ageGroup: '16–17',
          city: 'Tashkent',
          message: req.message || 'Study partner request sent.',
          timeAgo: req.created_at ? new Date(req.created_at).toLocaleDateString() : 'Recent',
          status: window.EduApi.normalizeRequestStatus(req.status)
        };
      });

      // 7. Active Mates (Pairs)
      const rawMates = await window.EduApi.getMates('active').catch(() => []);
      state.activePairs = (rawMates || []).map((m) => {
        const name = m.full_name || `Partner #${m.partner_id || m.id}`;
        const parts = name.split(' ');
        const initials = parts.map((w) => w[0]).join('').toUpperCase().slice(0, 2);
        return {
          id: m.id,
          partnerId: m.partner_id || m.id,
          name: name,
          avatarClass: 'avatar-aziza',
          avatarInitials: initials,
          track: m.track_name || m.track,
          target: 'Active Partner',
          ageGroup: '16–17',
          city: m.city || 'Tashkent',
          sessionsTogether: 2,
          hoursTogether: 3.0,
          streakDays: 2,
          nextSession: 'Upcoming',
          contact: m.contact || { telegram: '@partner_study', email: 'partner@example.uz' },
          focusNotes: `Matched for ${m.track_name || m.track}. Connected on EduMate.`
        };
      });
      state.user.activePartnersCount = state.activePairs.length;

      // Isolated mock data for in-development screens
      if (window.EduMockData) {
        state.sessions = clone(window.EduMockData.sessions);
        state.notifications = clone(window.EduMockData.notifications);
        state.user.weeklyActivity = clone(window.EduMockData.weeklyActivity);
      }

      saveState(state);
    } catch (e) {
      console.warn('[EduData Backend Refresh Error]:', e);
    }

    return state;
  }

  // Expose global EduData API
  window.EduData = {
    get() {
      return state;
    },
    update(updater) {
      if (typeof updater === 'function') {
        updater(state);
      }
      saveState(state);
      return state;
    },
    async refresh() {
      return await refreshFromBackend();
    },
    async refreshFromBackend() {
      return await refreshFromBackend();
    },
    reset() {
      state = clone(DEFAULT_DATA);
      saveState(state);
      return state;
    }
  };
})();
