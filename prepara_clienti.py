# Taglia un foglio di personaggi in tanti PNG trasparenti.
# Prima, nel prompt dei comandi:  pip install pillow numpy scipy
# Metti il foglio nella stessa cartella di questo file, cambia SHEET e premi F5 in IDLE.
import os, numpy as np
from PIL import Image
from scipy import ndimage as nd
SHEET = "parsonaggi.png"      # nome del foglio da tagliare
PREFIX = "c"                  # i file saranno c13.png, c14.png ...
START = 13                    # numero da cui iniziare (c01-c12 esistono già)
ALTEZZA = 340
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "assets", "clienti"); os.makedirs(out, exist_ok=True)
a = np.array(Image.open(os.path.join(here, SHEET)).convert("RGBA"))
bianco = a[..., :3].min(axis=2) > 228
lab, _ = nd.label(bianco)
bordo = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
a[..., 3] = np.where(np.isin(lab, list(bordo)), 0, 255)
a[..., 3] = nd.binary_opening(a[..., 3] > 0) * 255
m = a[..., 3] > 0
def runs(v, gap=6):
    idx = np.where(v)[0]; r = []; s = p = idx[0]
    for i in idx[1:]:
        if i - p > gap: r.append((s, p)); s = i
        p = i
    r.append((s, p)); return [x for x in r if x[1] - x[0] > 40]
k = START
for y0, y1 in runs(m.any(axis=1)):
    for x0, x1 in runs(m[y0:y1 + 1].any(axis=0)):
        c = Image.fromarray(a[y0:y1 + 1, x0:x1 + 1])
        c = c.resize((int(c.width * ALTEZZA / c.height), ALTEZZA), Image.LANCZOS)
        c.save(os.path.join(out, "%s%02d.png" % (PREFIX, k))); k += 1
print("Fatto! Creati", k - START, "personaggi. Aggiungili alla lista CH in index.html")
