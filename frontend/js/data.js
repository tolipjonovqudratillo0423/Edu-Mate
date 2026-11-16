/**
 * EduMate — data store.
 * Real backend data only. No demo, mock or fallback values: anything the backend
 * does not provide stays null and the UI must show an "In development" placeholder.
 * State lives in memory only (tokens are handled by EduApi).
 */
(function () {
  'use strict';

  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const AVATAR_CLASSES = ['avatar-madina', 'avatar-nilufar', 'avatar-jasur', 'avatar-aziza']; // styling only
  const LEVEL_MAP = {
    1: 'Beginner (1)',
    2: 'Elementary (2)',
    3: 'Intermediate (3)',
    4: 'Upper Intermediate (4)',
    5: 'Advanced (5)'
  };

  function emptyState() {
    return {
      user: {
        id: null,
        name: '',
        avatarInitials: '',
        avatarClass: AVATAR_CLASSES[0],
        email: '',
        telegram: '',
        ageGroup: null,
        city: '',
        bio: '',
        primaryTrack: null,
        currentLevel: null,
        targetLevel: null,
        hoursPerWeek: null,
        studyStreak: null,
        totalHours: null,
        sessionsCompleted: null,
        activePartnersCount: 0,
        goals: [],
        weeklyActivity: [],
        availability: {},
        privacy: { isHidden: false }
      },
      tracks: [],
      candidates: [],
      partnersTrackId: null,
      maxScore: null,
      incomingRequests: [],
      outgoingRequests: [],
      activePairs: [],
      sessions: [],
      notifications: []
    };
  }

  let state = emptyState();

  // ---- helpers ----
  const initialsOf = (name) =>
    (name || '').split(' ').filter(Boolean).map((w) => w[0]).join('').toUpperCase().slice(0, 2);
  const avatarFor = (id) => AVATAR_CLASSES[Math.abs(Number(id) || 0) % AVATAR_CLASSES.length];
  const ageGroupLabel = (ag) => (ag === 'under_18' ? 'Under 18' : ag === 'adult' ? '18+' : null);
  const levelLabel = (n) => (n == null ? null : LEVEL_MAP[n] || 'Level ' + n);
  const dateLabel = (iso) => {
    if (!iso) return null;
    const d = new Date(iso);
    return isNaN(d) ? null : d.toLocaleDateString();
  };
  const asList = (x) => (Array.isArray(x) ? x : x && Array.isArray(x.results) ? x.results : []);

  function mapRequest(req, direction) {
    const incoming = direction === 'in';
    const otherId = incoming ? req.from_user : req.to_user;
    const name = (incoming ? req.from_user_name : req.to_user_name) || 'User #' + otherId;
    return {
      id: req.id,
      candidateId: otherId,
      name: name,
      avatarClass: avatarFor(otherId),
      avatarInitials: initialsOf(name),
      track: req.track_name || null,
      track_id: req.track || null,
      compatibility: null,
      ageGroup: null,
      city: null,
      message: req.message || '',
      createdAt: req.created_at || null,
      timeAgo: dateLabel(req.created_at),
      status: window.EduApi.normalizeRequestStatus(req.status)
    };
  }

  // ---- backend sync ----
  async function refreshFromBackend() {
    if (!window.EduApi || !window.EduApi.isAuthenticated()) {
      state = emptyState();
      return state;
    }

    const failed = [];
    const run = async (name, fn) => {
      try {
        await fn();
      } catch (e) {
        failed.push(name);
        console.warn('[EduData] ' + name + ' failed:', e);
      }
    };

    // Independent sections load in parallel; one failure never blocks the others.
    await Promise.all([
      run('tracks', async () => {
        state.tracks = asList(await window.EduApi.getTracks());
      }),

      run('profile', async () => {
        const [aboutMe, profile] = await Promise.all([
          window.EduApi.getAboutMe().catch(() => null),
          window.EduApi.getProfile().catch((err) => { if (err.status === 404) return null; throw err; })
        ]);
        if (!aboutMe && !profile) throw new Error('no user data');
        const u = state.user;
        if (aboutMe) {
          u.id = aboutMe.id != null ? aboutMe.id : u.id;
          u.email = aboutMe.email || '';
          u.telegram = aboutMe.telegram_username ? '@' + aboutMe.telegram_username : '';
          u.name = ((aboutMe.first_name || '') + ' ' + (aboutMe.last_name || '')).trim();
        }
        if (profile) {
          u.name = profile.full_name || u.name;
          u.city = profile.city || '';
          u.bio = profile.bio || '';
          u.ageGroup = ageGroupLabel(profile.age_group);
          u.sessionsCompleted = null;
          u.privacy.isHidden = !!profile.is_hidden;
        }
        u.avatarInitials = initialsOf(u.name);
        u.avatarClass = avatarFor(u.id);
      }),

      run('goals', async () => {
        const raw = asList(await window.EduApi.getGoals());
        const u = state.user;
        u.goals = raw.map((g, i) => ({
          id: g.id,
          title: g.track_name,
          track: g.track_name,
          track_id: g.track,
          track_slug: g.track_slug,
          currentLevel: levelLabel(g.current_level),
          targetLevel: levelLabel(g.target_level),
          current_level_num: g.current_level,
          target_level_num: g.target_level,
          currentScore: g.current_score != null ? g.current_score : null,
          targetScore: g.target_score != null ? g.target_score : null,
          deadline: g.deadline || null,
          weekly_hours: g.weekly_hours != null ? g.weekly_hours : null,
          // no backend source yet -> null -> "In development" in the UI
          progress: null,
          hoursDone: null,
          hoursTotal: null,
          sessionsCount: null,
          isPrimary: i === 0
        }));
        const first = u.goals[0];
        u.primaryTrack = first ? first.track : null;
        u.currentLevel = first ? first.currentLevel : null;
        u.targetLevel = first ? first.targetLevel : null;
        u.hoursPerWeek = first ? first.weekly_hours : null;
      }),

      run('availability', async () => {
        const map = {};
        asList(await window.EduApi.getAvailability()).forEach((item) => {
          const d = DAYS[item.weekday];
          if (d) map[d + '-' + item.slot] = true;
        });
        state.user.availability = map;
      }),

      run('requests', async () => {
        const [incoming, outgoing] = await Promise.all([
          window.EduApi.getIncomingRequests(),
          window.EduApi.getOutgoingRequests()
        ]);
        state.incomingRequests = asList(incoming).map((r) => mapRequest(r, 'in'));
        state.outgoingRequests = asList(outgoing).map((r) => mapRequest(r, 'out'));
      }),

      run('mates', async () => {
        const raw = asList(await window.EduApi.getMates('active'));
        state.activePairs = raw.map((m) => {
          const name = m.full_name || null;
          const partnerId = m.partner_user_id != null ? m.partner_user_id : null;
          return {
            id: m.id,
            partnerId: partnerId,
            name: name,
            avatarClass: avatarFor(partnerId != null ? partnerId : m.id),
            avatarInitials: initialsOf(name),
            track: m.track_name || null,
            city: m.city || null,
            ageGroup: null,
            contact: m.contact && (m.contact.telegram || m.contact.email) ? m.contact : null,
            createdDate: m.created_date || null,
            // no backend source yet -> null -> "In development"
            sessionsTogether: null,
            hoursTogether: null,
            streakDays: null,
            nextSession: null,
            focusNotes: ''
          };
        });
        state.user.activePartnersCount = state.activePairs.length;
      })
    ]);

    // Partners depend on the user's goal track (the backend requires ?track=<id>).
    await run('partners', async () => {
      const goal = state.user.goals[0];
      state.partnersTrackId = goal ? goal.track_id : null;
      if (!goal) {
        state.candidates = [];
        state.maxScore = null;
        return;
      }
      const raw = await window.EduApi.getPartners(goal.track_id);
      state.maxScore = null;
      state.candidates = asList(raw).map((p) => {
        const g = p.goal || p;
        const userId = p.user_id != null ? p.user_id : (p.id != null ? p.id : null);
        const slots = (p.availability || []).map((s) => DAYS[s.weekday] + ' ' + s.slot);
        const cur = levelLabel(g.current_level);
        const tgt = levelLabel(g.target_level);
        const trackName = p.track_name || goal.track;
        return {
          id: userId,
          user_id: userId,
          name: p.full_name || null,
          ageGroup: ageGroupLabel(p.age_group),
          city: p.city || null,
          avatarClass: avatarFor(userId),
          avatarInitials: initialsOf(p.full_name),
          track: trackName,
          track_id: goal.track_id,
          level: cur,
          target: tgt,
          weeklyHours: g.weekly_hours != null ? g.weekly_hours : null,
          deadline: g.deadline || null,
          score: typeof p.score === 'number' ? p.score : null,
          compatibility: null,
          goalText: cur && tgt ? trackName + ': ' + cur + ' \u2192 ' + tgt : null,
          tags: [trackName, p.city].filter(Boolean),
          availability: slots.length ? slots.slice(0, 3).join(', ') : null,
          availabilitySlots: p.availability || [],
          status: 'none'
        };
      });
    });

    if (failed.length) {
      document.dispatchEvent(new CustomEvent('edudata:errors', { detail: { sections: failed } }));
    }
    return state;
  }

  window.EduData = {
    get() {
      return state;
    },
    update(updater) {
      if (typeof updater === 'function') updater(state);
      return state;
    },
    refresh: refreshFromBackend,
    refreshFromBackend: refreshFromBackend, // app.js calls this name
    reset() {
      state = emptyState();
      return state;
    }
  };
})();
