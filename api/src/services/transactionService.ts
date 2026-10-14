import { and, desc, eq, isNull, sql } from 'drizzle-orm';
import { db } from '../db/client';
import { children, transactions } from '../db/schema';
import { getFamilyForParent } from './familyService';
import { TransactionInput } from '@digital-bank/shared';
import { error } from 'console';

type Executor = typeof db | Parameters<Parameters<typeof db.transaction>[0]>[0];

export async function getBalance(executor: Executor, childId: string): Promise<number> {
  const [row] = await executor
    .select({
      balance: sql<string>`COALESCE(SUM(CASE WHEN ${transactions.type} = 'deposit' THEN ${transactions.amountCents} ELSE -${transactions.amountCents} END), 0)`,
    })
    .from(transactions)
    .where(eq(transactions.childId, childId));

  return Number(row.balance);
}

export async function listRecentTransactions(executor: Executor, childId: string, limit = 20) {
  const recentTransactions = await executor
    .select()
    .from(transactions)
    .where(eq(transactions.childId, childId))
    .orderBy(desc(transactions.createdAt))
    .limit(limit);

  return recentTransactions;
}

export async function createTransaction(
  parentId: string,
  childId: string,
  input: TransactionInput
) {
  const family = await getFamilyForParent(parentId);

  return db.transaction(async (tx) => {
    const [child] = await tx
      .select()
      .from(children)
      .where(
        and(eq(children.id, childId), eq(children.familyId, family.id), isNull(children.archivedAt))
      )
      .for('update');

    if (!child) {
      throw new Error('CHILD_NOT_FOUND');
    }

    const balance = await getBalance(tx, childId);

    if (input.type === 'withdrawal') {
      const capCents = child.capCents ?? family.defaultCapCents;

      if (capCents != null && input.amountCents > capCents) {
        throw new Error('CAP_EXCEEDED');
      }

      if (input.amountCents > balance) {
        throw new Error('INSUFFICIENT_BALANCE');
      }
    }

    const [transaction] = await tx
      .insert(transactions)
      .values({
        childId,
        type: input.type,
        amountCents: input.amountCents,
        createdBy: parentId,
        category: input.type === 'deposit' ? input.category : null,
        comment: input.type === 'withdrawal' ? input.comment : null,
      })
      .returning();

    const newBalance =
      input.type === 'deposit' ? balance + input.amountCents : balance - input.amountCents;

    return { transaction, balance: newBalance };
  });
}
