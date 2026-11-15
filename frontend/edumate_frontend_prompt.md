# EduMate frontend prototype: prompt for the coding agent

Paste everything below the line into the agent. Attach nothing else.

---

You are a senior product designer and front-end engineer. Build a modern, polished, fully working front-end prototype of a web app called **EduMate**. You decide the design direction, layout, typography, color and motion. Research current, well-documented dashboard design practice first (for example Material Design 3 and its motion guidelines, Apple Human Interface Guidelines, Radix/shadcn-style component patterns, and how products like Linear, Stripe Dashboard, Notion, Google Classroom and Duolingo handle layout, hierarchy and micro-interactions). Choose one coherent direction, then write a short `DESIGN.md` explaining the choices (palette, type scale, spacing, motion principles, and which references you used). Prefer proven, widely used patterns over trends.

## What EduMate is
A platform for students and young developers in Uzbekistan to find a study partner with the same goal. Users pick a **track** (IELTS Speaking, SAT Math, Python, and similar), describe their **goal** (current level, target level, deadline, hours per week) and **availability** (days and time slots). The app suggests compatible people, the user sends a **match request**, the other person accepts, and the pair studies together in **sessions**. After a session both people confirm it happened and leave a short **review**. The key success metric is how many pairs actually study together. Many users are under 18, so safety is part of the product: users can **block** and **report** others, people are matched only inside their age group, and contact details are revealed only after a request is accepted.

## What to build
A single-page prototype in plain HTML, CSS and vanilla JavaScript (you may load fonts, icons and small libraries from a CDN if you think they improve the result). It uses realistic hardcoded data only. Use fictional Uzbek and international names and generated avatars (initials on gradients or inline SVG), never real people. The interface language is English.

Screens (navigate between them without a page reload):
1. **Dashboard**: greeting, goal progress, suggested partners, upcoming sessions, activity stats
2. **Find partners**: search and filters (track, level, availability), candidate cards with a compatibility score and a Connect action
3. **Requests and matches**: incoming, outgoing, active pairs, with accept/decline interactions
4. **Profile and goals**: edit profile, create and edit goals, weekly availability picker
5. **Session**: schedule and confirm a session, then leave a review
6. **Landing, login and register**

Shared pieces you should design well: sidebar navigation, top bar (search, notifications, profile menu), empty states, loading states, toasts, modals for Connect and Report/Block.

## Motion and feel
Make it feel alive and premium: purposeful micro-interactions, smooth page and panel transitions, animated progress rings and number count-ups, hover and press feedback, skeleton loading, and satisfying accept/confirm moments. Motion should clarify what is happening, not decorate. Respect `prefers-reduced-motion`. A light and dark theme with a toggle is a welcome bonus.

## It must actually work (non-negotiable)
These are acceptance criteria, not design limits:
- Opens by double-clicking `index.html`, with no build step and no server.
- Every nav item, button, menu, modal, tab and form control that appears on screen does something sensible.
- Sidebar and top bar work on desktop and mobile. On small screens the sidebar becomes a drawer with a working toggle, closes on outside click and Escape, and never overlaps content incorrectly.
- No horizontal scrolling and no broken layout at 375, 768, 1024 and 1440 px widths.
- No console errors. Keyboard navigation and visible focus states work; contrast is readable.
- Code is organized in clear files and folders and commented so a student can read it and explain how the sidebar, routing and animations work.

## How to work
1. Plan first: write the design direction and the file structure.
2. Build the app shell (layout, sidebar, top bar, routing, theme) and **verify it in a browser at all four widths, including the mobile drawer**, before building any screen. Fix what is broken.
3. Build the screens one by one, testing each in the browser as you go.
4. Finish with a full pass: click through every interaction at all four widths and fix everything that fails.
5. Save screenshots of every screen at desktop (1440 px) and mobile (375 px) into a `screenshots/` folder, and give me a short report of what you tested and what you found and fixed.
