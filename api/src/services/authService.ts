import { LoginInputSchema, SignupInput } from '@digital-bank/shared';
import { db } from '../db/client';
import { families, parents } from '../db/schema';
import { eq } from 'drizzle-orm';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET as string;
if (!JWT_SECRET) {
  throw new Error('JWT_SECRET is not set');
}

export async function signup(input: SignupInput) {
  const parentExists = await db
    .select()
    .from(parents)
    .where(eq(parents.email, input.email.toLowerCase()));

  if (parentExists.length > 0) {
    throw new Error('EMAIL_TAKEN');
  }

  if (input.inviteCode) {
    throw new Error('INVITE_SIGNUP_NOT_IMPLEMENTED');
  }

  const passwordHash = await bcrypt.hash(input.password, 12);

  const result = await db.transaction(async (tx) => {
    const [family] = await tx.insert(families).values({ name: input.familyName! }).returning();
    const [parent] = await tx
      .insert(parents)
      .values({
        familyId: family.id,
        email: input.email.toLowerCase(),
        passwordHash,
      })
      .returning();

    return { family, parent };
  });

  const token = jwt.sign({ sub: result.parent.id }, JWT_SECRET, { expiresIn: '30d' });
  return {
    token,
    parent: { id: result.parent.id, email: result.parent.email, familyId: result.family.id },
  };
}
