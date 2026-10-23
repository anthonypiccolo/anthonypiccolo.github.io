// Client-side formatting shared by the vitals card and the running page.

export function pace(durationSec: number, km: number): string {
  const perKm = Math.round(durationSec / km);
  return `${Math.floor(perKm / 60)}:${String(perKm % 60).padStart(2, '0')}/km`;
}

/** "Wed, 21 Oct" for a YYYY-MM-DD local date. */
export function shortDate(date: string, withWeekday = true): string {
  return new Date(`${date}T12:00:00`).toLocaleDateString('en-AU', {
    weekday: withWeekday ? 'short' : undefined,
    day: 'numeric',
    month: 'short',
  });
}
