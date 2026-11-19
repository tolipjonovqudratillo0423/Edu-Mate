# Current State Assessment (STATE.md)

## What Earlier Agents Did
- Built Django backend (models, DRF views, JWT auth, matching algorithms, seed commands).
- Began connecting vanilla JS frontend: introduced `js/api.js` client, updated `js/data.js` and `js/app.js` to call backend endpoints.
- Added "In development" placeholders for unbacked features (sessions, reviews, stats, registration, profile editing).
- Added `seed_demo` management command for demo accounts (`demo0`–`demo4`).

## What Is Half-Finished
- Onboarding & Navigation: onboarding flow partially wired, redirects to profile instead of dashboard; route handling on page refresh is fragile.
- Token refresh: refresh logic in `api.js` had race conditions and retry issues on 401.
- Frontend-backend data syncing: goals, availability, partner discovery, and match request lifecycle are partially integrated.
- Demo seeding: `seed_demo` did not set `is_verified` or `is_onboarded`, and `demo0` lacked initial goal seeds.

## What Looks Broken
- `requirements.txt` is encoded as UTF-16 LE with CRLF line endings, which breaks Linux tools/pip.
- CORS configuration in `settings.py` was missing frontend origin `http://localhost:8001`.
- API response unwrapping and error formats differ between backend (`{status, message, data}`) and frontend expectations.
- Field name mismatches: match request status (`canceled` vs `cancelled`), goal/track parameters (`track` vs track object/id).
- Windows crash left uncommitted changes and unverified commits.
