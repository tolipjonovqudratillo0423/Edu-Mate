# INTEGRATION_NOTES

Goal: connect frontend/ (vanilla JS, offline, localStorage) to the Django backend (edumate/).
Backend response wrapper everywhere: {status: bool, message, data}. Errors: status=false, data=errors.

## Backend endpoints (JWT Bearer on everything except auth)
- POST /auth/register/  req: email, first_name, last_name, password, password2. 201, user only, NO tokens.
- POST /auth/login/  req: email, password. data: {tokens: {access, refresh}, user}.
- POST /auth/refresh-token/  req: {refresh}.
- GET /users/about-me/ (User), GET|PUT /users/profile/ (Profile: full_name, city, bio, is_hidden, age_group; email and telegram_username belong to User, not Profile).
- GET|POST /availability/, DELETE /availability/<id>/ (PATCH/PUT per spec, verify). Item: {id, weekday 0..6 (Mon=0), slot: morning|afternoon|evening}.
- GET|POST /goals/, GET|PATCH|PUT|DELETE /goals/<id>/. Fields: track (id), track_name, track_slug, current_level 1..5, target_level 1..5, current_score, target_score, deadline YYYY-MM-DD, weekly_hours 1..40. No title/progress/hoursDone.
- GET /partners/?track=<id>  (track REQUIRED, else 400). Item: full_name, city, age_group, track, goal fields, availability [{weekday, slot}], score (int 0..8).
- POST /match-requests/  req: {to_user (user id), track (id), message}.
- GET /match-requests/?box=sent|received (default received). Item: id, from_user(+_name), to_user(+_name), track(+_name), message, status, responded_at.
- PATCH /match-requests/<id>/  body {status: accepted|declined} (recipient, one time only; accepted creates Match) or {status: canceled} (sender, one l).
- GET /mates/?status=active|ended; DELETE /mates/<id>/ ends it. Item: id, full_name, city, track, track_name, status, created_date. No contacts yet.
- Session and Review: models exist, NO endpoints.

## Frontend facts
- No network layer at all. State in window.EduData + localStorage key 'edumate_data_v1' (js/data.js). Login/register only switch to #dashboard.
- Register sends: name, age, city, track, email, password. Profile form: name, city, email, telegram, bio; user also has ageGroup ("16-17"), studyStreak, sessionsCompleted.
- Availability: object {"Mon-evening": true, ...}.
- Goal: {title, track "IELTS Speaking", current "Band 6.0", target "Band 7.5", deadline "Dec 2026", hours; plus progress, hoursDone}.
- Partners: {id "cand-jasur", name, ageGroup, city, track, level, target, compatibility %, availability string}; fetched globally without track.
- Requests: incomingRequests / outgoingRequests {id, candidateId, name, track, message, status}; frontend status "cancelled" vs backend "canceled".
- Active pairs: {id, partnerId, name, track, city, contact{telegram,email}, sessionsTogether, hoursTogether, streakDays}.
- Sessions/reviews: local state only (renderSessions, openScheduleModal).

## Cross-cutting issues
- CORS: corsheaders was commented out in settings.py (app, middleware, CORS_ALLOWED_ORIGINS). Needed for any browser origin.
- JWT: tokens must be stored, Bearer header added, on 401 refresh once via /auth/refresh-token/ then retry or go to login. Unwrap {status, message, data}.

## Previous agent progress (stopped by quota; NOTHING was run or tested)
Backend edited: settings.py (django-cors-headers installed and configured), serializers.py (2 edits), views.py, urls.py (one created, one edited); tracks seeded in DB via seed-tracks.
Frontend edited: created js/api.js and js/mock-data.js; edited js/data.js, index.html, js/app.js (one big edit pass).
It was reading api.js and data.js again (verification) when it stopped. Treat all of the above as UNVERIFIED: read it, fix it, finish it.

END OF NOTES

## REMAINING
- Step A seed_demo command was added but not run or validated; confirm model field names before use.
- Steps B–E remain: backend login flow and state loading; goal/availability persistence; partner/request/mate actions; in-development badges.
