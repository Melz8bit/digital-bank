import { eq } from 'drizzle-orm';
import { db } from '../db/client';
import { families, parents } from '../db/schema';
import bcrypt from 'bcrypt';

async function getFamilyForParent(parentId: string) {
  const [parent] = await db.select().from(parents).where(eq(parents.id, parentId));
  const [family] = await db.select().from(families).where(eq(families.id, parent.familyId));
  return family;
}

export async function getPinStatus(parentId: string) {
  const family = await getFamilyForParent(parentId);
  return { pinSet: !!family.pinHash };
}

export async function setPin(parentId: string, pin: string) {
  const family = await getFamilyForParent(parentId);

  if (family.pinHash) {
    throw new Error('PIN_ALREADY_SET');
  }

  const pinHash = await bcrypt.hash(pin, 12);
  await db.update(families).set({ pinHash }).where(eq(families.id, family.id));
}

export async function verifyPin(parentId: string, pin: string) {
  const family = await getFamilyForParent(parentId);

  if (!family.pinHash) {
    throw new Error('PIN_NOT_SET');
  }

  if (family.pinLockedUntil && family.pinLockedUntil > new Date()) {
    throw new Error('PIN_LOCKED');
  }

  const pinMatch = await bcrypt.compare(pin, family.pinHash);
  if (pinMatch) {
    await db
      .update(families)
      .set({ pinAttempts: 0, pinLockedUntil: null })
      .where(eq(families.id, family.id));
  } else {
    const [result] = await db
      .update(families)
      .set({ pinAttempts: family.pinAttempts + 1 })
      .where(eq(families.id, family.id))
      .returning();

    if (result.pinAttempts === 5) {
      await db
        .update(families)
        .set({ pinLockedUntil: new Date(Date.now() + 5 * 60 * 1000) })
        .where(eq(families.id, family.id));
      throw new Error('PIN_LOCKED');
    }
    throw new Error('INVALID_PIN');
  }
}
