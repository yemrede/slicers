import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-slicers/1fb4aaf9-12b8-5cf7-8738-c907c6a2a6f6/scratchpad/gta6")
import engine as e
from PIL import Image, ImageDraw, ImageEnhance
W, H = 1080, 1920
def panel(p, cx, cy, h, ch=900):
    im = Image.open(p).convert("RGB"); iw, ih = im.size
    cw = int(ch * W / h)
    x0 = max(0, min(iw - cw, cx - cw // 2)); y0 = max(0, min(ih - ch, cy - ch // 2))
    im = im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, h), Image.LANCZOS)
    return ImageEnhance.Color(im).enhance(1.15)
c = Image.new("RGB", (W, H))
c.paste(panel("cA.png", 930, 430, 960, ch=780), (0, 0))
c.paste(panel("cB.png", 1000, 500, 960), (0, 960))
d = ImageDraw.Draw(c)
d.rectangle([0, 950, W, 970], fill=(255, 222, 0))
def T(y, s, size, fill, box=None):
    f = e.font(e.FONT_BLACK, size); w = e.text_w(d, s, f)
    if w > W - 60: f = e.font(e.FONT_BLACK, int(size * (W - 60) / w)); w = e.text_w(d, s, f)
    if box: d.rounded_rectangle([(W - w) // 2 - 28, y - 10, (W + w) // 2 + 28, y + f.size + 18], 24, fill=box)
    d.text(((W - w) // 2, y), s, font=f, fill=fill, stroke_width=0 if box else 12, stroke_fill=(0, 0, 0))
T(640, "KIZ ARKADAŞI", 120, (255, 255, 255))
T(775, "EVDE YOKKEN", 140, e.YELLOW)
T(1440, "KIZ ARKADAŞI", 120, (255, 255, 255))
T(1580, "EVE GELİRKEN", 140, (255, 255, 255), box=e.TRRED)
c.save("kapak.jpg", quality=93)
