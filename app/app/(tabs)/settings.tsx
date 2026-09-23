import { useState } from 'react';
import { StyleSheet, Text, TextInput, Pressable, View } from 'react-native';
import { useQueryClient } from '@tanstack/react-query';
import { usePinStatusQuery, useSetPinMutation, useVerifyPinMutation } from '@/hooks/usePinMutations';
import { usePinStore } from '@/store/pinStore';

export default function SettingsScreen() {
  const queryClient = useQueryClient();
  const { data, isLoading } = usePinStatusQuery();
  const { unlocked, unlock } = usePinStore();
  const [pin, setPin] = useState('');

  const setPinMutation = useSetPinMutation();
  const verifyPinMutation = useVerifyPinMutation();

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  if (!data?.pinSet) {
    const handleSetPin = () => {
      setPinMutation.mutate(
        { pin },
        {
          onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pinStatus'] });
            unlock();
          },
        }
      );
    };

    return (
      <View style={styles.container}>
        <Text style={styles.title}>Set a PIN</Text>
        <TextInput
          value={pin}
          onChangeText={setPin}
          placeholder="4-digit PIN"
          keyboardType="number-pad"
          maxLength={4}
          secureTextEntry
        />
        <Pressable onPress={handleSetPin} disabled={setPinMutation.isPending}>
          <Text>{setPinMutation.isPending ? 'Setting...' : 'Set PIN'}</Text>
        </Pressable>
        {setPinMutation.error && <Text>{setPinMutation.error.message}</Text>}
      </View>
    );
  }

  if (!unlocked) {
    const handleVerifyPin = () => {
      verifyPinMutation.mutate(
        { pin },
        {
          onSuccess: () => unlock(),
        }
      );
    };

    return (
      <View style={styles.container}>
        <Text style={styles.title}>Enter PIN</Text>
        <TextInput
          value={pin}
          onChangeText={setPin}
          placeholder="4-digit PIN"
          keyboardType="number-pad"
          maxLength={4}
          secureTextEntry
        />
        <Pressable onPress={handleVerifyPin} disabled={verifyPinMutation.isPending}>
          <Text>{verifyPinMutation.isPending ? 'Checking...' : 'Unlock'}</Text>
        </Pressable>
        {verifyPinMutation.error && <Text>{verifyPinMutation.error.message}</Text>}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Settings</Text>
      <Text>The rest of the parent settings land here in a later phase.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 24,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
  },
});
