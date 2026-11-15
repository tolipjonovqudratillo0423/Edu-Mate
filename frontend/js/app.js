/**
 * EduMate — Accessible, responsive single-page application prototype.
 *
 * Core architecture:
 * 1. Icon Library: SVG icons rendered offline without external fonts.
 * 2. Hash Router: Manages client-side routing, document title, and shell state.
 * 3. Screen Renderers: Generates modular HTML templates with rich micro-interactions.
 * 4. Dialog & Toast System: Accessible modals (Connect, Report/Block, Schedule, Review) and feedback toasts.
 * 5. State Management: Reads and updates the dataset in EduData with offline persistence.
 */

(function () {
  'use strict';

  /* ==========================================================================
     1. SVG ICON REGISTRY
     ========================================================================== */

  const ICONS = {
    'layout-dashboard': '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'heart-handshake': '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 5 9.04 7.96a2.17 2.17 0 0 0 0 3.08c.82.82 2.13.85 3 .07l2.07-1.9a2.82 2.82 0 0 1 3.18 0l1.9 1.9c.78.78 2.05.78 2.83 0 .8-.8.8-2.08 0-2.88L19 5"/>',
    'calendar-days': '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
    'calendar': '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
    'user-round': '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
    'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    'shield': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    'chevron-right': '<path d="m9 18 6-6-6-6"/>',
    'chevron-down': '<path d="m6 9 6 6 6-6"/>',
    'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    'menu': '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
    'search': '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    'moon': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
    'bell': '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    'log-out': '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'check': '<path d="M20 6 9 17l-5-5"/>',
    'check-circle': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    'star': '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    'flag': '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/>',
    'ban': '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    'plus': '<path d="M5 12h14"/><path d="M12 5v14"/>',
    'send': '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    'sparkles': '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
    'video': '<path d="m22 7-6 4v2l6 4V7z"/><rect width="14" height="12" x="2" y="6" rx="2"/>',
    'arrow-right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    'filter': '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    'lock': '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    'mail': '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    'eye': '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    'eye-off': '<path d="9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/>',
    'flame': '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    'award': '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
    'external-link': '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/>',
    'info': '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    'message-square': '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    'more-vertical': '<circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/>'
  };

  /**
   * Generates inline SVG markup for an icon
   */
  function icon(name, extraClass = '') {
    const content = ICONS[name] || ICONS['info'];
    return `<svg class="icon ${extraClass}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${content}</svg>`;
  }

  /**
   * Scans container for [data-icon] elements and populates them if empty
   */
  function hydrateIcons(root = document) {
    const elements = root.querySelectorAll('[data-icon]');
    elements.forEach((el) => {
      const name = el.getAttribute('data-icon');
      if (ICONS[name] && !el.querySelector('svg.icon')) {
        const svgString = icon(name);
        el.insertAdjacentHTML('afterbegin', svgString);
      }
    });
  }

  /* ==========================================================================
     2. TOAST NOTIFICATIONS & ACCESSIBILITY
     ========================================================================== */

  const toastRegion = document.getElementById('toast-region');

  function showToast(message, type = 'success', iconName = 'check-circle') {
    if (!toastRegion) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <span>${icon(iconName)}</span>
      <p>${escapeHtml(message)}</p>
      <button aria-label="Dismiss toast">${icon('x')}</button>
    `;

    const closeBtn = toast.querySelector('button');
    const dismiss = () => {
      toast.classList.add('leaving');
      setTimeout(() => toast.remove(), 200);
    };

    closeBtn.addEventListener('click', dismiss);
    toastRegion.appendChild(toast);

    setTimeout(dismiss, 3800);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /* ==========================================================================
     3. MODAL DIALOG SYSTEM
     ========================================================================== */

  const modalRoot = document.getElementById('modal-root');
  let activeModal = null;
  let lastFocusedElement = null;

  function openModal(htmlContent, onOpen) {
    closeModal();
    lastFocusedElement = document.activeElement;

    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.innerHTML = htmlContent;

    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        closeModal();
      }
    });

    const closeButtons = backdrop.querySelectorAll('[data-close-modal]');
    closeButtons.forEach((btn) => btn.addEventListener('click', closeModal));

    modalRoot.appendChild(backdrop);
    activeModal = backdrop;
    document.body.style.overflow = 'hidden';

    hydrateIcons(backdrop);

    const firstFocusable = backdrop.querySelector('button, input, select, textarea, [tabindex="0"]');
    if (firstFocusable) {
      firstFocusable.focus();
    }

    if (typeof onOpen === 'function') {
      onOpen(backdrop);
    }
  }

  function closeModal() {
    if (activeModal) {
      activeModal.remove();
      activeModal = null;
      document.body.style.overflow = '';
      if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
        lastFocusedElement.focus();
      }
    }
  }

  /* Specific modal dialogs */

  function openConnectModal(candidateId) {
    const data = EduData.get();
    const candidate = data.candidates.find((c) => c.id === candidateId);
    if (!candidate) return;

    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-connect-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-connect-title">Connect with ${escapeHtml(candidate.name)}</h2>
            <p>Send a study partner request to start learning together</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="modal-person">
            <span class="avatar ${escapeHtml(candidate.avatarClass)}">${escapeHtml(candidate.avatarInitials)}</span>
            <div>
              <strong>${escapeHtml(candidate.name)} · ${escapeHtml(candidate.ageGroup)}</strong>
              <small>${escapeHtml(candidate.track)} · ${escapeHtml(candidate.target)}</small>
            </div>
            <span class="badge badge-success" style="margin-left: auto;">${candidate.compatibility}% match</span>
          </div>

          <div class="field">
            <label for="connect-message">Personal note (optional)</label>
            <textarea id="connect-message" rows="3" placeholder="Hi ${escapeHtml(candidate.name.split(' ')[0])}! I saw your ${escapeHtml(candidate.track)} goal and would love to practice together...">Hi ${escapeHtml(candidate.name.split(' ')[0])}! I saw your ${escapeHtml(candidate.track)} goal and our schedules align well. Let's do structured study sessions!</textarea>
            <small>Be polite and specify which topics or days you want to study.</small>
          </div>

          <div class="modal-notice">
            ${icon('shield-check')}
            <div>
              <strong>Safety first</strong>
              <p>Your Telegram and email remain hidden until ${escapeHtml(candidate.name)} accepts your request.</p>
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Cancel</button>
          <button class="btn btn-primary" id="btn-submit-connect">${icon('send')} Send request</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      modalEl.querySelector('#btn-submit-connect').addEventListener('click', async () => {
        const note = modalEl.querySelector('#connect-message').value.trim();
        const cand = (EduData.get().candidates || []).find((c) => c.id === candidateId);
        if (!cand) return;

        try {
          if (window.EduApi && window.EduApi.isAuthenticated()) {
            await window.EduApi.sendMatchRequest(cand.user_id || cand.id, cand.track_id || 1, note);
            await EduData.refresh();
          } else {
            EduData.update((state) => {
              cand.status = 'pending';
              state.outgoingRequests.unshift({
                id: 'req-out-' + Date.now(),
                candidateId: cand.id,
                name: cand.name,
                avatarClass: cand.avatarClass,
                avatarInitials: cand.avatarInitials,
                track: cand.track,
                compatibility: cand.compatibility,
                ageGroup: cand.ageGroup,
                city: cand.city,
                message: note || `Study partner request sent for ${cand.track}`,
                timeAgo: 'Just now',
                status: 'pending'
              });
            });
          }
          closeModal();
          showToast(`Request sent to ${candidate.name}!`, 'success', 'send');
          updateBadgeCounts();
          renderCurrentRoute();
        } catch (err) {
          showToast(err.message || 'Could not send match request', 'danger', 'alert-circle');
        }
      });
    });
  }

  function openReportModal(targetName, type = 'user') {
    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-report-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-report-title" class="text-danger">Report or Block ${escapeHtml(targetName)}</h2>
            <p>EduMate strictly protects students in our verified age network</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label for="report-reason">Reason for report</label>
            <select id="report-reason" class="input">
              <option value="inappropriate">Inappropriate or disrespectful behavior</option>
              <option value="age">Suspected age mismatch (not 16–17)</option>
              <option value="spam">Commercial solicitations or spam</option>
              <option value="no-show">Repeatedly missed agreed study sessions</option>
              <option value="other">Other reason</option>
            </select>
          </div>

          <div class="field">
            <label for="report-details">Additional details (optional)</label>
            <textarea id="report-details" rows="2" placeholder="Briefly describe what happened..."></textarea>
          </div>

          <label class="check-control" style="margin-top: 4px;">
            <input type="checkbox" id="block-confirm" checked>
            <span><strong>Block this user immediately</strong>. They won't be able to message you, view your profile, or match with you.</span>
          </label>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Cancel</button>
          <button class="btn btn-danger" id="btn-submit-report">${icon('ban')} Submit report & block</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      modalEl.querySelector('#btn-submit-report').addEventListener('click', () => {
        closeModal();
        showToast(`${targetName} has been reported and blocked.`, 'danger', 'shield');
      });
    });
  }

  function openScheduleModal(preselectedPartnerId = null) {
    const data = EduData.get();
    const pairs = data.activePairs || [];

    if (pairs.length === 0) {
      showToast('You do not have any active study pairs yet. Accept or send a match first!', 'info', 'info');
      return;
    }

    const partnerOptions = pairs
      .map(
        (p) =>
          `<option value="${p.partnerId}" ${p.partnerId === preselectedPartnerId ? 'selected' : ''}>${escapeHtml(p.name)} (${escapeHtml(p.track)})</option>`
      )
      .join('');

    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-sched-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-sched-title">Schedule a Study Session</h2>
            <p>Set a date, time, and topic with your study partner</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label for="sched-partner">Study partner</label>
            <select id="sched-partner" class="input">${partnerOptions}</select>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="sched-date">Date</label>
              <input type="text" id="sched-date" class="input" value="Friday, Nov 1" placeholder="e.g. Friday, Nov 1">
            </div>
            <div class="field">
              <label for="sched-time">Time (UZT)</label>
              <input type="text" id="sched-time" class="input" value="18:00 – 19:00" placeholder="e.g. 18:00 – 19:00">
            </div>
          </div>

          <div class="field">
            <label for="sched-topic">Topic & Agenda</label>
            <input type="text" id="sched-topic" class="input" value="IELTS Speaking Part 2: Practice Cue Cards 1–4" placeholder="What will you study?">
          </div>

          <div class="field">
            <label for="sched-platform">Study Platform</label>
            <select id="sched-platform" class="input">
              <option value="Google Meet">Google Meet</option>
              <option value="Telegram Audio Call">Telegram Audio Call</option>
              <option value="Discord / Zoom">Discord / Zoom</option>
            </select>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Cancel</button>
          <button class="btn btn-primary" id="btn-save-session">${icon('calendar-days')} Confirm & Schedule</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      modalEl.querySelector('#btn-save-session').addEventListener('click', () => {
        const partnerSelect = modalEl.querySelector('#sched-partner');
        const selectedId = partnerSelect.value;
        const partner = pairs.find((p) => p.partnerId === selectedId) || pairs[0];
        const date = modalEl.querySelector('#sched-date').value.trim() || 'Upcoming';
        const time = modalEl.querySelector('#sched-time').value.trim() || '18:00 – 19:00 (UZT)';
        const topic = modalEl.querySelector('#sched-topic').value.trim() || 'Study Session';
        const platform = modalEl.querySelector('#sched-platform').value;

        EduData.update((state) => {
          state.sessions.unshift({
            id: 'sess-' + Date.now(),
            partnerId: partner.partnerId,
            partnerName: partner.name,
            partnerAvatar: partner.avatarClass,
            partnerInitials: partner.avatarInitials,
            topic: topic,
            date: date,
            time: time,
            dayNum: '01',
            monthStr: 'NOV',
            format: platform,
            link: 'https://meet.google.com/edu-mate-talk',
            status: 'upcoming',
            canConfirmComplete: true,
            track: partner.track,
            partnerContact: partner.contact.telegram
          });
        });

        closeModal();
        showToast(`Session with ${partner.name} scheduled!`, 'success', 'calendar');
        renderCurrentRoute();
      });
    });
  }

  function openConfirmSessionModal(sessionId) {
    const data = EduData.get();
    const session = data.sessions.find((s) => s.id === sessionId);
    if (!session) return;

    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-confirm-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-confirm-title">Confirm Completed Session</h2>
            <p>Dual confirmation keeps study streaks real and accountable</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="modal-person">
            <span class="avatar ${escapeHtml(session.partnerAvatar)}">${escapeHtml(session.partnerInitials)}</span>
            <div>
              <strong>${escapeHtml(session.partnerName)}</strong>
              <small>${escapeHtml(session.topic)} · ${escapeHtml(session.date)}</small>
            </div>
          </div>

          <label class="check-control" style="margin-top: 6px;">
            <input type="checkbox" id="check-attended" checked>
            <span><strong>Yes, we both attended</strong> and completed our study session as scheduled.</span>
          </label>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Not yet</button>
          <button class="btn btn-primary" id="btn-proceed-review">${icon('check-circle')} Confirm & leave review</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      modalEl.querySelector('#btn-proceed-review').addEventListener('click', () => {
        closeModal();
        openReviewModal(session);
      });
    });
  }

  function openReviewModal(session) {
    let selectedStars = 5;

    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-review-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-review-title">Peer Review for ${escapeHtml(session.partnerName)}</h2>
            <p>Leave constructive feedback to help each other grow</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="celebration">
            <div class="success-burst">${icon('award')}</div>
            <h3>Session Completed!</h3>
            <p>How was your practice session with ${escapeHtml(session.partnerName)}?</p>
          </div>

          <div class="field" style="text-align: center;">
            <div class="star-input" id="star-input" role="radiogroup" aria-label="Rating">
              <button type="button" data-val="1" class="active" aria-label="1 star">${icon('star')}</button>
              <button type="button" data-val="2" class="active" aria-label="2 stars">${icon('star')}</button>
              <button type="button" data-val="3" class="active" aria-label="3 stars">${icon('star')}</button>
              <button type="button" data-val="4" class="active" aria-label="4 stars">${icon('star')}</button>
              <button type="button" data-val="5" class="active" aria-label="5 stars">${icon('star')}</button>
            </div>
          </div>

          <div class="field">
            <label for="review-comment">Feedback & notes</label>
            <textarea id="review-comment" rows="3" placeholder="e.g. Great pace, shared helpful vocabulary tips and strictly kept the timer!">Great focus today! Covered 4 Part 2 cue cards and gave each other actionable vocabulary notes.</textarea>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Skip review</button>
          <button class="btn btn-primary" id="btn-submit-review">${icon('check')} Submit review & save progress</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      const starButtons = modalEl.querySelectorAll('#star-input button');
      starButtons.forEach((btn) => {
        btn.addEventListener('click', () => {
          selectedStars = parseInt(btn.getAttribute('data-val'), 10);
          starButtons.forEach((b) => {
            const v = parseInt(b.getAttribute('data-val'), 10);
            b.classList.toggle('active', v <= selectedStars);
          });
        });
      });

      modalEl.querySelector('#btn-submit-review').addEventListener('click', () => {
        const comment = modalEl.querySelector('#review-comment').value.trim();

        EduData.update((state) => {
          const sess = state.sessions.find((s) => s.id === session.id);
          if (sess) {
            sess.status = 'completed';
            sess.canConfirmComplete = false;
            sess.review = {
              stars: selectedStars,
              comment: comment || 'Productive and punctual session.',
              reviewer: state.user.name
            };
          }
          state.user.sessionsCompleted += 1;
          state.user.totalHours += 1;
          state.user.studyStreak += 1;
        });

        closeModal();
        showToast('Session confirmed! +1 hour added to your streak 🔥', 'success', 'award');
        renderCurrentRoute();
      });
    });
  }

  function openAddGoalModal() {
    const modalHtml = `
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-goal-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-goal-title">Create New Study Goal</h2>
            <p>Define what you want to achieve and find matching peers</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label for="goal-track">Study track</label>
            <select id="goal-track" class="input">
              <option value="IELTS Speaking">IELTS Speaking</option>
              <option value="SAT Math">SAT Math</option>
              <option value="Python & Web Dev">Python & Web Dev</option>
              <option value="General English">General English</option>
            </select>
          </div>

          <div class="field">
            <label for="goal-title">Goal title</label>
            <input type="text" id="goal-title" class="input" value="IELTS Speaking 7.5 Band" placeholder="e.g. IELTS 7.5 Band">
          </div>

          <div class="field-row">
            <div class="field">
              <label for="goal-current">Current level</label>
              <input type="text" id="goal-current" class="input" value="Band 6.0" placeholder="e.g. Band 6.0">
            </div>
            <div class="field">
              <label for="goal-target">Target level</label>
              <input type="text" id="goal-target" class="input" value="Band 7.5" placeholder="e.g. Band 7.5">
            </div>
          </div>

          <div class="field-row">
            <div class="field">
              <label for="goal-deadline">Target deadline</label>
              <input type="text" id="goal-deadline" class="input" value="Dec 2026" placeholder="e.g. Dec 2026">
            </div>
            <div class="field">
              <label for="goal-hours">Target hours / week</label>
              <input type="number" id="goal-hours" class="input" value="6" min="1" max="40">
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-secondary" data-close-modal>Cancel</button>
          <button class="btn btn-primary" id="btn-save-goal">${icon('plus')} Create Goal</button>
        </div>
      </div>
    `;

    openModal(modalHtml, (modalEl) => {
      modalEl.querySelector('#btn-save-goal').addEventListener('click', async () => {
        const title = modalEl.querySelector('#goal-title').value.trim() || 'New Goal';
        const track = modalEl.querySelector('#goal-track').value;
        const current = modalEl.querySelector('#goal-current').value.trim() || 'Beginner';
        const target = modalEl.querySelector('#goal-target').value.trim() || 'Advanced';
        const deadline = modalEl.querySelector('#goal-deadline').value.trim() || '2026';

        try {
          await EduApi.saveGoalFromForm({ trackName: track, current, target, deadline, weeklyHours: Number(modalEl.querySelector('#goal-hours').value) || 1 });
          await EduData.refreshFromBackend();
          EduData.update((state) => {
          state.user.goals.push({
            id: 'goal-' + Date.now(),
            title: title,
            track: track,
            currentLevel: current,
            targetLevel: target,
            deadline: deadline,
            progress: 10,
            hoursDone: 2,
            hoursTotal: 25,
            sessionsCount: 1,
            isPrimary: false
          });
          });

          closeModal(); showToast(`Goal "${title}" created!`, 'success', 'check-circle'); renderCurrentRoute();
        } catch (err) { showToast(err.message || 'Could not save goal', 'danger', 'alert-circle'); }
      });
    });
  }

  function openSafetyModal() {
    const modalHtml = `
      <div class="modal modal-wide" role="dialog" aria-modal="true" aria-labelledby="modal-safety-title">
        <div class="modal-head">
          <div>
            <h2 id="modal-safety-title">EduMate Trust & Safety Standards</h2>
            <p>Built specifically for students and young learners in Uzbekistan</p>
          </div>
          <button class="icon-btn" data-close-modal aria-label="Close dialog">${icon('x')}</button>
        </div>
        <div class="modal-body">
          <div class="modal-notice">
            ${icon('shield-check')}
            <div>
              <strong>Strict Age-Group Isolation (16–17)</strong>
              <p>Underage students are only matched with peers in their exact verified age cohort. Adults are strictly barred from teenage pools.</p>
            </div>
          </div>

          <div class="privacy-list" style="padding: 0;">
            <div class="privacy-row">
              ${icon('lock')}
              <div>
                <strong>Private Contact Details</strong>
                <small>Telegram handles and email addresses remain completely invisible until both students mutually accept a match request.</small>
              </div>
            </div>
            <div class="privacy-row">
              ${icon('check-circle')}
              <div>
                <strong>Dual Session Confirmation</strong>
                <small>Study time and streaks only count toward your record after both study partners confirm the session took place.</small>
              </div>
            </div>
            <div class="privacy-row">
              ${icon('ban')}
              <div>
                <strong>Immediate Zero-Tolerance Reporting</strong>
                <small>Any inappropriate message, impersonation, or discomfort can be reported in 1 click, instantly revoking visibility and access.</small>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-primary" data-close-modal>Understood</button>
        </div>
      </div>
    `;
    openModal(modalHtml);
  }

  /* ==========================================================================
     4. SHELL CONTROLS (NAV, THEME, SEARCH, POPOVERS)
     ========================================================================== */

  const appEl = document.getElementById('app');
  const sidebar = document.getElementById('sidebar');
  const sidebarScrim = document.getElementById('sidebar-scrim');
  const menuToggle = document.getElementById('menu-toggle');
  const sidebarClose = document.getElementById('sidebar-close');
  const themeToggle = document.getElementById('theme-toggle');
  const notificationToggle = document.getElementById('notification-toggle');
  const notificationPopover = document.getElementById('notification-popover');
  const profileToggle = document.getElementById('profile-toggle');
  const profilePopover = document.getElementById('profile-popover');
  const globalSearchInput = document.getElementById('global-search');
  const requestCountEl = document.getElementById('request-count');
  const mainContent = document.getElementById('main-content');

  // Mobile sidebar controls
  function openSidebar() {
    document.body.classList.add('sidebar-open');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    document.body.classList.remove('sidebar-open');
    if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
  }

  if (menuToggle) menuToggle.addEventListener('click', openSidebar);
  if (sidebarClose) sidebarClose.addEventListener('click', closeSidebar);
  if (sidebarScrim) sidebarScrim.addEventListener('click', closeSidebar);

  // Close popovers helper
  function closeAllPopovers() {
    if (notificationPopover) notificationPopover.hidden = true;
    if (notificationToggle) notificationToggle.setAttribute('aria-expanded', 'false');
    if (profilePopover) profilePopover.hidden = true;
    if (profileToggle) profileToggle.setAttribute('aria-expanded', 'false');

    const searchDrop = document.getElementById('search-dropdown');
    if (searchDrop) searchDrop.remove();
  }

  // Popover toggles
  if (notificationToggle) {
    notificationToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = notificationPopover.hidden;
      closeAllPopovers();
      if (isHidden) {
        renderNotificationPopover();
        notificationPopover.hidden = false;
        notificationToggle.setAttribute('aria-expanded', 'true');
      }
    });
  }

  if (profileToggle) {
    profileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = profilePopover.hidden;
      closeAllPopovers();
      if (isHidden) {
        profilePopover.hidden = false;
        profileToggle.setAttribute('aria-expanded', 'true');
      }
    });
  }

  // Theme toggle
  function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const nextTheme = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    try {
      localStorage.setItem('edumate_theme', nextTheme);
    } catch (e) {}

    // Update icon
    const nextIcon = isDark ? 'moon' : 'sun';
    if (themeToggle) {
      themeToggle.innerHTML = icon(nextIcon);
      themeToggle.setAttribute('aria-label', isDark ? 'Switch to dark theme' : 'Switch to light theme');
    }
  }

  // Initialize theme
  try {
    const savedTheme = localStorage.getItem('edumate_theme');
    if (savedTheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      if (themeToggle) {
        themeToggle.innerHTML = icon('sun');
        themeToggle.setAttribute('aria-label', 'Switch to light theme');
      }
    }
  } catch (e) {}

  if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
  const menuThemeBtn = document.getElementById('menu-theme');
  if (menuThemeBtn) menuThemeBtn.addEventListener('click', toggleTheme);

  // Badge count updates
  function updateBadgeCounts() {
    const data = EduData.get();
    const count = (data.incomingRequests || []).filter((r) => r.status === 'pending').length;
    if (requestCountEl) {
      requestCountEl.textContent = count;
      requestCountEl.style.display = count > 0 ? 'grid' : 'none';
    }
  }

  // Notifications content
  function renderNotificationPopover() {
    const data = EduData.get();
    const list = data.notifications || [];

    let itemsHtml = '';
    if (list.length === 0) {
      itemsHtml = '<p style="padding: 20px; text-align: center; color: var(--muted); font-size: 12px;">No new notifications</p>';
    } else {
      itemsHtml = list
        .map(
          (n) => `
        <div class="notification-item ${n.unread ? 'unread' : ''}" data-route="${n.route || 'dashboard'}">
          <div class="notice-icon">${icon(n.route === 'matches' ? 'heart-handshake' : n.route === 'sessions' ? 'calendar-days' : 'sparkles')}</div>
          <div>
            <p><strong>${escapeHtml(n.title)}</strong><br>${escapeHtml(n.text)}</p>
            <time>${escapeHtml(n.time)}</time>
          </div>
        </div>
      `
        )
        .join('');
    }

    notificationPopover.innerHTML = `
      <div class="notification-head">
        <h3>Notifications</h3>
        <button id="btn-mark-read" style="background:none; border:none; cursor:pointer;">Mark all read</button>
      </div>
      <div class="notification-list">${itemsHtml}</div>
    `;

    hydrateIcons(notificationPopover);

    const markReadBtn = notificationPopover.querySelector('#btn-mark-read');
    if (markReadBtn) {
      markReadBtn.addEventListener('click', () => {
        EduData.update((state) => {
          (state.notifications || []).forEach((n) => (n.unread = false));
        });
        const dot = document.querySelector('.notification-dot');
        if (dot) dot.style.display = 'none';
        renderNotificationPopover();
        showToast('All notifications marked as read', 'info', 'check');
      });
    }

    notificationPopover.querySelectorAll('.notification-item').forEach((item) => {
      item.addEventListener('click', () => {
        const route = item.getAttribute('data-route');
        closeAllPopovers();
        window.location.hash = '#/' + route;
      });
    });
  }

  // Global search autocomplete
  if (globalSearchInput) {
    globalSearchInput.addEventListener('input', (e) => {
      const query = e.target.value.trim().toLowerCase();
      let drop = document.getElementById('search-dropdown');

      if (!query) {
        if (drop) drop.remove();
        return;
      }

      if (!drop) {
        drop = document.createElement('div');
        drop.id = 'search-dropdown';
        drop.className = 'search-dropdown';
        globalSearchInput.parentElement.appendChild(drop);
      }

      const data = EduData.get();
      const matchedCand = data.candidates.filter(
        (c) => c.name.toLowerCase().includes(query) || c.track.toLowerCase().includes(query)
      );
      const matchedGoals = data.user.goals.filter(
        (g) => g.title.toLowerCase().includes(query) || g.track.toLowerCase().includes(query)
      );

      let content = '';

      if (matchedCand.length > 0) {
        content += '<div class="search-dropdown-head">Study Partners</div>';
        content += matchedCand
          .slice(0, 3)
          .map(
            (c) => `
          <button class="search-dropdown-item" data-action="partner" data-id="${c.id}">
            <span class="avatar avatar-sm ${c.avatarClass}">${c.avatarInitials}</span>
            <div>
              <strong>${escapeHtml(c.name)}</strong>
              <small>${escapeHtml(c.track)} · ${c.compatibility}% match</small>
            </div>
          </button>
        `
          )
          .join('');
      }

      if (matchedGoals.length > 0) {
        content += '<div class="search-dropdown-head">Your Goals</div>';
        content += matchedGoals
          .map(
            (g) => `
          <button class="search-dropdown-item" data-action="profile">
            ${icon('target')}
            <div>
              <strong>${escapeHtml(g.title)}</strong>
              <small>${g.progress}% completed · ${escapeHtml(g.deadline)}</small>
            </div>
          </button>
        `
          )
          .join('');
      }

      if (!content) {
        content = '<div class="search-dropdown-empty">No results found for "' + escapeHtml(query) + '"</div>';
      }

      drop.innerHTML = content;
      hydrateIcons(drop);

      drop.querySelectorAll('.search-dropdown-item').forEach((btn) => {
        btn.addEventListener('click', () => {
          const action = btn.getAttribute('data-action');
          if (action === 'partner') {
            window.location.hash = '#/partners';
          } else {
            window.location.hash = '#/profile';
          }
          if (drop) drop.remove();
          globalSearchInput.value = '';
        });
      });
    });

    globalSearchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = globalSearchInput.value.trim();
        if (query) {
          window.location.hash = '#/partners';
          const drop = document.getElementById('search-dropdown');
          if (drop) drop.remove();
        }
      }
    });
  }

  // Global click & key listeners
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.popover-wrap') && !e.target.closest('.global-search')) {
      closeAllPopovers();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllPopovers();
      closeModal();
      closeSidebar();
    }
    // Ctrl + K focus search
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      if (globalSearchInput) {
        globalSearchInput.focus();
        globalSearchInput.select();
      }
    }
  });

  // Action listeners for generic data-nav
  document.addEventListener('click', (e) => {
    const navBtn = e.target.closest('[data-nav]');
    if (navBtn) {
      const targetRoute = navBtn.getAttribute('data-nav');
      window.location.hash = '#/' + targetRoute;
      closeSidebar();
      closeAllPopovers();
    }
  });

  /* ==========================================================================
     5. ANIMATION UTILITIES (COUNT-UP & SMOOTH REVEAL)
     ========================================================================== */

  function animateCountUp(element, endVal, duration = 800) {
    if (!element) return;
    const startVal = 0;
    const startTime = performance.now();

    function update(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(startVal + (endVal - startVal) * easeProgress);
      element.textContent = current;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = endVal;
      }
    }
    requestAnimationFrame(update);
  }

  /* ==========================================================================
     6. SCREEN RENDERERS
     ========================================================================== */

  /**
   * Screen 1: Dashboard
   */
  function renderDashboard() {
    const data = EduData.get();
    const user = data.user;
    const primaryGoal = user.goals.find((g) => g.isPrimary) || user.goals[0];
    const topCandidates = data.candidates.slice(0, 3);
    const nextSession = data.sessions.find((s) => s.status === 'upcoming') || data.sessions[0];

    // Calculate ring offset for 68% progress: circumference = 2 * PI * 52 ≈ 327
    const circumference = 327;
    const progressOffset = circumference - (circumference * (primaryGoal.progress / 100));

    const html = `
      <div class="page-enter">
        <div class="welcome-row">
          <div>
            <h1>Good morning, ${escapeHtml(user.name.split(' ')[0])} 👋</h1>
            <p>Ready to make steady progress on your <strong>${escapeHtml(user.primaryTrack)}</strong> goal today?</p>
          </div>
          <div class="date-chip">
            ${icon('calendar')}
            <span>Thursday, Oct 29 · <strong>${user.studyStreak}-day streak 🔥</strong></span>
          </div>
        </div>
        <span class="badge badge-info">In development · progress and streaks are demo data</span>

        <div class="dashboard-grid">
          <!-- Main column -->
          <div class="dashboard-main">
            <!-- Goal Hero -->
            <div class="card goal-hero">
              <div>
                <div class="goal-kicker">${icon('target')} Primary Study Goal</div>
                <h2>${escapeHtml(primaryGoal.title)}</h2>
                <p>Target: <strong>${escapeHtml(primaryGoal.targetLevel)}</strong> by ${escapeHtml(primaryGoal.deadline)}. Maintaining ${user.hoursPerWeek} hours/week of focused study.</p>
                <div class="goal-meta">
                  <span class="badge">${primaryGoal.sessionsCount} sessions completed</span>
                  <span class="badge">${primaryGoal.hoursDone} of ${primaryGoal.hoursTotal} target hrs</span>
                  <span class="badge">3x / week schedule</span>
                </div>
                <div style="margin-top: 24px; display: flex; gap: 10px; flex-wrap: wrap;">
                  <a href="#/partners" class="btn btn-primary" style="background: #ffffff; color: #173f35; font-weight: 700;">${icon('users')} Find a study partner</a>
                  <a href="#/profile" class="btn btn-secondary" style="border-color: rgba(255,255,255,.3); color: #ffffff; background: rgba(255,255,255,.08);">${icon('user-round')} Edit goal details</a>
                </div>
              </div>

              <div class="progress-ring" style="--ring-offset: ${progressOffset};">
                <svg viewBox="0 0 120 120">
                  <circle class="ring-bg" cx="60" cy="60" r="52"></circle>
                  <circle class="ring-value" cx="60" cy="60" r="52"></circle>
                </svg>
                <div class="ring-label">
                  <strong data-countup="${primaryGoal.progress}">0</strong>%
                  <span>COMPLETED</span>
                </div>
              </div>
            </div>

            <!-- Stats Row -->
            <div class="stats-row">
              <div class="card stat-card">
                <div class="stat-top">
                  <span>Study Streak</span>
                  <div class="stat-icon apricot">${icon('flame')}</div>
                </div>
                <div class="stat-value">
                  <strong data-countup="${user.studyStreak}">0</strong>
                  <span>days</span>
                </div>
                <div class="stat-foot">Personal best: <b>14 days</b></div>
              </div>

              <div class="card stat-card">
                <div class="stat-top">
                  <span>Total Study Time</span>
                  <div class="stat-icon">${icon('clock')}</div>
                </div>
                <div class="stat-value">
                  <strong data-countup="${user.totalHours}">0</strong>
                  <span>hours</span>
                </div>
                <div class="stat-foot"><b>+4.5 hrs</b> this week</div>
              </div>

              <div class="card stat-card">
                <div class="stat-top">
                  <span>Sessions Completed</span>
                  <div class="stat-icon blue">${icon('award')}</div>
                </div>
                <div class="stat-value">
                  <strong data-countup="${user.sessionsCompleted}">0</strong>
                  <span>sessions</span>
                </div>
                <div class="stat-foot"><b>100%</b> completion rate</div>
              </div>
            </div>

            <!-- Suggested Study Partners -->
            <div class="card card-pad">
              <div class="section-head">
                <div>
                  <h2>Suggested study partners for you</h2>
                  <p>Students in your age group (16–17) with matching goals & schedules</p>
                </div>
                <a href="#/partners" class="section-link">View all 8 candidates ${icon('arrow-right')}</a>
              </div>

              <div class="partner-list">
                ${topCandidates
                  .map(
                    (cand) => `
                  <div class="partner-row">
                    <span class="avatar ${cand.avatarClass}">${cand.avatarInitials}</span>
                    <div class="partner-info">
                      <strong>${escapeHtml(cand.name)} <span class="badge badge-success" style="font-size: 9px; padding: 2px 6px;">${cand.compatibility}% match</span></strong>
                      <p>${escapeHtml(cand.track)} · Target: ${escapeHtml(cand.target)} · ${escapeHtml(cand.city)}</p>
                    </div>
                    ${
                      cand.status === 'pending'
                        ? `<button class="btn btn-sm btn-secondary" disabled>✓ Request Sent</button>`
                        : `<button class="btn btn-sm btn-primary" data-action="connect" data-id="${cand.id}">${icon('send')} Connect</button>`
                    }
                  </div>
                `
                  )
                  .join('')}
              </div>
            </div>
          </div>

          <!-- Side column -->
          <div class="dashboard-side">
            <!-- Next Scheduled Session -->
            <div class="card session-card-next">
              <div class="section-head" style="margin-bottom: 0;">
                <div>
                  <div class="eyebrow">${icon('calendar')} Up next</div>
                  <h3 style="font-size: 16px;">Next study session</h3>
                </div>
              </div>

              <div class="next-date">
                <div class="calendar-tile">
                  <span>${escapeHtml(nextSession.monthStr)}</span>
                  <strong>${escapeHtml(nextSession.dayNum)}</strong>
                </div>
                <div>
                  <h3>${escapeHtml(nextSession.topic)}</h3>
                  <p>${escapeHtml(nextSession.time)}</p>
                </div>
              </div>

              <div class="session-person">
                <span class="avatar avatar-sm ${escapeHtml(nextSession.partnerAvatar)}">${escapeHtml(nextSession.partnerInitials)}</span>
                <div>
                  <strong>${escapeHtml(nextSession.partnerName)}</strong>
                  <small>Partner · ${escapeHtml(nextSession.format)}</small>
                </div>
              </div>

              <div style="display: flex; gap: 8px;">
                ${
                  nextSession.canConfirmComplete
                    ? `<button class="btn btn-primary btn-block btn-sm" data-action="confirm-session" data-id="${nextSession.id}">${icon('check-circle')} Confirm completed</button>`
                    : `<a href="${escapeHtml(nextSession.link)}" target="_blank" class="btn btn-secondary btn-block btn-sm">${icon('video')} Open meeting link</a>`
                }
              </div>
            </div>

            <!-- Weekly Activity Graph -->
            <div class="card weekly-card">
              <div class="section-head" style="margin-bottom: 0;">
                <div>
                  <h3>Weekly study momentum</h3>
                  <p>Study hours per day this week</p>
                </div>
                <strong style="color: var(--primary); font-size: 13px;">12.0 hrs</strong>
              </div>

              <div class="week-bars">
                ${user.weeklyActivity
                  .map(
                    (d) => `
                  <div class="day-bar ${d.isToday ? 'today' : ''}" title="${d.day}: ${d.hours} hrs">
                    <div class="day-bar-track">
                      <div class="day-bar-fill" style="height: ${d.heightPct}%;"></div>
                    </div>
                    <small>${d.day}</small>
                  </div>
                `
                  )
                  .join('')}
              </div>
            </div>

            <!-- Safety & Trust Mini Banner -->
            <div class="card safety-mini">
              <span>${icon('shield-check')}</span>
              <div>
                <h3>Safe & verified network</h3>
                <p>You only study with verified students in the 16–17 age group. Your contact info is private.</p>
                <button type="button" data-action="open-safety">Learn about safety standards</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    // Run count-ups
    mainContent.querySelectorAll('[data-countup]').forEach((el) => {
      const target = parseInt(el.getAttribute('data-countup'), 10) || 0;
      animateCountUp(el, target, 750);
    });

    // Bind action buttons
    mainContent.querySelectorAll('[data-action="connect"]').forEach((btn) => {
      btn.addEventListener('click', () => openConnectModal(btn.getAttribute('data-id')));
    });

    mainContent.querySelectorAll('[data-action="confirm-session"]').forEach((btn) => {
      btn.addEventListener('click', () => openConfirmSessionModal(btn.getAttribute('data-id')));
    });

    mainContent.querySelectorAll('[data-action="open-safety"]').forEach((btn) => {
      btn.addEventListener('click', openSafetyModal);
    });
  }

  /**
   * Screen 2: Find Partners
   */
  let partnerFilters = {
    search: '',
    track: 'all',
    level: 'all',
    availability: 'all'
  };

  function renderPartners() {
    const data = EduData.get();
    const candidates = data.candidates || [];

    // Filter logic
    const filtered = candidates.filter((c) => {
      if (partnerFilters.search) {
        const q = partnerFilters.search.toLowerCase();
        const matchName = c.name.toLowerCase().includes(q);
        const matchGoal = c.goalText.toLowerCase().includes(q);
        const matchTrack = c.track.toLowerCase().includes(q);
        const matchCity = c.city.toLowerCase().includes(q);
        if (!matchName && !matchGoal && !matchTrack && !matchCity) return false;
      }
      if (partnerFilters.track !== 'all') {
        if (!c.track.toLowerCase().includes(partnerFilters.track.toLowerCase())) return false;
      }
      if (partnerFilters.level !== 'all') {
        if (partnerFilters.level === 'advanced' && !c.target.includes('7.5') && !c.target.includes('8.0') && !c.target.includes('780') && !c.target.includes('750')) return false;
        if (partnerFilters.level === 'intermediate' && !c.level.includes('B1') && !c.level.includes('B2') && !c.level.includes('620') && !c.level.includes('6.0')) return false;
      }
      if (partnerFilters.availability !== 'all') {
        if (partnerFilters.availability === 'evenings' && !c.availability.toLowerCase().includes('evening')) return false;
        if (partnerFilters.availability === 'weekends' && !c.availability.toLowerCase().includes('sat') && !c.availability.toLowerCase().includes('sun')) return false;
        if (partnerFilters.availability === 'weekdays' && !c.availability.toLowerCase().includes('mon') && !c.availability.toLowerCase().includes('tue') && !c.availability.toLowerCase().includes('wed') && !c.availability.toLowerCase().includes('thu') && !c.availability.toLowerCase().includes('fri') && !c.availability.toLowerCase().includes('weekdays')) return false;
      }
      return true;
    });

    const html = `
      <div class="page-enter">
        <div class="page-head">
          <div>
            <h1>Find your study partner</h1>
            <p>Connect with compatible students in your age group (16–17) with mutual study goals.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-secondary" id="btn-refresh-filters">${icon('filter')} Reset filters</button>
            <a href="#/matches" class="btn btn-primary">${icon('heart-handshake')} View active matches</a>
          </div>
        </div>

        <!-- Filter bar -->
        <div class="card filter-bar">
          <div class="search-field">
            <span data-icon="search"></span>
            <input type="text" id="filter-search" class="input" placeholder="Search by name, topic, or keyword..." value="${escapeHtml(partnerFilters.search)}">
          </div>

          <select id="filter-track" aria-label="Filter by track">
            <option value="all" ${partnerFilters.track === 'all' ? 'selected' : ''}>All study tracks</option>
            <option value="IELTS Speaking" ${partnerFilters.track === 'IELTS Speaking' ? 'selected' : ''}>IELTS Speaking</option>
            <option value="SAT Math" ${partnerFilters.track === 'SAT Math' ? 'selected' : ''}>SAT Math</option>
            <option value="Python" ${partnerFilters.track === 'Python' ? 'selected' : ''}>Python & Web Dev</option>
            <option value="General English" ${partnerFilters.track === 'General English' ? 'selected' : ''}>General English</option>
          </select>

          <select id="filter-level" aria-label="Filter by level">
            <option value="all" ${partnerFilters.level === 'all' ? 'selected' : ''}>All target levels</option>
            <option value="advanced" ${partnerFilters.level === 'advanced' ? 'selected' : ''}>Advanced / Band 7.5+ / SAT 750+</option>
            <option value="intermediate" ${partnerFilters.level === 'intermediate' ? 'selected' : ''}>Intermediate / Band 6.0–6.5</option>
          </select>

          <select id="filter-avail" aria-label="Filter by schedule">
            <option value="all" ${partnerFilters.availability === 'all' ? 'selected' : ''}>Any schedule</option>
            <option value="evenings" ${partnerFilters.availability === 'evenings' ? 'selected' : ''}>Weekday evenings</option>
            <option value="weekends" ${partnerFilters.availability === 'weekends' ? 'selected' : ''}>Weekends</option>
            <option value="weekdays" ${partnerFilters.availability === 'weekdays' ? 'selected' : ''}>Weekdays</option>
          </select>
        </div>

        <div class="results-meta">
          <span>Showing <strong>${filtered.length}</strong> compatible candidates in <strong>Age group 16–17</strong></span>
          <span class="badge badge-info">${icon('shield-check')} Verified students only</span>
        </div>

        <!-- Candidates Grid -->
        ${
          filtered.length === 0
            ? `
          <div class="card empty-state">
            <div class="empty-icon">${icon('users')}</div>
            <h3>No study partners match your filter criteria</h3>
            <p>Try clearing some filters or searching for broader keywords to discover more students.</p>
            <button class="btn btn-secondary" id="btn-empty-reset">Clear all filters</button>
          </div>
        `
            : `
          <div class="candidate-grid">
            ${filtered
              .map(
                (c) => `
              <div class="card candidate-card">
                <div class="candidate-top">
                  <span class="avatar avatar-lg ${c.avatarClass}">${c.avatarInitials}</span>
                  <div class="compatibility" style="--score: ${c.compatibility};" title="${c.compatibility}% compatibility based on schedule and track overlap">
                    <span>${c.compatibility}%</span>
                  </div>
                </div>

                <div class="candidate-name">
                  <h2>${escapeHtml(c.name)}</h2>
                  <p>${escapeHtml(c.ageGroup)} · ${escapeHtml(c.city)} · <strong>${escapeHtml(c.track)}</strong></p>
                </div>

                <div class="candidate-goal">
                  <p>"${escapeHtml(c.goalText)}"</p>
                </div>

                <div class="tag-list">
                  <span class="badge badge-success">Target: ${escapeHtml(c.target)}</span>
                  ${(c.tags || []).slice(0, 2).map((t) => `<span class="badge">${escapeHtml(t)}</span>`).join('')}
                </div>

                <div class="availability-line">
                  ${icon('clock')}
                  <span>${escapeHtml(c.availability)}</span>
                </div>

                <div class="candidate-actions">
                  ${
                    c.status === 'pending'
                      ? `<button class="btn btn-secondary candidate-sent" disabled>${icon('check')} Request Sent</button>`
                      : c.status === 'accepted'
                      ? `<a href="#/matches" class="btn btn-soft">${icon('heart-handshake')} Active Match</a>`
                      : `<button class="btn btn-primary" data-action="connect" data-id="${c.id}">${icon('send')} Connect</button>`
                  }
                  <button class="icon-btn" data-action="report" data-name="${escapeHtml(c.name)}" aria-label="Report or block ${escapeHtml(c.name)}">${icon('flag')}</button>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        `
        }
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    // Filter event listeners
    const searchInput = mainContent.querySelector('#filter-search');
    const trackSelect = mainContent.querySelector('#filter-track');
    const levelSelect = mainContent.querySelector('#filter-level');
    const availSelect = mainContent.querySelector('#filter-avail');
    const resetBtn = mainContent.querySelector('#btn-refresh-filters');
    const emptyResetBtn = mainContent.querySelector('#btn-empty-reset');

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        partnerFilters.search = e.target.value;
        renderPartners();
      });
    }

    if (trackSelect) {
      trackSelect.addEventListener('change', (e) => {
        partnerFilters.track = e.target.value;
        renderPartners();
      });
    }

    if (levelSelect) {
      levelSelect.addEventListener('change', (e) => {
        partnerFilters.level = e.target.value;
        renderPartners();
      });
    }

    if (availSelect) {
      availSelect.addEventListener('change', (e) => {
        partnerFilters.availability = e.target.value;
        renderPartners();
      });
    }

    const handleReset = () => {
      partnerFilters = { search: '', track: 'all', level: 'all', availability: 'all' };
      renderPartners();
      showToast('Filters reset', 'info', 'check');
    };

    if (resetBtn) resetBtn.addEventListener('click', handleReset);
    if (emptyResetBtn) emptyResetBtn.addEventListener('click', handleReset);

    // Actions
    mainContent.querySelectorAll('[data-action="connect"]').forEach((btn) => {
      btn.addEventListener('click', () => openConnectModal(btn.getAttribute('data-id')));
    });

    mainContent.querySelectorAll('[data-action="report"]').forEach((btn) => {
      btn.addEventListener('click', () => openReportModal(btn.getAttribute('data-name')));
    });
  }

  /**
   * Screen 3: Requests & Matches
   */
  let currentMatchesTab = 'incoming'; // incoming, outgoing, active

  function renderMatches() {
    const data = EduData.get();
    const incoming = data.incomingRequests || [];
    const outgoing = data.outgoingRequests || [];
    const active = data.activePairs || [];

    const incomingCount = incoming.filter((r) => r.status === 'pending').length;
    const outgoingCount = outgoing.filter((r) => r.status === 'pending').length;
    const activeCount = active.length;

    let tabContent = '';

    if (currentMatchesTab === 'incoming') {
      const pendingIncoming = incoming.filter((r) => r.status === 'pending');
      if (pendingIncoming.length === 0) {
        tabContent = `
          <div class="card empty-state">
            <div class="empty-icon">${icon('heart-handshake')}</div>
            <h3>No pending incoming requests</h3>
            <p>When compatible peers in your age group invite you to study, their requests will appear here.</p>
            <a href="#/partners" class="btn btn-primary">${icon('users')} Find study partners</a>
          </div>
        `;
      } else {
        tabContent = `
          <div class="request-list">
            ${pendingIncoming
              .map(
                (req) => `
              <div class="card request-card" id="req-card-${req.id}">
                <span class="avatar avatar-lg ${req.avatarClass}">${req.avatarInitials}</span>
                <div class="request-main">
                  <div class="request-title">
                    <h2>${escapeHtml(req.name)}</h2>
                    <span class="badge badge-success">${req.compatibility}% match</span>
                    <span class="badge">${escapeHtml(req.track)}</span>
                    <span class="badge">${escapeHtml(req.ageGroup)} · ${escapeHtml(req.city)}</span>
                  </div>
                  <p>Sent ${escapeHtml(req.timeAgo)}</p>
                  <div class="request-note">
                    "${escapeHtml(req.message)}"
                  </div>
                </div>
                <div class="request-actions">
                  <button class="btn btn-primary" data-action="accept-req" data-id="${req.id}">${icon('check')} Accept</button>
                  <button class="btn btn-secondary" data-action="decline-req" data-id="${req.id}">${icon('x')} Decline</button>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        `;
      }
    } else if (currentMatchesTab === 'outgoing') {
      const pendingOutgoing = outgoing.filter((r) => r.status === 'pending');
      if (pendingOutgoing.length === 0) {
        tabContent = `
          <div class="card empty-state">
            <div class="empty-icon">${icon('send')}</div>
            <h3>No outgoing requests</h3>
            <p>You have no pending requests sent to other students. Browse candidates to invite partners.</p>
            <a href="#/partners" class="btn btn-primary">${icon('users')} Explore candidates</a>
          </div>
        `;
      } else {
        tabContent = `
          <div class="request-list">
            ${pendingOutgoing
              .map(
                (req) => `
              <div class="card request-card">
                <span class="avatar avatar-lg ${req.avatarClass}">${req.avatarInitials}</span>
                <div class="request-main">
                  <div class="request-title">
                    <h2>${escapeHtml(req.name)}</h2>
                    <span class="badge badge-warning">${icon('clock')} Awaiting response</span>
                    <span class="badge">${escapeHtml(req.track)}</span>
                    <span class="badge">${escapeHtml(req.ageGroup)} · ${escapeHtml(req.city)}</span>
                  </div>
                  <p>Sent ${escapeHtml(req.timeAgo)}</p>
                  <div class="request-note">
                    "${escapeHtml(req.message)}"
                  </div>
                </div>
                <div class="request-actions">
                  <button class="btn btn-secondary" data-action="cancel-req" data-id="${req.id}">Cancel request</button>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        `;
      }
    } else if (currentMatchesTab === 'active') {
      if (active.length === 0) {
        tabContent = `
          <div class="card empty-state">
            <div class="empty-icon">${icon('heart-handshake')}</div>
            <h3>No active study pairs yet</h3>
            <p>Accept an incoming request or connect with partners to start studying together.</p>
            <a href="#/partners" class="btn btn-primary">${icon('users')} Find partners</a>
          </div>
        `;
      } else {
        tabContent = `
          <div class="active-grid">
            ${active
              .map(
                (pair) => `
              <div class="card active-card">
                <div class="active-head">
                  <span class="avatar avatar-lg ${pair.avatarClass}">${pair.avatarInitials}</span>
                  <div>
                    <h2>${escapeHtml(pair.name)}</h2>
                    <p>${escapeHtml(pair.track)} · Target: ${escapeHtml(pair.target)} · ${escapeHtml(pair.city)}</p>
                  </div>
                </div>

                <div class="contact-reveal">
                  ${icon('lock')}
                  <div>
                    <strong>Mutual match verified: Contact unlocked</strong>
                    <span>Telegram: <a href="https://t.me/${pair.contact.telegram.replace('@', '')}" target="_blank" style="text-decoration: underline; font-weight: 700;">${escapeHtml(pair.contact.telegram)}</a> · Email: ${escapeHtml(pair.contact.email)}</span>
                  </div>
                </div>

                <div class="active-stats">
                  <div class="active-stat">
                    <strong>${pair.sessionsTogether}</strong>
                    <span>Sessions</span>
                  </div>
                  <div class="active-stat">
                    <strong>${pair.hoursTogether}h</strong>
                    <span>Studied</span>
                  </div>
                  <div class="active-stat">
                    <strong>${pair.streakDays}d</strong>
                    <span>Streak</span>
                  </div>
                </div>

                <div class="active-next">
                  ${icon('calendar')}
                  <span>Next session: <strong>${escapeHtml(pair.nextSession)}</strong></span>
                </div>

                <div class="active-actions" style="margin-top: 16px;">
                  <button class="btn btn-primary btn-sm" data-action="schedule-with" data-id="${pair.partnerId}">${icon('calendar-days')} Schedule session</button>
                  <button class="btn btn-secondary btn-sm" data-action="copy-contact" data-contact="${escapeHtml(pair.contact.telegram)}">${icon('message-square')} Copy Telegram</button>
                  <button class="icon-btn" data-action="report" data-name="${escapeHtml(pair.name)}" aria-label="Report or block ${escapeHtml(pair.name)}">${icon('flag')}</button>
                </div>
              </div>
            `
              )
              .join('')}
          </div>
        `;
      }
    }

    const html = `
      <div class="page-enter">
        <div class="page-head">
          <div>
            <h1>Requests & study matches</h1>
            <p>Manage incoming study partner requests, pending invitations, and your active learning pairs.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-primary" id="btn-open-schedule">${icon('calendar-days')} Schedule session</button>
          </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs" role="tablist">
          <button class="tab ${currentMatchesTab === 'incoming' ? 'active' : ''}" data-tab="incoming" role="tab">
            Incoming requests
            <span class="tab-count">${incomingCount}</span>
          </button>
          <button class="tab ${currentMatchesTab === 'outgoing' ? 'active' : ''}" data-tab="outgoing" role="tab">
            Outgoing requests
            <span class="tab-count">${outgoingCount}</span>
          </button>
          <button class="tab ${currentMatchesTab === 'active' ? 'active' : ''}" data-tab="active" role="tab">
            Active study pairs
            <span class="tab-count">${activeCount}</span>
          </button>
        </div>

        <div id="tab-panel">
          ${tabContent}
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    // Tab buttons
    mainContent.querySelectorAll('.tab').forEach((tabBtn) => {
      tabBtn.addEventListener('click', () => {
        currentMatchesTab = tabBtn.getAttribute('data-tab');
        renderMatches();
      });
    });

    const openSchedBtn = mainContent.querySelector('#btn-open-schedule');
    if (openSchedBtn) {
      openSchedBtn.addEventListener('click', () => openScheduleModal());
    }

    // Accept request
    mainContent.querySelectorAll('[data-action="accept-req"]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const reqId = btn.getAttribute('data-id');
        try { await EduApi.updateMatchRequestStatus(reqId, 'accepted'); await EduData.refreshFromBackend(); } catch (err) { showToast(err.message, 'danger', 'alert-circle'); return; }
        EduData.update((state) => {
          const req = state.incomingRequests.find((r) => r.id === reqId);
          if (req) {
            req.status = 'accepted';
            // Add to active pairs
            state.activePairs.unshift({
              id: 'pair-' + Date.now(),
              partnerId: req.candidateId,
              name: req.name,
              avatarClass: req.avatarClass,
              avatarInitials: req.avatarInitials,
              track: req.track,
              target: 'Band 7.5',
              ageGroup: req.ageGroup,
              city: req.city,
              sessionsTogether: 1,
              hoursTogether: 1.5,
              streakDays: 1,
              nextSession: 'Saturday, 17:00 (UZT)',
              contact: {
                telegram: '@' + req.name.toLowerCase().replace(/\s+/g, '_'),
                email: req.name.toLowerCase().replace(/\s+/g, '.') + '@example.uz'
              },
              focusNotes: 'Goal: Practice structured IELTS topic cards together.'
            });

            // Update candidate status
            const cand = state.candidates.find((c) => c.id === req.candidateId);
            if (cand) cand.status = 'accepted';

            state.user.activePartnersCount += 1;
          }
        });

        showToast(`You accepted the study request! Contact details unlocked.`, 'success', 'heart-handshake');
        updateBadgeCounts();
        renderMatches();
      });
    });

    // Decline request
    mainContent.querySelectorAll('[data-action="decline-req"]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const reqId = btn.getAttribute('data-id');
        try { await EduApi.updateMatchRequestStatus(reqId, 'declined'); await EduData.refreshFromBackend(); } catch (err) { showToast(err.message, 'danger', 'alert-circle'); return; }
        EduData.update((state) => {
          const req = state.incomingRequests.find((r) => r.id === reqId);
          if (req) req.status = 'declined';
        });
        showToast('Study request declined.', 'info', 'x');
        updateBadgeCounts();
        renderMatches();
      });
    });

    // Cancel request
    mainContent.querySelectorAll('[data-action="cancel-req"]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const reqId = btn.getAttribute('data-id');
        try { await EduApi.updateMatchRequestStatus(reqId, 'cancelled'); await EduData.refreshFromBackend(); } catch (err) { showToast(err.message, 'danger', 'alert-circle'); return; }
        EduData.update((state) => {
          const req = state.outgoingRequests.find((r) => r.id === reqId);
          if (req) req.status = 'cancelled';
        });
        showToast('Request cancelled.', 'info', 'check');
        renderMatches();
      });
    });

    // Schedule with partner
    mainContent.querySelectorAll('[data-action="schedule-with"]').forEach((btn) => {
      btn.addEventListener('click', () => {
        openScheduleModal(btn.getAttribute('data-id'));
      });
    });

    // Copy contact
    mainContent.querySelectorAll('[data-action="copy-contact"]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const handle = btn.getAttribute('data-contact');
        try {
          navigator.clipboard.writeText(handle);
          showToast(`Copied ${handle} to clipboard!`, 'success', 'check');
        } catch (e) {
          showToast(`Contact: ${handle}`, 'info', 'message-square');
        }
      });
    });

    mainContent.querySelectorAll('[data-action="report"]').forEach((btn) => {
      btn.addEventListener('click', () => openReportModal(btn.getAttribute('data-name')));
    });
  }

  /**
   * Screen 4: Profile and Goals
   */
  function renderProfile() {
    const data = EduData.get();
    const user = data.user;
    const goals = user.goals || [];
    const availability = user.availability || {};

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const timeSlots = [
      { id: 'morning', label: 'Morning\n08:00–11:00' },
      { id: 'afternoon', label: 'Afternoon\n14:00–17:00' },
      { id: 'evening', label: 'Evening\n18:00–21:00' }
    ];

    let totalSelectedSlots = 0;
    days.forEach((d) => {
      timeSlots.forEach((s) => {
        if (availability[`${d}-${s.id}`]) totalSelectedSlots++;
      });
    });

    const html = `
      <div class="page-enter">
        <div class="page-head">
          <div>
            <h1>Profile & study goals</h1>
            <p>Customize your target levels, manage weekly study availability, and protect your privacy.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-secondary" id="btn-add-goal-top">${icon('plus')} Add new goal</button>
          </div>
        </div>

        <div class="profile-layout">
          <!-- Main Form Area -->
          <div class="profile-main">
            <!-- Edit Personal Info Card -->
            <div class="card card-pad">
              <div class="section-head">
                <div>
                  <h2>Personal Information</h2>
                  <p>Your name, city, and study biography</p>
                </div>
              </div>

              <form id="profile-form">
                <div class="form-grid">
                  <div class="field">
                    <label for="prof-name">Full name</label>
                    <input type="text" id="prof-name" class="input" value="${escapeHtml(user.name)}" required>
                  </div>
                  <div class="field">
                    <label for="prof-city">City / Region</label>
                    <input type="text" id="prof-city" class="input" value="${escapeHtml(user.city)}" required>
                  </div>
                </div>

                <div class="form-grid" style="margin-top: 16px;">
                  <div class="field">
                    <label for="prof-email">Email (Private until matched)</label>
                    <input type="email" id="prof-email" class="input" value="${escapeHtml(user.email)}" required>
                  </div>
                  <div class="field">
                    <label for="prof-telegram">Telegram Handle (Revealed upon match)</label>
                    <input type="text" id="prof-telegram" class="input" value="${escapeHtml(user.telegram)}" required>
                  </div>
                </div>

                <div class="field" style="margin-top: 16px;">
                  <label for="prof-bio">Study Bio & Topic Preferences</label>
                  <textarea id="prof-bio" class="input" rows="3">${escapeHtml(user.bio)}</textarea>
                  <small>Share what you want to practice so compatible partners can find you easily.</small>
                </div>

                <div class="form-actions">
                  <button type="submit" class="btn btn-primary">${icon('check')} Save profile changes</button>
                </div>
              </form>
            </div>

            <!-- Study Goals Section -->
            <div class="card card-pad">
              <div class="section-head">
                <div>
                  <h2>Your Study Goals</h2>
                  <p>Track progress and milestones for each subject</p>
                </div>
                <button class="btn btn-sm btn-secondary" id="btn-add-goal">${icon('plus')} Add goal</button>
              </div>

              <div class="goals-list">
                ${goals
                  .map(
                    (g) => `
                  <div class="goal-item">
                    <div class="goal-item-head">
                      <div>
                        <h3>${escapeHtml(g.title)} ${g.isPrimary ? '<span class="badge badge-success">Primary</span>' : ''}</h3>
                        <p>${escapeHtml(g.track)} · Target: <strong>${escapeHtml(g.targetLevel)}</strong> (Starting: ${escapeHtml(g.currentLevel)})</p>
                      </div>
                      <span class="badge badge-info">Deadline: ${escapeHtml(g.deadline)}</span>
                    </div>

                    <div class="goal-progress-meta">
                      <span>Overall progress</span>
                      <strong>${g.progress}%</strong>
                    </div>
                    <div class="progress-track">
                      <span style="width: ${g.progress}%;"></span>
                    </div>

                    <div class="goal-item-foot">
                      <span>${g.sessionsCount} sessions completed · ${g.hoursDone} of ${g.hoursTotal} target hrs</span>
                      <button type="button" data-action="log-study">Log study hours</button>
                    </div>
                  </div>
                `
                  )
                  .join('')}
              </div>
            </div>

            <!-- Weekly Availability Picker -->
            <div class="card card-pad">
              <div class="section-head">
                <div>
                  <h2>Weekly Availability Schedule</h2>
                  <p>Click time slots when you are free for partner study sessions (Tashkent Time UTC+5)</p>
                </div>
                <strong style="color: var(--primary); font-size: 13px;" id="selected-slots-count">${totalSelectedSlots} slots selected (~${totalSelectedSlots * 3} hrs)</strong>
              </div>

              <div class="availability-picker">
                <div class="availability-grid">
                  <div></div>
                  ${days.map((d) => `<div class="day-head">${d}</div>`).join('')}

                  ${timeSlots
                    .map(
                      (s) => `
                    <div class="time-label">${s.label.replace('\n', '<br>')}</div>
                    ${days
                      .map((d) => {
                        const key = `${d}-${s.id}`;
                        const isSelected = !!availability[key];
                        return `<button type="button" class="slot ${isSelected ? 'selected' : ''}" data-slot-key="${key}" aria-label="${d} ${s.id} slot" aria-pressed="${isSelected}"></button>`;
                      })
                      .join('')}
                  `
                    )
                    .join('')}
                </div>
              </div>

              <div class="picker-legend">
                <div class="legend-selected">Selected available slot</div>
                <button class="btn btn-primary btn-sm" id="btn-save-avail">${icon('check')} Save schedule</button>
              </div>
            </div>
          </div>

          <!-- Side Panel -->
          <div class="profile-side">
            <!-- Profile Summary Card -->
            <div class="card profile-summary">
              <span class="avatar avatar-xl ${user.avatarClass}" style="margin: 0 auto 14px;">${user.avatarInitials}</span>
              <h2>${escapeHtml(user.name)}</h2>
              <p>${escapeHtml(user.primaryTrack)}</p>

              <div class="tag-list">
                <span class="badge badge-success">${icon('shield-check')} Verified 16–17 age group</span>
                <span class="badge">${escapeHtml(user.city)}, UZ</span>
              </div>

              <div class="profile-completeness">
                <div>
                  <span>Profile completeness</span>
                  <strong>92%</strong>
                </div>
                <div class="progress-track">
                  <span style="width: 92%;"></span>
                </div>
              </div>
            </div>

            <!-- Safety & Privacy Controls -->
            <div class="card card-pad">
              <div class="section-head">
                <div>
                  <h3>Safety & Privacy</h3>
                  <p>Strict safeguards for students</p>
                </div>
              </div>

              <div class="privacy-list" style="padding: 0;">
                <div class="privacy-row">
                  ${icon('shield-check')}
                  <div>
                    <strong>Age-Group Matching</strong>
                    <small>Matched only with peers aged 16–17</small>
                  </div>
                  <button type="button" class="toggle" role="switch" aria-checked="true" disabled></button>
                </div>

                <div class="privacy-row">
                  ${icon('lock')}
                  <div>
                    <strong>Contact Protection</strong>
                    <small>Hide Telegram until match accepted</small>
                  </div>
                  <button type="button" class="toggle" role="switch" id="toggle-privacy-contact" aria-checked="true"></button>
                </div>

                <div class="privacy-row">
                  ${icon('award')}
                  <div>
                    <strong>Public Study Streak</strong>
                    <small>Show your ${user.studyStreak}-day streak on profile</small>
                  </div>
                  <button type="button" class="toggle" role="switch" id="toggle-privacy-streak" aria-checked="true"></button>
                </div>
              </div>

              <div style="margin-top: 18px;">
                <button type="button" class="btn btn-secondary btn-block btn-sm" data-action="open-safety">${icon('shield')} View safety charter</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    // Form submit
    const profileForm = mainContent.querySelector('#profile-form');
    if (profileForm) {
      profileForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const name = mainContent.querySelector('#prof-name').value.trim();
        const city = mainContent.querySelector('#prof-city').value.trim();
        const email = mainContent.querySelector('#prof-email').value.trim();
        const telegram = mainContent.querySelector('#prof-telegram').value.trim();
        const bio = mainContent.querySelector('#prof-bio').value.trim();

        EduData.update((state) => {
          state.user.name = name;
          state.user.city = city;
          state.user.email = email;
          state.user.telegram = telegram;
          state.user.bio = bio;
        });

        showToast('Profile information successfully saved!', 'success', 'check-circle');
      });
    }

    // Availability slots click handler
    const slotButtons = mainContent.querySelectorAll('.slot');
    const slotsCounter = mainContent.querySelector('#selected-slots-count');

    slotButtons.forEach((slotBtn) => {
      slotBtn.addEventListener('click', () => {
        const isSelected = slotBtn.classList.toggle('selected');
        slotBtn.setAttribute('aria-pressed', isSelected);
        const key = slotBtn.getAttribute('data-slot-key');
        availability[key] = isSelected;

        let total = 0;
        slotButtons.forEach((b) => {
          if (b.classList.contains('selected')) total++;
        });
        if (slotsCounter) {
          slotsCounter.textContent = `${total} slots selected (~${total * 3} hrs)`;
        }
      });
    });

    const saveAvailBtn = mainContent.querySelector('#btn-save-avail');
    if (saveAvailBtn) {
      saveAvailBtn.addEventListener('click', async () => {
        try {
          await EduApi.saveAvailabilitySchedule(availability);
        EduData.update((state) => {
          state.user.availability = availability;
        });
        showToast('Weekly availability schedule saved!', 'success', 'calendar');
        } catch (err) { showToast(err.message || 'Could not save availability', 'danger', 'alert-circle'); }
      });
    }

    // Add goal buttons
    const addGoalBtn = mainContent.querySelector('#btn-add-goal');
    const addGoalTopBtn = mainContent.querySelector('#btn-add-goal-top');
    if (addGoalBtn) addGoalBtn.addEventListener('click', openAddGoalModal);
    if (addGoalTopBtn) addGoalTopBtn.addEventListener('click', openAddGoalModal);

    // Toggles
    const contactToggle = mainContent.querySelector('#toggle-privacy-contact');
    if (contactToggle) {
      contactToggle.addEventListener('click', () => {
        const state = contactToggle.getAttribute('aria-checked') === 'true';
        contactToggle.setAttribute('aria-checked', !state);
        showToast(`Contact privacy ${!state ? 'enabled' : 'disabled'}.`, 'info', 'lock');
      });
    }

    const streakToggle = mainContent.querySelector('#toggle-privacy-streak');
    if (streakToggle) {
      streakToggle.addEventListener('click', () => {
        const state = streakToggle.getAttribute('aria-checked') === 'true';
        streakToggle.setAttribute('aria-checked', !state);
        showToast(`Streak visibility ${!state ? 'visible' : 'hidden'}.`, 'info', 'flame');
      });
    }

    mainContent.querySelectorAll('[data-action="open-safety"]').forEach((btn) => {
      btn.addEventListener('click', openSafetyModal);
    });

    mainContent.querySelectorAll('[data-action="log-study"]').forEach((btn) => {
      btn.addEventListener('click', () => {
        EduData.update((state) => {
          state.user.totalHours += 1;
          state.user.goals[0].hoursDone += 1;
        });
        showToast('Logged +1 study hour!', 'success', 'check-circle');
        renderProfile();
      });
    });
  }

  /**
   * Screen 5: Study Sessions
   */
  function renderSessions() {
    const data = EduData.get();
    const sessions = data.sessions || [];
    const upcoming = sessions.filter((s) => s.status === 'upcoming');
    const completed = sessions.filter((s) => s.status === 'completed');

    const html = `
      <div class="page-enter">
        <div class="page-head">
          <div>
            <h1>Study sessions & reviews</h1>
            <p>Schedule your next session, confirm completed meetings, and build your peer study record.</p>
          </div>
          <div class="page-actions">
            <button class="btn btn-primary" id="btn-schedule-session">${icon('calendar-days')} Schedule session</button>
          </div>
        </div>

        <div class="session-layout">
          <!-- Main List -->
          <div>
            <h2 style="font-size: 17px; margin-bottom: 14px;">Upcoming Sessions (${upcoming.length})</h2>
            ${
              upcoming.length === 0
                ? `
              <div class="card empty-state">
                <div class="empty-icon">${icon('calendar-days')}</div>
                <h3>No upcoming study sessions</h3>
                <p>Plan a session with one of your active study partners.</p>
                <button class="btn btn-primary" id="btn-empty-sched">${icon('calendar-days')} Schedule a session</button>
              </div>
            `
                : `
              <div class="session-list">
                ${upcoming
                  .map(
                    (s) => `
                  <div class="card session-item">
                    <div class="calendar-tile">
                      <span>${escapeHtml(s.monthStr)}</span>
                      <strong>${escapeHtml(s.dayNum)}</strong>
                    </div>

                    <div>
                      <h2>${escapeHtml(s.topic)}</h2>
                      <p>With <strong>${escapeHtml(s.partnerName)}</strong> (${escapeHtml(s.track)}) · <strong>${escapeHtml(s.format)}</strong></p>
                      <div class="session-time">
                        ${icon('clock')}
                        <span>${escapeHtml(s.date)} · ${escapeHtml(s.time)}</span>
                      </div>
                    </div>

                    <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">
                      ${
                        s.canConfirmComplete
                          ? `<button class="btn btn-primary btn-sm" data-action="confirm" data-id="${s.id}">${icon('check-circle')} Confirm completed</button>`
                          : `<a href="${escapeHtml(s.link)}" target="_blank" class="btn btn-secondary btn-sm">${icon('video')} Open link</a>`
                      }
                      <button class="btn btn-secondary btn-sm" data-action="reschedule" data-id="${s.id}">Reschedule</button>
                    </div>
                  </div>
                `
                  )
                  .join('')}
              </div>
            `
            }

            <h2 style="font-size: 17px; margin: 32px 0 14px;">Completed Sessions & Peer Reviews (${completed.length})</h2>
            <div class="session-list">
              ${completed
                .map(
                  (s) => `
                <div class="card session-item">
                  <div class="calendar-tile">
                    <span>${escapeHtml(s.monthStr)}</span>
                    <strong>${escapeHtml(s.dayNum)}</strong>
                  </div>

                  <div>
                    <h2>${escapeHtml(s.topic)}</h2>
                    <p>Studied with <strong>${escapeHtml(s.partnerName)}</strong> (${escapeHtml(s.track)})</p>
                    <div class="session-time">
                      <span class="badge badge-success">${icon('check-circle')} Completed & Confirmed</span>
                      <span>${escapeHtml(s.date)}</span>
                    </div>

                    ${
                      s.review
                        ? `
                      <div class="review-stars" style="margin: 8px 0 4px;">
                        ${Array.from({ length: 5 })
                          .map((_, i) => (i < s.review.stars ? icon('star') : '☆'))
                          .join('')}
                      </div>
                      <blockquote style="margin: 0; color: var(--muted); font-size: 12px; font-style: italic;">"${escapeHtml(s.review.comment)}"</blockquote>
                    `
                        : ''
                    }
                  </div>

                  <span class="badge badge-info" style="align-self: center;">+1 hr logged</span>
                </div>
              `
                )
                .join('')}
            </div>
          </div>

          <!-- Sidebar Tips -->
          <div class="session-side">
            <div class="card session-tip">
              <span class="badge badge-success">${icon('sparkles')} Best Practices</span>
              <h3>4 rules for a high-yield study session</h3>
              <p>How top pairs maintain momentum and reach high scores:</p>
              <ol>
                <li><strong>Agree on the agenda</strong> during the first 5 minutes.</li>
                <li><strong>Enforce a strict timer</strong> for speaking tasks or math drills.</li>
                <li><strong>Give honest, kind feedback</strong> on vocabulary or solution steps.</li>
                <li><strong>Confirm completion immediately</strong> to lock in your study streak.</li>
              </ol>
            </div>

            <div class="card review-card">
              <div class="section-head" style="margin-bottom: 0;">
                <div>
                  <h3>Recent review received</h3>
                </div>
              </div>
              <div class="review-stars">
                ${icon('star')}${icon('star')}${icon('star')}${icon('star')}${icon('star')}
              </div>
              <blockquote>"Madina is punctual, highly disciplined with speaking timers, and gives great constructive feedback on Part 3 answers!"</blockquote>
              <div class="review-person">
                <span class="avatar avatar-sm avatar-aziza">AU</span>
                <span>Aziza Usmanova · IELTS Partner</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    const schedBtn = mainContent.querySelector('#btn-schedule-session');
    const emptySchedBtn = mainContent.querySelector('#btn-empty-sched');
    if (schedBtn) schedBtn.addEventListener('click', () => openScheduleModal());
    if (emptySchedBtn) emptySchedBtn.addEventListener('click', () => openScheduleModal());

    mainContent.querySelectorAll('[data-action="confirm"]').forEach((btn) => {
      btn.addEventListener('click', () => openConfirmSessionModal(btn.getAttribute('data-id')));
    });

    mainContent.querySelectorAll('[data-action="reschedule"]').forEach((btn) => {
      btn.addEventListener('click', () => {
        openScheduleModal();
      });
    });
  }

  /**
   * Screen 6: Landing, Login, and Register
   */
  function renderLanding() {
    const html = `
      <div class="landing page-enter">
        <header class="landing-nav">
          <a class="brand" href="#/landing">
            <span class="brand-mark" aria-hidden="true"><span></span><span></span></span>
            <span>EduMate</span>
          </a>

          <div class="landing-links">
            <a href="#/partners">Find Partners</a>
            <a href="#/sessions">How Sessions Work</a>
            <a href="#/profile">Safety Standards</a>
          </div>

          <div class="landing-actions">
            <a href="#/login" class="btn btn-secondary btn-sm">Sign in</a>
            <a href="#/dashboard" class="btn btn-primary btn-sm">${icon('arrow-right')} Open App</a>
          </div>
        </header>

        <section class="landing-hero">
          <div class="landing-copy">
            <div class="landing-pill">
              <span>Verified peer study network in Uzbekistan</span>
            </div>
            <h1>Find your ideal study partner. <em>Reach your goal.</em></h1>
            <p>Connect with vetted students in your exact age group preparing for IELTS, SAT, and coding. Study together in structured sessions, stay accountable, and turn mutual goals into real results.</p>

            <div class="landing-cta">
              <a href="#/dashboard" class="btn btn-primary btn-lg">${icon('users')} Start studying together</a>
              <a href="#/login" class="landing-text-link">Sign in to your account ${icon('chevron-right')}</a>
            </div>

            <div class="landing-proof">
              <div class="avatar-stack">
                <span class="avatar avatar-sm avatar-jasur">JR</span>
                <span class="avatar avatar-sm avatar-nilufar">NK</span>
                <span class="avatar avatar-sm avatar-aziza">AU</span>
                <span class="avatar avatar-sm avatar-temur">TA</span>
              </div>
              <span>Joined by <strong>1,200+ students</strong> across Tashkent, Samarkand & Bukhara</span>
            </div>
          </div>

          <div class="landing-visual">
            <div class="visual-blob"></div>

            <!-- Preview Card -->
            <div class="match-preview">
              <div class="preview-head">
                <strong>High compatibility match</strong>
                <span class="badge badge-success">96% match</span>
              </div>

              <div class="preview-person">
                <span class="avatar avatar-lg avatar-jasur">JR</span>
                <div>
                  <h3>Jasur Rakhimov</h3>
                  <p>IELTS Speaking · 16–17 · Tashkent</p>
                </div>
              </div>

              <div class="preview-divider"></div>

              <div class="preview-row">
                ${icon('target')}
                <span>Target: <strong>Band 7.5 (C1)</strong></span>
              </div>
              <div class="preview-row">
                ${icon('clock')}
                <span>Mon, Wed, Fri · Evening (19:00–21:00)</span>
              </div>

              <div class="preview-tags">
                <span class="badge">Part 2 & 3</span>
                <span class="badge">Lexical Focus</span>
              </div>

              <a href="#/dashboard" class="btn btn-primary btn-sm">${icon('send')} Connect & practice together</a>
            </div>

            <div class="floating-note">
              <span>${icon('award')}</span>
              <div>
                <strong>12-day study streak</strong>
                <small>+4.5 hours completed this week</small>
              </div>
            </div>
          </div>
        </section>

        <!-- Benefits -->
        <section class="landing-benefits">
          <div class="benefits-head">
            <div>
              <h2>Engineered for real learning, not endless scrolling.</h2>
            </div>
            <p>Traditional study groups fall apart because of mismatched goals and unreliable schedules. EduMate solves this with purposeful matching and dual confirmation.</p>
          </div>

          <div class="benefit-grid">
            <div class="benefit">
              <span>${icon('target')}</span>
              <h3>Goal & Track Overlap</h3>
              <p>Match with students targeting the exact same score or syllabus (IELTS Speaking, SAT Math, Python) with compatible free hours.</p>
            </div>

            <div class="benefit">
              <span>${icon('shield-check')}</span>
              <h3>Safe Age Isolation</h3>
              <p>Strict peer isolation for learners under 18. Contact details remain hidden until both study partners explicitly agree to match.</p>
            </div>

            <div class="benefit">
              <span>${icon('check-circle')}</span>
              <h3>Dual Session Accountability</h3>
              <p>Sessions and streaks are only recorded when both partners confirm the meeting happened, keeping everyone honest and motivated.</p>
            </div>
          </div>
        </section>

        <!-- Footer -->
        <footer class="landing-footer">
          <span>EduMate Prototype — Designed for students in Uzbekistan. 100% offline enabled.</span>
          <div>
            <a href="#/dashboard" style="color: #ffffff; font-weight: 700; margin-right: 18px;">Open Demo App</a>
            <button id="btn-reset-demo" style="color: #94afa2; text-decoration: underline; background: none; border: none; cursor: pointer;">Reset demo data</button>
          </div>
        </footer>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    const resetBtn = mainContent.querySelector('#btn-reset-demo');
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        EduData.reset();
        showToast('Demo data restored to initial state', 'info', 'check');
        renderLanding();
      });
    }
  }

  function renderLogin() {
    const html = `
      <div class="auth-page page-enter">
        <div class="auth-panel">
          <a class="brand" href="#/landing" style="margin-bottom: 24px;">
            <span class="brand-mark" aria-hidden="true"><span></span><span></span></span>
            <span>EduMate</span>
          </a>

          <div class="auth-form-wrap">
            <h1>Welcome back</h1>
            <p>Sign in to continue your study sessions</p>

            <form class="auth-form" id="login-form">
              <div class="field">
                <label for="login-email">Email address</label>
                <input type="email" id="login-email" class="input" value="madina@example.com" required autocomplete="email">
              </div>

              <div class="field">
                <label for="login-password">Password</label>
                <div class="password-wrap">
                  <input type="password" id="login-password" class="input" value="password123" required>
                  <button type="button" id="toggle-pw" aria-label="Toggle password visibility">${icon('eye')}</button>
                </div>
              </div>

              <button type="submit" class="btn btn-primary btn-block">${icon('arrow-right')} Sign in</button>
            </form>

            <div class="auth-divider">DEMO ACCESS</div>

            <button type="button" class="btn btn-secondary btn-block" id="btn-fast-demo">${icon('sparkles')} Instant Sign In as Madina (Student)</button>

            <p class="auth-switch">
              Don't have an account? <a href="#/register">Sign up for free</a>
            </p>
          </div>
        </div>

        <div class="auth-visual">
          <div class="auth-quote">
            <div class="quote-icon">${icon('heart-handshake')}</div>
            <h2>"Studying alone was exhausting. With my partner Aziza, we practiced IELTS every evening and both got Band 7.5!"</h2>
            <div class="auth-quote-person">
              <span class="avatar avatar-aziza">AU</span>
              <div>
                <strong>Aziza & Madina</strong>
                <small>IELTS Speaking study pair · Tashkent</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    const pwInput = mainContent.querySelector('#login-password');
    const toggleBtn = mainContent.querySelector('#toggle-pw');
    if (toggleBtn && pwInput) {
      toggleBtn.addEventListener('click', () => {
        const isPw = pwInput.type === 'password';
        pwInput.type = isPw ? 'text' : 'password';
        toggleBtn.innerHTML = icon(isPw ? 'eye-off' : 'eye');
      });
    }

    const form = mainContent.querySelector('#login-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        try {
          const email = mainContent.querySelector('#login-email').value.trim();
          const password = mainContent.querySelector('#login-password').value;
          await EduApi.login(email, password);
          await EduData.refreshFromBackend();
          showToast('Signed in successfully!', 'success', 'check-circle');
          window.location.hash = '#/dashboard';
        } catch (err) { showToast(err.message || 'Unable to sign in', 'danger', 'alert-circle'); }
      });
    }

    const demoBtn = mainContent.querySelector('#btn-fast-demo');
    if (demoBtn) {
      demoBtn.addEventListener('click', async () => {
        try {
          await EduApi.login('demo0@edumate.demo', 'demo12345');
          await EduData.refreshFromBackend();
          showToast('Welcome to the demo!', 'success', 'sparkles');
          window.location.hash = '#/dashboard';
        } catch (err) { showToast(err.message || 'Unable to sign in', 'danger', 'alert-circle'); }
      });
    }
  }

  function renderRegister() {
    const html = `
      <div class="auth-page page-enter">
        <div class="auth-panel">
          <a class="brand" href="#/landing" style="margin-bottom: 24px;">
            <span class="brand-mark" aria-hidden="true"><span></span><span></span></span>
            <span>EduMate</span>
          </a>

          <div class="auth-form-wrap">
            <h1>Create your account</h1>
            <p>Join the verified student study network</p>

            <form class="auth-form" id="register-form">
              <div class="field">
                <label for="reg-name">Full name</label>
                <input type="text" id="reg-name" class="input" placeholder="e.g. Jasur Rakhimov" value="Madina Azimova" required>
              </div>

              <div class="field-row">
                <div class="field">
                  <label for="reg-age">Age</label>
                  <input type="number" id="reg-age" class="input" value="17" min="14" max="25" required>
                </div>
                <div class="field">
                  <label for="reg-city">City</label>
                  <input type="text" id="reg-city" class="input" value="Tashkent" required>
                </div>
              </div>

              <div class="field">
                <label for="reg-track">Primary study track</label>
                <select id="reg-track" class="input">
                  <option value="IELTS Speaking">IELTS Speaking</option>
                  <option value="SAT Math">SAT Math</option>
                  <option value="Python">Python & Web Dev</option>
                  <option value="General English">General English</option>
                </select>
              </div>

              <div class="field">
                <label for="reg-email">Email address</label>
                <input type="email" id="reg-email" class="input" value="madina@example.com" required>
              </div>

              <div class="field">
                <label for="reg-password">Password</label>
                <input type="password" id="reg-password" class="input" value="password123" required>
              </div>

              <button type="submit" class="btn btn-primary btn-block">${icon('arrow-right')} Create Account</button>
            </form>

            <p class="auth-switch">
              Already have an account? <a href="#/login">Sign in here</a>
            </p>
          </div>
        </div>

        <div class="auth-visual">
          <div class="auth-quote">
            <div class="quote-icon">${icon('shield-check')}</div>
            <h2>Safe. Focused. Verified.</h2>
            <p>We believe every motivated student in Uzbekistan deserves a reliable partner who shows up, studies hard, and keeps them moving forward.</p>
          </div>
        </div>
      </div>
    `;

    mainContent.innerHTML = html;
    hydrateIcons(mainContent);

    const form = mainContent.querySelector('#register-form');
    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        showToast('Account created! Welcome to EduMate.', 'success', 'check-circle');
        window.location.hash = '#/dashboard';
      });
    }
  }

  /* ==========================================================================
     7. ROUTER AND SHELL MANAGEMENT
     ========================================================================== */

  const ROUTES = {
    dashboard: { render: renderDashboard, title: 'EduMate — Dashboard', isAuth: false },
    partners: { render: renderPartners, title: 'EduMate — Find study partners', isAuth: false },
    matches: { render: renderMatches, title: 'EduMate — Requests & matches', isAuth: false },
    sessions: { render: renderSessions, title: 'EduMate — Study sessions', isAuth: false },
    profile: { render: renderProfile, title: 'EduMate — Profile & goals', isAuth: false },
    landing: { render: renderLanding, title: 'EduMate — Better, together', isAuth: true },
    login: { render: renderLogin, title: 'EduMate — Sign in', isAuth: true },
    register: { render: renderRegister, title: 'EduMate — Create account', isAuth: true }
  };

  function getCurrentRouteKey() {
    const hash = window.location.hash.replace(/^#\/?/, '').trim();
    return hash || 'dashboard';
  }

  function renderCurrentRoute() {
    const routeKey = getCurrentRouteKey();
    const route = ROUTES[routeKey] || ROUTES['dashboard'];

    document.title = route.title;

    // Toggle auth-mode on shell
    if (route.isAuth) {
      appEl.classList.add('auth-mode');
    } else {
      appEl.classList.remove('auth-mode');
    }

    // Update active nav links
    document.querySelectorAll('[data-route-link]').forEach((link) => {
      const target = link.getAttribute('data-route-link');
      if (target === routeKey) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
      } else {
        link.classList.remove('active');
        link.removeAttribute('aria-current');
      }
    });

    closeSidebar();
    closeAllPopovers();

    // Render screen
    route.render();

    // Update badges
    updateBadgeCounts();

    // Scroll top
    window.scrollTo({ top: 0, behavior: 'auto' });
  }

  // Hash change listener
  window.addEventListener('hashchange', renderCurrentRoute);

  // Initialize on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    hydrateIcons(document.body);
    updateBadgeCounts();
    renderCurrentRoute();
  });

  // Fallback if DOM already loaded
  if (document.readyState !== 'loading') {
    hydrateIcons(document.body);
    updateBadgeCounts();
    renderCurrentRoute();
  }
})();
