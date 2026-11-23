"""Shorts serisini yatay (1920x1080) derlemeye çevirir.
usage: yatay_seri.py plan.json
plan: {"out": "...mp4", "tag": "...", "parts": [{"spec": path, "voice": path, "align": path|null, "card": [num, title]|null, "cut_cta": bool, "t0": float, "t1": float|null}]}
"""
import sys, os, json, subprocess, re
sys.path.insert(0, "/tmp/claude-0/-home-user-slicers/1fb4aaf9-12b8-5cf7-8738-c907c6a2a6f6/scratchpad/gta6")
import engine as e
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS = 1920, 1080, 30
OVM = {
 "k1": (1, "SHIRLEY'NİN ROMU", "KOMŞUNUN İLK İŞİ"), "k2": (2, "PEGGY'NİN SCOOTER'I", "ÇAL VE KAÇ!"),
 "kwarn": (None, "TOURIST TRAP'TEN ÖNCE YAP!", "SONRA KİLİTLENİR"), "k3": (3, "BALKON MEDİTASYONU", "SADECE BÖLÜM 1'DE"),
 "g1": (1, "PAPAĞANIN ZULASI", "2.361$"), "g2": (2, "DONNIE'NİN .38'İ", "SADECE BU GÖREVDE"),
 "g3": (3, "PARANI KURTAR!", "AİLE BİRİKİM HESABI"), "gwarn": (None, "BÖLÜM 2'DE SİLİNİYOR!", "CÜZDAN + EV ZULASI"),
 "s1": (1, "EKRANDA GTA 5 HARİTASI", "MICHAEL'IN TEKNESİ Mİ?"), "s2": (2, "MANDY'NİN LAVABOSU", "BU BİR PARMAK MI?"),
 "s3": (3, "5 DERGİ VE KİTAP", "SADECE BÖLÜM 1'DE"),
 "l1": (1, "BERBER", "YENİ SAÇ KESİMİ"), "l2": (2, "ÖZEL KOLYE", "SONRA ÖNEMLİ!"), "l3": (3, "GÜL SİPARİŞİ", "EVE TESLİM"),
 "l4": (4, "MARKET", "BUZDOLABINI DOLDUR"), "l5": (5, "KIYAFETLER", "ANDY'DEN AL, BAGAJA"),
 "lbonus": (None, "BONUS: EVİ TAMİR ET", "LUCIA FARK EDİYOR"), "lwarn": (None, "LUCIA GELİNCE KAYBOLUR!", "SOYGUNLA TELAFİ ET"),
 "c1": (1, "JASON'IN ARABASI GİDİYOR", "MODİFİYEYE PARA HARCAMA"), "c2": (2, "İLK KAYIT BEDAVA", "SONRA 6.750$"),
 "c3": (3, "ARTAN PARAYA SİLAH AL", "SATIN ALINAN SİLAH KALIR"),
 "b1": (1, "LUCIA'NIN GÜNEŞ GÖZLÜĞÜ", "DAY RELEASE • YATTA"), "b2": (2, "DONNIE'NİN AVIATOR'U", "KARAVANIN BANYOSU"),
 "b3": (3, "ANDY'NİN CEKETİ", "HOME SWEET HOME"),
}
PINK, YEL, WHITE = (255, 60, 150), (255, 222, 0), (255, 255, 255)
fCap = e.font(e.FONT_BLACK, 64); fT = e.font(e.FONT_BLACK, 56); fS = e.font(e.FONT_BLACK, 40); fTag = e.font(e.FONT_BLACK, 30)
fRank = e.font(e.FONT_BLACK, 64); fCard = e.font(e.FONT_BLACK, 120); fCardS = e.font(e.FONT_BLACK, 48)

class Reader:
    def __init__(self, path, start):
        self.p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-i", path, "-vf",
            f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE)
        self.last = Image.new("RGB", (W, H))
    def next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3: self.last = Image.frombytes("RGB", (W, H), b)
        return self.last
    def close(self):
        try: self.p.kill()
        except Exception: pass

def lower_third(fr, key, t, dur):
    if key not in OVM: return
    rank, title, sub = OVM[key]
    d = ImageDraw.Draw(fr)
    k = min(1, t / 0.25); x0 = int(70 - (1 - k) * 600)
    y = 70
    if rank:
        d.ellipse([x0, y, x0 + 110, y + 110], fill=PINK, outline=WHITE, width=6)
        s = f"#{rank}"; w = e.text_w(d, s, fRank); d.text((x0 + 55 - w // 2, y + 18), s, font=fRank, fill=WHITE)
        x1 = x0 + 135
    else:
        x1 = x0
    tw = e.text_w(d, title, fT)
    d.rounded_rectangle([x1, y + 8, x1 + tw + 50, y + 100], 22, fill=(200, 0, 40) if rank is None else (20, 20, 30))
    d.text((x1 + 25, y + 20), title, font=fT, fill=WHITE)
    if sub and t > min(1.2, dur * 0.3):
        sw = e.text_w(d, sub, fS)
        d.rounded_rectangle([x1, y + 115, x1 + sw + 40, y + 180], 18, fill=YEL)
        d.text((x1 + 20, y + 124), sub, font=fS, fill=(10, 10, 10))

def caption(fr, chunks, t):
    d = ImageDraw.Draw(fr)
    for i, c in enumerate(chunks):
        cs = c[0]["start"]; ce = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else c[-1]["end"] + 0.3
        if cs <= t < ce:
            words = [e.tr_upper(x["text"]) for x in c]
            ws = [e.text_w(d, w + " ", fCap) for w in words]
            x = (W - sum(ws)) // 2; y = 930
            for w, x_w, tok in zip(words, ws, c):
                col = YEL if tok["start"] <= t < tok["end"] + 0.05 else WHITE
                d.text((x, y), w, font=fCap, fill=col, stroke_width=8, stroke_fill=(0, 0, 0)); x += x_w
            return

def tag(fr, s):
    d = ImageDraw.Draw(fr); w = e.text_w(d, s, fTag)
    d.rounded_rectangle([W - w - 90, 40, W - 40, 96], 26, fill=(0, 0, 0, 170)); d.text((W - w - 65, 50), s, font=fTag, fill=YEL)

def card_frames(bgimg, num, title, n):
    base = bgimg.filter(ImageFilter.GaussianBlur(18))
    base = Image.blend(base, Image.new("RGB", (W, H), (15, 8, 30)), 0.6)
    out = []
    for i in range(n):
        fr = base.copy(); d = ImageDraw.Draw(fr); k = min(1, i / 8)
        s1 = "BÖLÜM 1'DE KAÇIRMA"; w1 = e.text_w(d, s1, fCardS); d.text(((W - w1) // 2, 300), s1, font=fCardS, fill=YEL)
        if num:
            r = int(95 * (0.6 + 0.4 * k)); cx, cy = W // 2, 470
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PINK, outline=WHITE, width=8)
            s = f"#{num}"; w = e.text_w(d, s, fCard); d.text((cx - w // 2, cy - 75), s, font=fCard, fill=WHITE)
        w2 = e.text_w(d, title, fCard)
        f = fCard if w2 < W - 120 else e.font(e.FONT_BLACK, int(120 * (W - 120) / w2)); w2 = e.text_w(d, title, f)
        d.text(((W - w2) // 2, 610), title, font=f, fill=WHITE, stroke_width=10, stroke_fill=(0, 0, 0))
        out.append(fr)
    return out

def first_frame(path, start):
    b = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-i", path, "-frames:v", "1", "-vf",
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombytes("RGB", (W, H), b)

plan = json.load(open(sys.argv[1])); outd = os.path.dirname(os.path.abspath(sys.argv[1]))
vid = os.path.join(outd, "yatay_noaudio.mp4")
ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
audio_parts = []; T = 0.0; chapters = []
for part in plan["parts"]:
    spec = json.load(open(part["spec"]))
    spoken, words, tokens, events = e.parse(spec["script"])
    if part.get("align") and os.path.exists(part["align"]):
        times = json.load(open(part["align"]))["times"]
    else:
        times, _, _ = e.align(part["voice"], words)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", part["voice"]]))
    def ev(wi): return times[wi][0] if wi < len(times) else dur
    for tk in tokens:
        tk["start"] = times[tk["idx"][0]][0]; tk["end"] = times[tk["idx"][-1]][1]
    t0 = part.get("t0", 0.0)
    t1 = part.get("t1")
    if t1 is None:
        cta = next((ev(wi) for wi, k, a in events if k == "cta"), None)
        t1 = (cta - 0.08) if (part.get("cut_cta") and cta) else dur + 0.3
    scenes = [(ev(wi), a) for wi, k, a in events if k == "s"]
    ovs = [(ev(wi), a) for wi, k, a in events if k == "ov"]
    toks = [tk for tk in tokens if t0 <= tk["start"] < t1]
    chunks = e.chunk_tokens(toks)
    # chapter card
    if part.get("card"):
        num, title = part["card"]
        key = next(a for st, a in scenes if st >= t0 - 0.01) if scenes else None
        p = key[2:].split("@"); bg = first_frame(p[0], float(p[1]))
        n = int(2.4 * FPS)
        for fr in card_frames(bg, num, title, n): ff.stdin.write(fr.tobytes())
        audio_parts.append(("sil", n / FPS)); chapters.append((T, title)); T += n / FPS
    readers = {}
    nfr = int((t1 - t0) * FPS)
    for i in range(nfr):
        t = t0 + i / FPS
        si = max([j for j, (st, _) in enumerate(scenes) if st <= t] or [0])
        st, key = scenes[si]
        if si not in readers:
            for r in readers.values(): r.close()
            readers.clear()
            p = key[2:].split("@"); readers[si] = Reader(p[0], float(p[1]) + max(0, t - st))
        fr = readers[si].next().copy()
        if i > 0 and t - st < 0.1 and st > t0: fr = Image.blend(fr, Image.new("RGB", (W, H), WHITE), 0.4 * (1 - (t - st) / 0.1))
        ov = [(s, a) for s, a in ovs if s <= t]
        if ov and ov[-1][1] != "none":
            s0, a = ov[-1]
            nxt = [s for s, _ in ovs if s > s0]
            lower_third(fr, a, t - s0, (nxt[0] if nxt else t1) - s0)
        caption(fr, chunks, t)
        tag(fr, plan["tag"])
        ff.stdin.write(fr.tobytes())
    for r in readers.values(): r.close()
    audio_parts.append(("voice", part["voice"], t0, t1)); T += nfr / FPS
ff.stdin.close(); ff.wait()
# audio
inputs, filt, labs = [], [], []
for k, ap in enumerate(audio_parts):
    if ap[0] == "sil":
        filt.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{ap[1]}[a{k}]")
    else:
        inputs += ["-i", ap[1]]; n = len(inputs) // 2 - 1
        filt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,atrim={ap[2]}:{ap[3]},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, ap[3]-ap[2]-0.06)}:d=0.06[a{k}]")
    labs.append(f"[a{k}]")
filt.append("".join(labs) + f"concat=n={len(labs)}:v=0:a=1[a]")
out = os.path.join(outd, plan["out"])
subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + inputs + ["-i", vid, "-filter_complex", ";".join(filt), "-map", f"{len(inputs)//2}:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
json.dump(chapters, open(os.path.join(outd, "chapters.json"), "w"), ensure_ascii=False)
print("OUT", out, T)
