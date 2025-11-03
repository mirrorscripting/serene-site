import { describe, expect, it } from 'vitest';
import { getMoonPhase } from '../src/lib/moon.js';

describe('getMoonPhase', () => {
  it('identifies the phase near the April 2024 new moon', () => {
    const phase = getMoonPhase(new Date('2024-04-08T18:00:00Z'));
    expect(phase.name).toBe('New Moon');
    expect(phase.illumination).toBeLessThan(0.1);
  });

  it('returns illumination between 0 and 1', () => {
    const phase = getMoonPhase(new Date('2024-08-19T12:00:00Z'));
    expect(phase.illumination).toBeGreaterThanOrEqual(0);
    expect(phase.illumination).toBeLessThanOrEqual(1);
  });
});
