# Digital Bank — Todo

Full plan lives at the plan file from the initial planning session; this tracks day-to-day progress.

## Phase 0 — Scaffolding
- [x] npm workspaces root (`app`, `api`, `packages/shared`)
- [x] `packages/shared` skeleton (`money.ts` real, `types.ts`/`schemas.ts` stubs)
- [x] `api` skeleton — Express + `/health`
- [x] `app` skeleton — Expo Router tab shell (Home/Settings placeholders)
- [x] Verified: api boots, `/health` returns 200; `expo export --platform web` bundles clean; both typecheck clean

## Phase 1 — Auth + PIN (in progress)
- [x] Drizzle schema for `families`/`parents` (`api/src/db/schema.ts`)
- [x] Migration generated + applied against local dev Postgres, verified with `psql`
- [x] `db/client.ts` (Drizzle + pg Pool) and `db/migrate.ts` (runs automatically on `index.ts` boot)
- [x] Shared zod schemas: `SignupInputSchema` (with `.refine()` enforcing exactly one of `familyName`/`inviteCode`), `LoginInputSchema`
- [x] `authService.signup()` — bcrypt hash, transaction-wrapped family+parent creation, JWT issuance. Verified end-to-end against real Postgres (happy path + duplicate-email rejection), test data cleaned up.
- [x] `authService.login()` — bcrypt.compare against stored hash, same JWT pattern as signup(), generic `INVALID_CREDENTIALS` for bad email/password. Verified end-to-end against real Postgres (correct password, wrong password, unknown email), test data cleaned up.
- [x] `requireAuth` middleware (`api/src/middleware/requireAuth.ts`) — Bearer header parsing, `jwt.verify` in try/catch, guards against string-payload and missing-`sub` cases, sets `req.parentId` via `express.d.ts` declaration-merge augmentation. Now gates both `/auth`-adjacent and all `/pin` routes, verified end-to-end.
- [x] `env.ts` — extracted `JWT_SECRET` guard out of `authService.ts` into its own module so `authService` and `requireAuth` share one source instead of duplicating the check
- [x] `auth.routes.ts` — wire signup/login to real HTTP endpoints
  - [x] `POST /signup` — validates with `SignupInputSchema`, calls `authService.signup()`, maps `EMAIL_TAKEN`→409 / `INVITE_SIGNUP_NOT_IMPLEMENTED`→501 / unknown→500 with real messages.
  - [x] `POST /login` — validates with `LoginInputSchema`, calls `authService.login()`, maps `INVALID_CREDENTIALS`→401 with generic "Invalid email or password." message.
  - [x] mounted the router in `app.ts` (`app.use('/auth', authRouter)`)
  - [x] verified both endpoints end-to-end with real HTTP requests (curl) against the real dev DB — signup (201 + JWT), login correct password (200 + JWT), login wrong password (401), login unknown email (401, same generic message). Test data cleaned up.
- [x] PIN set/verify endpoints + rate limiting (`pin_attempts`/`pin_locked_until` lockout) — schema already had these fields on `families` (shared PIN across co-managing parents, not per-parent)
  - [x] `pinService.ts` — `getPinStatus()`, `setPin()` (`PIN_ALREADY_SET` guard), `verifyPin()` (5 wrong attempts → 5-min lockout via `pinLockedUntil`, resets `pinAttempts` only on success)
  - [x] `pin.routes.ts` — `GET /status`, `POST /set` (201), `POST /verify` (200 / 401 `INVALID_PIN` / 423 `PIN_LOCKED` / 409 `PIN_NOT_SET`), all behind `requireAuth`
  - [x] mounted at `app.use('/pin', pinRouter)`
  - [x] verified end-to-end against real dev DB: status before/after set, duplicate-set rejection, correct verify, 4x wrong→401 then 5th→423, locked-out correct PIN still 423, verify against a family with no PIN set→409. Test data cleaned up.
  - [x] design decisions: PIN is family-wide (not per-parent); second parent joining via invite code skips PIN setup entirely (client-side routing off which signup branch was used, not an API concern); PIN change (requires old PIN) deferred to the later account-settings phase
- [x] Client: login/signup screens wired via React Query + `useAuthStore`
  - [x] Installed `@tanstack/react-query`, `zustand`, `@react-native-async-storage/async-storage` in the `app` workspace
  - [x] Design decisions: AsyncStorage for token persistence everywhere (not `expo-secure-store`, which doesn't work on web — matches the app's established low-threat-model reasoning); route gating via Expo Router 6's `<Stack.Protected guard={...}>` with an `(auth)` group for login/signup and the existing `(tabs)` group protected behind `!!token`
  - [x] `app/store/authStore.ts` — zustand store wrapped in `persist` with `createJSONStorage(() => AsyncStorage)`; `onRehydrateStorage` flips `hasHydrated` to `true` once storage has loaded. (`partialize` for `hasHydrated` still undecided — harmless without it.)
  - [x] `app/lib/queryClient.ts` + `QueryClientProvider` wrapping the root `_layout.tsx`
  - [x] `app/lib/apiClient.ts` (`postJson` + `EXPO_PUBLIC_API_URL`, falls back to `http://localhost:3000`) and `app/hooks/useAuthMutations.ts` (`useSignupMutation` / `useLoginMutation`, `onSuccess` writes the session into the store)
  - [x] API CORS: `cors` package, `CORS_ORIGIN` in `api/src/env.ts` (default `http://localhost:19006`), `app.use(cors(...))` in `app.ts`. `env.ts` now loads `dotenv` itself (import order bug when `app.ts` imported it first).
  - [x] `(auth)` route group (`_layout.tsx`, placeholder `login.tsx` / `signup.tsx`) + `Stack.Protected` gating in root `_layout.tsx` (`guard={!!token}` for `(tabs)`, `guard={!token}` for `(auth)`, `return null` until `hasHydrated`). Verified in headless Edge: logged-out lands on Login.
  - [x] Fixed blank web screen: zustand's middleware build uses `import.meta.env`, which Metro's web bundle can't parse — added `app/babel.config.js` with `unstable_transformImportMeta: true`
  - [x] Pinned `@react-native-async-storage/async-storage` to `2.2.0` via `npx expo install` (Expo SDK 54's expected version; v3.x was installed first)
  - [x] actual login/signup screen UI (forms, `isPending`/`error` display, link between screens via `expo-router`'s `<Link>`)
  - [x] verify the logged-in side of the gate — signed up for real, landed in `(tabs)` (2026-09-22)
  - [x] committed and pushed (2026-09-19)
  - [x] Dev-server gotcha: after any dependency change, restart Expo with `--clear` (Metro cached a stale `node_modules` map after the AsyncStorage downgrade → "Unable to resolve module merge-options" → JSON bundle error → blank page)
  - [x] Dev-server gotcha #2 (2026-09-22): a stray duplicate `app/(auth)/` directory existed at the workspace root (outside `app/app/`, the actual Expo Router root) — all form work briefly landed there and was invisible to the router, which kept serving the old September 19 placeholder screens instead. Fixed by moving the finished `login.tsx`/`signup.tsx` into `app/app/(auth)/` and deleting the stray directory. When editing route files, confirm the path is under `app/app/`, not `app/`.
- [x] Client: PIN unlock screen gating the Settings tab
  - [x] `app/lib/apiClient.ts` extended with authenticated variants: `handleResponse()` shared helper, `getJsonAuth()`/`postJsonAuth()` attach `Authorization: Bearer <token>` via `useAuthStore.getState()`
  - [x] `app/hooks/usePinMutations.ts` — `usePinStatusQuery` (`useQuery`, since it's a read), `useSetPinMutation`/`useVerifyPinMutation` (`useMutation`, via `postJsonAuth`)
  - [x] `app/store/pinStore.ts` — `usePinStore` (`unlocked` boolean, `unlock()`/`lock()`), deliberately *not* persisted so it resets every app restart (session-scoped unlock, not permanent)
  - [x] `app/app/(tabs)/settings.tsx` — three-state gate: loading → set-PIN form (no `pinSet`) → verify-PIN form (`pinSet` but not `unlocked`) → real settings. Setting a PIN also invalidates the `pinStatus` query and calls `unlock()` directly so you don't immediately have to re-enter it.
  - [x] Verified end-to-end in the real app (2026-09-22): set PIN, landed in settings; reload required PIN re-entry; wrong PIN showed error; correct PIN unlocked.
- [x] Client: `AppState` re-lock on backgrounding (2026-09-30)
  - [x] `app/hooks/useAutoLock.ts` — `AppState` `change` listener in a `useEffect([])` with `subscription.remove()` cleanup; any state other than `'active'` calls `usePinStore.getState().lock()` (no stale closure, no deps). Called in root `_layout.tsx` above the `hasHydrated` early return (rules of hooks).
  - [x] `settings.tsx` — PIN input cleared after set, successful verify, and failed verify. Bug found in testing: `SettingsScreen` stays mounted across lock/unlock (tabs don't unmount), so the old PIN was still in the box after re-lock, making re-lock pointless.
  - [x] Verified in the real app (web): unlock → switch browser tab → back → PIN required again, input empty.

**Phase 1 complete.**

## Environment setup on Linux host (2026-09-19, second session)
- [x] Fresh checkout had no `node_modules` / `api/.env` — ran `npm install` (823 packages), wrote gitignored `api/.env` (`DATABASE_URL`, random `JWT_SECRET`, `CORS_ORIGIN`)
- [x] Dependency audit: all imports declared, `expo install --check` clean, `tsc` clean in api/app/shared
- [x] Docker daemon enabled + `melz` added to `docker` group; Postgres up, API boots, migrations applied, CORS preflight verified
- [x] Rewrite `session-start` / `restore-project` / `backup-projects` skills for Linux (skills now have Linux sections; confirmed working 2026-10-08)
- [x] Mount the NAS share (`\\RASPBERRYPI\Data-NAS`) on this host so backup/restore can run (mounted at `/mnt/nas` via fstab; restore worked 2026-10-08)
- [ ] `npm audit` reports 20 vulns (9 high), mostly inside Expo's tree — revisit on next Expo SDK bump, don't `--force`
- [ ] This Linux machine has system npm **9.2.0**: `npm install` strips `libc` fields from `package-lock.json` (reverted 2026-10-14). Upgrade npm here, or `git checkout -- package-lock.json` after installs
- [x] 2026-10-14: fresh checkout again (no `node_modules`/`api/.env`); new SSH keys since 2026-10-12 → re-added to the Pi with `ssh-copy-id`; `/mnt/nas` gone (NAS now reached through `~/.claude` → `~/NetworkDrive/Melz/Claude`)

## Also done this session (not phase-numbered)
- [x] Build Ledger artifact (https://claude.ai/artifact/XsCEU2QLwnw5h8QYb5FFkZ) restructured into a navigable guide: build order, architecture, stack, 5 build parts, troubleshooting, command reference (No. 001–026). Keep appending to it as new features land (login/signup forms, PIN unlock, re-lock).
- [x] Prettier + format-on-save, matching `chores-chart`/`meal-planner` convention
- [x] GitHub repo created (`Melz8bit/digital-bank`, public, no license) and pushed

## Shared dev database (2026-09-30)
- [x] Dev Postgres moved to the Pi (`~/digital-bank-devdb`, db `digitalbank_dev`) so every computer shares one set of accounts/data; Windows `api/.env` switched over, migrations applied, local `compose.dev.yml` container stopped (kept as an offline fallback)
- [x] Point the Linux machine's `api/.env` at the Pi DB too (done 2026-10-08; also added this machine's SSH key to the Pi):
  ```bash
  PW=$(ssh pi@192.168.1.73 "grep POSTGRES_PASSWORD ~/digital-bank-devdb/.env | cut -d= -f2")
  sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgres://digitalbank:$PW@192.168.1.73:5432/digitalbank_dev|" api/.env
  docker compose -f compose.dev.yml stop
  ```

## Open nice-to-haves
- [ ] `~/.claude` setup (revised 2026-10-14): local git clone of `Melz8bit/claude-sync` on every machine = live sync for config; NAS (`~/NetworkDrive/Melz/Claude/projects/`) holds only memory/transcripts. Linux laptop swapped from the share symlink to a local clone (2026-10-14, done).
  - [x] One-time `git checkout -f -B main origin/main` in the share to bring in the GitHub skills/settings, then re-added `"tui": "fullscreen"` (done 2026-10-14 from a normal terminal; `!` commands from inside Claude Code didn't take effect)
  - [x] Linux branches of `restore-project`/`backup-projects` now use `~/.claude/projects/<project-name>/` (inside the share) instead of `/mnt/nas`; backup refuses to commit if `.credentials.json`/history show up in `git status` (2026-10-14)
  - [x] Windows `~/.claude` confirmed as a local claude-sync clone (2026-10-14)
  - [ ] Never `git add -A` there without checking `.gitignore` first: `.credentials.json` and `history.jsonl` sit in the same folder
  - [x] (2026-10-14) add `skills/synced/`, `plugins/synced/**/.in_use/` and `.last-update-result.json` to `~/.claude/.gitignore` (auto-rewritten by Claude Code; always show as modified)
- [ ] Logout button in unlocked Settings: `clearSession()` + `usePinStore.getState().lock()` + `queryClient.clear()` (for now: DevTools console `localStorage.removeItem('auth-storage'); location.reload();`)
- [ ] Add `"lib": ["ES2020"]` to `api/tsconfig.json` to remove accidental DOM globals (see the `parent` bug, Build Ledger No. 019) — flagged three times now (2026-10-13: `tsc` suggested `IDBTransaction`), still not applied

## Not started
- [ ] Phase 2 — core deposit/withdrawal flows + dashboard (in progress, 2026-09-30)
  - [x] Step 1: `children` + `transactions` in `schema.ts` (CHECKs `amount_positive`/`type_check`, index `(child_id, created_at DESC)`), migration `0001_premium_landau` applied to the Pi dev DB
  - [x] Step 2: shared zod — `CreateChildInput`, `TransactionInput` (discriminated union: deposit+category / withdrawal+required comment)
  - [x] Step 3: `childService` + routes (minimal create/list, family-scoped; full CRUD stays Phase 3)
    - `familyService.getFamilyForParent()` extracted from `pinService` (shared by pin + child services); `childService`: `createChild`, `listChildren` (active only, oldest first), `getChildForParent` (family-scoped, excludes archived, throws `CHILD_NOT_FOUND` — unused until Step 5); `children.routes.ts` mounted at `/children` behind `router.use(requireAuth)`, `GET /` → `{ children }`, `POST /` → 201 `{ child }`. Verified with curl (health 200, no token 401, empty list, blank name 400, create trims name, list, other family sees nothing); test data cleaned up.
  - [x] Step 4: `transactionService` — computed balance, recent list, transactional insert with cap/balance enforcement (422 `CAP_EXCEEDED` / `INSUFFICIENT_BALANCE`)
    - [x] 4a `getBalance(executor, childId)` — `COALESCE(SUM(CASE ...)), 0)`, `Number()` on the bigint string; `Executor` type accepts `db` or `tx`. Tested on Pi DB (0 for empty child; 1000+250−300 = 950). (2026-10-08)
    - [x] 4b `listRecentTransactions(executor, childId, limit = 20)` — newest first, returns full array. Tested (order, limit, other child excluded, empty → `[]`). (2026-10-08)
    - [x] 4c part 1 `createTransaction(parentId, childId, input)` — `getFamilyForParent`, `db.transaction`, family-scoped non-archived child lookup with `.for('update')`, `CHILD_NOT_FOUND`. Temporarily `return child;`. Tested (own child ok; other-family and archived → `CHILD_NOT_FOUND`). (2026-10-08)
    - [x] 4c part 2 (2026-10-13) — inside the tx: `getBalance(tx, ...)`; withdrawal: cap check first (`CAP_EXCEEDED`), then `INSUFFICIENT_BALANCE`; insert with `category`/`comment` narrowed by `input.type`, `createdBy: parentId`, `.returning()`; return `{ transaction, balance: newBalance }`
    - [x] Tested 4c end to end on the Pi DB (2026-10-13): deposit/withdrawal balances + row shape, INSUFFICIENT_BALANCE (no row inserted), family cap, withdraw-exactly-cap allowed, child cap overrides family, cap 0 blocks, deposits ignore cap, other family → CHILD_NOT_FOUND; race: 5 concurrent 300 withdrawals on 1000 → exactly 3 succeed, final 100. Temp families deleted.
    - Cap decision (2026-10-08): cap = max amount **per withdrawal** (not a max balance). `child.capCents ?? family.defaultCapCents`; both null by default = no cap; parent sets it in Settings (Phase 3). Deposits are never capped.
  - [x] Step 5: transaction routes (2026-10-13) — in `children.routes.ts`: `GET /children/:childId/transactions` → 200 `{ balance, transactions }` (ownership check via `getChildForParent`, then balance + list in `Promise.all`); `POST /children/:childId/transactions` → 201 `{ transaction, balance }`, 404 `CHILD_NOT_FOUND`, 422 `CAP_EXCEEDED` / `INSUFFICIENT_BALANCE` with kid-friendly messages, 400 with readable `issues[0].message` string. `ChildIdSchema = z.uuid()` makes malformed ids 404 instead of a Postgres 500. Verified over HTTP (14/14, incl. other family → 404, withdraw to exactly 0, API still healthy).
    - Polish later: zod's default messages leak through for missing fields (withdrawal without `comment` → "Invalid input: expected string, received undefined"; negative amount → "Too small: expected number to be >0"). Add custom `error` messages in `TransactionInputSchema`.
    - Idea: ESLint `@typescript-eslint/no-floating-promises` — missing `await` bit us 3× today and `tsc` caught none of them.
  - [ ] Rebuild `docs/project-map.pdf` after each step/phase: `uv run --no-project --with reportlab==5.0.1 --with pypdf python -I tools/project-map/build.py` (new files must be added to `tools/project-map/map_page.py` NODES + `content.py`; see its README). Also on page 21: unused `import { error } from 'console'` in `transactionService.ts`.
  - [ ] Prettier: 5 files never formatted (`api/src/db/client.ts`, `app/app/(tabs)/_layout.tsx`, `app/app/(tabs)/index.tsx`, `packages/shared/src/index.ts`, `money.ts`). One formatting-only commit: `npx prettier --write "api/src/**/*.ts" "app/**/*.{ts,tsx}" "packages/shared/src/**/*.ts"`
  - [x] Step 6: client React Query hooks + invalidation (2026-10-14)
    - `packages/shared/src/types.ts`: hand-written `Child` / `Transaction` response types (dates are `string`: JSON has no Date; shared can't import Drizzle types from `api`)
    - `app/hooks/useTransactions.ts`: `useChildrenQuery()` (`['children']`), `useTransactionsQuery(childId?)` (`['transactions', childId]`, `enabled: !!childId`), `useCreateTransactionMutation(childId)` (`postJsonAuth`, `onSuccess` returns `invalidateQueries` so `isPending` lasts until the refetch)
    - All 400s now send `issues[0].message` strings (`auth.routes.ts`, `pin.routes.ts`; `treeifyError` gone). Zod defaults still leak for missing `pin` and short login password: fold into the custom-messages polish item; consider `min(1)` for login password.
    - Verified against the real API: response keys match `Child`/`Transaction`, deposit 500 → withdraw 200 → balance 300, overdraft 422, GET newest first; temp family deleted. Hooks not yet used in UI (Step 7).
  - [ ] Step 7: dashboard — balance card + recent list
    - Later: parent-selectable "show N transactions" dropdown (e.g. 10/20/50). Service already takes `limit`; route reads `?limit=` (validate with `z.coerce.number().int().min(1).max(100)`); client puts `limit` in the React Query key so each choice caches separately.
  - [ ] Step 8: deposit / withdrawal screens
  - [ ] Step 9: income vs. spending chart (`react-native-gifted-charts`) + `/summary`
  - [ ] Step 10: kid-friendly styling pass
  - Step 5 PIN decision (2026-10-13): **client-side gating only** for now (option 3). Server does not enforce "deposit requires PIN"; acceptable for a family app. Revisit with a short-lived parent-mode token from `/pin/verify` if needed later.
  - Step 6 fix: 400 responses send `message: treeifyError(...)` (an object) → client `new Error(message)` would show `[object Object]`. Send a readable string (e.g. first issue message) from `children.routes.ts` and `pin.routes.ts`.
  - Gotcha: new migration `.sql` files are NOT picked up by `tsx watch` (not imported) — restart the API to apply them
  - Phase 3 note: `transactions.created_by` → `parents` has no `onDelete`, so deleting a parent with transactions is refused; "remove co-parent" must handle this
- [ ] Phase 3 — settings completeness + multi-child + family/invite (this is where `invite_codes` table + the stubbed `INVITE_SIGNUP_NOT_IMPLEMENTED` branch in `signup()` get filled in for real)
- [ ] Phase 4 — Pi deployment
- [ ] Phase 5 — stretch goals
