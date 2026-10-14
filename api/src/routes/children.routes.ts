import { Router } from 'express';
import { requireAuth } from '../middleware/requireAuth';
import { CreateChildInputSchema, TransactionInputSchema } from '@digital-bank/shared';
import { createChild, getChildForParent, listChildren } from '../services/childService';
import z from 'zod';
import {
  createTransaction,
  getBalance,
  listRecentTransactions,
} from '../services/transactionService';
import { db } from '../db/client';

const ChildIdSchema = z.uuid();

const router = Router();
router.use(requireAuth);
router.get('/', async (req, res) => {
  try {
    const childrenList = await listChildren(req.parentId!);
    return res.status(200).json({ children: childrenList });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

router.post('/', async (req, res) => {
  const result = CreateChildInputSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({ message: result.error.issues[0].message });
  }

  try {
    const newChild = await createChild(req.parentId!, result.data.name);
    return res.status(201).json({ child: newChild });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

router.get('/:childId/transactions', async (req, res) => {
  try {
    const childId = req.params.childId;

    const result = ChildIdSchema.safeParse(childId);
    if (!result.success) {
      return res.status(404).json({ message: 'Child not found.' });
    }

    await getChildForParent(req.parentId!, childId);

    const getChildBalance = getBalance(db, childId);
    const getRecentTransactions = listRecentTransactions(db, childId);

    const [balance, transactions] = await Promise.all([getChildBalance, getRecentTransactions]);

    return res.status(200).json({ balance, transactions });
  } catch (err) {
    if (err instanceof Error) {
      if (err.message === 'CHILD_NOT_FOUND') {
        return res.status(404).json({ message: 'Child not found.' });
      }
    }
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

router.post('/:childId/transactions', async (req, res) => {
  const childId = req.params.childId;

  const result = ChildIdSchema.safeParse(childId);
  if (!result.success) {
    return res.status(404).json({ message: 'Child not found.' });
  }

  const checkTransactionBody = TransactionInputSchema.safeParse(req.body);
  if (!checkTransactionBody.success) {
    return res.status(400).json({ message: checkTransactionBody.error.issues[0].message });
  }

  try {
    const transaction = await createTransaction(req.parentId!, childId, checkTransactionBody.data);
    return res.status(201).json(transaction);
  } catch (err) {
    if (err instanceof Error) {
      if (err.message === 'CHILD_NOT_FOUND') {
        return res.status(404).json({ message: 'Child not found.' });
      }

      if (err.message === 'CAP_EXCEEDED') {
        return res
          .status(422)
          .json({ message: "That's more than you're allowed to spend at once." });
      }

      if (err.message === 'INSUFFICIENT_BALANCE') {
        return res.status(422).json({ message: "You don't have enough money for that." });
      }
    }
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
