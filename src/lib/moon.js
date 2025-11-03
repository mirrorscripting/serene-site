const SYNODIC_MONTH = 29.53058867; // Average length of a lunar cycle in days
const BASE_NEW_MOON = Date.UTC(2000, 0, 6, 18, 14); // Known new moon reference

const PHASES = [
  { name: 'New Moon', start: 0, end: 1.84566, emoji: '🌑' },
  { name: 'Waxing Crescent', start: 1.84566, end: 5.53699, emoji: '🌒' },
  { name: 'First Quarter', start: 5.53699, end: 9.22831, emoji: '🌓' },
  { name: 'Waxing Gibbous', start: 9.22831, end: 12.91963, emoji: '🌔' },
  { name: 'Full Moon', start: 12.91963, end: 16.61096, emoji: '🌕' },
  { name: 'Waning Gibbous', start: 16.61096, end: 20.30228, emoji: '🌖' },
  { name: 'Last Quarter', start: 20.30228, end: 23.99361, emoji: '🌗' },
  { name: 'Waning Crescent', start: 23.99361, end: 27.68493, emoji: '🌘' },
  { name: 'New Moon', start: 27.68493, end: SYNODIC_MONTH, emoji: '🌑' }
];

function normalizeDate(input) {
  if (input instanceof Date) {
    return new Date(input);
  }

  if (typeof input === 'number') {
    return new Date(input);
  }

  if (typeof input === 'string') {
    return new Date(input);
  }

  throw new Error('Invalid date provided');
}

function getMoonAge(date) {
  const ms = normalizeDate(date).getTime();
  const diff = (ms - BASE_NEW_MOON) / 86400000; // convert to days
  const age = diff % SYNODIC_MONTH;
  return age < 0 ? age + SYNODIC_MONTH : age;
}

export function getMoonPhase(date = new Date()) {
  const age = getMoonAge(date);
  const illumination = (1 - Math.cos((2 * Math.PI * age) / SYNODIC_MONTH)) / 2;
  const phase = PHASES.find((entry) => age >= entry.start && age < entry.end) ?? PHASES[0];

  return {
    age,
    illumination,
    name: phase.name,
    emoji: phase.emoji
  };
}

export function nextFullMoon(fromDate = new Date()) {
  const date = normalizeDate(fromDate);
  const age = getMoonAge(date);
  const fullMoonAge = SYNODIC_MONTH / 2;

  let daysUntil = fullMoonAge - age;
  if (daysUntil <= 0) {
    daysUntil += SYNODIC_MONTH;
  }

  return new Date(date.getTime() + daysUntil * 86400000);
}
