export function toCents(dollars: number): number {
  return Math.round(dollars * 100);
}

export function fromCents(cents: number): number {
  return cents / 100;
}

export function formatCents(cents: number): string {
  return fromCents(cents).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
  });
}
