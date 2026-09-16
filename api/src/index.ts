import { createApp } from './app';
import { runMigrations } from './db/migrate';

const port = process.env.PORT ? Number(process.env.PORT) : 3000;

async function main() {
  await runMigrations();

  createApp().listen(port, () => {
    console.log(`api listening on :${port}`);
  });
}

main();
