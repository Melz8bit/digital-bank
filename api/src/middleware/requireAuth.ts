import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '../env';

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Invalid authorization format' });
  }

  const bearerToken = authHeader.slice(7);

  let payload;

  try {
    payload = jwt.verify(bearerToken, JWT_SECRET);
  } catch {
    return res.status(401).json({ message: 'Invalid JWT' });
  }

  if (typeof payload == 'string' || !payload.sub) {
    return res.status(401).json({ message: 'Invalid JWT format' });
  }

  req.parentId = payload.sub;
  next();
}
