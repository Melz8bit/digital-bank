import { eq } from 'drizzle-orm';
import { db } from '../db/client';
import { families, parents } from '../db/schema';

export async function getFamilyForParent(parentId: string) {
  const [parent] = await db.select().from(parents).where(eq(parents.id, parentId));
  const [family] = await db.select().from(families).where(eq(families.id, parent.familyId));
  return family;
}
