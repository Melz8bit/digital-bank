"""Full-project map on an 11x17 landscape page.

Boxes sit on a column/row grid. Edges are routed orthogonally through the gaps between columns
and the channels between rows, so no line ever passes through a box. Parallel lines in the same
gap/channel get their own lane (greedy interval colouring)."""
import math
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white

W, H = 1224, 792
COLS = 8
BOX_W, BOX_H = 116, 36
LEFT = 30
GAP = (W - 2 * LEFT - 26 - COLS * BOX_W) / (COLS - 1)
ROW0 = 168
PITCH = 72
LANE = 3.4

# key: (label, sub, ws, col, row)
NODES = {
    'app/app/_layout.tsx':           ('_layout.tsx', 'app/app/  root layout', 'app', 0, 0),
    'app/app/(auth)/_layout.tsx':    ('_layout.tsx', 'app/app/(auth)/', 'app', 0, 1),
    'app/app/(auth)/login.tsx':      ('login.tsx', 'app/app/(auth)/', 'app', 0, 2),
    'app/app/(auth)/signup.tsx':     ('signup.tsx', 'app/app/(auth)/', 'app', 0, 3),
    'app/app/(tabs)/_layout.tsx':    ('_layout.tsx', 'app/app/(tabs)/  tab bar', 'app', 0, 4),
    'app/app/(tabs)/index.tsx':      ('index.tsx', 'app/app/(tabs)/  Home', 'app', 0, 5),
    'app/app/(tabs)/settings.tsx':   ('settings.tsx', 'app/app/(tabs)/  PIN gate', 'app', 0, 6),
    'app/hooks/useAutoLock.ts':      ('useAutoLock.ts', 'app/hooks/', 'app', 1, 0),
    'app/hooks/useAuthMutations.ts': ('useAuthMutations.ts', 'app/hooks/', 'app', 1, 2),
    'app/hooks/useTransactions.ts':  ('useTransactions.ts', 'app/hooks/  Step 6', 'app', 1, 5),
    'app/hooks/usePinMutations.ts':  ('usePinMutations.ts', 'app/hooks/', 'app', 1, 6),
    'app/store/pinStore.ts':         ('pinStore.ts', 'app/store/  not saved', 'app', 2, 0),
    'app/lib/queryClient.ts':        ('queryClient.ts', 'app/lib/  RQ cache', 'app', 2, 1),
    'app/lib/apiClient.ts':          ('apiClient.ts', 'app/lib/  only fetch()', 'app', 2, 2),
    'app/store/authStore.ts':        ('authStore.ts', 'app/store/  saved token', 'app', 2, 3),
    'packages/shared/src/index.ts':  ('index.ts', 'shared/src/  front door', 'shared', 3, 3),
    'packages/shared/src/schemas.ts': ('schemas.ts', 'shared/src/  zod rules', 'shared', 3, 4),
    'packages/shared/src/types.ts':  ('types.ts', 'shared/src/  Step 6', 'shared', 3, 5),
    'packages/shared/src/money.ts':  ('money.ts', 'shared/src/  not used yet', 'shared', 3, 6),
    'api/src/index.ts':              ('index.ts', 'api/src/  entry point', 'api', 4, 0),
    'api/src/app.ts':                ('app.ts', 'api/src/  switchboard', 'api', 4, 1),
    'api/src/env.ts':                ('env.ts', 'api/src/  reads .env', 'api', 4, 2),
    'api/src/types/express.d.ts':    ('express.d.ts', 'api/src/types/', 'api', 4, 4),
    'api/src/routes/auth.routes.ts': ('auth.routes.ts', 'api/src/routes/  /auth', 'api', 5, 0),
    'api/src/routes/pin.routes.ts':  ('pin.routes.ts', 'api/src/routes/  /pin', 'api', 5, 1),
    'api/src/routes/children.routes.ts': ('children.routes.ts', 'api/src/routes/  /children', 'api', 5, 2),
    'api/src/middleware/requireAuth.ts': ('requireAuth.ts', 'api/src/middleware/', 'api', 5, 3),
    'api/src/services/authService.ts': ('authService.ts', 'api/src/services/', 'api', 6, 0),
    'api/src/services/pinService.ts':  ('pinService.ts', 'api/src/services/', 'api', 6, 1),
    'api/src/services/childService.ts': ('childService.ts', 'api/src/services/', 'api', 6, 2),
    'api/src/services/transactionService.ts': ('transactionService.ts', 'api/src/services/', 'api', 6, 3),
    'api/src/services/familyService.ts': ('familyService.ts', 'api/src/services/', 'api', 6, 4),
    'api/src/db/migrate.ts':         ('migrate.ts', 'api/src/db/', 'api', 7, 0),
    'api/src/db/client.ts':          ('client.ts', 'api/src/db/  the db pool', 'api', 7, 1),
    'api/src/db/schema.ts':          ('schema.ts', 'api/src/db/  4 tables', 'api', 7, 2),
    'MIGRATIONS':                    ('migrations/', 'api/src/db/  0000, 0001, meta', 'api', 7, 4),
    'api/drizzle.config.ts':         ('drizzle.config.ts', 'api/  drizzle-kit CLI', 'api', 7, 5),
    'POSTGRES':                      ('Postgres', 'on the Pi  192.168.1.73', 'ext', 7, 6),
}

EXTRA = [
    # (src, dst, kind, label)
    ('app/hooks/useAuthMutations.ts', 'api/src/routes/auth.routes.ts', 'http', 'POST /auth/signup  ·  /auth/login'),
    ('app/hooks/useTransactions.ts', 'api/src/routes/children.routes.ts', 'http', 'GET /children  ·  GET + POST /children/:id/transactions'),
    ('app/hooks/usePinMutations.ts', 'api/src/routes/pin.routes.ts', 'http', 'GET /pin/status  ·  POST /pin/set  ·  /pin/verify'),
    ('app/app/(tabs)/index.tsx', 'app/hooks/useTransactions.ts', 'planned', 'Step 7'),
    ('api/src/types/express.d.ts', 'api/src/middleware/requireAuth.ts', 'link', 'types req.parentId'),
    ('api/drizzle.config.ts', 'api/src/db/schema.ts', 'link', 'reads'),
    ('api/drizzle.config.ts', 'MIGRATIONS', 'link', 'writes'),
    ('api/src/db/migrate.ts', 'MIGRATIONS', 'link', 'applies'),
    ('api/src/db/client.ts', 'POSTGRES', 'sql', 'SQL'),
]

SAME_COL_SIDE = {3: 'left'}  # shared column: brackets on the left, api arrows arrive on the right


def col_x(c):
    return LEFT + c * (BOX_W + GAP)

def gap_x(c):
    """centre of the gap to the right of column c (c=-1 is the left margin)."""
    if c >= COLS - 1:
        return col_x(COLS - 1) + BOX_W + 15
    return col_x(c) + BOX_W + GAP / 2

def row_y(r):
    return ROW0 + r * PITCH  # top-down centre

def chan_y(k):
    return row_y(k) + PITCH / 2


def draw(path, edges, WS, HTTP, INK, MUTED, RULE, today):
    E = [(a, b, 'import', None) for a, b in edges] + EXTRA
    missing = {x for a, b, *_ in E for x in (a, b)} - set(NODES)
    if missing:
        raise SystemExit('These files are imported but have no box on the map yet. Add them to NODES in '
                         'tools/project-map/map_page.py (and a card in content.py):\n  ' + '\n  '.join(sorted(missing)))

    def box(k):
        _, _, _, c, r = NODES[k]
        x = col_x(c); y = row_y(r)
        return dict(x0=x, x1=x + BOX_W, y=y, top=y - BOX_H / 2, c=c, r=r)

    # ---- 1. route skeleton (which gaps / channels each edge uses) ----
    routes = []
    for i, (a, b, kind, label) in enumerate(E):
        s, t = box(a), box(b)
        R = dict(i=i, a=a, b=b, kind=kind, label=label, s=s, t=t)
        if kind == 'http':
            R.update(type='http', g1=s['c'], g2=t['c'] - 1, side_s='r', side_t='l')
        elif s['c'] == t['c']:
            side = SAME_COL_SIDE.get(s['c'], 'right')
            R.update(type='same', g1=s['c'] if side == 'right' else s['c'] - 1,
                     side_s='r' if side == 'right' else 'l', side_t='r' if side == 'right' else 'l')
        elif t['c'] == s['c'] + 1:
            R.update(type='adj', g1=s['c'], side_s='r', side_t='l')
        elif t['c'] == s['c'] - 1:
            R.update(type='adj', g1=t['c'], side_s='l', side_t='r')
        else:
            right = t['c'] > s['c']
            ch = s['r'] if t['r'] >= s['r'] else s['r'] - 1
            # a straight line is fine when every column in between is empty on this row
            between = range(min(s['c'], t['c']) + 1, max(s['c'], t['c']))
            occupied = {(n[3], n[4]) for n in NODES.values()}
            if s['r'] == t['r'] and all((c, s['r']) not in occupied for c in between):
                R.update(type='straight', side_s='r' if right else 'l', side_t='l' if right else 'r')
            else:
                R.update(type='long', ch=ch,
                         g1=s['c'] if right else s['c'] - 1,
                         g2=t['c'] - 1 if right else t['c'],
                         side_s='r' if right else 'l', side_t='l' if right else 'r')
        routes.append(R)

    # ---- 2. ports: one shared point per box side (split in/out when a side has both) ----
    roles = defaultdict(set)
    for R in routes:
        roles[(R['a'], R['side_s'])].add('out'); roles[(R['b'], R['side_t'])].add('in')
    def port(k, side, role):
        y = box(k)['y']
        if len(roles[(k, side)]) == 2:
            return y - 7 if role == 'out' else y + 7
        return y
    port_y = {}
    for R in routes:
        port_y[(R['i'], 's')] = port(R['a'], R['side_s'], 'out')
        port_y[(R['i'], 't')] = port(R['b'], R['side_t'], 'in')

    # ---- 3. trunks: verticals into the same port share one lane; long edges also share a source lane ----
    trunks = defaultdict(lambda: [1e9, -1e9])   # (gap, trunk key) -> [lo, hi]
    seg_trunk = {}                               # (route i, which vertical) -> (gap, trunk key)
    def use(g, key, a, b, i, which):
        t = trunks[(g, key)]; t[0] = min(t[0], a, b); t[1] = max(t[1], a, b)
        seg_trunk[(i, which)] = (g, key)
    hsegs = defaultdict(list)
    for R in routes:
        i = R['i']; ys, yt = port_y[(i, 's')], port_y[(i, 't')]
        tin = ('in', R['b'], R['side_t']); sout = ('out', R['a'], R['side_s'])
        if R['type'] in ('adj', 'same'):
            use(R['g1'], tin, ys, yt, i, 1)
        elif R['type'] == 'long':
            yc = chan_y(R['ch'])
            use(R['g1'], sout, ys, yc, i, 1)
            use(R['g2'], tin, yc, yt, i, 2)
            x1, x2 = gap_x(R['g1']), gap_x(R['g2'])
            hsegs[R['ch']].append((min(x1, x2), max(x1, x2), i))
        elif R['type'] == 'http':
            use(R['g1'], ('http', i), ROW0 - 90, ys, i, 1)
            use(R['g2'], tin, ROW0 - 90, yt, i, 2)

    def colour(items):
        """items: [(lo, hi, key)] -> {key: offset}, greedy interval colouring, lanes centred."""
        lanes, out = [], {}
        for lo, hi, key in sorted(items, key=lambda s: -(s[1] - s[0])):
            for li, lane in enumerate(lanes):
                if all(hi + 6 < a or lo - 6 > b for a, b in lane):
                    lane.append((lo, hi)); out[key] = li; break
            else:
                lanes.append([(lo, hi)]); out[key] = len(lanes) - 1
        n = len(lanes)
        return {k: (v - (n - 1) / 2) * LANE for k, v in out.items()}

    by_gap = defaultdict(list)
    for (g, key), (lo, hi) in trunks.items():
        by_gap[g].append((lo, hi, key))
    trunk_x = {}
    for g, items in by_gap.items():
        for key, off in colour(items).items():
            trunk_x[(g, key)] = gap_x(g) + off
    vx = {k: trunk_x[v] for k, v in seg_trunk.items()}
    hy = {}
    for ch, segs in hsegs.items():
        for i, off in colour(segs).items():
            hy[i] = chan_y(ch) + off
    http_lanes = [R for R in routes if R['type'] == 'http']
    for j, R in enumerate(http_lanes):
        hy[R['i']] = ROW0 - 78 + j * 13

    # ---- 4. polylines ----
    for R in routes:
        i, s, t = R['i'], R['s'], R['t']
        ys, yt = port_y[(i, 's')], port_y[(i, 't')]
        xs = s['x1'] if R['side_s'] == 'r' else s['x0']
        xt = t['x0'] if R['side_t'] == 'l' else t['x1']
        if R['type'] == 'straight':
            pts = [(xs, ys), (xt, yt)]
        elif R['type'] in ('adj', 'same'):
            x = vx[(i, 1)]; pts = [(xs, ys), (x, ys), (x, yt), (xt, yt)]
        elif R['type'] == 'long':
            x1, x2, yc = vx[(i, 1)], vx[(i, 2)], hy[i]
            pts = [(xs, ys), (x1, ys), (x1, yc), (x2, yc), (x2, yt), (xt, yt)]
        else:  # http
            x1, x2, yl = vx[(i, 1)], vx[(i, 2)], hy[i]
            pts = [(xs, ys), (x1, ys), (x1, yl), (x2, yl), (x2, yt), (xt, yt)]
        R['pts'] = pts
        R['dir'] = 1 if R['side_t'] == 'l' else -1

    # ---- 5. paint ----
    c = canvas.Canvas(path, pagesize=(W, H))
    c.setTitle('Digital Bank: full project map')
    Y = lambda y: H - y

    # title + legend
    c.setFillColor(INK); c.setFont('Sans-Bold', 20); c.drawString(LEFT, Y(42), 'Digital Bank: full project map')
    c.setFont('Sans', 9); c.setFillColor(MUTED)
    c.drawString(LEFT, Y(60), 'Every source file and every import between them (generated from the code), plus HTTP calls and '
                              'non-import links.  Arrows point from the file that uses to the file being used.  ' + today)
    lx = W - 440; ly = 34
    legend = [('import', WS['app'][0], None, 0.9, 'imports (colour = workspace of the importing file)'),
              ('http', HTTP, (5, 3), 1.5, 'HTTP request over the network'),
              ('link', MUTED, (1, 2.2), 1.0, 'non-import link (types, config, files, SQL)'),
              ('planned', HexColor('#9CA3AF'), (3, 3), 0.9, 'planned (not written yet)')]
    for j, (_, col, dash, lw, txt) in enumerate(legend):
        yy = ly + (j % 2) * 15; xx = lx + (j // 2) * 215
        c.setStrokeColor(col); c.setLineWidth(lw)
        if dash: c.setDash(*dash)
        c.line(xx, Y(yy), xx + 22, Y(yy)); c.setDash()
        c.setFillColor(INK); c.setFont('Sans', 7.4); c.drawString(xx + 28, Y(yy + 2.5), txt)

    # workspace backgrounds
    groups = [('app', 0, 2, 'app/  Expo app: screens, hooks, plumbing'),
              ('shared', 3, 3, 'packages/shared'),
              ('api', 4, 7, 'api/  Express server: entry, routes, services, database')]
    gtop = ROW0 - 104; gbot = row_y(6) + BOX_H / 2 + 16
    for ws, c0, c1, title in groups:
        col, tint, _ = WS[ws]
        x0 = col_x(c0) - GAP / 2 + 3 if c0 > 0 else col_x(0) - 12
        x1 = col_x(c1) + BOX_W + GAP / 2 - 3 if c1 < COLS - 1 else col_x(c1) + BOX_W + 26
        c.setFillColor(tint); c.setStrokeColor(tint)
        c.roundRect(x0, Y(gbot), x1 - x0, gbot - gtop, 10, stroke=0, fill=1)
        c.setFillColor(col); c.setFont('Sans-Bold', 9.5); c.drawString(x0 + 10, Y(gtop + 15), title)
    # column captions
    caps = ['screens  (app/app/)', 'hooks', 'lib + store', 'shared', 'entry + config', 'routes + middleware', 'services', 'database']
    for ci, cap in enumerate(caps):
        c.setFont('Sans-Bold', 7); c.setFillColor(MUTED); c.drawCentredString(col_x(ci) + BOX_W / 2, Y(ROW0 - 30), cap.upper())

    # edges
    def edge_style(R):
        if R['kind'] == 'http': return HTTP, 1.5, (5, 3)
        if R['kind'] == 'planned': return HexColor('#9CA3AF'), 0.9, (3, 3)
        if R['kind'] in ('link', 'sql'): return MUTED, 1.0, (1, 2.2)
        return WS[NODES[R['a']][2]][0], 0.9, None

    for R in routes:
        col, lw, dash = edge_style(R)
        c.setStrokeColor(col); c.setLineWidth(lw); c.setLineJoin(1); c.setLineCap(1)
        if dash: c.setDash(*dash)
        p = c.beginPath(); x, y = R['pts'][0]; p.moveTo(x, Y(y))
        for x, y in R['pts'][1:]: p.lineTo(x, Y(y))
        c.drawPath(p, stroke=1, fill=0); c.setDash()
        # arrow head
        x, y = R['pts'][-1]; d = R['dir']; L = 5.2
        c.setFillColor(col)
        a = c.beginPath(); a.moveTo(x, Y(y)); a.lineTo(x - d * L, Y(y) + 2.6); a.lineTo(x - d * L, Y(y) - 2.6); a.close()
        c.drawPath(a, stroke=0, fill=1)
        # source dot
        x, y = R['pts'][0]; c.circle(x, Y(y), 1.3, stroke=0, fill=1)

    # http labels (on their lane, over the shared column)
    for R in http_lanes:
        yl = hy[R['i']]; xm = col_x(3) + BOX_W / 2
        c.setFont('Mono-Bold', 6.3); tw = c.stringWidth(R['label'], 'Mono-Bold', 6.3)
        c.setFillColor(white); c.rect(xm - tw / 2 - 3, Y(yl) - 3.4, tw + 6, 7.2, stroke=0, fill=1)
        c.setFillColor(HTTP); c.drawCentredString(xm, Y(yl) - 2.2, R['label'])
    # small labels for link/planned edges, stacked next to the arrow they belong to
    by_target = defaultdict(list)
    for R in routes:
        if R['kind'] in ('link', 'sql', 'planned') and R['label']:
            by_target[(R['b'], R['side_t'])].append(R)
    c.setFont('Sans-Italic', 6.2); c.setFillColor(MUTED)
    for (_, side), lst in by_target.items():
        for j, R in enumerate(lst):
            (xa, ya), (xb, yb) = R['pts'][-2], R['pts'][-1]
            if R['type'] == 'straight':
                c.drawCentredString((xa + xb) / 2, Y(ya - 4), R['label'])
            elif side == 'r':
                lx, ly = max(p[0] for p in R['pts']) + 3, yb - 2 - j * 8
                tw = c.stringWidth(R['label'], 'Sans-Italic', 6.2)
                c.setFillColor(white); c.rect(lx - 1.5, Y(ly) - 1.8, tw + 3, 7.4, stroke=0, fill=1)
                c.setFillColor(MUTED); c.drawString(lx, Y(ly), R['label'])
            else:
                c.drawRightString(xa - 3, Y(yb + 9 + j * 8), R['label'])

    # boxes
    for k, (label, sub, ws, ci, r) in NODES.items():
        b = box(k); col, tint, _ = WS[ws]
        c.setFillColor(white); c.setStrokeColor(col); c.setLineWidth(1.1)
        if k == 'POSTGRES':
            c.setFillColor(HexColor('#F8FAFC'))
        c.roundRect(b['x0'], Y(b['top'] + BOX_H), BOX_W, BOX_H, 5, stroke=1, fill=1)
        c.setFillColor(col); c.rect(b['x0'] + 0.6, Y(b['top'] + BOX_H) + 4, 3, BOX_H - 8, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont('Mono-Bold', 7.6); c.drawString(b['x0'] + 9, Y(b['top'] + 15), label)
        c.setFillColor(MUTED); c.setFont('Sans', 6.1); c.drawString(b['x0'] + 9, Y(b['top'] + 27), sub)

    # config strip
    sy = gbot + 22
    c.setFillColor(INK); c.setFont('Sans-Bold', 10); c.drawString(LEFT, Y(sy), 'Config and tooling')
    c.setFont('Sans', 8); c.setFillColor(MUTED)
    c.drawString(LEFT + 118, Y(sy), 'Not imported by any code file. Read by npm, Expo, TypeScript, Prettier or Docker instead.')
    chips = [
        ('root', 'package.json', 'workspaces: links app, api, shared'),
        ('root', 'package-lock.json', 'exact versions of every package'),
        ('root', '.gitignore', 'keeps .env + node_modules out of git'),
        ('root', '.prettierrc', 'format rules: VS Code + LazyVim'),
        ('root', 'compose.dev.yml', 'local Postgres (offline fallback)'),
        ('root', '.vscode/settings.json', 'format on save (Windows)'),
        ('shared', 'shared/package.json', 'main: src/index.ts (no build step)'),
        ('shared', 'shared/tsconfig.json', 'tsc -p packages/shared'),
        ('app', 'app/package.json', 'main: expo-router/entry  ·  port 19006'),
        ('app', 'app/app.json', 'Expo config: name, scheme, android'),
        ('app', 'app/tsconfig.json', 'defines the @/ alias for app imports'),
        ('app', 'app/babel.config.js', 'import.meta fix (zustand on web)'),
        ('api', 'api/package.json', 'npm run dev = tsx watch src/index.ts'),
        ('api', 'api/tsconfig.json', 'strict TS  ·  (todo: lib ES2020)'),
        ('api', 'api/.env  (not in git)', 'read by env.ts, client.ts, drizzle.config'),
        ('root', '.claude/todo + logs', 'session-start reads  ·  session-end writes'),
    ]
    per_row = 8; cw = (W - 2 * LEFT - (per_row - 1) * 8) / per_row; ch_h = 30
    for j, (ws, name, desc) in enumerate(chips):
        xx = LEFT + (j % per_row) * (cw + 8); yy = sy + 12 + (j // per_row) * (ch_h + 8)
        col, tint, _ = WS[ws]
        c.setFillColor(tint); c.setStrokeColor(col); c.setLineWidth(0.7)
        c.roundRect(xx, Y(yy + ch_h), cw, ch_h, 4, stroke=1, fill=1)
        c.setFillColor(col); c.setFont('Mono-Bold', 7); c.drawString(xx + 6, Y(yy + 12), name)
        c.setFillColor(INK); c.setFont('Sans', 6.2); c.drawString(xx + 6, Y(yy + 23), desc)

    c.showPage(); c.save()
