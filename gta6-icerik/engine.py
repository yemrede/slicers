"""Vertical Short renderer: script markup -> TTS -> word alignment -> 1080x1920 MP4.

Markup in script:
  {spoken|display}  spoken words go to TTS, display text shown in captions
  [[s:IMG]]         scene cut to image key (index in contact sheet or file path)
  [[row:CODE]]      reveal launch-board row
  [[panel:off]]     hide board
  [[hook]] / [[cta]] markers (hook headline shows from start until first scene change after 2.5s)
"""
import json, os, re, subprocess, sys, math, difflib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(ROOT)
IMG_DIR = os.path.join(SCR, "footage/official/img")
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
PINK, ORANGE, YELLOW, WHITE, BLACK = (255, 79, 163), (255, 158, 61), (255, 222, 0), (255, 255, 255), (0, 0, 0)
TRRED = (227, 10, 23)

_font_cache = {}
def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]

def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()

# ---------------------------------------------------------------- parsing
def parse(markup):
    """Return spoken_text, display tokens [{text, spoken_idx:[...]}], events [(spoken_word_idx, kind, arg)]"""
    tokens = []  # display tokens
    spoken_words = []
    events = []
    pos = 0
    pat = re.compile(r"\[\[(\w+)(?::([^\]]+))?\]\]|\{([^|}]+)\|([^}]+)\}|(\S+)")
    for m in pat.finditer(markup):
        if m.group(1):
            events.append((len(spoken_words), m.group(1), m.group(2)))
        elif m.group(3):
            sw = m.group(3).split()
            idxs = list(range(len(spoken_words), len(spoken_words) + len(sw)))
            spoken_words += sw
            # display may contain trailing punctuation outside braces; handled by next token
            tokens.append({"text": m.group(4), "idx": idxs})
        else:
            w = m.group(5)
            # punctuation glued after a {} group, e.g. "{x|y}."
            if re.fullmatch(r"[.,!?…:;]+", w) and tokens:
                tokens[-1]["text"] += w
                spoken_words[-1] += w
                continue
            spoken_words.append(w)
            tokens.append({"text": w, "idx": [len(spoken_words) - 1]})
    return " ".join(spoken_words), spoken_words, tokens, events

# ---------------------------------------------------------------- TTS
def tts_edge(text, out, voice="tr-TR-AhmetNeural", rate="+10%"):
    cmd = [sys.executable, "-m", "edge_tts", "--voice", voice, f"--rate={rate}", "--text", text, "--write-media", out]
    if os.environ.get("HTTPS_PROXY"):
        cmd[3:3] = ["--proxy", os.environ["HTTPS_PROXY"]]
    subprocess.run(cmd, check=True)

# ---------------------------------------------------------------- alignment
def norm(w):
    w = w.lower().replace("’", "'")
    return re.sub(r"[^a-zçğıöşü0-9']", "", w)

def align(audio, spoken_words):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    import numpy as np
    pcm = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", audio, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"])
    arr = np.frombuffer(pcm, dtype=np.float32)
    segs, _ = model.transcribe(arr, language="tr", word_timestamps=True,
                               initial_prompt=" ".join(spoken_words))
    rec = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    a = [norm(w) for w in spoken_words]
    b = [norm(w[0]) for w in rec]
    times = [None] * len(a)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (rec[j1 + k][1], rec[j1 + k][2])
        elif tag == "replace" and j2 > j1:
            # distribute recognised span across script span
            t0, t1 = rec[j1][1], rec[j2 - 1][2]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    # interpolate gaps
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio]).decode())
    for i in range(len(times)):
        if times[i] is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nj = next((j for j in range(i + 1, len(times)) if times[j]), None)
            nxt = times[nj][0] if nj is not None else dur
            gap = (nj if nj is not None else len(times)) - i
            step = (nxt - prev) / (gap + 1e-9)
            times[i] = (prev, prev + step)
            # fill consecutive
    return times, dur, rec

# ---------------------------------------------------------------- visuals
def load_bg(key, focus=0.5):
    path = key if os.path.isabs(str(key)) else None
    if path is None:
        idx = open(os.path.join(SCR, "contact_index.txt")).read().splitlines()
        name = dict(l.split(":", 1) for l in idx)[str(key)]
        path = os.path.join(IMG_DIR, name)
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    tw = int(ih * 9 / 16)
    if tw <= iw:
        x0 = int((iw - tw) * focus)
        im = im.crop((x0, 0, x0 + tw, ih))
    im = im.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)
    # grade: slightly darker for text legibility
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(0.78)
    im = ImageEnhance.Color(im).enhance(1.15)
    return im

def kenburns(im, p, zoom_in=True):
    z = 1.0 + 0.10 * (p if zoom_in else 1 - p)
    bw, bh = im.size
    cw, ch = int(bw / z), int(bh / z)
    x0 = (bw - cw) // 2
    y0 = (bh - ch) // 2
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)

def text_w(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

def draw_center(d, y, s, f, fill, stroke=8, sfill=BLACK):
    w = text_w(d, s, f)
    d.text(((W - w) // 2, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)

def gradient_bar(img, x0, y0, x1, y1, c0=PINK, c1=ORANGE):
    if x1 - x0 < 2:
        return
    g = Image.new("RGB", (x1 - x0, 1))
    for x in range(x1 - x0):
        t = x / max(1, x1 - x0 - 1)
        g.putpixel((x, 0), tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    img.paste(g.resize((x1 - x0, y1 - y0)), (x0, y0))

def chunk_tokens(tok_times):
    chunks, cur = [], []
    for t in tok_times:
        cur.append(t)
        txt = " ".join(x["text"] for x in cur)
        if len(cur) >= 3 or len(txt) >= 16 or re.search(r"[.,!?…]$", t["text"]):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    return chunks

def render(spec_path):
    spec = json.load(open(spec_path))
    out_dir = os.path.dirname(os.path.abspath(spec_path))
    spoken, spoken_words, tokens, events = parse(spec["script"])
    audio = os.path.join(out_dir, "voice.mp3")
    if spec.get("voice_file"):
        audio = spec["voice_file"]
    if not os.path.exists(audio):
        tts_edge(spoken, audio, spec.get("voice", "tr-TR-AhmetNeural"), spec.get("rate", "+10%"))
    times, dur, rec = align(audio, spoken_words)
    json.dump({"times": times, "rec": rec}, open(os.path.join(out_dir, "align.json"), "w"), ensure_ascii=False)
    for t in tokens:
        t["start"] = times[t["idx"][0]][0]
        t["end"] = times[t["idx"][-1]][1]
    def ev_time(wi):
        return times[wi][0] if wi < len(times) else dur
    scenes = [(ev_time(wi), arg) for wi, k, arg in events if k == "s"]
    rows_ev = {arg: ev_time(wi) for wi, k, arg in events if k == "row"}
    panel_off = next((ev_time(wi) for wi, k, a in events if k == "panel"), 1e9)
    cta_t = next((ev_time(wi) for wi, k, a in events if k == "cta"), 1e9)
    total = dur + 0.35
    nframes = int(total * FPS)
    focus = spec.get("focus", {})
    bgs = {}
    for _, key in scenes:
        if key not in bgs:
            bgs[key] = load_bg(key, focus.get(str(key), 0.5))
    chunks = chunk_tokens(tokens)
    board = spec.get("board", [])
    hook_lines = spec.get("hook_lines", [])

    vid = os.path.join(out_dir, "video_noaudio.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    f_cap = font(FONT_BLACK, 84)
    f_hook = font(FONT_BLACK, 92)
    f_row = font(FONT_BLACK, 50)
    f_rowsm = font(FONT_BOLD, 30)
    f_title = font(FONT_BLACK, 40)
    f_tag = font(FONT_BLACK, 34)
    for fi in range(nframes):
        t = fi / FPS
        # scene
        si = max([i for i, (st, _) in enumerate(scenes) if st <= t] or [0])
        st, key = scenes[si]
        en = scenes[si + 1][0] if si + 1 < len(scenes) else total
        p = min(1, (t - st) / max(0.1, en - st))
        frame = kenburns(bgs[key], p, zoom_in=(si % 2 == 0))
        # punch-in on cut
        dt = t - st
        if si > 0 and dt < 0.12:
            frame = Image.blend(frame, Image.new("RGB", (W, H), WHITE), 0.55 * (1 - dt / 0.12))
        # vignette bottom/top for legibility
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for y in range(0, 360):
            od.line([(0, y), (W, y)], fill=(0, 0, 0, int(150 * (1 - y / 360))))
        for y in range(H - 700, H):
            od.line([(0, y), (W, y)], fill=(0, 0, 0, int(190 * ((y - (H - 700)) / 700))))
        # board
        if board and t < panel_off + 0.3:
            alpha_mul = 1.0 if t < panel_off else max(0, 1 - (t - panel_off) / 0.3)
            visible = [r for r in board if rows_ev.get(r["code"], 1e9) <= t]
            if visible:
                x0, y0, x1 = 70, 470, W - 130
                rh = 86
                y1 = y0 + 70 + rh * len(board) + 10
                od.rounded_rectangle([x0, y0, x1, y1], 28, fill=(10, 6, 30, int(200 * alpha_mul)))
                last = visible[-1]["code"]
                for ri, r in enumerate(board):
                    rt = rows_ev.get(r["code"], 1e9)
                    if rt > t:
                        continue
                    k = min(1, (t - rt) / 0.18)
                    ry = y0 + 70 + ri * rh
                    xoff = int((1 - k) * 80)
                    a = int(255 * k * alpha_mul)
                    is_tr = r["code"] == "TR"
                    if r["code"] == last or is_tr:
                        col = TRRED if is_tr else PINK
                        od.rounded_rectangle([x0 + 14 + xoff, ry + 4, x1 - 14 + xoff, ry + rh - 6], 18, fill=col + (int(a * 0.92),))
                    od.rounded_rectangle([x0 + 30 + xoff, ry + 18, x0 + 112 + xoff, ry + rh - 20], 10, fill=(255, 255, 255, a))
                    cw_ = text_w(od, r["code"], f_rowsm)
                    od.text((x0 + 71 + xoff - cw_ // 2, ry + 25), r["code"], font=f_rowsm, fill=(20, 10, 40, a))
                    od.text((x0 + 132 + xoff, ry + 14), tr_upper(r["name"]), font=f_row, fill=(255, 255, 255, a))
                    tw_ = text_w(od, r["time"], f_row)
                    od.text((x1 - 36 - tw_ + xoff, ry + 14), r["time"], font=f_row, fill=(YELLOW if not is_tr else WHITE) + (a,))
                    if r.get("note"):
                        nw = text_w(od, r["note"], f_rowsm)
                        od.text((x1 - 36 - tw_ - 18 - nw + xoff, ry + 30), r["note"], font=f_rowsm, fill=(255, 255, 255, int(a * 0.85)))
                od.text((x0 + 32, y0 + 18), spec.get("board_title", ""), font=f_title, fill=(255, 255, 255, int(235 * alpha_mul)))
        frame = Image.alpha_composite(frame.convert("RGBA"), ov)
        d = ImageDraw.Draw(frame)
        # top tag + progress
        gradient_bar(frame, 0, 0, int(W * min(1, t / total)), 12)
        tag = spec.get("tag", "")
        if tag:
            tw_ = text_w(d, tag, f_tag)
            d.rounded_rectangle([(W - tw_) // 2 - 22, 60, (W + tw_) // 2 + 22, 116], 28, fill=(0, 0, 0, 170))
            d.text(((W - tw_) // 2, 66), tag, font=f_tag, fill=YELLOW)
        # hook headline
        hook_end = spec.get("hook_until", 2.8)
        if t < hook_end and hook_lines:
            k = min(1, t / 0.15)
            sc = 1.25 - 0.25 * k
            yy = 190
            for li, (line, colr) in enumerate(hook_lines):
                f = font(FONT_BLACK, int(92 * sc))
                draw_center(d, yy, line, f, tuple(colr), stroke=10)
                yy += int(108 * sc)
        # CTA
        if t >= cta_t:
            k = min(1, (t - cta_t) / 0.2)
            lines = spec.get("cta_lines", ["TAKİP ET"])
            f = font(FONT_BLACK, int(86 * (0.8 + 0.2 * k)))
            y = 640
            maxw = max(text_w(d, l, f) for l in lines)
            d.rounded_rectangle([(W - maxw) // 2 - 40, y - 26, (W + maxw) // 2 + 40, y + 104 * len(lines) + 10], 40, fill=TRRED)
            for l in lines:
                w = text_w(d, l, f)
                d.text(((W - w) // 2, y), l, font=f, fill=WHITE)
                y += 104
            f2 = font(FONT_BLACK, 52)
            l2 = spec.get("cta_sub", "👇 YORUMLARA YAZ").replace("👇 ", "")
            w2 = text_w(d, l2, f2)
            d.text(((W - w2) // 2, y + 40), l2, font=f2, fill=YELLOW, stroke_width=7, stroke_fill=BLACK)
        # captions
        ci = None
        for i, c in enumerate(chunks):
            cs = c[0]["start"]
            ce = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else c[-1]["end"] + 0.3
            if cs <= t < ce:
                ci = i
                break
        if ci is not None:
            c = chunks[ci]
            words = [tr_upper(x["text"]) for x in c]
            k = min(1, (t - c[0]["start"]) / 0.1)
            f = font(FONT_BLACK, int(84 * (1.12 - 0.12 * k)))
            sp = text_w(d, " ", f)
            ws = [text_w(d, w, f) for w in words]
            total_w = sum(ws) + sp * (len(ws) - 1)
            if total_w > W - 140:
                f = font(FONT_BLACK, int(84 * (W - 140) / total_w))
                ws = [text_w(d, w, f) for w in words]; sp = text_w(d, " ", f)
                total_w = sum(ws) + sp * (len(ws) - 1)
            x = (W - total_w) // 2
            y = spec.get("caption_y", 1390)
            for w, wd, tok in zip(words, ws, c):
                active = tok["start"] <= t < (tok["end"] + 0.05)
                d.text((x, y), w, font=f, fill=YELLOW if active else WHITE, stroke_width=9, stroke_fill=BLACK)
                x += wd + sp
        ff.stdin.write(frame.convert("RGB").tobytes())
        if fi % 150 == 0:
            print(f"frame {fi}/{nframes}", flush=True)
    ff.stdin.close(); ff.wait()
    # audio: voice + whoosh per cut
    sfx = os.path.join(ROOT, "whoosh.wav")
    if not os.path.exists(sfx):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.6",
                        "-af", "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.25,volume=0.5", sfx], check=True)
    cuts = [st for st, _ in scenes[1:]]
    inputs = ["-i", vid, "-i", audio]
    filt = []
    for i, c in enumerate(cuts):
        inputs += ["-i", sfx]
        filt.append(f"[{i+2}:a]adelay={int(max(0,c-0.15)*1000)}|{int(max(0,c-0.15)*1000)}[w{i}]")
    mix = "[1:a]" + "".join(f"[w{i}]" for i in range(len(cuts)))
    filt.append(f"{mix}amix=inputs={len(cuts)+1}:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    out = os.path.join(out_dir, spec.get("out", "short.mp4"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", ";".join(filt), "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    print("OUT", out, f"{total:.1f}s")

if __name__ == "__main__":
    render(sys.argv[1])
