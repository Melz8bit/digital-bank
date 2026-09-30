import { and, asc, eq, isNull } from 'drizzle-orm';
import { db } from '../db/client';
import { children } from '../db/schema';
import { getFamilyForParent } from './familyService';

export async function createChild(parentId: string, name: string) {
  const family = await getFamilyForParent(parentId);
  const [result] = await db
    .insert(children)
    .values({
      familyId: family.id,
      name,
    })
    .returning();

  return result;
}

export async function listChildren(parentId: string) {
  const family = await getFamilyForParent(parentId);
  return db
    .select()
    .from(children)
    .where(and(eq(children.familyId, family.id), isNull(children.archivedAt)))
    .orderBy(asc(children.createdAt));
}

export async function getChildForParent(parentId: string, childId: string) {
  const family = await getFamilyForParent(parentId);
  const [result] = await db
    .select()
    .from(children)
    .where(
      and(eq(children.id, childId), eq(children.familyId, family.id), isNull(children.archivedAt))
    );

  if (!result) {
    throw new Error('CHILD_NOT_FOUND');
  }

  return result;
}
