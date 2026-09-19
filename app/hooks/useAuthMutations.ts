import { useMutation } from '@tanstack/react-query';
import type { LoginInput, SignupInput } from '@digital-bank/shared';
import { postJson } from '@/lib/apiClient';
import { useAuthStore } from '@/store/authStore';

type AuthResponse = {
  token: string;
  parent: { id: string; email: string; familyId: string };
};

function saveSession({ token, parent }: AuthResponse) {
  useAuthStore.getState().setSession(token, parent);
}

export function useSignupMutation() {
  return useMutation({
    mutationFn: (input: SignupInput) => postJson<AuthResponse>('/auth/signup', input),
    onSuccess: saveSession,
  });
}

export function useLoginMutation() {
  return useMutation({
    mutationFn: (input: LoginInput) => postJson<AuthResponse>('/auth/login', input),
    onSuccess: saveSession,
  });
}
