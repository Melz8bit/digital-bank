import { Router } from 'express';
import { signup } from '../services/authService';
import { SignupInputSchema } from '@digital-bank/shared';
import { treeifyError } from 'zod';

const router = Router();
router.post('/signup', async (req, res) => {
  const result = SignupInputSchema.safeParse(req.body);

  if (!result.success) {
    return res.status(400).json({ message: treeifyError(result.error) });
  }

  try {
    const { token, parent } = await signup(result.data);
    return res.status(201).json({ token, parent });
  } catch (err) {
    if (err instanceof Error) {
      if (err.message == 'EMAIL_TAKEN') {
        return res.status(409).json({ message: 'An account with this email already exists.' });
      }

      if (err.message == 'INVITE_SIGNUP_NOT_IMPLEMENTED') {
        return res.status(501).json({ message: 'Invite Signup Method Not Implemented' });
      }
    }
    return res.status(500).json({ message: 'An unexpected error occurred.' });
  }
});

export default router;
