# LA KEBABBERIA - versione Python (pygame)
# Installa:  pip install pygame     |  Apri con IDLE e premi F5
import asyncio, math, os, random, time
import pygame

W, H = 1024, 768
INK = (90, 42, 12); CREAM = (255, 246, 224); OR = (249, 115, 22); YE = (245, 184, 61)
try: os.chdir(os.path.dirname(os.path.abspath(__file__)))
except Exception: pass
pygame.init()
screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("La Kebabberia")
f26, f34, f46, f70 = [pygame.font.Font(None, s) for s in (26, 34, 46, 70)]

def load(p, size=None, alpha=True):
    i = pygame.image.load(p)
    i = i.convert_alpha() if alpha else i.convert()
    return pygame.transform.smoothscale(i, size) if size else i

BG = load("assets/sfondo_locale.jpg", (W, H), False)
INS = pygame.image.load("assets/insegna.jpg").convert()
INS = pygame.transform.smoothscale(INS, (440, int(440 * INS.get_height() / INS.get_width())))
BG2 = load("assets/sfondo_postazione.png", (W, H), False) if os.path.exists("assets/sfondo_postazione.png") else None
CH = []
for f in sorted(os.listdir("assets/clienti")):
    if f.endswith(".png"):
        c = pygame.image.load("assets/clienti/" + f).convert_alpha()
        CH.append(pygame.transform.smoothscale(c, (int(c.get_width() * 292 / c.get_height()), 292)))

SP = []  # fotogrammi dello spiedo (assets/spiedo/spiedo_00.png, spiedo_01.png, ...)
if os.path.isdir("assets/spiedo"):
    for f in sorted(os.listdir("assets/spiedo")):
        if f.endswith(".png"): SP.append(pygame.image.load("assets/spiedo/" + f).convert_alpha())

COL = {"Kebab": (150, 75, 30), "Falafel": (170, 120, 50), "insalata": (110, 180, 70), "pomodoro": (220, 60, 40),
       "cipolla": (170, 100, 180), "cetriolo": (90, 150, 70), "yogurt": (250, 250, 245), "piccante": (224, 69, 42), "aglio": (242, 176, 30)}
BASE = ["Kebab", "Falafel"]; VEG = ["insalata", "pomodoro", "cipolla", "cetriolo"]; SAL = ["yogurt", "piccante", "aglio"]

def box(r, fill, rad=16, w=4):
    pygame.draw.rect(screen, fill, r, border_radius=rad); pygame.draw.rect(screen, INK, r, w, border_radius=rad)

def text(s, font, pos, col=INK, center=True):
    i = font.render(s, True, col); r = i.get_rect(center=pos) if center else i.get_rect(topleft=pos); screen.blit(i, r)

def wrap(s, font, maxw):
    out, line = [], ""
    for w in s.split():
        t = (line + " " + w).strip()
        if font.size(t)[0] > maxw: out.append(line); line = w
        else: line = t
    return out + [line]

def bar(x, y, w, p):
    pygame.draw.rect(screen, CREAM, (x, y, w, 16), border_radius=8)
    pygame.draw.rect(screen, OR, (x, y, int(w * max(0, p)), 16), border_radius=8)
    pygame.draw.rect(screen, INK, (x, y, w, 16), 3, border_radius=8)

# Pulsanti della postazione: (rettangolo, nome, tipo)
BTN = []
for i, n in enumerate(["Falafel"] + VEG): BTN.append((pygame.Rect(276 + i * 106, 177, 98, 113), n, "base" if n == "Falafel" else "veg"))
for i, n in enumerate(SAL): BTN.append((pygame.Rect(758 + i * 82, 376, 70, 154), n, "sal"))
SPIT = pygame.Rect(30, 70, 190, 450)
if SP: SPIT = pygame.Rect(24, 60, SP[0].get_width(), SP[0].get_height())
R_ACC = pygame.Rect(W - 330, H - 100, 300, 66)
R_TRASH = pygame.Rect(30, H - 70, 170, 52); R_SERVE = pygame.Rect(W - 220, H - 70, 190, 52)
R_OK = pygame.Rect(W // 2 - 110, 540, 220, 70)

shade = pygame.Surface((123, 287), pygame.SRCALPHA)
for x in range(123):
    shade.fill((0, 0, 0, int(130 * max(0, 1 - x / 38) + 100 * max(0, (x - 74) / 49))), (x, 0, 1, 287))
mask = pygame.Surface((123, 287), pygame.SRCALPHA)
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, 123, 287), border_radius=42)

G = dict(state="start", day=1, coin=0, n=0, msg="", mt=0, shake=0)

def draw_spit(t):
    if SP:  # animazione vera, 12 fotogrammi al secondo
        jit = int(math.sin(t * 60) * 4) if t - G["shake"] < .3 else 0
        screen.blit(SP[int(t * 12) % len(SP)], (SPIT.x + jit, SPIT.y)); return
    pygame.draw.rect(screen, (110, 110, 110), (124, 40, 10, 440), border_radius=4)
    pygame.draw.rect(screen, INK, (124, 40, 10, 440), 2, border_radius=4)
    for k in range(7):
        pygame.draw.rect(screen, (255, 154 + k * 10, 46), (200, 175 + k * 36, 22, 26), border_radius=6)
    meat = pygame.Surface((123, 287), pygame.SRCALPHA)
    off = int(t * 60) % 56
    for x in range(-56, 130, 56):
        for dx, w, c in ((0, 22, (184, 86, 28)), (22, 9, (146, 64, 15)), (31, 25, (207, 114, 48))):
            pygame.draw.rect(meat, c, (x + off + dx, 0, w, 287))
    meat.blit(shade, (0, 0)); meat.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(meat, (67, 154))
    pygame.draw.rect(screen, INK, (67, 154, 123, 287), 5, border_radius=42)
    for k in range(2):
        y = 140 - ((t * 40 + k * 30) % 70)
        pygame.draw.circle(screen, (235, 235, 235), (100 + k * 50, int(y)), 9, 3)


def new_customer():
    d = min(G["day"], 6)
    G["order"] = dict(base=random.choice(BASE), veg=random.sample(VEG, 1 + min(2, d // 2 + random.randint(0, 1))),
                      sal=random.sample(SAL, 1 + (1 if d > 2 and random.random() > .5 else 0)))
    G["cur"] = dict(base=None, veg=[], sal=[]); G["face"] = random.choice(CH)
    G["limit"] = max(18, 42 - d * 3); G["t0"] = G["arr"] = time.time(); G["state"] = "order"

def order_text():
    o = G["order"]; return "Vorrei: " + " + ".join([o["base"]] + o["veg"] + o["sal"])

def score():
    o, c = G["order"], G["cur"]; miss = 0
    for k in ("veg", "sal"):
        miss += len([x for x in o[k] if x not in c[k]]) + len([x for x in c[k] if x not in o[k]])
    return max(0, 5 - miss * 2) if c["base"] == o["base"] else 0

def finish(late):
    g = 0 if late else score(); tip = 0
    if g == 5: tip = math.ceil((G["limit"] - (time.time() - G["t0"])) / G["limit"] * 3)
    G["coin"] += g + tip; G["n"] += 1; G["last"] = g
    G["msg"] = "Uffa, troppa attesa!" if late else "Perfetto! +%d, mancia +%d" % (g, tip) if g == 5 else "Quasi giusto... +%d" % g if g else "Ordine sbagliato!"
    if G["n"] >= 5: G["day"] += 1; G["n"] = 0
    G["state"] = "result"; G["mt"] = time.time()

def click(p):
    s = G["state"]
    if s in ("start", "dayend"):
        if R_OK.collidepoint(p): new_customer()
    elif s == "order":
        if R_ACC.collidepoint(p): G["state"] = "prep"
    elif s == "prep":
        c = G["cur"]
        def tog(kind, n):
            if kind == "base": c["base"] = n
            elif n in c[kind]: c[kind].remove(n)
            else: c[kind].append(n)
        for r, n, k in BTN:
            if r.collidepoint(p): tog(k, n)
        if SPIT.collidepoint(p): c["base"] = "Kebab"; G["shake"] = time.time()
        if R_TRASH.collidepoint(p): G["cur"] = dict(base=None, veg=[], sal=[])
        if R_SERVE.collidepoint(p) and c["base"]: finish(False)

def hud():
    box((16, 14, 200, 40), CREAM, 20, 3); text("Giorno %d  %d/5" % (G["day"], min(G["n"] + 1, 5)), f26, (116, 34))
    box((226, 14, 130, 40), CREAM, 20, 3); text("Monete %d" % G["coin"], f26, (291, 34))

def card(msg, p):
    ls = wrap(msg, f34, 430); h = 40 + len(ls) * 34 + 30
    box((277, 38, 470, h), CREAM, 28, 4)
    for i, l in enumerate(ls): text(l, f34, (512, 70 + i * 34))
    bar(297, 38 + h - 26, 430, p)

def draw(now):
    s = G["state"]
    if s in ("start", "dayend"):
        screen.blit(BG, (0, 0)); box((200, 60, 624, 580), CREAM, 40, 6); screen.blit(INS, (292, 90))
        msg = "Ascolta l'ordine, preparalo e guadagna monete!" if s == "start" else "Fine giornata! Totale monete: %d" % G["coin"]
        for i, l in enumerate(wrap(msg, f34, 520)): text(l, f34, (512, 400 + i * 36))
        box(R_OK, OR, 24, 5); text("Gioca" if s == "start" else "Avanti", f46, R_OK.center, (255, 255, 255)); return
    p = 1 - (now - G["t0"]) / G["limit"]
    if s == "prep":
        if BG2: screen.blit(BG2, (0, 0))
        else:
            screen.fill((251, 232, 196))
            pygame.draw.rect(screen, OR, (0, 338, W, 32)); pygame.draw.rect(screen, INK, (0, 338, W, 32), 4)
            pygame.draw.rect(screen, (243, 217, 164), (0, 476, W, 292)); pygame.draw.line(screen, INK, (0, 476), (W, 476), 6)
            pygame.draw.rect(screen, OR, (0, 699, W, 69)); pygame.draw.line(screen, INK, (0, 699), (W, 699), 5)
            pygame.draw.rect(screen, (160, 90, 42), (256, 300, 552, 22), border_radius=5)
        draw_spit(now)
        c = G["cur"]
        for r, n, k in BTN:
            on = c["base"] == n or (k != "base" and n in c[k])
            box(r, (255, 227, 168) if on else CREAM, 14, 6 if on else 3)
            if on: pygame.draw.rect(screen, OR, r, 6, border_radius=14)
            if k == "sal": pygame.draw.rect(screen, COL[n], r.inflate(-14, -50).move(0, -12), border_radius=10); pygame.draw.rect(screen, INK, r.inflate(-14, -50).move(0, -12), 3, border_radius=10)
            else: pygame.draw.circle(screen, COL[n], (r.centerx, r.y + 45), 28); pygame.draw.circle(screen, INK, (r.centerx, r.y + 45), 28, 3)
            text(n, f26, (r.centerx, r.bottom - 18))
        pygame.draw.ellipse(screen, CREAM, (338, 507, 348, 161)); pygame.draw.ellipse(screen, INK, (338, 507, 348, 161), 5)
        items = [x for x in [c["base"]] + c["veg"] + c["sal"] if x]
        for i, n in enumerate(items):
            pygame.draw.circle(screen, COL[n], (400 + i * 38, 560), 16); pygame.draw.circle(screen, INK, (400 + i * 38, 560), 16, 2)
        text(", ".join(items) if items else "Piatto vuoto", f26, (512, 610))
        card(order_text(), p)
        box(R_TRASH, YE, 14, 4); text("Rifai", f34, R_TRASH.center)
        box(R_SERVE, OR, 14, 4); text("Servi!", f34, R_SERVE.center, (255, 255, 255))
    else:
        screen.blit(BG, (0, 0)); f = G["face"]; x, y = 512 - f.get_width() // 2, 520 - f.get_height()
        if s == "order": y += max(0, (.5 - (now - G["arr"])) * 160)
        else:
            g = G["last"]
            if g == 5: y -= abs(math.sin((now - G["mt"]) * 8)) * 24
            elif g < 3: x += math.sin((now - G["mt"]) * 40) * 8
        screen.blit(f, (x, y))
        if s == "order": card(order_text(), p); box(R_ACC, OR, 24, 5); text("Accetta ordine", f46, R_ACC.center, (255, 255, 255))
        else: card(G["msg"], 1 - (now - G["mt"]) / 1.7)
    hud()

async def main():
    clock = pygame.time.Clock()
    while True:
        now = time.time()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); return
            if e.type == pygame.MOUSEBUTTONDOWN: click(e.pos)
        if G["state"] in ("order", "prep") and now - G["t0"] > G["limit"]: finish(True)
        if G["state"] == "result" and now - G["mt"] > 1.7:
            if G["n"] == 0: G["state"] = "dayend"
            else: new_customer()
        draw(now); pygame.display.flip()
        await asyncio.sleep(0); clock.tick(60)

asyncio.run(main())
