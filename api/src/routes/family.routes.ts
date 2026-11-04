import { Router } from 'express';
import { requireAuth } from '../middleware/requireAuth';
import { getFamilyForParent } from '../services/familyService';
import type { Family } from '@digital-bank/shared';

const router = Router();
router.use(requireAuth);

router.get('/', async (req, res) => {
  try {
    const family = await getFamilyForParent(req.parentId!);

    const body: Family = {
      id: family.id,
      name: family.name,
    };

    return res.status(200).json({ family: body });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
