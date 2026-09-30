import { usePinStore } from '@/store/pinStore';
import { useEffect } from 'react';
import { AppState } from 'react-native';

export function useAutoLock() {
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextState) => {
      if (nextState !== 'active') {
        usePinStore.getState().lock();
      }
    });

    return () => {
      subscription.remove();
    };
  }, []);
}
