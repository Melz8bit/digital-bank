import os, sys
from collections import defaultdict
from reportlab.lib.pagesizes import letter, landscape, TABLOID
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, PageBreak, Flowable, NextPageTemplate)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfReader, PdfWriter

import subprocess, datetime, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from imports import find_edges
from content import SECTIONS, NOT_IN_GIT, FINDINGS

def _shrink(x):
    if isinstance(x, str):
        return x.replace("<font face='Mono'>", "<font face='Mono' size='8.3'>")
    if isinstance(x, list):
        return [_shrink(i) for i in x]
    if isinstance(x, tuple):
        return tuple(_shrink(i) for i in x)
    if isinstance(x, dict):
        return {k: _shrink(v) for k, v in x.items()}
    return x
SECTIONS, NOT_IN_GIT, FINDINGS = _shrink(SECTIONS), _shrink(NOT_IN_GIT), _shrink(FINDINGS)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'docs', 'project-map.pdf')
EDGES = find_edges(ROOT)
TODAY = datetime.date.today().isoformat()
COMMIT = subprocess.check_output(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD']).decode().strip()
TMP = tempfile.mkdtemp(prefix='project-map-')

# ---------- fonts ----------
LIB = '/usr/share/fonts/truetype/liberation/'
DJ = '/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('Sans', LIB + 'LiberationSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Sans-Bold', LIB + 'LiberationSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Sans-Italic', LIB + 'LiberationSans-Italic.ttf'))
pdfmetrics.registerFont(TTFont('Sans-BoldItalic', LIB + 'LiberationSans-BoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('Mono', DJ + 'DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('Mono-Bold', DJ + 'DejaVuSansMono-Bold.ttf'))
addMapping('Sans', 0, 0, 'Sans'); addMapping('Sans', 1, 0, 'Sans-Bold')
addMapping('Sans', 0, 1, 'Sans-Italic'); addMapping('Sans', 1, 1, 'Sans-BoldItalic')
addMapping('Mono', 0, 0, 'Mono'); addMapping('Mono', 1, 0, 'Mono-Bold')
addMapping('Mono', 0, 1, 'Mono'); addMapping('Mono', 1, 1, 'Mono-Bold')

# ---------- palette ----------
INK = HexColor('#1F2937'); MUTED = HexColor('#6B7280'); RULE = HexColor('#E5E7EB')
WS = {
    'app':    (HexColor('#2563EB'), HexColor('#EFF4FF'), 'app'),
    'shared': (HexColor('#7C3AED'), HexColor('#F4EFFE'), 'shared'),
    'api':    (HexColor('#059669'), HexColor('#EAF8F2'), 'api'),
    'root':   (HexColor('#4B5563'), HexColor('#F3F4F6'), 'repo'),
    'ext':    (HexColor('#334155'), HexColor('#F1F5F9'), 'external'),
}
HTTP = HexColor('#EA580C')

def ws_of(path):
    if path.startswith('app/'): return 'app'
    if path.startswith('packages/shared'): return 'shared'
    if path.startswith('api/'): return 'api'
    return 'root'

# ---------- styles ----------
def S(name, **kw):
    base = dict(fontName='Sans', fontSize=9.5, leading=13.2, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)

st_body = S('body', spaceAfter=6)
st_intro = S('intro', fontSize=10.5, leading=15, spaceAfter=10)
st_h1 = S('h1', fontName='Sans-Bold', fontSize=22, leading=26, spaceAfter=6)
st_h2 = S('h2', fontName='Sans-Bold', fontSize=13, leading=17, spaceBefore=10, spaceAfter=6)
st_label = S('label', fontName='Sans-Bold', fontSize=7.2, leading=10, textColor=MUTED)
st_cell = S('cell', fontSize=9, leading=12.4)
st_conn = S('conn', fontName='Mono', fontSize=7.4, leading=10.4, textColor=HexColor('#374151'))
st_small = S('small', fontSize=8, leading=11, textColor=MUTED)

def card_path(path, ws):
    color = WS[ws][0]
    return Paragraph(f"<font face='Mono-Bold' color='{color.hexval()}'>{path}</font>",
                     S('p', fontName='Mono-Bold', fontSize=9.6, leading=12.5))

# connections from the import graph
imports = defaultdict(list); used_by = defaultdict(list)
for a, b in EDGES:
    imports[a].append(b); used_by[b].append(a)

def short(p):
    return p.replace('packages/shared/src/', 'shared/').replace('api/src/', 'api/').replace('app/app/', 'app/')

def conn_par(paths):
    return Paragraph('<br/>'.join(short(p) for p in paths), st_conn)

def file_card(f, ws, flat=False):
    color, tint, _ = WS[ws]
    rows = [[card_path(f['path'], ws), '']]
    rows.append([Paragraph('WHAT IT DOES', st_label), Paragraph(f['what'], st_cell)])
    rows.append([Paragraph('WHY WE NEED IT', st_label), Paragraph(f['why'], st_cell)])
    key = f['path']
    if imports.get(key):
        rows.append([Paragraph('IMPORTS', st_label), conn_par(imports[key])])
    if used_by.get(key):
        rows.append([Paragraph('USED BY', st_label), conn_par(used_by[key])])
    if f.get('also'):
        rows.append([Paragraph('ALSO', st_label),
                     Paragraph('<br/>'.join(f['also']), S('a', fontSize=8.4, leading=11.4, textColor=HexColor('#374151')))])
    t = Table(rows, colWidths=[82, 418])
    t.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), tint),
        ('LINEBEFORE', (0, 0), (0, -1), 3, color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (1, 0), 6), ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, -1), (-1, -1), 0.6, RULE),
    ]))
    return [t, Spacer(1, 10)] if flat else KeepTogether([t, Spacer(1, 10)])

class SectionBanner(Flowable):
    def __init__(self, title, ws, kicker):
        super().__init__(); self.title, self.ws, self.kicker = title, ws, kicker
        self.height = 58
    def wrap(self, aw, ah):
        self.width = aw; return aw, self.height
    def draw(self):
        color, tint, _ = WS[self.ws]
        c = self.canv
        c.setFillColor(tint); c.roundRect(0, 0, self.width, self.height, 8, stroke=0, fill=1)
        c.setFillColor(color); c.roundRect(0, 0, 8, self.height, 4, stroke=0, fill=1)
        c.setFont('Sans-Bold', 8); c.setFillColor(color); c.drawString(22, self.height - 20, self.kicker.upper())
        c.setFont('Sans-Bold', 18); c.setFillColor(INK); c.drawString(22, 14, self.title)

class SubHeading(Flowable):
    def __init__(self, text, ws):
        super().__init__(); self.text, self.ws = text, ws; self.height = 26
    def wrap(self, aw, ah):
        self.width = aw; return aw, self.height
    def draw(self):
        color = WS[self.ws][0]; c = self.canv
        c.setFillColor(color); c.circle(5, 9, 3.2, stroke=0, fill=1)
        c.setFont('Sans-Bold', 12); c.setFillColor(INK); c.drawString(15, 5, self.text)

# ---------- big picture diagram ----------
class BigPicture(Flowable):
    def __init__(self):
        super().__init__(); self.height = 238
    def wrap(self, aw, ah):
        self.width = aw; return aw, self.height
    def box(self, x, y, w, h, ws, title, lines):
        c = self.canv; color, tint, _ = WS[ws]
        c.setFillColor(tint); c.setStrokeColor(color); c.setLineWidth(1.4)
        c.roundRect(x, y, w, h, 8, stroke=1, fill=1)
        c.setFillColor(color); c.setFont('Sans-Bold', 11); c.drawString(x + 10, y + h - 18, title)
        c.setFont('Sans', 7.8); c.setFillColor(INK)
        for i, ln in enumerate(lines):
            c.drawString(x + 10, y + h - 32 - i * 10.5, ln)
    def arrow(self, x1, y1, x2, y2, color, label, dash=None, lx=None, ly=None, align='c'):
        c = self.canv; c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.6)
        if dash: c.setDash(*dash)
        c.line(x1, y1, x2, y2); c.setDash()
        import math
        a = math.atan2(y2 - y1, x2 - x1); L = 7
        p = c.beginPath(); p.moveTo(x2, y2)
        p.lineTo(x2 - L * math.cos(a - 0.4), y2 - L * math.sin(a - 0.4))
        p.lineTo(x2 - L * math.cos(a + 0.4), y2 - L * math.sin(a + 0.4)); p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.setFont('Sans-Bold', 7.6)
        lx = (x1 + x2) / 2 if lx is None else lx; ly = (y1 + y2) / 2 + 4 if ly is None else ly
        for i, part in enumerate(label.split('\n')):
            if align == 'c': c.drawCentredString(lx, ly - i * 9.5, part)
            elif align == 'l': c.drawString(lx, ly - i * 9.5, part)
            else: c.drawRightString(lx, ly - i * 9.5, part)
    def draw(self):
        w = self.width
        bw, bh, pw = 140, 92, 80
        ax = 0; dbx = w - pw; apx = dbx - 46 - bw
        top = self.height - bh
        self.box(ax, top, bw, bh, 'app', 'app/  (Expo)', ['screens  ·  hooks', 'lib/apiClient (fetch)', 'stores (token, PIN lock)', 'runs in browser / phone'])
        self.box(apx, top, bw, bh, 'api', 'api/  (Express)', ['routes  ·  middleware', 'services (rules)', 'db/ (Drizzle)', 'runs in Node on :3000'])
        sx = (ax + apx) / 2; sy = 6
        self.box(sx, sy, bw, 84, 'shared', 'packages/shared', ['schemas (zod rules)', 'types (response shapes)', 'money (cents helpers)'])
        self.box(dbx, top + 10, pw, 72, 'ext', 'Postgres', ['on the Pi', '192.168.1.73', ':5432'])
        mid = (ax + bw + apx) / 2
        self.arrow(ax + bw + 4, top + bh - 34, apx - 4, top + bh - 34, HTTP, 'HTTP requests\n(JSON + login token)', dash=(5, 3), lx=mid, ly=top + bh - 16)
        self.arrow(apx - 4, top + 26, ax + bw + 4, top + 26, HTTP, 'JSON responses', dash=(5, 3), lx=mid, ly=top + 12)
        self.arrow(ax + bw * 0.55, top, sx + 30, sy + 84, WS['shared'][0], 'imports', lx=ax + bw * 0.55 + 8, ly=(top + sy + 84) / 2 - 8, align='l')
        self.arrow(apx + bw * 0.45, top, sx + bw - 30, sy + 84, WS['shared'][0], 'imports', lx=apx + bw * 0.45 - 8, ly=(top + sy + 84) / 2 - 8, align='r')
        self.arrow(apx + bw + 3, top + bh / 2, dbx - 3, top + bh / 2, INK, 'SQL', lx=(apx + bw + dbx) / 2, ly=top + bh / 2 + 6)

# ---------- traces ----------
def trace_table(steps):
    rows = []
    for i, (path, text) in enumerate(steps, 1):
        ws = ws_of(path) if path != 'HTTP' else None
        if path == 'HTTP':
            pcell = Paragraph(f"<font face='Mono-Bold' color='{HTTP.hexval()}'>~ network ~</font>", st_conn)
        else:
            pcell = Paragraph(f"<font face='Mono-Bold' color='{WS[ws][0].hexval()}'>{short(path)}</font>", st_conn)
        rows.append([Paragraph(f"<b>{i}</b>", S('n', fontSize=9, textColor=MUTED, alignment=TA_CENTER)), pcell, Paragraph(text, st_cell)])
    t = Table(rows, colWidths=[20, 152, 328])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, RULE),
        ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t

M = lambda s: f"<font face='Mono' size='8.3'>{s}</font>"
POSTJSON = "postJson('/auth/login', input)"
MUTATE = "useCreateTransactionMutation(childId).mutate({ type: 'deposit', amountCents: toCents(5), category: 'allowance' })"
TXKEY = "['transactions', childId]"
LOGIN_TRACE = [
    ('app/app/(auth)/login.tsx', f"You tap <b>Log In</b>. The screen calls {M('mutate({ email, password })')} from {M('useLoginMutation')}."),
    ('app/hooks/useAuthMutations.ts', f"The mutation's {M('mutationFn')} calls {M(POSTJSON)}. {M('LoginInput')} (from shared) makes sure the shape is right."),
    ('app/lib/apiClient.ts', f"{M('fetch')} sends a POST to {M('http://localhost:3000/auth/login')}."),
    ('HTTP', "The request travels to the API process."),
    ('api/src/app.ts', f"CORS allows the Expo origin, JSON is parsed, and the {M('/auth')} prefix hands it to the auth router. ({M('index.ts')} started all of this and ran migrations first.)"),
    ('api/src/routes/auth.routes.ts', f"{M('LoginInputSchema.safeParse')} (from shared) checks the body. If it's bad: <b>400</b> with a readable message."),
    ('api/src/services/authService.ts', f"Finds the parent with {M('db')} ({M('db/client.ts')} + {M('schema.ts')}), runs {M('bcrypt.compare')}, and signs a JWT with {M('JWT_SECRET')} from {M('env.ts')}."),
    ('app/lib/apiClient.ts', f"The <b>200</b> {M('{ token, parent }')} comes back. {M('handleResponse')} returns it (or throws the error message for 401)."),
    ('app/store/authStore.ts', f"{M('onSuccess: saveSession')} stores the token, which is saved to AsyncStorage."),
    ('app/app/_layout.tsx', f"{M('token')} is now set, so {M('Stack.Protected')} swaps {M('(auth)')} for {M('(tabs)')}. You're in."),
]
DEPOSIT_TRACE = [
    ('app/app/(tabs)/deposit  (Step 8)', f"<i>(The deposit screen doesn't exist yet.)</i> It will call {M(MUTATE)}."),
    ('app/hooks/useTransactions.ts', f"{M('postJsonAuth')} to {M('/children/:childId/transactions')}. The body is a shared {M('TransactionInput')}."),
    ('app/lib/apiClient.ts', f"Adds {M('Authorization: Bearer &lt;token&gt;')}, reading the token from {M('authStore')}."),
    ('api/src/routes/children.routes.ts', f"{M('router.use(requireAuth)')} runs first..."),
    ('api/src/middleware/requireAuth.ts', f"...verifies the JWT and sets {M('req.parentId')} (typed by {M('express.d.ts')}). A bad token stops here with <b>401</b>."),
    ('api/src/routes/children.routes.ts', f"{M('ChildIdSchema')} checks the id (404) and {M('TransactionInputSchema')} checks the body (400)."),
    ('api/src/services/transactionService.ts', f"{M('getFamilyForParent')}, then inside one DB transaction: lock the child row, {M('getBalance')}, check the cap and balance (withdrawals only), insert, and return {M('{ transaction, balance }')}."),
    ('api/src/routes/children.routes.ts', f"Replies <b>201</b>, or <b>422</b> \"You don't have enough money for that.\""),
    ('app/hooks/useTransactions.ts', f"{M('onSuccess')} invalidates {M(TXKEY)}, so {M('useTransactionsQuery')} refetches and the dashboard shows the new balance."),
]

# ---------- page decoration ----------
def on_page(c, doc):
    c.saveState()
    c.setStrokeColor(RULE); c.setLineWidth(0.6)
    c.line(54, 40, letter[0] - 54, 40)
    c.setFont('Sans', 7.5); c.setFillColor(MUTED)
    c.drawString(54, 28, f'Digital Bank  ·  project map  ·  {TODAY}')
    c.drawRightString(letter[0] - 54, 28, str(doc.page))
    c.restoreState()

def on_cover(c, doc):
    c.saveState()
    W, H = letter
    c.setFillColor(HexColor('#111827')); c.rect(0, H - 330, W, 330, stroke=0, fill=1)
    # three color bars
    for i, ws in enumerate(['app', 'shared', 'api']):
        c.setFillColor(WS[ws][0]); c.rect(54 + i * 62, H - 120, 54, 8, stroke=0, fill=1)
    c.setFillColor(white); c.setFont('Sans-Bold', 40); c.drawString(54, H - 180, 'Digital Bank')
    c.setFont('Sans', 22); c.setFillColor(HexColor('#D1D5DB')); c.drawString(54, H - 214, 'Project map')
    c.setFont('Sans', 11); c.setFillColor(HexColor('#9CA3AF'))
    c.drawString(54, H - 262, 'Every file: what it does, why it exists, and what it connects to.')
    c.drawString(54, H - 280, f'As of {TODAY}  ·  commit {COMMIT}')
    c.restoreState()

# ---------- build text document ----------
text_pdf = os.path.join(TMP, 'text.pdf')
doc = BaseDocTemplate(text_pdf, pagesize=letter, leftMargin=56, rightMargin=56, topMargin=54, bottomMargin=56,
                      title='Digital Bank: project map', author='Melz')
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='f', leftPadding=0, rightPadding=0)
cover_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, letter[1] - 340 - doc.bottomMargin, id='c', leftPadding=0, rightPadding=0)
doc.addPageTemplates([PageTemplate('cover', [cover_frame], onPage=on_cover),
                      PageTemplate('body', [frame], onPage=on_page)])

story = [NextPageTemplate('body')]
story.append(Paragraph('How to read this', st_h2))
story.append(Paragraph(
    "Each folder has a section, and each file has a card. A card answers three questions: <b>what it does</b>, "
    "<b>why we need it</b>, and <b>what it connects to</b>. The <b>IMPORTS</b> and <b>USED BY</b> lines are "
    "generated from the real <font face='Mono'>import</font> statements in the code, so they're exact. "
    "<b>ALSO</b> lists links that aren't imports: HTTP calls, config files, things read from disk.", st_body))
legend = Table([[Paragraph(f"<font color='{WS[w][0].hexval()}'><b>{lbl}</b></font>", st_cell), Paragraph(desc, st_cell)]
                for w, lbl, desc in [('app', 'Blue', 'the Expo app (<font face=\"Mono\">app/</font>)'),
                                     ('shared', 'Purple', 'the shared package (<font face=\"Mono\">packages/shared/</font>)'),
                                     ('api', 'Green', 'the server (<font face=\"Mono\">api/</font>)'),
                                     ('root', 'Grey', 'repo-level config and tooling')]],
               colWidths=[60, 440])
legend.setStyle(TableStyle([('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('LEFTPADDING', (0, 0), (-1, -1), 0)]))
story += [legend, Spacer(1, 6), Paragraph(
    "Paths on the cards are shortened: <font face='Mono'>api/</font> means <font face='Mono'>api/src/</font>, "
    "<font face='Mono'>shared/</font> means <font face='Mono'>packages/shared/src/</font>, and "
    "<font face='Mono'>app/(tabs)/…</font> means <font face='Mono'>app/app/(tabs)/…</font>. "
    "<b>The last page</b> is the full map, a large landscape sheet with every file and every connection.", st_small)]

story += [PageBreak(), SectionBanner('The big picture', 'root', 'Start here'), Spacer(1, 12)]
story.append(Paragraph(
    "The project is <b>three npm workspaces in one repo</b>. The <b>app</b> is what you see. The <b>api</b> holds the "
    "rules and the only key to the database. <b>shared</b> is the common language they both import, so a deposit "
    "means the same thing on both sides.", st_intro))
story += [BigPicture(), Spacer(1, 12)]
story.append(Paragraph('Three rules that shape every file', st_h2))
for t in [
    "<b>Dependencies only point inward:</b> app → shared ← api. shared imports neither of them, and the app never imports "
    "API code: it only talks to it over HTTP. That's why Drizzle and pg never end up in the phone bundle, and why "
    "<font face='Mono'>types.ts</font> is written by hand.",
    "<b>Never trust the client:</b> the app checks input for a friendly experience, but the API checks it <i>again</i> "
    "(same zod schemas) and makes every money decision: caps, balance, family ownership.",
    "<b>Each layer has one job:</b> routes speak HTTP, services apply rules, db/ talks SQL. In the app, screens draw, "
    "hooks fetch, apiClient does the network, and stores remember. When you add something, ask \"which layer is this?\"",
]:
    story.append(Paragraph('•&nbsp;&nbsp;' + t, S('b', leftIndent=10, firstLineIndent=-8, spaceAfter=5)))
story.append(Paragraph('Two kinds of state in the app', st_h2))
story.append(Paragraph(
    "<b>Server data</b> (balances, transactions, PIN status) lives in <b>React Query's cache</b>. It's a copy of what the "
    "API knows, refetched when marked stale. <b>App-only data</b> (the login token, \"is the PIN unlocked?\") lives in "
    "<b>zustand stores</b>. The token is saved to storage so you stay logged in; the PIN lock is not, so a restart re-locks it.", st_body))

story += [PageBreak(), SectionBanner('Follow a request', 'root', 'How the files connect at runtime'), Spacer(1, 12)]
story.append(Paragraph(
    "Imports show which file <i>can</i> use which. These two walkthroughs show what actually <i>happens</i>, file by file, "
    "when you use the app.", st_intro))
story.append(Paragraph('1.  Logging in', st_h2)); story.append(trace_table(LOGIN_TRACE))
story.append(Spacer(1, 8))
story.append(KeepTogether([Paragraph('2.  Depositing $5 (the hooks you built today)', st_h2), trace_table(DEPOSIT_TRACE)]))

for sec in SECTIONS:
    story += [PageBreak(), SectionBanner(sec['title'], sec['ws'], WS[sec['ws']][2] if sec['ws'] != 'root' else 'repo root'),
              Spacer(1, 12), Paragraph(sec['intro'], st_intro)]
    if 'files' in sec:
        for f in sec['files']:
            story.append(file_card(f, sec['ws']))
    for sub, files in sec.get('subs', []):
        story.append(KeepTogether([SubHeading(sub, sec['ws']), Spacer(1, 4)] + file_card(files[0], sec['ws'], flat=True)))
        for f in files[1:]:
            story.append(file_card(f, sec['ws']))

story += [PageBreak(), SectionBanner('Not in git, and things I noticed', 'root', 'Odds and ends'), Spacer(1, 12)]
story.append(Paragraph('Folders and files that exist on disk but are not committed', st_h2))
for p, d in NOT_IN_GIT:
    story.append(Paragraph(f"<font face='Mono-Bold'>{p}</font>  {d}", S('n', spaceAfter=6)))
story.append(Paragraph('Things I noticed while mapping', st_h2))
story.append(Paragraph("None of these are urgent, and nothing is broken today. They're worth knowing about.", st_small))
story.append(Spacer(1, 4))
rows = [[Paragraph(f"<font face='Mono-Bold'>{p}</font>", st_conn), Paragraph(d, st_cell)] for p, d in FINDINGS]
ft = Table(rows, colWidths=[170, 330])
ft.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -2), 0.5, RULE),
                        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LEFTPADDING', (0, 0), (-1, -1), 2)]))
story.append(ft)
story.append(Spacer(1, 14))
story.append(Paragraph("<b>Next page:</b> the full map. It's printed on a larger 11×17 landscape sheet so every label stays readable.", st_small))

doc.build(story)

# ---------- map page ----------
import map_page
map_pdf = os.path.join(TMP, 'map.pdf')
map_page.draw(map_pdf, EDGES, WS, HTTP, INK, MUTED, RULE, TODAY)

w = PdfWriter()
for p in (text_pdf, map_pdf):
    for page in PdfReader(p).pages:
        w.add_page(page)
w.add_metadata({'/Title': 'Digital Bank: project map', '/Author': 'Melz'})
with open(OUT, 'wb') as fh:
    w.write(fh)
print(f'wrote {os.path.relpath(OUT, ROOT)}  ({len(PdfReader(OUT).pages)} pages, {len(EDGES)} imports)')
