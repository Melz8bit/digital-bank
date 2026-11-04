import { useAuthStore } from '@/store/authStore';
import { logout } from '@/lib/logout';

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:3000';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const data = await res.json().catch(() => null);

    // Expired or invalid token (sent only by requireAuth): drop the session so the user lands on Login
    // instead of being stuck on an error. Wrong-PIN / wrong-password 401s have no code and fall through.
    if (res.status === 401 && data?.code === 'SESSION_INVALID') {
      logout();
      throw new Error('Your session has expired. Please log in again.');
    }

    throw new Error(typeof data?.message === 'string' ? data.message : 'Something went wrong.');
  }

  return res.json();
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}

function authHeaders(): HeadersInit {
  const token = useAuthStore.getState().token;
  return { Authorization: `Bearer ${token}` };
}

export async function getJsonAuth<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { headers: authHeaders() });
  return handleResponse<T>(res);
}

export async function postJsonAuth<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(res);
}
