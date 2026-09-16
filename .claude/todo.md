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
- [x] `requireAuth` middleware (`api/src/middleware/requireAuth.ts`) — Bearer header parsing, `jwt.verify` in try/catch, guards against string-payload and missing-`sub` cases, sets `req.parentId` via `express.d.ts` declaration-merge augmentation. Typechecks clean; not yet exercised against a live route (no routes wired up yet).
- [x] `env.ts` — extracted `JWT_SECRET` guard out of `authService.ts` into its own module so `authService` and `requireAuth` share one source instead of duplicating the check
- [ ] `auth.routes.ts` — wire signup/login to real HTTP endpoints
  - [x] `POST /signup` — validates with `SignupInputSchema`, calls `authService.signup()`, maps `EMAIL_TAKEN`→409 / `INVITE_SIGNUP_NOT_IMPLEMENTED`→501 / unknown→500 with real messages. Typechecks clean; not yet hit with a live HTTP request (router isn't mounted in `app.ts` yet).
  - [ ] `POST /login` — next up, same shape as signup (validate with `LoginInputSchema`, call `authService.login()`, map `INVALID_CREDENTIALS`→401)
  - [ ] mount the router in `app.ts` (e.g. `app.use('/auth', authRouter)`)
  - [ ] verify both endpoints end-to-end with real HTTP requests (curl/Postman) against the real dev DB
- [ ] PIN set/verify endpoints + rate limiting (`pin_attempts`/`pin_locked_until` lockout)
- [ ] Client: login/signup screens wired via React Query + `useAuthStore`
- [ ] Client: PIN unlock screen gating the Settings tab
- [ ] Client: `AppState` re-lock on backgrounding

## Also done this session (not phase-numbered)
- [x] Prettier + format-on-save, matching `chores-chart`/`meal-planner` convention
- [x] GitHub repo created (`Melz8bit/digital-bank`, public, no license) and pushed

## Not started
- [ ] Phase 2 — core deposit/withdrawal flows + dashboard
- [ ] Phase 3 — settings completeness + multi-child + family/invite (this is where `invite_codes` table + the stubbed `INVITE_SIGNUP_NOT_IMPLEMENTED` branch in `signup()` get filled in for real)
- [ ] Phase 4 — Pi deployment
- [ ] Phase 5 — stretch goals
