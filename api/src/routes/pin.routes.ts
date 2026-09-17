import { Router } from 'express';
import { setPin, verifyPin, getPinStatus } from '../services/pinService';
import { PinInputSchema } from '@digital-bank/shared';
import { treeifyError } from 'zod';
import { requireAuth } from '../middleware/requireAuth';
import { de } from 'zod/v4/locales';

const router = Router();
router.get('/status', requireAuth, async (req, res) => {
  try {
    const { pinSet } = await getPinStatus(req.parentId!);
    return res.status(200).json({ pinSet });
  } catch (err) {
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

router.post('/set', requireAuth, async (req, res) => {
  const result = PinInputSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({ message: treeifyError(result.error) });
  }

  try {
    await setPin(req.parentId!, result.data.pin);
    return res.status(201).json({ message: 'PIN set successfully.' });
  } catch (err) {
    if (err instanceof Error) {
      if (err.message === 'PIN_ALREADY_SET') {
        return res.status(409).json({ message: 'A PIN already exists for this family.' });
      }
    }
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

router.post('/verify', requireAuth, async (req, res) => {
  const result = PinInputSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({ message: treeifyError(result.error) });
  }

  try {
    await verifyPin(req.parentId!, result.data.pin);
    return res.status(200).json({ message: 'PIN verified successfully.' });
  } catch (err) {
    if (err instanceof Error) {
      if (err.message === 'PIN_NOT_SET') {
        return res.status(409).json({ message: 'A PIN does not exist for this family.' });
      }

      if (err.message === 'PIN_LOCKED') {
        return res.status(423).json({ message: 'PIN locked due to too many attempts.' });
      }

      if (err.message === 'INVALID_PIN') {
        return res.status(401).json({ message: 'Incorrect PIN.' });
      }
    }
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
