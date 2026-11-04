import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '../env';

// The client logs out on this code. Other 401s (wrong PIN, wrong password) don't carry it.
const SESSION_INVALID = 'SESSION_INVALID';

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ code: SESSION_INVALID, message: 'Invalid authorization format' });
  }

  const bearerToken = authHeader.slice(7);

  let payload;

  try {
    payload = jwt.verify(bearerToken, JWT_SECRET);
  } catch {
    return res.status(401).json({ code: SESSION_INVALID, message: 'Invalid JWT' });
  }

  if (typeof payload == 'string' || !payload.sub) {
    return res.status(401).json({ code: SESSION_INVALID, message: 'Invalid JWT format' });
  }

  req.parentId = payload.sub;
  next();
}
