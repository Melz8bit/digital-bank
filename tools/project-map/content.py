# Text content for the project map. Plain-language explanations per file.
# Each file: path, what (what it does), why (why we need it), also (connections that
# aren't imports: HTTP calls, config, files read). Imports / used-by come from edges.json.

SECTIONS = [
    {
        "id": "root",
        "title": "The repository root",
        "ws": "root",
        "intro": (
            "The top folder ties the three parts together. It doesn't hold app code itself: it holds the "
            "settings that make <b>app</b>, <b>api</b> and <b>packages/shared</b> behave like one project, "
            "and the files that keep every machine set up the same way."
        ),
        "files": [
            {
                "path": "package.json",
                "what": "Declares the three <b>npm workspaces</b> (<font face='Mono'>app</font>, <font face='Mono'>api</font>, "
                        "<font face='Mono'>packages/shared</font>). One <font face='Mono'>npm install</font> here installs "
                        "all three and links the shared package into <font face='Mono'>node_modules/@digital-bank/shared</font>. "
                        "Also holds Prettier for the whole repo.",
                "why": "Without workspaces, the app and the API couldn't import <font face='Mono'>@digital-bank/shared</font> "
                       "without publishing it to npm first.",
                "also": ["Links: <font face='Mono'>app/package.json</font>, <font face='Mono'>api/package.json</font>, "
                         "<font face='Mono'>packages/shared/package.json</font>"],
            },
            {
                "path": "package-lock.json",
                "what": "The exact version of every installed package (about 12,000 lines). Written by npm, never by hand.",
                "why": "Every machine (Windows, Linux, later the Pi) installs identical versions, so \"works on my machine\" "
                       "stays true everywhere. <i>Note: this Linux machine's npm 9.2.0 rewrites it, so check "
                       "<font face='Mono'>git status</font> after installs.</i>",
            },
            {
                "path": ".gitignore",
                "what": "Lists what git must never track: <font face='Mono'>node_modules/</font>, every <font face='Mono'>.env</font> "
                        "file, Expo's build output, <font face='Mono'>api/dist/</font>, signing keys.",
                "why": "Secrets (database password, JWT secret) must never reach GitHub, and generated folders are huge "
                       "and can be rebuilt with <font face='Mono'>npm install</font>.",
            },
            {
                "path": ".prettierrc",
                "what": "The formatting rules: single quotes, semicolons, 2-space indents, 100-character lines.",
                "why": "VS Code (Windows) and LazyVim (Linux) both read it, so code looks the same whichever editor saved it.",
                "also": ["Read by: <font face='Mono'>.vscode/settings.json</font> (format on save), LazyVim's prettier extra"],
            },
            {
                "path": "compose.dev.yml",
                "what": "A Docker Compose file that runs Postgres 16 in a local container.",
                "why": "This was the first dev database. Since 2026-09-30 the shared dev database lives on the Pi, "
                       "so this is now an <b>offline fallback</b> (normally stopped).",
            },
            {
                "path": ".vscode/settings.json",
                "what": "VS Code settings: format with Prettier on every save.",
                "why": "Editor setup for the Windows machine. LazyVim does the same thing on Linux.",
            },
            {
                "path": ".claude/todo.md  +  .claude/session-logs/",
                "what": "Your project diary: the running todo list and one log per working day.",
                "why": "<font face='Mono'>session-start</font> reads them to pick up where you left off, and "
                       "<font face='Mono'>session-end</font> writes them. Not code: nothing imports them.",
            },
        ],
    },
    {
        "id": "shared",
        "title": "packages/shared: the common language",
        "ws": "shared",
        "intro": (
            "The small package that <b>both</b> the app and the API import. It holds the things both sides must agree on: "
            "what valid input looks like, what responses look like, and how money is handled. "
            "The golden rule: <b>shared imports nothing from app or api</b>. Arrows only point <i>into</i> it."
        ),
        "files": [
            {
                "path": "packages/shared/package.json",
                "what": "Names the package <font face='Mono'>@digital-bank/shared</font>. <font face='Mono'>main</font> and "
                        "<font face='Mono'>types</font> point straight at <font face='Mono'>src/index.ts</font>. Depends on zod.",
                "why": "Pointing at the TypeScript source means there's <b>no build step</b>: the API (via tsx) and the app "
                       "(via Metro) read the .ts files directly.",
            },
            {
                "path": "packages/shared/tsconfig.json",
                "what": "TypeScript settings for checking the shared code by itself.",
                "why": "Lets you run <font face='Mono'>npx tsc --noEmit -p packages/shared</font> to type-check just this package.",
            },
            {
                "path": "packages/shared/src/index.ts",
                "what": "The front door: re-exports everything from <font face='Mono'>types</font>, "
                        "<font face='Mono'>schemas</font> and <font face='Mono'>money</font>.",
                "why": "Other files write <font face='Mono'>from '@digital-bank/shared'</font> without needing to know "
                       "which internal file something lives in.",
            },
            {
                "path": "packages/shared/src/schemas.ts",
                "what": "zod schemas, plus the TypeScript types inferred from them: <font face='Mono'>SignupInput</font> "
                        "(exactly one of family name / invite code), <font face='Mono'>LoginInput</font>, "
                        "<font face='Mono'>PinInput</font> (4 digits), <font face='Mono'>CreateChildInput</font>, "
                        "<font face='Mono'>TransactionInput</font> (deposit needs a category; withdrawal needs a comment).",
                "why": "One definition of \"valid input\" used on both sides. The API checks every request with "
                       "<font face='Mono'>safeParse</font>, and the app's hooks use the same types, so the form and "
                       "the server can never disagree about the rules.",
            },
            {
                "path": "packages/shared/src/types.ts",
                "what": "The shapes of API <b>responses</b>: <font face='Mono'>Child</font> and "
                        "<font face='Mono'>Transaction</font>. Dates are typed as <font face='Mono'>string</font>. "
                        "<i>Written 2026-10-14 (Step 6).</i>",
                "why": "So the app's hooks know exactly what JSON comes back. Hand-written instead of imported from the "
                       "API's Drizzle schema, because shared must never depend on api. Dates are strings because "
                       "JSON has no date type.",
            },
            {
                "path": "packages/shared/src/money.ts",
                "what": "<font face='Mono'>toCents</font>, <font face='Mono'>fromCents</font>, "
                        "<font face='Mono'>formatCents</font> (turns 1250 into \"$12.50\").",
                "why": "All money is stored as <b>whole cents</b> (integers), because decimals in JavaScript round badly "
                       "(0.1 + 0.2 = 0.30000000000000004). <i>Not used yet: the dashboard (Step 7) and the deposit "
                       "screen (Step 8) will be the first users.</i>",
            },
        ],
    },
    {
        "id": "api",
        "title": "api/: the server",
        "ws": "api",
        "intro": (
            "An Express server in Node. It's the only part that touches the database, and the only part that can be "
            "trusted, because a phone or browser can be tampered with. Requests flow through it in layers: "
            "<b>app.ts</b> picks a router by URL, <b>middleware</b> checks the login token, <b>routes</b> speak HTTP "
            "(status codes, request and response), <b>services</b> apply the business rules, and <b>db/</b> talks to Postgres."
        ),
        "subs": [
            ("Configuration and startup", [
                {
                    "path": "api/package.json",
                    "what": "The API's dependencies (express, drizzle-orm, pg, bcrypt, jsonwebtoken, cors, dotenv, zod) and "
                            "scripts. <font face='Mono'>npm run dev</font> = <font face='Mono'>tsx watch</font>, which restarts "
                            "the server on every save.",
                    "why": "tsx runs TypeScript directly, with no build step while developing. Remember it does <b>not</b> "
                           "type-check: run <font face='Mono'>npx tsc --noEmit -p api</font> for that.",
                },
                {
                    "path": "api/tsconfig.json",
                    "what": "TypeScript settings for the server (strict mode, CommonJS modules).",
                    "why": "<font face='Mono'>tsc</font> uses it to check and build. <i>It has no <font face='Mono'>lib</font> "
                           "setting, so browser (DOM) types leak in. That's the \"add lib ES2020\" todo item.</i>",
                },
                {
                    "path": "api/.env   (not in git)",
                    "what": "Secrets and settings: <font face='Mono'>DATABASE_URL</font> (the Pi database), "
                            "<font face='Mono'>JWT_SECRET</font>, <font face='Mono'>CORS_ORIGIN</font>.",
                    "why": "Keeps passwords out of the code and out of GitHub. Each machine has its own copy. "
                           "Rebuilt from the Pi on 2026-10-14.",
                    "also": ["Read by: <font face='Mono'>env.ts</font>, <font face='Mono'>db/client.ts</font>, "
                             "<font face='Mono'>drizzle.config.ts</font> (via dotenv)"],
                },
                {
                    "path": "api/drizzle.config.ts",
                    "what": "Settings for the <b>drizzle-kit command-line tool</b> (not the running server): where the schema "
                            "is, where migrations go, which database to use.",
                    "why": "When you change <font face='Mono'>schema.ts</font>, <font face='Mono'>npx drizzle-kit generate</font> "
                           "compares it with the last snapshot and writes a new SQL migration file.",
                    "also": ["Reads: <font face='Mono'>src/db/schema.ts</font>", "Writes: <font face='Mono'>src/db/migrations/</font>"],
                },
                {
                    "path": "api/src/index.ts",
                    "what": "The entry point. Runs any pending database migrations, <i>then</i> starts listening on port 3000.",
                    "why": "Migrating first means the tables always match the code before the first request arrives. It's "
                           "kept separate from <font face='Mono'>app.ts</font> so the app can be built without opening a port "
                           "(handy for tests later).",
                },
                {
                    "path": "api/src/app.ts",
                    "what": "Builds the Express app: CORS (only the Expo web address may call it), JSON body parsing, then mounts "
                            "the routers at <font face='Mono'>/auth</font>, <font face='Mono'>/pin</font>, "
                            "<font face='Mono'>/children</font>, plus <font face='Mono'>GET /health</font>.",
                    "why": "It's the switchboard: the first part of the URL decides which routes file handles the request.",
                },
                {
                    "path": "api/src/env.ts",
                    "what": "Loads <font face='Mono'>.env</font>, then exports <font face='Mono'>JWT_SECRET</font> (the server "
                            "refuses to start without it) and <font face='Mono'>CORS_ORIGIN</font> (with a default).",
                    "why": "One place for configuration. It was pulled out of authService so that "
                           "<font face='Mono'>requireAuth</font> uses the <i>same</i> secret check.",
                },
            ]),
            ("Security: who is asking?", [
                {
                    "path": "api/src/middleware/requireAuth.ts",
                    "what": "The doorman. Reads the <font face='Mono'>Authorization: Bearer &lt;token&gt;</font> header, verifies "
                            "the JWT with <font face='Mono'>JWT_SECRET</font>, puts the parent's id on "
                            "<font face='Mono'>req.parentId</font>, then lets the request through. Otherwise it replies 401.",
                    "why": "Every protected route needs to know which parent is calling. Doing it once here means no route can "
                           "forget to check.",
                },
                {
                    "path": "api/src/types/express.d.ts",
                    "what": "Teaches TypeScript that Express requests can have a <font face='Mono'>parentId</font> property "
                            "(\"declaration merging\").",
                    "why": "Without it, <font face='Mono'>req.parentId</font> would be a type error. It has no imports: TypeScript "
                           "picks it up globally, which is why it shows as a dotted link on the map.",
                    "also": ["Gives types to: <font face='Mono'>requireAuth.ts</font> and every route that reads "
                             "<font face='Mono'>req.parentId</font>"],
                },
            ]),
            ("Routes: the HTTP layer", [
                {
                    "path": "api/src/routes/auth.routes.ts",
                    "what": "<font face='Mono'>POST /auth/signup</font> and <font face='Mono'>POST /auth/login</font>. "
                            "Each one validates the body (400 with a readable message), calls authService, and turns its error "
                            "codes into status codes: 409 email taken, 501 invite signup, 401 bad login.",
                    "why": "This is the only router without <font face='Mono'>requireAuth</font>: you can't have a token before "
                           "you've logged in.",
                    "also": ["Called over HTTP by: <font face='Mono'>app/hooks/useAuthMutations.ts</font>"],
                },
                {
                    "path": "api/src/routes/pin.routes.ts",
                    "what": "<font face='Mono'>GET /pin/status</font>, <font face='Mono'>POST /pin/set</font>, "
                            "<font face='Mono'>POST /pin/verify</font>, each behind requireAuth. Maps PIN errors to 409 (not set or "
                            "already set), 423 (locked) and 401 (wrong PIN).",
                    "why": "The PIN keeps kids out of the parent-only parts of the app.",
                    "also": ["Called over HTTP by: <font face='Mono'>app/hooks/usePinMutations.ts</font>"],
                },
                {
                    "path": "api/src/routes/children.routes.ts",
                    "what": "<font face='Mono'>router.use(requireAuth)</font> protects everything in it. "
                            "<font face='Mono'>GET</font>/<font face='Mono'>POST /children</font> and "
                            "<font face='Mono'>GET</font>/<font face='Mono'>POST /children/:childId/transactions</font>. "
                            "<font face='Mono'>ChildIdSchema</font> turns a malformed id into a clean 404. A refused withdrawal "
                            "gets a 422 with a kid-friendly message.",
                    "why": "The money routes. It imports <font face='Mono'>db</font> directly only to pass it into "
                           "<font face='Mono'>getBalance</font> and <font face='Mono'>listRecentTransactions</font> as the "
                           "\"executor\" (the thing that runs the queries).",
                    "also": ["Called over HTTP by: <font face='Mono'>app/hooks/useTransactions.ts</font>"],
                },
            ]),
            ("Services: the business rules", [
                {
                    "path": "api/src/services/authService.ts",
                    "what": "<font face='Mono'>signup</font>: checks the email isn't taken, hashes the password with bcrypt, and "
                            "creates the family and parent together in one database transaction. <font face='Mono'>login</font>: "
                            "checks the password with bcrypt. Both return a JWT that lasts 30 days.",
                    "why": "Passwords are never stored, only hashes. Unknown email and wrong password give the <i>same</i> "
                           "error, so nobody can probe which emails have accounts.",
                },
                {
                    "path": "api/src/services/familyService.ts",
                    "what": "<font face='Mono'>getFamilyForParent(parentId)</font>: looks up the parent, then their family.",
                    "why": "The family is the security boundary: every child or PIN action first asks \"which family is "
                           "yours?\". It was pulled out of pinService so three services can share it.",
                },
                {
                    "path": "api/src/services/pinService.ts",
                    "what": "PIN status, set (once only) and verify. Five wrong tries lock it for 5 minutes "
                            "(<font face='Mono'>pinAttempts</font> / <font face='Mono'>pinLockedUntil</font> on families).",
                    "why": "The PIN belongs to the family, not to each parent, so a co-parent uses the same one. The lockout "
                           "stops a kid from guessing all 10,000 combinations.",
                },
                {
                    "path": "api/src/services/childService.ts",
                    "what": "<font face='Mono'>createChild</font>, <font face='Mono'>listChildren</font> (not archived, oldest "
                            "first) and <font face='Mono'>getChildForParent</font> (the ownership check: throws "
                            "<font face='Mono'>CHILD_NOT_FOUND</font> for anyone else's child).",
                    "why": "Every query is filtered by family id, so one family can never see or touch another family's kids.",
                },
                {
                    "path": "api/src/services/transactionService.ts",
                    "what": "<font face='Mono'>getBalance</font>: deposits minus withdrawals (the balance is <b>calculated, "
                            "never stored</b>). <font face='Mono'>listRecentTransactions</font>: the newest 20. "
                            "<font face='Mono'>createTransaction</font>: locks the child's row, checks the spending cap, then "
                            "the balance, then inserts.",
                    "why": "The row lock (<font face='Mono'>FOR UPDATE</font>) makes simultaneous withdrawals wait their turn, "
                           "which you tested: 5 at once on $10 gave exactly 3 successes. Calculating the balance means it can "
                           "never drift out of step with the transaction history.",
                },
            ]),
            ("Database", [
                {
                    "path": "api/src/db/schema.ts",
                    "what": "The four tables written in TypeScript: <font face='Mono'>families</font>, "
                            "<font face='Mono'>parents</font>, <font face='Mono'>children</font>, "
                            "<font face='Mono'>transactions</font>. Also their links (family_id foreign keys), CHECK rules "
                            "(amount &gt; 0; type is deposit or withdrawal) and an index for \"newest transactions per child\".",
                    "why": "The single source of truth for the database. Drizzle uses it to type every query, and drizzle-kit "
                           "uses it to write migrations.",
                },
                {
                    "path": "api/src/db/client.ts",
                    "what": "Opens a pool of Postgres connections from <font face='Mono'>DATABASE_URL</font> and creates the "
                            "Drizzle <font face='Mono'>db</font> object.",
                    "why": "One shared pool for the whole server. Every service imports <font face='Mono'>db</font> from here "
                           "instead of opening its own connection.",
                    "also": ["Connects to: Postgres on the Pi (192.168.1.73:5432)"],
                },
                {
                    "path": "api/src/db/migrate.ts",
                    "what": "Applies any migration files the database hasn't seen yet. Drizzle records which ones ran in a table "
                            "of its own.",
                    "why": "Called by <font face='Mono'>index.ts</font> on every start, so a new migration is applied automatically. "
                           "<i>Its folder path is relative, so start the API from <font face='Mono'>api/</font> (which "
                           "<font face='Mono'>npm run dev</font> does).</i>",
                    "also": ["Reads: <font face='Mono'>src/db/migrations/</font>"],
                },
                {
                    "path": "api/src/db/migrations/  (2 .sql files + meta/)",
                    "what": "<font face='Mono'>0000_soft_the_anarchist.sql</font> creates families and parents (Phase 1). "
                            "<font face='Mono'>0001_premium_landau.sql</font> creates children and transactions (Phase 2). "
                            "<font face='Mono'>meta/</font> holds drizzle-kit's bookkeeping: the order of migrations and a "
                            "snapshot of the schema after each one.",
                    "why": "Migrations are the step-by-step history of the database, so any empty database (a new machine, "
                           "the Pi in Phase 4) can be built up to today's shape. Generated files with random names: never edit "
                           "them by hand. <i>tsx watch doesn't notice new ones, so restart the API.</i>",
                },
            ]),
        ],
    },
    {
        "id": "app",
        "title": "app/: the Expo app",
        "ws": "app",
        "intro": (
            "The React Native app, built with Expo. It runs on the web now and on Android later. It holds no secrets and "
            "makes no money decisions: it shows data and sends requests. It uses two kinds of state: <b>server data</b> "
            "(balances, PIN status) lives in React Query's cache, and <b>app-only state</b> (your login token, whether the "
            "PIN is unlocked) lives in small zustand stores."
        ),
        "subs": [
            ("Configuration", [
                {
                    "path": "app/package.json",
                    "what": "Expo SDK 54, React Native 0.81, expo-router, React Query, zustand, AsyncStorage (pinned at 2.2.0 "
                            "for SDK 54). <font face='Mono'>\"main\": \"expo-router/entry\"</font> means Expo Router starts the "
                            "app from the <font face='Mono'>app/app/</font> folder.",
                    "why": "The scripts pin port 19006, because 5173 belongs to another project.",
                },
                {
                    "path": "app/app.json",
                    "what": "Expo's app settings: the name, the <font face='Mono'>digitalbank://</font> link scheme, the Android "
                            "package id, the Metro bundler for web, the expo-router plugin.",
                    "why": "Expo reads this to know how to build and run the app on each platform.",
                },
                {
                    "path": "app/tsconfig.json",
                    "what": "Builds on Expo's TypeScript settings and defines the <font face='Mono'>@/</font> shortcut, which "
                            "points at the <font face='Mono'>app/</font> folder.",
                    "why": "<font face='Mono'>@/lib/apiClient</font> reads better than <font face='Mono'>../../lib/apiClient</font> "
                           "and doesn't break when files move.",
                },
                {
                    "path": "app/babel.config.js",
                    "what": "Expo's Babel preset with <font face='Mono'>unstable_transformImportMeta</font> switched on.",
                    "why": "This fixes the blank web screen: zustand uses <font face='Mono'>import.meta</font>, which Metro's "
                           "web bundle couldn't read until this setting was added.",
                },
            ]),
            ("Screens: app/app/ (Expo Router)", [
                {
                    "path": "app/app/_layout.tsx",
                    "what": "The root of every screen. It wraps the app in <font face='Mono'>QueryClientProvider</font>, shows "
                            "nothing until the saved login has loaded, then uses <font face='Mono'>Stack.Protected</font> to "
                            "decide: token means <font face='Mono'>(tabs)</font>, no token means "
                            "<font face='Mono'>(auth)</font>. Also starts <font face='Mono'>useAutoLock</font>.",
                    "why": "This is the login gate for the whole app. <b>File-based routing:</b> files under "
                           "<font face='Mono'>app/app/</font> <i>are</i> the screens. Folders in (parentheses) group screens "
                           "without changing the URL, and a <font face='Mono'>_layout.tsx</font> wraps the screens in its folder. "
                           "<i>Route files must live under app/app/, not app/ (the September stray-folder gotcha).</i>",
                },
                {
                    "path": "app/app/(auth)/_layout.tsx",
                    "what": "A plain screen stack, with no headers, for login and signup.",
                    "why": "Groups the logged-out screens so the root layout can show or hide them together.",
                },
                {
                    "path": "app/app/(auth)/login.tsx",
                    "what": "The email and password form. It calls <font face='Mono'>useLoginMutation</font>, shows "
                            "\"Logging in...\" while waiting and the error message if login fails, and links to signup.",
                    "why": "How a parent gets a token.",
                },
                {
                    "path": "app/app/(auth)/signup.tsx",
                    "what": "A \"Create a family\" / \"Join with invite code\" toggle, plus email and password.",
                    "why": "Creates the family and the first parent. The invite branch gets a 501 until Phase 3.",
                },
                {
                    "path": "app/app/(tabs)/_layout.tsx",
                    "what": "The bottom tab bar: Home and Settings, with icons.",
                    "why": "The main navigation once logged in.",
                },
                {
                    "path": "app/app/(tabs)/index.tsx",
                    "what": "The Home tab. Currently a placeholder.",
                    "why": "<b>Step 7 builds the dashboard here</b>, using <font face='Mono'>useChildrenQuery</font>, "
                           "<font face='Mono'>useTransactionsQuery</font> and <font face='Mono'>formatCents</font>.",
                },
                {
                    "path": "app/app/(tabs)/settings.tsx",
                    "what": "A PIN gate with three states: <i>set a PIN</i>, then <i>enter the PIN</i>, then the real settings. "
                            "After a PIN is set it refreshes <font face='Mono'>['pinStatus']</font>, and it clears the box "
                            "after every attempt.",
                    "why": "Keeps parent settings (caps, children, invites) away from kids.",
                },
            ]),
            ("Hooks: how screens talk to the server", [
                {
                    "path": "app/hooks/useAuthMutations.ts",
                    "what": "<font face='Mono'>useSignupMutation</font> and <font face='Mono'>useLoginMutation</font>. When either "
                            "succeeds, it saves the token and parent into authStore.",
                    "why": "Screens just call <font face='Mono'>mutate(...)</font>. The hook handles the request and saving the "
                           "session.",
                    "also": ["HTTP to: <font face='Mono'>api/src/routes/auth.routes.ts</font>"],
                },
                {
                    "path": "app/hooks/usePinMutations.ts",
                    "what": "<font face='Mono'>usePinStatusQuery</font> (a read, so <font face='Mono'>useQuery</font>) and "
                            "<font face='Mono'>useSetPinMutation</font> / <font face='Mono'>useVerifyPinMutation</font>.",
                    "why": "Same pattern for the PIN routes. <i>Reads are queries, changes are mutations.</i>",
                    "also": ["HTTP to: <font face='Mono'>api/src/routes/pin.routes.ts</font>"],
                },
                {
                    "path": "app/hooks/useTransactions.ts",
                    "what": "<font face='Mono'>useChildrenQuery</font>, <font face='Mono'>useTransactionsQuery(childId)</font> "
                            "(waits until a child is known) and <font face='Mono'>useCreateTransactionMutation(childId)</font>, "
                            "which marks that child's data stale after success so the balance refreshes. "
                            "<i>Written 2026-10-14 (Step 6).</i>",
                    "why": "The bridge between the money screens (Steps 7 and 8) and the money routes. The cache key "
                           "<font face='Mono'>['transactions', childId]</font> is what links the mutation to the query.",
                    "also": ["HTTP to: <font face='Mono'>api/src/routes/children.routes.ts</font>"],
                },
                {
                    "path": "app/hooks/useAutoLock.ts",
                    "what": "Watches <font face='Mono'>AppState</font>. As soon as the app stops being active (switched away, "
                            "browser tab hidden), it locks the PIN.",
                    "why": "A parent who unlocks Settings and hands the phone to a kid isn't leaving it unlocked.",
                },
            ]),
            ("lib/ and store/: plumbing and memory", [
                {
                    "path": "app/lib/apiClient.ts",
                    "what": "The <b>only</b> file that calls <font face='Mono'>fetch</font>. It knows the API's address "
                            "(<font face='Mono'>EXPO_PUBLIC_API_URL</font> or localhost:3000). <font face='Mono'>handleResponse</font> "
                            "turns error replies into <font face='Mono'>Error(message)</font>. "
                            "<font face='Mono'>postJson</font> sends no token; <font face='Mono'>getJsonAuth</font> and "
                            "<font face='Mono'>postJsonAuth</font> attach the token from authStore.",
                    "why": "One place for the address, headers and error handling. That error message is what every form "
                           "shows, which is why readable 400 messages matter.",
                    "also": ["HTTP to: the API on port 3000"],
                },
                {
                    "path": "app/lib/queryClient.ts",
                    "what": "Creates the one React Query cache for the whole app.",
                    "why": "<font face='Mono'>_layout.tsx</font> provides it to every screen. Invalidating a key affects every "
                           "screen using that key.",
                },
                {
                    "path": "app/store/authStore.ts",
                    "what": "A zustand store holding the token and parent, saved to AsyncStorage under "
                            "<font face='Mono'>auth-storage</font>. <font face='Mono'>hasHydrated</font> becomes true once the "
                            "saved copy has loaded.",
                    "why": "You stay logged in across reloads. AsyncStorage was chosen because it also works on the web, where "
                           "expo-secure-store doesn't.",
                },
                {
                    "path": "app/store/pinStore.ts",
                    "what": "One <font face='Mono'>unlocked</font> true/false value with <font face='Mono'>unlock()</font> and "
                            "<font face='Mono'>lock()</font>. Deliberately <b>not</b> saved.",
                    "why": "Every restart starts locked, so the PIN unlock only lasts one session.",
                },
            ]),
        ],
    },
]

NOT_IN_GIT = [
    ("node_modules/", "Every installed package, rebuilt by <font face='Mono'>npm install</font>. "
     "<font face='Mono'>node_modules/@digital-bank/shared</font> is a <i>link</i> back to "
     "<font face='Mono'>packages/shared</font>, which is how the imports resolve. "),
    ("api/.env", "The API's secrets (see the API section)."),
    ("app/.expo/", "Expo's cache and generated route types. Safe to delete; Expo recreates it."),
]

FINDINGS = [
    ("api/src/services/transactionService.ts:6",
     "<font face='Mono'>import { error } from 'console';</font> is never used. It's probably an accidental editor "
     "auto-import, and it's safe to delete."),
    ("api/src/services/familyService.ts",
     "It assumes the parent exists. A valid token for a parent who has since been deleted would crash with a "
     "TypeError, giving a generic 500 instead of a 401. Worth handling when \"remove co-parent\" arrives in Phase 3."),
    ("packages/shared/src/money.ts",
     "Nothing imports it yet. It has no arrows on the map, and the dashboard in Step 7 will be its first user."),
    ("app/app/(tabs)/_layout.tsx, index.tsx, db/client.ts, shared index.ts, money.ts",
     "These 5 files predate Prettier (they use double quotes). They're already on the todo list as a formatting-only commit."),
    ("app/package.json vs api/package.json",
     "The app asks for shared as <font face='Mono'>\"^0.0.0\"</font> and the API as <font face='Mono'>\"*\"</font>. "
     "Both work with workspaces, so it's cosmetic only."),
]
