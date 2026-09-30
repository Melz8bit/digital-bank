import { Router } from 'express';
import { requireAuth } from '../middleware/requireAuth';
import { CreateChildInputSchema } from '@digital-bank/shared';
import { createChild, listChildren } from '../services/childService';
import { treeifyError } from 'zod';

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
    return res.status(400).json({ message: treeifyError(result.error) });
  }

  try {
    const newChild = await createChild(req.parentId!, result.data.name);
    return res.status(201).json({ child: newChild });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
