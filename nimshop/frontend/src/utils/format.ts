/**
 * Convert Luna (integer) to NIM (string with 5 decimals).
 * 1 NIM = 100,000 Luna.
 */
export function lunaToNim(luna: number): string {
  if (!Number.isInteger(luna)) {
    throw new Error("Luna must be an integer");
  }
  if (luna < 0) {
    throw new Error("Luna cannot be negative");
  }
  return (luna / 100_000).toFixed(5);
}

export function formatNim(luna: number): string {
  return `${lunaToNim(luna)} NIM`;
}
