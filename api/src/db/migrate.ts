import { migrate } from 'drizzle-orm/node-postgres/migrator';
import { db } from './client';

export async function runMigrations() {
  await migrate(db, { migrationsFolder: './src/db/migrations' });
}

if (require.main === module) {
  runMigrations()
    .then(() => {
      console.log('migrations applied');
      process.exit(0);
    })
    .catch((err) => {
      console.error('migration failed', err);
      process.exit(1);
    });
}
