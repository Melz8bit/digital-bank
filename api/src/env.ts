import 'dotenv/config';

export const JWT_SECRET = process.env.JWT_SECRET as string;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET is not set');
}

export const CORS_ORIGIN = process.env.CORS_ORIGIN ?? 'http://localhost:19006';
