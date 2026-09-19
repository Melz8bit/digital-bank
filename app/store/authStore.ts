import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  token: string | null;
  parent: { id: string; email: string; familyId: string } | null;
  hasHydrated: boolean;
  setSession: (token: string, parent: AuthState['parent']) => void;
  clearSession: () => void;
  setHasHydrated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      parent: null,
      hasHydrated: false,
      setSession: (token, parent) => set({ token, parent }),
      clearSession: () => set({ token: null, parent: null }),
      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
