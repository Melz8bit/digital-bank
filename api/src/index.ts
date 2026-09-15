import { createApp } from "./app";

const port = process.env.PORT ? Number(process.env.PORT) : 3000;

createApp().listen(port, () => {
  console.log(`api listening on :${port}`);
});
