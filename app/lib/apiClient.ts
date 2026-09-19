const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:3000';

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    throw new Error(typeof data?.message === 'string' ? data.message : 'Something went wrong.');
  }
  return res.json();
}
