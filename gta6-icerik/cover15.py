import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as e
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
W, H = 1080, 1920
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]
# background: blurred gameplay + purple tint
iw, ih = src.size; tw = int(ih * W / H); x0 = (iw - tw) // 2
bg = src.crop((x0, 0, x0 + tw, ih)).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
bg = Image.blend(bg, Image.new("RGB", (W, H), (40, 16, 70)), 0.55).convert("RGBA")
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
gd.ellipse([40, 560, 1040, 1420], fill=(255, 60, 170, 110))
bg = Image.alpha_composite(bg, glow.filter(ImageFilter.GaussianBlur(120)))
d = ImageDraw.Draw(bg)

def C(y, s, size, fill, stroke=12):
    f = e.font(e.FONT_BLACK, size); w = e.text_w(d, s, f)
    if w > W - 70:
        f = e.font(e.FONT_BLACK, int(size * (W - 70) / w)); w = e.text_w(d, s, f)
    d.text(((W - w) // 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

C(255, "KONSOLU OLMAYANLARA", 104, (255, 255, 255))
C(372, "MÜJDE!", 230, e.YELLOW, stroke=16)

# browser window
bx0, by0, bw, bar, ch = 60, 690, 960, 74, 540
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
sd.rounded_rectangle([bx0 - 6, by0 + 14, bx0 + bw + 6, by0 + bar + ch + 26], 34, fill=(0, 0, 0, 200))
bg = Image.alpha_composite(bg, sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(bg)
d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bar + ch], 30, fill=(24, 24, 34), outline=(255, 255, 255), width=5)
for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
    cx = bx0 + 42 + i * 40; d.ellipse([cx - 13, by0 + 24, cx + 13, by0 + 50], fill=c)
ax0 = bx0 + 170; d.rounded_rectangle([ax0, by0 + 15, bx0 + bw - 28, by0 + 59], 22, fill=(52, 52, 66))
# lock icon
lx, ly = ax0 + 24, by0 + 26
d.rounded_rectangle([lx, ly + 9, lx + 20, ly + 25], 4, fill=(120, 230, 140))
d.arc([lx + 3, ly - 1, lx + 17, ly + 17], 180, 360, fill=(120, 230, 140), width=4)
fu = e.font(e.FONT_BOLD, 30); d.text((lx + 36, by0 + 20), "tarayıcıda oyna  •  konsol gerekmez", font=fu, fill=(225, 225, 235))
inner = src.resize((bw - 10, ch - 5), Image.LANCZOS)
inner = ImageEnhance.Color(inner).enhance(1.25); inner = ImageEnhance.Contrast(inner).enhance(1.08)
mask = Image.new("L", inner.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, -40, inner.size[0], inner.size[1]], 26, fill=255)
bg.paste(inner, (bx0 + 5, by0 + bar), mask); d = ImageDraw.Draw(bg)
# CANLI badge
fb = e.font(e.FONT_BLACK, 40); d.rounded_rectangle([bx0 + 26, by0 + bar + 24, bx0 + 222, by0 + bar + 88], 14, fill=(230, 20, 40))
d.ellipse([bx0 + 42, by0 + bar + 44, bx0 + 66, by0 + bar + 68], fill=(255, 255, 255)); d.text((bx0 + 78, by0 + bar + 30), "CANLI", font=fb, fill=(255, 255, 255))
# play button
pcx, pcy, r = bx0 + bw // 2, by0 + bar + ch // 2, 105
pl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
pd.ellipse([pcx - r, pcy - r, pcx + r, pcy + r], fill=(0, 0, 0, 120), outline=(255, 255, 255, 255), width=10)
pd.polygon([(pcx - 34, pcy - 52), (pcx - 34, pcy + 52), (pcx + 56, pcy)], fill=(255, 255, 255, 255))
bg = Image.alpha_composite(bg, pl); d = ImageDraw.Draw(bg)
# mouse cursor
mx, my = pcx + 70, pcy + 60
cur = [(0, 0), (0, 92), (24, 70), (42, 110), (60, 102), (42, 64), (74, 64)]
d.polygon([(mx + x, my + y) for x, y in cur], fill=(255, 255, 255), outline=(0, 0, 0), width=5)
# crossed-out controller badge
gx, gy, gr = bx0 + bw - 78, by0 + 6, 104
d.ellipse([gx - gr - 8, gy - gr - 8, gx + gr + 8, gy + gr + 8], fill=(0, 0, 0))
d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(255, 255, 255), outline=(230, 20, 40), width=16)
pc = (30, 30, 40)
d.rounded_rectangle([gx - 70, gy - 30, gx + 70, gy + 26], 26, fill=pc)
d.ellipse([gx - 82, gy - 16, gx - 34, gy + 50], fill=pc); d.ellipse([gx + 34, gy - 16, gx + 82, gy + 50], fill=pc)
d.rectangle([gx - 56, gy - 6, gx - 30, gy + 2], fill=(255, 255, 255)); d.rectangle([gx - 47, gy - 15, gx - 39, gy + 11], fill=(255, 255, 255))
for ox, oy in [(38, -10), (52, 2), (24, 2), (38, 14)]:
    d.ellipse([gx + ox - 6, gy + oy - 6, gx + ox + 6, gy + oy + 6], fill=(255, 255, 255))
d.line([(gx - 72, gy - 72), (gx + 72, gy + 72)], fill=(230, 20, 40), width=20)
# bottom text
C(1340, "GTA 6 TARAYICIDAN", 128, (255, 255, 255))
f = e.font(e.FONT_BLACK, 116); s = "DA OYNANIYOR!"; w = e.text_w(d, s, f)
d.rounded_rectangle([(W - w) // 2 - 34, 1494, (W + w) // 2 + 34, 1640], 30, fill=e.TRRED)
d.text(((W - w) // 2, 1502), s, font=f, fill=(255, 255, 255))
f2 = e.font(e.FONT_BLACK, 52); s2 = "10 DAKİKA ÜCRETSİZ"; w2 = e.text_w(d, s2, f2)
e.gradient_bar(bg, (W - w2) // 2 - 32, 1690, (W + w2) // 2 + 32, 1774)
d = ImageDraw.Draw(bg); d.text(((W - w2) // 2, 1698), s2, font=f2, fill=(20, 10, 40))
bg.convert("RGB").save(out, quality=93); print(out)
