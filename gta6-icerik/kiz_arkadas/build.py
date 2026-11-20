import sys, os, subprocess, numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-slicers/1fb4aaf9-12b8-5cf7-8738-c907c6a2a6f6/scratchpad/gta6")
import engine as e
from PIL import Image, ImageDraw
K = os.path.dirname(os.path.abspath(__file__)); S = K + "/src/"
W, H, FPS = 1080, 1920, 30
VW, VH, VY = 1080, 705, 640
# (src, start, srcdur, speed, cropx, top, bottom, audio)
A = "KIZ ARKADAŞI EVDE|YOKKEN ERKEKLER:"
B = "KIZ ARKADAŞI|EVE GELİRKEN:"
shots = [
 ("bros", 23.6, 3.0, 1, 240, A, "BİRALAR AÇILDI", "game"),
 ("bros", 35.0, 2.6, 1, 240, A, "SABAHA KADAR OYUN", "game"),
 ("bros", 161.6, 6.2, 1, 240, A, "ERTESİ SABAH...", "game"),
 ("bros", 173.8, 4.2, 1, 300, "AMA SONRA|TELEFON ÇALDI...", "LUCIA ARIYOR: EVE GELİYOR!", "game"),
 ("fix", 105.0, 4.4, 2, 240, B, "BOYA", "music"),
 ("fix", 125.0, 4.4, 2, 240, B, "BOYA", "music"),
 ("feng", 260.0, 4.4, 2, 240, B, "MOBİLYA", "music"),
 ("fix", 200.0, 4.4, 2, 240, B, "MERDİVEN", "music"),
 ("fix", 283.0, 4.4, 2, 240, B, "ÇATI", "music"),
 ("fix", 365.0, 4.4, 2, 240, B, "KORKULUK", "music"),
 ("reunite", 183.5, 6.5, 1, 480, "SEN HANGİSİSİN?", "YORUMLARA YAZ!", "music"),
]
fT = e.font(e.FONT_BLACK, 104); fB = e.font(e.FONT_BLACK, 84)
def draw_text(d, y, s, f, fill, maxw=W - 70):
    ff = f; w = e.text_w(d, s, ff)
    if w > maxw:
        ff = e.font(e.FONT_BLACK, int(f.size * maxw / w)); w = e.text_w(d, s, ff)
    d.text(((W - w) // 2, y), s, font=ff, fill=fill, stroke_width=10, stroke_fill=(0, 0, 0))
    return ff.size
bg = Image.new("RGB", (W, H), (14, 12, 22))
gd = ImageDraw.Draw(bg)
for y in range(H):
    k = abs(y - H / 2) / (H / 2); c = int(14 + 18 * (1 - k)); gd.line([(0, y), (W, y)], fill=(c + 8, c, c + 18))
out = K + "/v_noaudio.mp4"
ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
t = 0.0; marks = []
for si, (src, st, dur, sp, cx, top, bot, au) in enumerate(shots):
    od = dur / sp; n = int(round(od * FPS))
    DL = {"fix": "delogo=x=1588:y=108:w=280:h=64,", "feng": "delogo=x=18:y=12:w=380:h=56,", "reunite": "delogo=x=1728:y=76:w=150:h=42,"}.get(src, "")
    cy = 62 if src == "reunite" else 15
    vf = f"{DL}setpts=PTS/{sp},fps={FPS},crop=1440:940:{cx}:{cy},scale={VW}:{VH}"
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(st), "-i", S + src + ".mp4", "-t", str(dur), "-vf", vf, "-an",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for i in range(n):
        b = p.stdout.read(VW * VH * 3)
        if len(b) == VW * VH * 3: last = Image.frombytes("RGB", (VW, VH), b)
        fr = bg.copy()
        if last: fr.paste(last, (0, VY))
        d = ImageDraw.Draw(fr)
        lt = i / FPS
        # flash on cut
        if si > 0 and lt < 0.08:
            fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), 0.5 * (1 - lt / 0.08)); d = ImageDraw.Draw(fr)
        lines = top.split("|"); y = VY - 50 - 120 * len(lines)
        for li, l in enumerate(lines):
            draw_text(d, y + li * 120, l, fT, (255, 255, 255) if li < len(lines) - 1 or len(lines) == 1 else e.YELLOW)
        # bottom caption pops in
        k = min(1, lt / 0.12); sc = 1.25 - 0.25 * k
        fb = e.font(e.FONT_BLACK, int(96 * sc))
        col = (255, 60, 60) if "LUCIA" in bot else (e.YELLOW if si == len(shots) - 1 else (255, 255, 255))
        draw_text(d, VY + VH + 70, bot, fb, col)
        if si == len(shots) - 1:
            pass
        ff.stdin.write(fr.tobytes())
    p.stdout.close(); p.wait()
    marks.append((t, od, src, st, dur, sp, au)); t += n / FPS
ff.stdin.close(); ff.wait()
import json; json.dump(marks, open(K + "/marks.json", "w"))
print("video", t)
