# EduMate design direction

## Concept: quiet momentum

EduMate should feel like a calm, capable study companion rather than a social feed. The interface combines the clarity of a productivity dashboard with the warmth of a learning product. The primary job is always visible: find a compatible partner, make a plan, and complete the next session.

## References

- **Material Design 3:** navigation drawer behavior, single-topic cards, clear top-bar actions, and short transitions that preserve spatial context.
- **Material motion guidance:** eased entrances and exits, responsive feedback, and motion that explains changes rather than decorating them.
- **shadcn/ui patterns:** composable sidebar, dialog, dropdown, skeleton, and form conventions; strong keyboard behavior and visible state.
- **Linear / Stripe Dashboard:** restrained density, strong typography, clear data hierarchy, and purposeful hover feedback.
- **Google Classroom / Duolingo:** friendly learning language, visible progress, and achievable next steps without turning the experience into a game.

## Palette

- Canvas: warm mist `#F5F7F4`; surfaces: white.
- Ink: deep slate-green `#172A25`; secondary text: muted sage-gray.
- Brand: evergreen `#173F35`; action: emerald `#287A60`.
- Accent: apricot `#F2B879`, used sparingly for highlights and momentum.
- Semantic colors are separate from brand colors: blue for information, green for success, amber for warning, red for destructive actions.
- Dark mode uses blue-green charcoal surfaces rather than pure black, with raised borders and adjusted semantic contrast.

## Typography

A system-first sans stack keeps the prototype fast and works offline. Page titles use a tight 30–36 px scale, section titles 18–22 px, body 14–16 px, and labels 12–13 px. Numeric stats use tabular figures. Weight and spacing—not excessive size—establish hierarchy.

## Spacing and shape

The base spacing unit is 4 px. Common gaps are 12, 16, 24, and 32 px. Cards use 16–20 px radii, controls 10–12 px, and pills use fully rounded corners. Borders are soft but visible; shadows are reserved for floating layers and key progress surfaces.

## Layout

- Desktop: fixed 248 px sidebar, sticky top bar, fluid content with a 1440 px reading ceiling.
- Tablet: compact spacing and two-column content where space permits.
- Mobile below 900 px: off-canvas drawer, scrim, 56 px touch-friendly header, single-column content, and no content reflow underneath the drawer.
- Every interactive element has a visible focus ring and a minimum practical pointer target.

## Motion

Standard transitions last 160–240 ms with an ease-out curve. Drawers and modals preserve entry/exit direction. Progress rings animate once on entry; count-ups reinforce new information. Toasts, accept states, and session confirmation provide concise feedback. `prefers-reduced-motion: reduce` disables nonessential animation and smooth scrolling.

## Safety and trust

Age-group matching, hidden contact details, reporting, and blocking are visible product behaviors. Destructive actions require confirmation and use direct, nonjudgmental language. Contact details appear only in an accepted, active match.

## File structure

```text
index.html              App shell and accessible overlay roots
css/styles.css          Tokens, responsive layout, components, motion
js/data.js              Fictional people, goals, sessions, requests, activity
js/app.js               Hash router, screen templates, state, interactions
screenshots/            Desktop and mobile evidence for every screen
tests/                  Optional browser verification script
DESIGN.md               This design rationale
TEST_REPORT.md          Responsive and interaction test results
```
