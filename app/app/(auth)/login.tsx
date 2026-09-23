import { useState } from 'react';
import { useLoginMutation } from '@/hooks/useAuthMutations';
import { TextInput, Pressable, Text, View } from 'react-native';
import { Link } from 'expo-router';

export default function LoginScreen() {
  const { mutate, isPending, error } = useLoginMutation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = () => {
    mutate({ email, password });
  };

  return (
    <View>
      <TextInput
        value={email}
        onChangeText={setEmail}
        placeholder="Email"
        autoCapitalize="none"
        keyboardType="email-address"
        textContentType="emailAddress"
      />

      <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
        textContentType="password"
      />

      <Pressable onPress={handleSubmit} disabled={isPending}>
        <Text>{isPending ? 'Logging in...' : 'Log In'}</Text>
      </Pressable>

      <Link href="/signup">
        <Text>Need an account? Sign up</Text>
      </Link>

      {error && <Text>{error.message}</Text>}
    </View>
  );
}
