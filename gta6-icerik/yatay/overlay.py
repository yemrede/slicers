import json, subprocess, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
W, Hh, FPS = 1920, 1080, 30
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FBo = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
f_cap = ImageFont.truetype(FB, 58); f_num = ImageFont.truetype(FB, 64); f_tit = ImageFont.truetype(FB, 50)
f_sub = ImageFont.truetype(FBo, 34); f_cbig = ImageFont.truetype(FB, 120); f_csm = ImageFont.truetype(FB, 46)
f_tag = ImageFont.truetype(FB, 28); f_hook1 = ImageFont.truetype(FB, 92); f_hook2 = ImageFont.truetype(FB, 72)
PINK, ORANGE, YEL, WHITE, BLACK = (255, 46, 136), (255, 140, 0), (255, 222, 0), (255, 255, 255), (0, 0, 0)
D = json.load(open("timeline.json")); TL, WORDS, TOTAL = D["tl"], D["words"], D["total"]
def up(s): return s.replace("i", "İ").replace("ı", "I").upper()
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def grad(w, h, c0=PINK, c1=ORANGE):
    g = Image.new("RGBA", (w, h)); d = ImageDraw.Draw(g)
    for x in range(w):
        t = x / max(1, w - 1); d.line([(x, 0), (x, h)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)) + (255,))
    return g
def rrect_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
# caption chunks (<= 6 words or sentence end), per block
chunks = []; curc = []
for i, (w, s, e, bi) in enumerate(WORDS):
    curc.append(i)
    nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    if len(curc) >= 6 or w[-1] in ".!?:" or nxt is None or nxt[3] != bi or (nxt[1] - e) > 0.5:
        chunks.append(curc); curc = []
chunk_of = {}
for ci, c in enumerate(chunks):
    for i in c: chunk_of[i] = ci
def caption(img, t):
    # active chunk: last chunk whose first word started <= t and last word end+0.3 >= t
    act = None
    for ci, c in enumerate(chunks):
        if WORDS[c[0]][1] - 0.05 <= t <= WORDS[c[-1]][2] + 0.25: act = ci
    if act is None: return None
    c = chunks[act]; d = ImageDraw.Draw(img)
    words = [up(WORDS[i][0]) for i in c]
    sp = 18; widths = [d.textlength(w, font=f_cap) for w in words]; tw = sum(widths) + sp * (len(words) - 1)
    x = (W - tw) / 2; y = 930
    for w, i, ww in zip(words, c, widths):
        on = WORDS[i][1] <= t
        d.text((x, y), w, font=f_cap, fill=YEL if (on and t <= WORDS[i][2] + 0.15) else WHITE, stroke_width=7, stroke_fill=BLACK)
        x += ww + sp
    return act
def badge(img, e, t):
    if not e.get("title"): return
    lt = t - e["t0"]; a = ease(lt / 0.45); out = ease((e["t1"] - t) / 0.3)
    k = min(a, out)
    if k <= 0: return
    no = e["no"]; label = "BONUS" if no == 15 else str(no)
    d0 = ImageDraw.Draw(img)
    tw = max(d0.textlength(up(e["title"]), font=f_tit), d0.textlength(e["sub"], font=f_sub)) + 60
    bw = int(150 + tw); bh = 150
    x = int(-bw + (60 + bw) * k); y = 60
    panel = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=(10, 10, 18, 215))
    sq = grad(130 if label != "BONUS" else 130, bh); panel.paste(sq, (0, 0), rrect_mask(130, bh, 26))
    pd.rectangle((100, 0, 130, bh), fill=None)
    fn = f_num if label != "BONUS" else ImageFont.truetype(FB, 30)
    lw = pd.textlength(label, font=fn); pd.text(((130 - lw) / 2, (bh - (64 if label != "BONUS" else 30)) / 2 - 6), label, font=fn, fill=WHITE)
    pd.text((155, 22), up(e["title"]), font=f_tit, fill=WHITE)
    pd.text((155, 88), e["sub"], font=f_sub, fill=YEL)
    img.alpha_composite(panel, (x, y))
def card(img, e, t):
    lt = t - e["t0"]; d = e["t1"] - e["t0"]
    a = ease(lt / 0.35) * ease((d - lt) / 0.3)
    ov = Image.new("RGBA", (W, Hh), (0, 0, 0, int(120 * a))); img.alpha_composite(ov)
    small, big, _ = e["card"]
    dd = ImageDraw.Draw(img)
    sw = dd.textlength(small, font=f_csm); bw_ = dd.textlength(big, font=f_cbig)
    yo = int(40 * (1 - ease(lt / 0.5)))
    g = grad(int(sw + 60), 70); m = rrect_mask(int(sw + 60), 70, 35)
    gi = Image.new("RGBA", g.size); gi.paste(g, (0, 0), m)
    if a > 0:
        gi.putalpha(Image.eval(m, lambda v: int(v * a)))
        img.alpha_composite(gi, (int((W - sw - 60) / 2), 380 + yo))
        dd.text(((W - sw) / 2, 388 + yo), small, font=f_csm, fill=(255, 255, 255, int(255 * a)))
        dd.text(((W - bw_) / 2, 480 + yo), big, font=f_cbig, fill=(255, 255, 255, int(255 * a)), stroke_width=6, stroke_fill=(0, 0, 0, int(255 * a)))
def hook(img, t):
    if t > 7.5: return
    a = ease((t - 0.1) / 0.5) * ease((7.5 - t) / 0.4)
    if a <= 0: return
    dd = ImageDraw.Draw(img)
    l1, l2 = "GTA 6'DA İLK SAATLER", "BUNU BİLMEDEN BAŞLAMA!"
    w1 = dd.textlength(l1, font=f_hook1); w2 = dd.textlength(l2, font=f_hook2)
    yo = int(30 * (1 - ease(t / 0.6)))
    dd.text(((W - w1) / 2, 300 + yo), l1, font=f_hook1, fill=(255, 255, 255, int(255 * a)), stroke_width=9, stroke_fill=(0, 0, 0, int(255 * a)))
    g = grad(int(w2 + 70), 110); m = rrect_mask(int(w2 + 70), 110, 22)
    gi = Image.new("RGBA", g.size); gi.paste(g, (0, 0), m); gi.putalpha(Image.eval(m, lambda v: int(v * a)))
    img.alpha_composite(gi, (int((W - w2 - 70) / 2), 420 + yo))
    dd.text(((W - w2) / 2, 432 + yo), l2, font=f_hook2, fill=(255, 255, 255, int(255 * a)))
def endcard(img, e, t):
    lt = t - e["t0"]; a = ease(lt / 0.5)
    img.alpha_composite(Image.new("RGBA", (W, Hh), (0, 0, 0, int(110 * a))))
    dd = ImageDraw.Draw(img)
    l1, l2, l3 = "SEN HANGİSİNİ BİLMİYORDUN?", "YORUMLARA YAZ", "ABONE OL • BİLDİRİMLERİ AÇ"
    for (s, f, y, fill) in ((l1, f_hook2, 330, WHITE), (l3, f_csm, 620, YEL)):
        w = dd.textlength(s, font=f); dd.text(((W - w) / 2, y), s, font=f, fill=fill + (int(255 * a),), stroke_width=6, stroke_fill=(0, 0, 0, int(255 * a)))
    w2 = dd.textlength(l2, font=f_hook1); g = grad(int(w2 + 80), 130); m = rrect_mask(int(w2 + 80), 130, 30)
    gi = Image.new("RGBA", g.size); gi.paste(g, (0, 0), m); gi.putalpha(Image.eval(m, lambda v: int(v * a)))
    img.alpha_composite(gi, (int((W - w2 - 80) / 2), 445)); dd.text(((W - w2) / 2, 458), l2, font=f_hook1, fill=(255, 255, 255, int(255 * a)))
def tag(img):
    dd = ImageDraw.Draw(img); s = "GTA 6 • İLK SAATLER REHBERİ"; w = dd.textlength(s, font=f_tag)
    dd.rounded_rectangle((W - w - 70, 40, W - 40, 92), 26, fill=(0, 0, 0, 150)); dd.text((W - w - 55, 50), s, font=f_tag, fill=WHITE)

N = int(round(TOTAL * FPS))
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", "base.mp4", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{Hh}", "-r", str(FPS), "-i", "-",
                      "-i", "audio.m4a", "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
                      "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "copy", "-movflags", "+faststart", "-shortest", "GTA6_ilk_saatler_yatay.mp4"], stdin=subprocess.PIPE)
cache_key = None; cache = None
for fi in range(N):
    t = fi / FPS
    e = next((x for x in TL if x["t0"] <= t < x["t1"]), TL[-1])
    animating = (e["kind"] in ("card", "end") and t - e["t0"] < 0.6) or (e["kind"] == "card" and e["t1"] - t < 0.35) or t < 8 or \
                (e["kind"] == "block" and e.get("title") and (t - e["t0"] < 0.5 or e["t1"] - t < 0.35))
    capi = None
    if e["kind"] == "block":
        act = None
        for ci, c in enumerate(chunks):
            if WORDS[c[0]][1] - 0.05 <= t <= WORDS[c[-1]][2] + 0.25: act = ci
        hl = tuple(i for i in (chunks[act] if act is not None else []) if WORDS[i][1] <= t <= WORDS[i][2] + 0.15)
        capi = (act, hl)
    key = (id(e), capi) if not animating else None
    if key is not None and key == cache_key:
        p.stdin.write(cache); continue
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    if e["kind"] == "card": card(img, e, t)
    elif e["kind"] == "end": endcard(img, e, t)
    else:
        if t > 8: tag(img)
        badge(img, e, t); hook(img, t); caption(img, t)
    b = img.tobytes(); p.stdin.write(b)
    if key is not None: cache_key, cache = key, b
p.stdin.close(); p.wait(); print("done", N)
