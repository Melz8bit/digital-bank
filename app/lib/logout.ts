import { useAuthStore } from '@/store/authStore';
import { usePinStore } from '@/store/pinStore';
import { queryClient } from '@/lib/queryClient';

// Clearing the token flips the Stack.Protected guards in the root layout, which sends the user to Login.
// Shared by the automatic logout on an expired/invalid session and the (future) Logout button.
export function logout() {
  useAuthStore.getState().clearSession();
  usePinStore.getState().lock();
  queryClient.clear();
}
