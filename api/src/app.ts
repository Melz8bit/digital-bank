import express from 'express';
import authRouter from './routes/auth.routes';
import pinRouter from './routes/pin.routes';

export function createApp() {
  const app = express();
  app.use(express.json());

  app.use('/auth', authRouter);
  app.use('/pin', pinRouter);

  app.get('/health', (_req, res) => {
    res.json({ status: 'ok' });
  });

  return app;
}
