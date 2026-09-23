import { useState } from 'react';
import { useSignupMutation } from '@/hooks/useAuthMutations';
import { TextInput, Pressable, Text, View } from 'react-native';
import { Link } from 'expo-router';

export default function SignupScreen() {
  const { mutate, isPending, error } = useSignupMutation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState<'family' | 'invite'>('family');
  const [familyName, setFamilyName] = useState('');
  const [inviteCode, setInviteCode] = useState('');

  const handleSubmit = () => {
    mutate({
      email,
      password,
      ...(mode === 'family' ? { familyName } : { inviteCode }),
    });
  };

  return (
    <View>
      <View>
        <Pressable onPress={() => setMode('family')}>
          <Text>Create a family</Text>
        </Pressable>
        <Pressable onPress={() => setMode('invite')}>
          <Text>Join with invite code</Text>
        </Pressable>
      </View>

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

      {mode === 'family' ? (
        <TextInput
          value={familyName}
          onChangeText={setFamilyName}
          placeholder="Family Name"
          autoCapitalize="words"
        />
      ) : (
        <TextInput
          value={inviteCode}
          onChangeText={setInviteCode}
          placeholder="Invite code"
          autoCapitalize="none"
        />
      )}

      <Pressable onPress={handleSubmit} disabled={isPending}>
        <Text>{isPending ? 'Signing up...' : 'Sign Up'}</Text>
      </Pressable>

      <Link href="/login">
        <Text>Have an account? Log in</Text>
      </Link>

      {error && <Text>{error.message}</Text>}
    </View>
  );
}
