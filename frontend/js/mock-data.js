/**
 * EduMate — Isolated Static Mock Data for Features in Development
 *
 * NOTE: These features (Sessions, Reviews, Notifications, Weekly Activity Chart)
 * do not have backend endpoints yet. All mock data is strictly isolated in this
 * single file so it can be easily located and removed when backend endpoints are ready.
 */

(function () {
  'use strict';

  window.EduMockData = {
    weeklyActivity: [
      { day: 'Mon', hours: 1.5, heightPct: 50 },
      { day: 'Tue', hours: 2.0, heightPct: 67 },
      { day: 'Wed', hours: 1.0, heightPct: 33 },
      { day: 'Thu', hours: 2.5, heightPct: 83, isToday: true },
      { day: 'Fri', hours: 1.5, heightPct: 50 },
      { day: 'Sat', hours: 3.0, heightPct: 100 },
      { day: 'Sun', hours: 0.5, heightPct: 17 }
    ],

    sessions: [
      {
        id: 'sess-1',
        partnerId: 2,
        partnerName: 'Aziza Usmanova',
        partnerAvatar: 'avatar-aziza',
        partnerInitials: 'AU',
        topic: 'IELTS Speaking Part 2 Cue Cards: Tech & Climate Change',
        date: 'Tomorrow (Oct 30)',
        time: '17:00 – 18:00 (UZT)',
        dayNum: '30',
        monthStr: 'OCT',
        format: 'Google Meet',
        link: 'https://meet.google.com/edu-mate-talk',
        status: 'upcoming',
        canConfirmComplete: true,
        track: 'IELTS Speaking',
        partnerContact: '@aziza_study'
      },
      {
        id: 'sess-2',
        partnerId: 3,
        partnerName: 'Ali Mirzaev',
        partnerAvatar: 'avatar-ali',
        partnerInitials: 'AM',
        topic: 'SAT Math: Timed Hard Practice Questions Set 4',
        date: 'Saturday, Oct 31',
        time: '15:00 – 16:30 (UZT)',
        dayNum: '31',
        monthStr: 'OCT',
        format: 'Telegram Audio & Screen Share',
        link: 'https://t.me/ali_math_uz',
        status: 'upcoming',
        canConfirmComplete: false,
        track: 'SAT Math',
        partnerContact: '@ali_math_uz'
      },
      {
        id: 'sess-3',
        partnerId: 2,
        partnerName: 'Aziza Usmanova',
        partnerAvatar: 'avatar-aziza',
        partnerInitials: 'AU',
        topic: 'IELTS Speaking Part 3: Global Economic Trends',
        date: 'Oct 25, 2026',
        time: '17:00 – 18:00 (UZT)',
        dayNum: '25',
        monthStr: 'OCT',
        format: 'Google Meet',
        status: 'completed',
        track: 'IELTS Speaking',
        review: {
          stars: 5,
          comment: 'Super productive 1-hour speaking drill! Covered 4 Part 3 questions with constructive vocabulary feedback.',
          reviewer: 'Madina Azimova'
        }
      },
      {
        id: 'sess-4',
        partnerId: 3,
        partnerName: 'Ali Mirzaev',
        partnerAvatar: 'avatar-ali',
        partnerInitials: 'AM',
        topic: 'SAT Math: Quadratic Equations and Graph Transformation',
        date: 'Oct 22, 2026',
        time: '18:30 – 19:45 (UZT)',
        dayNum: '22',
        monthStr: 'OCT',
        format: 'Telegram Audio',
        status: 'completed',
        track: 'SAT Math',
        review: {
          stars: 5,
          comment: 'Great peer problem solving. We figured out 3 tricky question types from past official tests.',
          reviewer: 'Madina Azimova'
        }
      }
    ],

    notifications: [
      {
        id: 'notif-1',
        title: 'New match request',
        text: 'Nilufar Karimova sent you a study partner request for IELTS Speaking.',
        time: '2 hours ago',
        unread: true,
        route: 'matches'
      },
      {
        id: 'notif-2',
        title: 'Session confirmed',
        text: 'Aziza Usmanova confirmed your upcoming session for IELTS Part 2 drills.',
        time: 'Yesterday',
        unread: true,
        route: 'sessions'
      },
      {
        id: 'notif-3',
        title: 'Weekly milestone reached',
        text: 'You completed 12.5 study hours this week, exceeding your goal by 15%!',
        time: '2 days ago',
        unread: true,
        route: 'dashboard'
      }
    ]
  };
})();
