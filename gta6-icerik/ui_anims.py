"""Procedural UI animation scenes for 1080x1920 Shorts.
Scene keys: ui:<name>; render(name, t, dur, ctx) -> RGB Image.
Screenshots (1170x1992, iPhone 13 Pro) live in ctx['ui_dir'].
Codes shown are placeholders (XXXX), never real.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H = 1080, 1920
KICK = (83, 252, 24)
TWITCH = (145, 70, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 222, 0)
ORANGE = (255, 158, 61)

_cache = {}
def _img(ctx, name):
    k = ("img", name)
    if k not in _cache:
        _cache[k] = Image.open(os.path.join(ctx["ui_dir"], name + ".png")).convert("RGB")
    return _cache[k]

def _bg(ctx, name):
    k = ("bg", name)
    if k not in _cache:
        im = _img(ctx, name)
        b = im.resize((W, int(W * im.size[1] / im.size[0])))
        b = b.crop((0, 0, W, min(b.size[1], H))).resize((W, H))
        b = b.filter(ImageFilter.GaussianBlur(28))
        _cache[k] = ImageEnhance.Brightness(b).enhance(0.45)
    return _cache[k].copy()

def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

PW = 860  # phone screen width
PX, PY = (W - PW) // 2, 150

def phone(ctx, name, t, zoom=0.0):
    """Blurred bg + phone with screenshot. Returns (frame, mapper px->frame)."""
    fr = _bg(ctx, name)
    shot = _img(ctx, name)
    s = PW / shot.size[0] * (1 + zoom)
    sw, sh = int(shot.size[0] * s), int(shot.size[1] * s)
    scr = shot.resize((sw, sh), Image.BILINEAR)
    # crop to phone window
    ph = int(1992 * PW / 1170)
    ox = (sw - PW) // 2
    scr = scr.crop((ox, 0, ox + PW, ph))
    # entrance: slide up
    k = ease(t / 0.35)
    py = int(PY + (1 - k) * 260)
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle([PX - 22, py - 22, PX + PW + 22, py + ph + 22], 70, fill=(12, 12, 14))
    mask = Image.new("L", (PW, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, PW, ph], 52, fill=255)
    fr.paste(scr, (PX, py), mask)
    def m(x, y):
        return (PX + (x * s - ox), py + y * s)
    return fr, m, py

def ripple(fr, x, y, t0, t):
    if t < t0 or t > t0 + 0.6:
        return
    p = (t - t0) / 0.6
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    r = 30 + 90 * p
    d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, int(255 * (1 - p))), width=10)
    rr = 34
    d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, int(170 * (1 - p))))
    fr.paste(Image.alpha_composite(fr.convert("RGBA"), ov).convert("RGB"))

def chip(fr, text, y, color, t, t0, font, fg=(10, 10, 10), x=None):
    if t < t0:
        return
    k = ease((t - t0) / 0.25)
    d = ImageDraw.Draw(fr)
    f = font(int(64 * (0.7 + 0.3 * k)))
    b = d.textbbox((0, 0), text, font=f); w = b[2] - b[0]
    cx = W // 2 if x is None else x
    d.rounded_rectangle([cx - w // 2 - 34, y - 16, cx + w // 2 + 34, y + 86], 40, fill=color)
    d.text((cx - w // 2, y), text, font=f, fill=fg)

# ------------------------------------------------------------------ scenes
def kick_home(ctx, t, dur, font):
    fr, m, py = phone(ctx, "kick_home", t)
    x, y = m(585, 343)
    ripple(fr, x, y, 1.4, t)
    if t > 1.3:  # highlight banner
        d = ImageDraw.Draw(fr)
        a0 = m(40, 200); a1 = m(1130, 490)
        d.rounded_rectangle([a0[0], a0[1], a1[0], a1[1]], 30, outline=KICK, width=8)
    chip(fr, "10.000 KOD", 1440, KICK, t, 2.0, font)
    return fr

def kick_login(ctx, t, dur, font):
    fr, m, py = phone(ctx, "kick_login", t)
    d = ImageDraw.Draw(fr)
    f = font(46, bold=True)
    user = "oyuncu_tr"
    t0 = 0.15
    cdt = max(0.03, dur * 0.40 / len(user))
    pdt = max(0.02, dur * 0.18 / 10)
    n = int(max(0, (t - t0)) / cdt)
    ux, uy = m(80, 520)
    d.text((ux, uy), user[:n], font=f, fill=WHITE)
    tp = t0 + len(user) * cdt
    pn = int(max(0, (t - tp)) / pdt)
    px, pyy = m(80, 752)
    d.text((px, pyy), "•" * min(pn, 10), font=f, fill=WHITE)
    tb = tp + 10 * pdt + 0.05
    bx, by = m(585, 1053)
    ripple(fr, bx, by, tb, t)
    chip(fr, "1) GİRİŞ YAP", 1440, KICK, t, 0.05, font)
    return fr

def kick_watch(ctx, t, dur, font):
    fr, m, py = phone(ctx, "kick_gta", t)
    d = ImageDraw.Draw(fr)
    # live dot + timer pill over stream card
    p = ease(t / max(0.6, dur - 0.3))
    mins = int(180 * p)
    y = 1120
    d.rounded_rectangle([150, y, W - 150, y + 170], 40, fill=(15, 15, 18), outline=KICK, width=6)
    f = font(54)
    d.text((190, y + 22), f"İZLEME SÜRESİ  {mins:3d} / 180 dk", font=f, fill=WHITE)
    d.rounded_rectangle([190, y + 105, W - 190, y + 140], 18, fill=(50, 50, 55))
    d.rounded_rectangle([190, y + 105, 190 + int((W - 380) * p), y + 140], 18, fill=KICK)
    chip(fr, "2) 180 DK İZLE", 1440, KICK, t, 0.1, font)
    return fr

def kick_case(ctx, t, dur, font):
    # full-frame dark scene with glowing case
    fr = Image.new("RGB", (W, H), (8, 10, 8))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    glow = 0.5 + 0.5 * math.sin(t * 6)
    for r in range(520, 60, -40):
        a = int(10 + 22 * glow * (1 - r / 520))
        d.ellipse([W // 2 - r, 900 - r, W // 2 + r, 900 + r], fill=KICK + (a,))
    fr = Image.alpha_composite(fr.convert("RGBA"), ov)
    d = ImageDraw.Draw(fr)
    ft = font(58)
    s = "KICK • SUNSET REWARD CASE"
    b = d.textbbox((0, 0), s, font=ft); d.text(((W - b[2] + b[0]) // 2, 190), s, font=ft, fill=KICK)
    # phases
    drop = ease(t / 0.45)
    cy = int(-300 + (950 + 300) * drop)
    shake = 0
    if 0.6 < t < 1.5:
        shake = int(18 * math.sin(t * 60) * (1 - abs((t - 1.05) / 0.45)))
    open_k = ease((t - 1.5) / 0.35)
    cx = W // 2 + shake
    bw, bh = 520, 330
    # body
    d.rounded_rectangle([cx - bw // 2, cy - bh // 2 + 40, cx + bw // 2, cy + bh // 2 + 40], 36, fill=(30, 36, 30), outline=KICK, width=10)
    d.rectangle([cx - 40, cy - bh // 2 + 40, cx + 40, cy + bh // 2 + 40], fill=KICK)
    # lid
    lid_y = cy - bh // 2 + 40 - int(260 * open_k)
    lid_rot_alpha = int(255 * (1 - 0.5 * open_k))
    d.rounded_rectangle([cx - bw // 2 - 20, lid_y - 110, cx + bw // 2 + 20, lid_y + 10], 30, fill=(40, 48, 40, lid_rot_alpha), outline=KICK, width=10)
    d.rectangle([cx - 40, lid_y - 110, cx + 40, lid_y + 10], fill=KICK)
    # flash + rays
    if t > 1.5:
        fk = max(0, 1 - (t - 1.5) / 0.5)
        ov2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(ov2)
        for i in range(14):
            ang = i / 14 * 2 * math.pi + t
            x2 = cx + math.cos(ang) * 900; y2 = cy + math.sin(ang) * 900
            d2.polygon([(cx, cy), (x2 - 60, y2), (x2 + 60, y2)], fill=(200, 255, 170, int(60 * (0.4 + 0.6 * glow))))
        d2.rectangle([0, 0, W, H], fill=(255, 255, 255, int(200 * fk)))
        fr = Image.alpha_composite(fr, ov2); d = ImageDraw.Draw(fr)
    # card rises
    ck = ease((t - 1.8) / 0.5)
    if ck > 0:
        cw, ch = 640, 400
        y0 = int(cy - 40 - 330 * ck)
        art = _img(ctx, "card_art") if os.path.exists(os.path.join(ctx["ui_dir"], "card_art.png")) else None
        d.rounded_rectangle([W // 2 - cw // 2, y0 - ch // 2, W // 2 + cw // 2, y0 + ch // 2], 34, fill=(16, 16, 20), outline=YELLOW, width=8)
        if art is not None:
            a = art.resize((cw - 40, 200))
            fr.paste(a, (W // 2 - cw // 2 + 20, y0 - ch // 2 + 20))
        f1 = font(46); f2 = font(54)
        s1 = "GTA VI • ULTIMATE EDITION"
        b = d.textbbox((0, 0), s1, font=f1); d.text(((W - b[2] + b[0]) // 2, y0 + 40), s1, font=f1, fill=WHITE)
        s2 = "XXXX-XXXX-XXXX"
        b = d.textbbox((0, 0), s2, font=f2); d.text(((W - b[2] + b[0]) // 2, y0 + 110), s2, font=f2, fill=YELLOW)
    fr = fr.convert("RGB")
    chip(fr, "3) KASAYI AÇ • HER GÜN 1", 1440, KICK, t, 0.2, font)
    return fr

def kick_drops(ctx, t, dur, font):
    fr, m, py = phone(ctx, "kick_drops", t)
    x, y = m(1640 / 4 * 1.0, 0)  # unused
    bx, by = m(1170 * 0.70, 1580)
    ripple(fr, bx, by, 0.3, t)
    chip(fr, "12 KASIM – 7 ARALIK", 1050, (255, 255, 255), t, 0.5, font)
    third = dur / 3
    chip(fr, "XBOX ✓ DÜNYA GENELİ", 1200, KICK, t, max(0.9, dur * 0.38), font)
    chip(fr, "PS5 ⚠ BÖLGEYE BAĞLI", 1340, ORANGE, t, max(1.6, dur * 0.70), font)
    return fr

def twitch_login(ctx, t, dur, font):
    fr, m, py = phone(ctx, "twitch_login", t)
    d = ImageDraw.Draw(fr)
    f = font(46, bold=True)
    user = "oyuncu_tr"
    n = int(max(0, (t - 0.3)) / 0.1)
    ux, uy = m(80, 270)
    d.text((ux, uy), user[:n], font=f, fill=(20, 20, 20))
    chip(fr, "TWITCH", 1440, TWITCH, t, 0.1, font, fg=WHITE)
    return fr

def twitch_drop(ctx, t, dur, font):
    fr, m, py = phone(ctx, "twitch_gta", t)
    d = ImageDraw.Draw(fr)
    k = ease((t - 0.4) / 0.4)
    ty = int(py - 260 + 360 * k)
    tx0, tx1 = PX + 30, PX + PW - 30
    d.rounded_rectangle([tx0, ty, tx1, ty + 250], 30, fill=(24, 24, 27), outline=TWITCH, width=6)
    # gift icon
    gx, gy = tx0 + 40, ty + 60
    d.rounded_rectangle([gx, gy + 30, gx + 120, gy + 130], 12, fill=TWITCH)
    d.rectangle([gx - 8, gy + 10, gx + 128, gy + 40], fill=(170, 110, 255))
    d.rectangle([gx + 50, gy + 10, gx + 70, gy + 130], fill=YELLOW)
    f1 = font(44); f2 = font(36, bold=True)
    p = ease((t - 0.9) / max(0.5, dur - 1.6))
    won = p >= 0.999
    d.text((gx + 160, ty + 36), "GTA VI kodu kazandın!" if won else "Drop ilerlemesi", font=f1, fill=WHITE)
    d.text((gx + 160, ty + 100), "Her gün • 19–30 Kasım", font=f2, fill=(200, 200, 210))
    d.rounded_rectangle([gx + 160, ty + 165, tx1 - 40, ty + 195], 15, fill=(60, 60, 66))
    d.rounded_rectangle([gx + 160, ty + 165, gx + 160 + int((tx1 - 40 - gx - 160) * p), ty + 195], 15, fill=TWITCH)
    chip(fr, "HER GÜN KOD DROP'U", 1440, TWITCH, t, 0.2, font, fg=WHITE)
    return fr

SCENES = {f.__name__: f for f in [kick_home, kick_login, kick_watch, kick_case, kick_drops, twitch_login, twitch_drop]}

def render(name, t, dur, ctx, font):
    return SCENES[name](ctx, t, dur, font)


# ------------------------------------------------------------------ overlays on top of any scene
VID_TOP, VID_BOT = 510, 1330  # letterboxed video window
DBLUE, LBLUE = (30, 70, 200), (150, 200, 255)

def _section_chip(fr, text, t, font, color=YELLOW):
    k = ease(t / 0.25)
    d = ImageDraw.Draw(fr)
    f = font(int(58 * (0.8 + 0.2 * k)))
    b = d.textbbox((0, 0), text, font=f); w = b[2] - b[0]
    x = (W - w) // 2; y = 400
    d.rounded_rectangle([x - 30, y - 12, x + w + 30, y + 78], 36, fill=(10, 10, 12, 235), outline=color, width=6)
    d.text((x, y), text, font=f, fill=color)

def _sub_chip(fr, text, y, color, t, t0, font, fg=(10, 10, 10)):
    if t < t0:
        return
    k = ease((t - t0) / 0.25)
    d = ImageDraw.Draw(fr)
    f = font(int(54 * (0.75 + 0.25 * k)))
    b = d.textbbox((0, 0), text, font=f); w = b[2] - b[0]
    x = (W - w) // 2
    d.rounded_rectangle([x - 30, y - 12, x + w + 30, y + 74], 34, fill=color)
    d.text((x, y), text, font=f, fill=fg)

def _controller(fr, cx, cy, t, press):
    d = ImageDraw.Draw(fr)
    w, h = 460, 250
    d.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], 110, fill=(30, 30, 36, 240), outline=WHITE, width=6)
    for sx in (cx - 95, cx + 95):
        r = 52
        pr = 10 if press else 0
        d.ellipse([sx - r, cy + 10 - r + pr, sx + r, cy + 10 + r + pr], fill=(70, 70, 80), outline=YELLOW if press else WHITE, width=6)
        d.ellipse([sx - 26, cy + 10 - 26 + pr, sx + 26, cy + 10 + 26 + pr], fill=(110, 110, 120))
        if press:
            d.polygon([(sx - 22, cy - 92), (sx + 22, cy - 92), (sx, cy - 62)], fill=YELLOW)

def _rings(fr, cx, cy, t):
    ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(4):
        p = ((t * 0.8) + i / 4) % 1.0
        r = 30 + 260 * p
        a = int(230 * (1 - p))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 222, 0, a), width=10)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 222, 0, 230))
    fr.alpha_composite(ov)

def ov_rule1(fr, t, dur, font):
    _section_chip(fr, "1 • ÖNCE AÇILIŞ GÖREVLERİ", t, font)
    _sub_chip(fr, "HARİTA + TELEFON AÇILIR", 1210, KICK, t, dur * 0.55, font)

def ov_focus(fr, t, dur, font):
    _section_chip(fr, "2 • FOCUS MODE", t, font)
    press = (t > 0.6 and (int(t * 3) % 2 == 0)) or (dur * 0.25 < t < dur * 0.45)
    if t < dur * 0.5:
        _controller(fr, W // 2, 1150, t, press)
        _sub_chip(fr, "L3 + R3  /  İKİ ANALOĞA BAS", 1310, YELLOW, t, 0.4, font)
    else:
        _rings(fr, int(W * 0.66), 860, t)
        _sub_chip(fr, "GİZLİ KARŞILAŞMA YAKINDA!", 1230, YELLOW, t, dur * 0.5, font)

def ov_map(fr, t, dur, font):
    _section_chip(fr, "3 • HARİTA RENKLERİ", t, font)
    k = ease((t - 0.2) / 0.35)
    if k <= 0:
        return
    d = ImageDraw.Draw(fr)
    pw, ph = 440, 330
    px0 = W - pw - 60 + int((1 - k) * 200); py0 = 540
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], 26, fill=(18, 24, 36, 240), outline=WHITE, width=5)
    d.text((px0 + 24, py0 + 14), "HARİTA", font=font(34), fill=WHITE)
    cols, rows = 3, 2
    cw, ch = (pw - 40) // cols, (ph - 80) // rows
    pattern = [True, False, True, False, True, False]
    fm = font(52)
    for i in range(cols * rows):
        gx, gy = i % cols, i // cols
        bx = px0 + 20 + gx * cw + 8; by = py0 + 64 + gy * ch + 8
        dark = pattern[i]
        d.rounded_rectangle([bx, by, bx + cw - 16, by + ch - 16], 12, fill=DBLUE if dark else LBLUE)
        if t > dur * 0.40:
            d.text((bx + (cw - 16) // 2 - 18, by + (ch - 16) // 2 - 34), "✓" if dark else "✗", font=fm,
                   fill=(120, 255, 120) if dark else (255, 90, 90), stroke_width=4, stroke_fill=(0, 0, 0))
    _sub_chip(fr, "KOYU MAVİ = GİRİLEBİLİR ✓", 1120, DBLUE, t, dur * 0.25, font, fg=WHITE)
    _sub_chip(fr, "AÇIK MAVİ = GİRİLEMEZ ✗", 1230, LBLUE, t, dur * 0.70, font)

def ov_npc(fr, t, dur, font):
    _section_chip(fr, "4 • NPC'LERİ DİNLE", t, font)
    k = ease((t - 0.3) / 0.3)
    if k > 0:
        d = ImageDraw.Draw(fr)
        bx, by = int(W * 0.58), 600
        bw, bh = int(330 * k), int(150 * k)
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 40, fill=(255, 255, 255, 240))
        d.polygon([(bx + 40, by + bh - 4), (bx + 90, by + bh - 4), (bx + 20, by + bh + 50)], fill=(255, 255, 255, 240))
        n = int(t * 3) % 4
        for i in range(3):
            c = (30, 30, 30) if i < n else (180, 180, 180)
            d.ellipse([bx + 70 + i * 70, by + bh // 2 - 18, bx + 106 + i * 70, by + bh // 2 + 18], fill=c)
    _sub_chip(fr, "GİZLİ SAKLANMA YERLERİNİ ÖĞREN", 1230, YELLOW, t, dur * 0.4, font)

OVERLAYS = {"rule1": ov_rule1, "focus": ov_focus, "map": ov_map, "npc": ov_npc}

def overlay(name, fr, t, dur, font):
    f = OVERLAYS.get(name)
    if f:
        f(fr, t, dur, font)


# ------------------------------------------------------------------ countdown overlays (en çılgın 5 detay)
PINK2 = (255, 79, 163)

def _rank(fr, n, t, font):
    k = ease(t / 0.22)
    d = ImageDraw.Draw(fr)
    s = int(190 * (1.4 - 0.4 * k))
    cx, cy = 150, 640
    d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=PINK2, outline=WHITE, width=8)
    f = font(int(s * 0.55)); txt = f"#{n}"
    b = d.textbbox((0, 0), txt, font=f)
    d.text((cx - (b[2] - b[0]) // 2 - b[0], cy - (b[3] - b[1]) // 2 - b[1]), txt, font=f, fill=WHITE)

def _icon_lock(d, cx, cy, s, col=(255, 70, 70)):
    d.rounded_rectangle([cx - s, cy - s * 0.2, cx + s, cy + s * 1.1], int(s * 0.25), fill=col)
    d.arc([cx - s * 0.65, cy - s * 1.2, cx + s * 0.65, cy + s * 0.2], 180, 360, fill=col, width=int(s * 0.28))
    d.ellipse([cx - s * 0.18, cy + s * 0.25, cx + s * 0.18, cy + s * 0.6], fill=WHITE)

def _icon_bed(d, cx, cy, s):
    d.rounded_rectangle([cx - s * 1.3, cy - s * 0.1, cx + s * 1.3, cy + s * 0.5], 14, fill=(120, 170, 255))
    d.rounded_rectangle([cx - s * 1.3, cy - s * 0.9, cx - s * 0.9, cy + s * 0.9], 10, fill=(80, 120, 220))
    d.rounded_rectangle([cx - s * 0.85, cy - s * 0.5, cx - s * 0.2, cy - s * 0.1], 14, fill=WHITE)

def _icon_cat(d, cx, cy, s, t):
    sh = int(8 * math.sin(t * 30))
    cx += sh
    d.polygon([(cx - s * 0.9, cy - s * 0.4), (cx - s * 0.6, cy - s * 1.2), (cx - s * 0.2, cy - s * 0.7)], fill=(255, 158, 61))
    d.polygon([(cx + s * 0.9, cy - s * 0.4), (cx + s * 0.6, cy - s * 1.2), (cx + s * 0.2, cy - s * 0.7)], fill=(255, 158, 61))
    d.ellipse([cx - s, cy - s * 0.9, cx + s, cy + s * 0.9], fill=(255, 158, 61))
    for ex in (-0.4, 0.4):
        d.line([(cx + s * (ex - 0.25), cy - s * 0.35), (cx + s * (ex + 0.25), cy - s * 0.15 if ex < 0 else cy - s * 0.55)], fill=(20, 20, 20), width=10)
        d.ellipse([cx + s * (ex - 0.12), cy - s * 0.15, cx + s * (ex + 0.12), cy + s * 0.1], fill=(20, 20, 20))
    d.arc([cx - s * 0.35, cy + s * 0.25, cx + s * 0.35, cy + s * 0.75], 200, 340, fill=(20, 20, 20), width=8)

def _icon_dog(d, cx, cy, s, t):
    bob = int(10 * math.sin(t * 8))
    cy += bob
    d.ellipse([cx - s * 1.25, cy - s * 0.6, cx - s * 0.55, cy + s * 0.6], fill=(150, 95, 50))
    d.ellipse([cx + s * 0.55, cy - s * 0.6, cx + s * 1.25, cy + s * 0.6], fill=(150, 95, 50))
    d.ellipse([cx - s, cy - s * 0.9, cx + s, cy + s * 0.9], fill=(210, 160, 100))
    d.rounded_rectangle([cx - s * 0.85, cy - s * 0.35, cx - s * 0.08, cy + s * 0.05], 14, fill=(15, 15, 15))
    d.rounded_rectangle([cx + s * 0.08, cy - s * 0.35, cx + s * 0.85, cy + s * 0.05], 14, fill=(15, 15, 15))
    d.line([(cx - s * 0.1, cy - s * 0.2), (cx + s * 0.1, cy - s * 0.2)], fill=(15, 15, 15), width=8)
    d.ellipse([cx - s * 0.2, cy + s * 0.2, cx + s * 0.2, cy + s * 0.5], fill=(30, 20, 20))

def _birds(fr, t):
    ov = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    rng = random.Random(3)
    for i in range(9):
        x0 = rng.randint(-200, 900); y0 = rng.randint(560, 1100); sp = rng.uniform(140, 260)
        x = (x0 + t * sp) % 1300 - 100; y = y0 + 20 * math.sin(t * 3 + i)
        w = 26 + 10 * abs(math.sin(t * 8 + i))
        d.line([(x - w, y - w * 0.5), (x, y), (x + w, y - w * 0.5)], fill=(255, 255, 255, 230), width=7)
    fr.alpha_composite(ov)

def _card(fr, title, sub, t, font, color):
    _sub_chip(fr, title, 1180, color, t, 0.15, font, fg=WHITE if color != YELLOW else (10, 10, 10))
    if sub:
        _sub_chip(fr, sub, 1290, YELLOW, t, 0.7, font)

def ov_c5(fr, t, dur, font):
    _rank(fr, 5, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_lock(d, W - 190, 680, 70)
    _card(fr, "TERLİK + ÇORAP = KİLİTLİ", "ROCKSTAR İZİN VERMİYOR", t, font, (200, 0, 20))

def ov_c4(fr, t, dur, font):
    _rank(fr, 4, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_bed(d, W - 200, 680, 70)
    _card(fr, "ODANI DEKORE ET", "SUÇ YERİNE EV DEKORU", t, font, (60, 110, 230))

def ov_c3(fr, t, dur, font):
    _rank(fr, 3, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_cat(d, W - 190, 690, 75, t)
    _card(fr, "SİNİRLİ KEDİ ALARMI", None, t, font, (230, 110, 20))

def ov_c2(fr, t, dur, font):
    _rank(fr, 2, t, font); d = ImageDraw.Draw(fr)
    if t > dur * 0.45: _icon_dog(d, W - 200, 700, 80, t)
    _card(fr, "KÖPEK KURTARMAYA GELİYOR!", None, t, font, (40, 150, 90)) if t > dur * 0.45 else _card(fr, "DENİZDE KAYBOLURSAN…", None, t, font, (40, 110, 200))

def ov_c1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _birds(fr, t)
    _card(fr, "62 KUŞ TÜRÜ + DOĞA DEFTERİ", "KUŞ GÖZLEMCİSİ GTA?!" if t > dur * 0.55 else None, t, font, (40, 150, 90))

OVERLAYS.update({"c5": ov_c5, "c4": ov_c4, "c3": ov_c3, "c2": ov_c2, "c1": ov_c1})

# --- 4'lü versiyon (gerçek kliplerle) ---
def ov_d4(fr, t, dur, font):
    _rank(fr, 4, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_lock(d, W - 190, 680, 70)
    _card(fr, "TERLİK + ÇORAP = KİLİTLİ", "ROCKSTAR İZİN VERMİYOR", t, font, (200, 0, 20))

def ov_d3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "EVİ KENDİN TAMİR ET", "LUCIA İLE İLİŞKİN GÜÇLENİYOR" if t > dur * 0.6 else "ALÇIPAN + BOYA", t, font, (60, 110, 230))

def ov_d2(fr, t, dur, font):
    _rank(fr, 2, t, font); d = ImageDraw.Draw(fr)
    if t > dur * 0.4: _icon_cat(d, W - 190, 690, 75, t)
    _card(fr, "ARKA KOLTUKTA KEDİ!", "TUŞA HIZLI BAS" if t > dur * 0.6 else None, t, font, (230, 110, 20))

def ov_d1(fr, t, dur, font):
    _rank(fr, 1, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_dog(d, W - 200, 700, 80, t)
    _card(fr, "JET SKİYİ KÖPEK SÜRÜYOR", None, t, font, (40, 150, 90))

OVERLAYS.update({"d4": ov_d4, "d3": ov_d3, "d2": ov_d2, "d1": ov_d1})

# --- easter egg videosu ---
def ov_e4(fr, t, dur, font):
    _rank(fr, 4, t, font)
    _card(fr, "DEXTER'IN APARTMANI", "ÇATIDA ALETLER VAR" if t > dur * 0.5 else None, t, font, (200, 0, 20))
def ov_e3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "KULEDEKİ YUMURTA", "AŞAĞI AT = GİZLİ SAHNE" if t > dur * 0.55 else None, t, font, (230, 110, 20))
def ov_e2(fr, t, dur, font):
    _rank(fr, 2, t, font); d = ImageDraw.Draw(fr)
    if t > 0.3: _icon_dog(d, W - 200, 700, 80, t)
    _card(fr, "COOL DOG + KÖPEK ADASI", "1.000$+ PARA" if t > dur * 0.6 else None, t, font, (40, 150, 90))
def ov_e1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _card(fr, "GECE 02:00'DEN SONRA UFO", "GİZLİ KUPA AÇILIYOR" if t > dur * 0.6 else None, t, font, (60, 110, 230))
OVERLAYS.update({"e4": ov_e4, "e3": ov_e3, "e2": ov_e2, "e1": ov_e1})

# --- Türkçe NPC videosu ---
def ov_trnpc(fr, t, dur, font):
    _card(fr, "ORİJİNAL OYUN SESİ", "HASTANE GÖREVİ" if t > dur * 0.4 else None, t, font, (200, 0, 20))
def ov_trrs(fr, t, dur, font):
    _card(fr, "ROCKSTAR DOĞRULADI", "TÜRKÇE KONUŞAN KARAKTER VAR" if t > dur * 0.3 else None, t, font, (40, 150, 90))
OVERLAYS.update({"trnpc": ov_trnpc, "trrs": ov_trrs})

# --- Paul Walker videosu ---
def ov_pwloc(fr, t, dur, font):
    _card(fr, "VESPUCCI ADASI", "RIALTO ADALARI • BEYAZ EV" if t > dur * 0.35 else None, t, font, (40, 110, 200))
def ov_pwcar(fr, t, dur, font):
    _card(fr, "MAIBATSU PENUMBRA", "= BRIAN'IN ECLIPSE'İ" if t > dur * 0.4 else None, t, font, (40, 150, 90))
def ov_pwplate(fr, t, dur, font):
    _card(fr, "PLAKA: HAD YOU", "\"NEREDEYSE YAKALIYORDUM\"" if t > dur * 0.4 else None, t, font, (200, 0, 20))
OVERLAYS.update({"pwloc": ov_pwloc, "pwcar": ov_pwcar, "pwplate": ov_pwplate})

# --- tarayıcıdan GTA 6 videosu ---
def ov_trcd(fr, t, dur, font):
    from PIL import ImageFont
    d = ImageDraw.Draw(fr)
    rem = max(0, 600 - int(t * 40))
    s = f"{rem//60:02d}:{rem%60:02d}"
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 120)
    w = d.textlength(s, font=f)
    d.rounded_rectangle(((W - w) / 2 - 40, 330, (W + w) / 2 + 40, 490), 36, fill=(10, 10, 18, 220))
    d.text(((W - w) / 2, 345), s, font=f, fill=(90, 230, 255))
    _card(fr, "KONTROL SENDE!", "10 DAKİKA ÜCRETSİZ", t, font, (40, 150, 90))
def ov_trwarn(fr, t, dur, font):
    d = ImageDraw.Draw(fr)
    if t > 0.2: _icon_lock(d, W - 190, 680, 70)
    _card(fr, "TAKLİT SİTELERE DİKKAT!", "PARA KAPTIRMA" if t > dur * 0.4 else None, t, font, (200, 0, 20))
def ov_trnot(fr, t, dur, font):
    _card(fr, "RESMİ DEĞİL", "ROCKSTAR İLE BAĞI YOK", t, font, (230, 110, 20))
OVERLAYS.update({"trcd": ov_trcd, "trwarn": ov_trwarn, "trnot": ov_trnot})

# --- geri dönen karakterler ---
def ov_dn1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _card(fr, "NİKO BELLİC", "GTA 4'ÜN ANA KARAKTERİ" if t > dur * 0.35 else None, t, font, (200, 0, 20))
def ov_dn2(fr, t, dur, font):
    _rank(fr, 2, t, font)
    _card(fr, "JIMMY DE SANTA", "55.275 TAKİPÇİ" if t > dur * 0.35 else None, t, font, (230, 110, 20))
def ov_dn3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "VALENTINA", "GTA ONLINE'DAN" if t > dur * 0.35 else None, t, font, (150, 60, 200))
OVERLAYS.update({"dn1": ov_dn1, "dn2": ov_dn2, "dn3": ov_dn3})

# --- Bölüm 1 kaçırma #1 ---
def ov_k1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _card(fr, "SHIRLEY'NİN ROMU", "KOMŞUNUN İLK İŞİ" if t > dur * 0.35 else None, t, font, (230, 110, 20))
def ov_k2(fr, t, dur, font):
    _rank(fr, 2, t, font)
    _card(fr, "PEGGY'NİN SCOOTER'I", "ÇAL VE KAÇ!" if t > dur * 0.35 else None, t, font, (200, 0, 20))
def ov_kwarn(fr, t, dur, font):
    d = ImageDraw.Draw(fr)
    if t > 0.2: _icon_lock(d, W // 2, 640, 80)
    _card(fr, "TOURIST TRAP'TEN ÖNCE YAP!", "SONRA KİLİTLENİR" if t > dur * 0.3 else None, t, font, (200, 0, 20))
def ov_k3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "BALKON MEDİTASYONU", "SADECE BÖLÜM 1'DE" if t > dur * 0.35 else None, t, font, (60, 110, 230))
OVERLAYS.update({"k1": ov_k1, "k2": ov_k2, "kwarn": ov_kwarn, "k3": ov_k3})

# --- Bölüm 1 kaçırma #2 ---
def ov_g1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _card(fr, "PAPAĞANIN ZULASI", "2.361$" if t > dur * 0.35 else None, t, font, (40, 150, 90))
def ov_g2(fr, t, dur, font):
    _rank(fr, 2, t, font)
    _card(fr, "DONNIE'NİN .38'İ", "SADECE BU GÖREVDE" if t > dur * 0.35 else None, t, font, (200, 0, 20))
def ov_g3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "PARANI KURTAR!", "AİLE BİRİKİM HESABI" if t > dur * 0.35 else None, t, font, (230, 110, 20))
def ov_gwarn(fr, t, dur, font):
    d = ImageDraw.Draw(fr)
    if t > 0.2: _icon_lock(d, W // 2, 640, 80)
    _card(fr, "BÖLÜM 2'DE SİLİNİYOR!", "CÜZDAN + EV ZULASI" if t > dur * 0.3 else None, t, font, (200, 0, 20))
OVERLAYS.update({"g1": ov_g1, "g2": ov_g2, "g3": ov_g3, "gwarn": ov_gwarn})

# --- Bölüm 1 kaçırma #3 ---
def ov_s1(fr, t, dur, font):
    _rank(fr, 1, t, font)
    _card(fr, "EKRANDA GTA 5 HARİTASI", "MICHAEL'IN TEKNESİ Mİ?" if t > dur * 0.35 else None, t, font, (60, 110, 230))
def ov_s2(fr, t, dur, font):
    _rank(fr, 2, t, font)
    _card(fr, "MANDY'NİN LAVABOSU", "BU BİR PARMAK MI?" if t > dur * 0.35 else None, t, font, (200, 0, 20))
def ov_s3(fr, t, dur, font):
    _rank(fr, 3, t, font)
    _card(fr, "5 DERGİ VE KİTAP", "SADECE BÖLÜM 1'DE" if t > dur * 0.35 else None, t, font, (230, 110, 20))
OVERLAYS.update({"s1": ov_s1, "s2": ov_s2, "s3": ov_s3})

# --- Bölüm 1 kaçırma #4 (Lucia) ---
def _lstep(fr, t, dur, font, n, title, sub, col):
    _rank(fr, n, t, font)
    _card(fr, title, sub if t > dur * 0.3 else None, t, font, col)
OVERLAYS.update({
 "l1": lambda fr, t, dur, font: _lstep(fr, t, dur, font, 1, "BERBER", "YENİ SAÇ KESİMİ", (60, 110, 230)),
 "l2": lambda fr, t, dur, font: _lstep(fr, t, dur, font, 2, "ÖZEL KOLYE", "SONRA ÖNEMLİ!", (230, 110, 20)),
 "l3": lambda fr, t, dur, font: _lstep(fr, t, dur, font, 3, "GÜL SİPARİŞİ", "EVE TESLİM", (200, 0, 80)),
 "l4": lambda fr, t, dur, font: _lstep(fr, t, dur, font, 4, "MARKET", "BUZDOLABINI DOLDUR", (40, 150, 90)),
 "l5": lambda fr, t, dur, font: _lstep(fr, t, dur, font, 5, "KIYAFETLER", "ANDY'DEN AL, BAGAJA", (150, 60, 200)),
 "lbonus": lambda fr, t, dur, font: _card(fr, "BONUS: EVİ TAMİR ET", "LUCIA FARK EDİYOR" if t > dur * 0.3 else None, t, font, (230, 110, 20)),
 "lwarn": lambda fr, t, dur, font: _card(fr, "LUCIA GELİNCE KAYBOLUR!", "SOYGUNLA TELAFİ ET" if t > dur * 0.45 else None, t, font, (200, 0, 20)),
})

# --- Bölüm 1 kaçırma #5 ---
OVERLAYS.update({
 "c1": lambda fr, t, dur, font: (_rank(fr, 1, t, font), _card(fr, "JASON'IN ARABASI GİDİYOR", "MODİFİYEYE PARA HARCAMA" if t > dur * 0.3 else None, t, font, (200, 0, 20))),
 "c2": lambda fr, t, dur, font: (_rank(fr, 2, t, font), _card(fr, "İLK KAYIT BEDAVA", "SONRA 6.750$" if t > dur * 0.4 else None, t, font, (40, 150, 90))),
 "c3": lambda fr, t, dur, font: (_rank(fr, 3, t, font), _card(fr, "ARTAN PARAYA SİLAH AL", "SATIN ALINAN SİLAH KALIR" if t > dur * 0.3 else None, t, font, (60, 110, 230))),
})

# --- Vercetti malikanesi ---
OVERLAYS.update({
 "vloc": lambda fr, t, dur, font: _card(fr, "STARFISH ISLAND", "VICE CITY'NİN KARŞISI" if t > dur * 0.3 else None, t, font, (60, 110, 230)),
 "vcop": lambda fr, t, dur, font: _card(fr, "DİKKAT: POLİS GELİYOR!", "ARANMA YILDIZI" if t > dur * 0.3 else None, t, font, (200, 0, 20)),
 "vcar": lambda fr, t, dur, font: _card(fr, "ÖZEL ARAÇ", "MODİFİYE ETME!" if t > dur * 0.3 else None, t, font, (230, 110, 20)),
 "vgar": lambda fr, t, dur, font: _card(fr, "GARAJDA SÜPER ARABALAR", None, t, font, (40, 150, 90)),
})
