import { sql } from 'drizzle-orm';
import { check, integer, pgTable, text, timestamp, uuid, index } from 'drizzle-orm/pg-core';

export const families = pgTable('families', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  pinHash: text('pin_hash'),
  pinAttempts: integer('pin_attempts').notNull().default(0),
  pinLockedUntil: timestamp('pin_locked_until', { withTimezone: true }),
  defaultCapCents: integer('default_cap_cents'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const parents = pgTable('parents', {
  id: uuid('id').primaryKey().defaultRandom(),
  familyId: uuid('family_id')
    .notNull()
    .references(() => families.id, { onDelete: 'cascade' }),
  email: text('email').notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const children = pgTable('children', {
  id: uuid('id').primaryKey().defaultRandom(),
  familyId: uuid('family_id')
    .notNull()
    .references(() => families.id, { onDelete: 'cascade' }),
  name: text('name').notNull(),
  avatar: text('avatar').notNull().default('default'),
  colorHex: text('color_hex').notNull().default('#4F8EF7'),
  capCents: integer('cap_cents'),
  archivedAt: timestamp('archived_at', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const transactions = pgTable(
  'transactions',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    childId: uuid('child_id')
      .notNull()
      .references(() => children.id, { onDelete: 'cascade' }),
    type: text('type').notNull(),
    amountCents: integer('amount_cents').notNull(),
    category: text('category'),
    comment: text('comment'),
    createdBy: uuid('created_by')
      .notNull()
      .references(() => parents.id),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    check('amount_positive', sql`${t.amountCents} > 0`),
    check('type_check', sql`${t.type} IN ('deposit', 'withdrawal')`),
    index('transactions_child_created_idx').on(t.childId, t.createdAt.desc()),
  ]
);
