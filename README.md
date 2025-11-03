# Serene Site

This project now includes a lunar phase experience for quickly exploring the moon's cycle.

## Lunar Widget
- `src/lib/moon.js` exposes `getMoonPhase(date)` and `nextFullMoon(fromDate)` helpers.
- `src/components/LunarWidget.jsx` renders the current phase and lets you step through days.
- The widget is mounted from `src/main.js`.

## Setup
1. Install dependencies: `npm install`
2. Start the dev server: `npm run dev`
3. Run tests: `npm test`

Vitest powers the test suite; see `tests/moon.test.js` for an example.
