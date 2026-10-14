export type Child = {
  id: string;
  familyId: string;
  name: string;
  avatar: string;
  colorHex: string;
  capCents: number | null;
  archivedAt: string | null;
  createdAt: string;
};

export type Transaction = {
  id: string;
  childId: string;
  type: 'deposit' | 'withdrawal';
  amountCents: number;
  category: string | null;
  comment: string | null;
  createdBy: string;
  createdAt: string;
};
