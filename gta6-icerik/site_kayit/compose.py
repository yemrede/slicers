import json, sys, subprocess, numpy as np
from PIL import Image, ImageDraw
D = sys.argv[1]; OUTD = sys.argv[2]
L = json.load(open(f"{D}/log.json"))
W, H, FPS = 1080, 1920, 30
PW, PH = 1170, 1992
VR = (166, 510, 838, 471)  # video rect in page coords at scrollY=0 (CSS y 170 -> 510)
TOP, BOT = (38, 22, 58), (20, 12, 33)

def stream_reader(off, dur):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(off), "-i", f"{D}/stream.mp4", "-t", str(dur + 1),
                          "-vf", f"fps={FPS},scale={VR[2]}:{VR[3]}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = [None]
    def nxt():
        b = p.stdout.read(VR[2] * VR[3] * 3)
        if len(b) == VR[2] * VR[3] * 3:
            last[0] = Image.frombytes("RGB", (VR[2], VR[3]), b)
        return last[0]
    return nxt

def lerp(a, b, k): return a + (b - a) * k
def ease(k): return k * k * (3 - 2 * k)

def scene(name, label, rel0, dur, box0, box1, soff=None, tap=None):
    fr = [x for x in L if x["label"] == label]
    t0 = fr[0]["t"] + rel0
    sr = stream_reader(soff, dur) if soff is not None else None
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", f"{OUTD}/{name}.mp4"], stdin=subprocess.PIPE)
    cache = {}
    canvas = Image.new("RGB", (PW, PH + 400))
    for i in range(int(dur * FPS)):
        tt = t0 + i / FPS
        f = max([x for x in fr if x["t"] <= tt] or [fr[0]], key=lambda x: x["t"])
        if f["name"] not in cache:
            cache.clear(); cache[f["name"]] = Image.open(f"{D}/fr/{f['name']}").convert("RGB")
        page = cache[f["name"]].copy()
        if sr:
            s = sr()
            vy = VR[1] - f["y"] * 3
            if s is not None and vy + VR[3] > 0:
                page.paste(s, (VR[0], vy))
        if tap and tap[2] <= i / FPS < tap[2] + 0.9:
            k = (i / FPS - tap[2]) / 0.9
            ov = Image.new("RGBA", page.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            x, y = tap[0], tap[1]
            r = 40 + 130 * k
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, int(230 * (1 - k))), width=10)
            if k < 0.55:
                d.ellipse([x - 46, y - 46, x + 46, y + 46], fill=(255, 255, 255, 150))
            page = Image.alpha_composite(page.convert("RGBA"), ov).convert("RGB")
        # pad canvas: page at y=200 inside a taller canvas with bg colors
        canvas.paste(TOP, (0, 0, PW, 200)); canvas.paste(BOT, (0, PH + 200, PW, PH + 400))
        canvas.paste(page, (0, 200))
        k = ease(i / max(1, dur * FPS - 1))
        cx, cy, bw = [lerp(a, b, k) for a, b in zip(box0, box1)]
        bh = bw * H / W
        box = (cx - bw / 2, cy - bh / 2 + 200, cx + bw / 2, cy + bh / 2 + 200)
        out = canvas.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
        ff.stdin.write(out.tobytes())
    ff.stdin.close(); ff.wait()
    print("ok", name)

which = sys.argv[3:] or ["c1", "c2", "c3"]
if "c1" in which: scene("c1", "top", 0.0, 7.0, (585, 996, 1170), (585, 930, 1110), soff=2.0)
if "c2" in which: scene("c2", "top", 6.0, 5.5, (585, 900, 1000), (585, 840, 920), soff=12.0)
if "c3" in which: scene("c3", "timer", 1.0, 4.5, (585, 996, 1170), (585, 930, 1040), soff=20.0, tap=(585, 921, 1.0))
