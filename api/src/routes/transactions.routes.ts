import { Router } from 'express';
import z from 'zod';
import { requireAuth } from '../middleware/requireAuth';
import { getFamilyForParent } from '../services/familyService';
import { getFamilyBalances, listFamilyTransactions } from '../services/transactionService';

const QuerySchema = z.object({
  childId: z.uuid().optional(),
});

const router = Router();
router.use(requireAuth);

router.get('/', async (req, res) => {
  const result = QuerySchema.safeParse(req.query);
  if (!result.success) {
    return res.status(404).json({ message: 'Child not found.' });
  }

  try {
    const family = await getFamilyForParent(req.parentId!);

    const [balances, transactions] = await Promise.all([
      getFamilyBalances(family.id),
      listFamilyTransactions(family.id, result.data.childId),
    ]);

    return res.status(200).json({ balances, transactions });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
