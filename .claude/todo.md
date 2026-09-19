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
- [ ] Client: login/signup screens wired via React Query + `useAuthStore`
  - [x] Installed `@tanstack/react-query`, `zustand`, `@react-native-async-storage/async-storage` in the `app` workspace
  - [x] Design decisions: AsyncStorage for token persistence everywhere (not `expo-secure-store`, which doesn't work on web — matches the app's established low-threat-model reasoning); route gating via Expo Router 6's `<Stack.Protected guard={...}>` with an `(auth)` group for login/signup and the existing `(tabs)` group protected behind `!!token`
  - [x] `app/store/authStore.ts` — zustand store wrapped in `persist` with `createJSONStorage(() => AsyncStorage)`; `onRehydrateStorage` flips `hasHydrated` to `true` once storage has loaded. (`partialize` for `hasHydrated` still undecided — harmless without it.)
  - [x] `app/lib/queryClient.ts` + `QueryClientProvider` wrapping the root `_layout.tsx`
  - [x] `app/lib/apiClient.ts` (`postJson` + `EXPO_PUBLIC_API_URL`, falls back to `http://localhost:3000`) and `app/hooks/useAuthMutations.ts` (`useSignupMutation` / `useLoginMutation`, `onSuccess` writes the session into the store)
  - [x] API CORS: `cors` package, `CORS_ORIGIN` in `api/src/env.ts` (default `http://localhost:19006`), `app.use(cors(...))` in `app.ts`. `env.ts` now loads `dotenv` itself (import order bug when `app.ts` imported it first).
  - [x] `(auth)` route group (`_layout.tsx`, placeholder `login.tsx` / `signup.tsx`) + `Stack.Protected` gating in root `_layout.tsx` (`guard={!!token}` for `(tabs)`, `guard={!token}` for `(auth)`, `return null` until `hasHydrated`). Verified in headless Edge: logged-out lands on Login.
  - [x] Fixed blank web screen: zustand's middleware build uses `import.meta.env`, which Metro's web bundle can't parse — added `app/babel.config.js` with `unstable_transformImportMeta: true`
  - [x] Pinned `@react-native-async-storage/async-storage` to `2.2.0` via `npx expo install` (Expo SDK 54's expected version; v3.x was installed first)
  - [ ] actual login/signup screen UI (forms, `isPending`/`error` display, link between screens) — **next**; first real end-to-end test of the mutations + CORS
  - [ ] verify the logged-in side of the gate (tabs reachable with a token, back to login after `clearSession()`)
  - [x] committed and pushed (2026-09-19)
  - [x] Dev-server gotcha: after any dependency change, restart Expo with `--clear` (Metro cached a stale `node_modules` map after the AsyncStorage downgrade → "Unable to resolve module merge-options" → JSON bundle error → blank page)
- [ ] Client: PIN unlock screen gating the Settings tab
- [ ] Client: `AppState` re-lock on backgrounding

## Environment setup on Linux host (2026-09-19, second session)
- [x] Fresh checkout had no `node_modules` / `api/.env` — ran `npm install` (823 packages), wrote gitignored `api/.env` (`DATABASE_URL`, random `JWT_SECRET`, `CORS_ORIGIN`)
- [x] Dependency audit: all imports declared, `expo install --check` clean, `tsc` clean in api/app/shared
- [x] Docker daemon enabled + `melz` added to `docker` group; Postgres up, API boots, migrations applied, CORS preflight verified
- [ ] Rewrite `session-start` / `restore-project` / `backup-projects` skills for Linux (they are PowerShell + Windows/NAS paths)
- [ ] Mount the NAS share (`\\RASPBERRYPI\Data-NAS`) on this host so backup/restore can run
- [ ] `npm audit` reports 20 vulns (9 high), mostly inside Expo's tree — revisit on next Expo SDK bump, don't `--force`

## Also done this session (not phase-numbered)
- [x] Build Ledger artifact (https://claude.ai/artifact/XsCEU2QLwnw5h8QYb5FFkZ) restructured into a navigable guide: build order, architecture, stack, 5 build parts, troubleshooting, command reference (No. 001–026). Keep appending to it as new features land (login/signup forms, PIN unlock, re-lock).
- [x] Prettier + format-on-save, matching `chores-chart`/`meal-planner` convention
- [x] GitHub repo created (`Melz8bit/digital-bank`, public, no license) and pushed

## Open nice-to-haves
- [ ] Add `"lib": ["ES2020"]` to `api/tsconfig.json` to remove accidental DOM globals (see the `parent` bug, Build Ledger No. 019) — flagged twice now, still not applied

## Not started
- [ ] Phase 2 — core deposit/withdrawal flows + dashboard
- [ ] Phase 3 — settings completeness + multi-child + family/invite (this is where `invite_codes` table + the stubbed `INVITE_SIGNUP_NOT_IMPLEMENTED` branch in `signup()` get filled in for real)
- [ ] Phase 4 — Pi deployment
- [ ] Phase 5 — stretch goals
