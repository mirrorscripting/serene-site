# Agent Notes

- Lunar calculations live in `src/lib/moon.js`. Both helpers accept native `Date` instances (or anything the `Date` constructor accepts).
- `src/components/LunarWidget.jsx` returns a DOM node; mount it by appending the result to any container.
- Tests rely on Vitest (`npm test`). Add new specs under `tests/`.
- Keep the project as an ES module (`package.json` defines `"type": "module"`). Use ES imports/exports everywhere.
