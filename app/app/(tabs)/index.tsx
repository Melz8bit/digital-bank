import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View, FlatList } from 'react-native';
import { useChildrenQuery, useFamilyTransactionsQuery } from '@/hooks/useTransactions';
import { formatCents } from '@digital-bank/shared';

export default function HomeScreen() {
  const { data, isLoading, error } = useChildrenQuery();
  const [selectedChildId, setSelectedChildId] = useState<string | undefined>(undefined);
  const { data: txData, isLoading: txIsLoading } = useFamilyTransactionsQuery(selectedChildId);

  if (isLoading) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text>{error.message}</Text>
      </View>
    );
  }

  const children = data?.children ?? [];

  if (children.length === 0) {
    return (
      <View style={styles.container}>
        <Text>No kids yet. Add one in Settings!</Text>
      </View>
    );
  }

  const childById = new Map(children.map((child) => [child.id, child]));

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Family Bank</Text>

      <Pressable
        onPress={() => setSelectedChildId(undefined)}
        style={[styles.chip, selectedChildId === undefined && styles.chipSelected]}
      >
        <Text style={[styles.chipText, selectedChildId === undefined && styles.chipTextSelected]}>
          All
        </Text>
      </Pressable>

      <ScrollView
        horizontal
        style={{ flexGrow: 0 }}
        contentContainerStyle={styles.cardRow}
        showsHorizontalScrollIndicator={false}
      >
        {children.map((child) => (
          <Pressable key={child.id} onPress={() => setSelectedChildId(child.id)}>
            <View
              style={[
                styles.balanceCard,
                { backgroundColor: child.colorHex },
                selectedChildId !== undefined && selectedChildId !== child.id && styles.cardDimmed,
              ]}
            >
              <Text style={styles.cardName}>{child.name}</Text>
              <Text style={styles.cardAmount}>
                {txIsLoading ? '...' : formatCents(txData?.balances[child.id] ?? 0)}
              </Text>
            </View>
          </Pressable>
        ))}
      </ScrollView>

      <FlatList
        data={txData?.transactions ?? []}
        keyExtractor={(tx) => tx.id}
        renderItem={({ item }) => {
          const child = childById.get(item.childId);
          const isDeposit = item.type === 'deposit';
          return (
            <View style={styles.txRow}>
              {/* Dot */}
              <View style={[styles.dot, { backgroundColor: child?.colorHex ?? '#999' }]} />
              {/* Middle: Transaction Info */}
              <View style={styles.txMiddle}>
                {/* Child's Name */}
                <Text style={styles.txName}>{child?.name ?? 'Unknown'}</Text>
                {/* Comment/Category */}
                <Text style={styles.txDetail}>
                  {item.comment ?? item.category} · {new Date(item.createdAt).toLocaleDateString()}
                </Text>
              </View>
              {/* Amount */}
              <Text style={[styles.txAmount, isDeposit ? styles.deposit : styles.withdrawal]}>
                {isDeposit ? '+' : '-'}
                {formatCents(item.amountCents)}
              </Text>
            </View>
          );
        }}
        ListEmptyComponent={<Text>No transactions yet.</Text>}
        style={{ flex: 1 }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 24,
    gap: 16,
    backgroundColor: '#FFF8EC', // warm cream, friendlier than plain white
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
  },
  balanceCard: {
    width: 160,
    padding: 20,
    borderRadius: 24,
    gap: 4,
  },
  cardName: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    opacity: 0.9,
  },
  cardAmount: {
    color: 'white',
    fontSize: 32,
    fontWeight: '800',
  },
  cardRow: {
    gap: 12,
  },
  cardDimmed: { opacity: 0.4 },
  chip: {
    alignSelf: 'flex-start', // otherwise it stretches full width
    paddingVertical: 8,
    paddingHorizontal: 18,
    borderRadius: 999, // a huge radius gives it a pill shape
    borderWidth: 2,
    borderColor: '#333',
  },
  chipSelected: { backgroundColor: '#333' },
  chipText: { fontWeight: '700', color: '#333' },
  chipTextSelected: { color: 'white' },
  txRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingVertical: 10,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6, // half the size turns the square into a circle
  },
  txMiddle: { flex: 1 }, // takes the leftover width, pushing the amount right
  txName: { fontWeight: '600' },
  txDetail: { fontSize: 13, color: '#666' },
  txAmount: { fontWeight: '600' },
  deposit: { color: '#16A34A' },
  withdrawal: { color: '#DC2626' },
});
