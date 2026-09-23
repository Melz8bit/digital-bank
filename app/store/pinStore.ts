import { create } from 'zustand';

interface PinState {
  unlocked: boolean;
  unlock: () => void;
  lock: () => void;
}

export const usePinStore = create<PinState>()((set) => ({
  unlocked: false,
  unlock: () => set({ unlocked: true }),
  lock: () => set({ unlocked: false }),
}));
