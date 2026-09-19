import express from 'express';
import cors from 'cors';
import { CORS_ORIGIN } from './env';
import authRouter from './routes/auth.routes';
import pinRouter from './routes/pin.routes';

export function createApp() {
  const app = express();
  app.use(cors({ origin: CORS_ORIGIN }));
  app.use(express.json());

  app.use('/auth', authRouter);
  app.use('/pin', pinRouter);

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  return app;
}
