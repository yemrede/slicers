import json, subprocess, os, sys, numpy as np, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H = os.path.dirname(os.path.abspath(__file__)); os.chdir(H)
SCR = os.path.dirname(H)
W_, H_, FPS, SR = 1920, 1080, 30, 44100
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FBo = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
def F(p, s): return ImageFont.truetype(p, s)
def up(s): return s.replace("i", "İ").replace("ı", "I").upper()
A = json.load(open("align.json"))

SRC = {
 "P": ("src/prologue.mp4", "crop=1600:900:0:180"),
 "B1": ("src/bigfoot1.mp4", "crop=1820:1024:0:0"),
 "B2": ("src/bigfoot2.mp4", "crop=1216:684:0:18"),
 "D": ("src/drive.mp4", "crop=854:480:0:0"),
 "G": ("src/gas.mp4", "crop=940:529:0:0"),
 "GO": ("src/golf.mp4", "crop=654:368:200:0"),
 "W": ("src/walk.mp4", "crop=640:360:0:0"),
 "XC": (SCR + "/footage/gameplay2/x_cat_2123070187343638528.mp4", None),
 "F": ("src/focus.mp4", "VERT"),
}
# blocks: (part, w0, w1, chapter_card or None, item_no, title, sub, shots)
B = [
 (0, 0, 50, None, 0, None, None, [("B2",300),("P",47),("B2",340),("XC",3),("B2",410),("P",168)]),
 (0, 50, 86, ("BÖLÜM 1", "İLK SAATLER", ("B2",520)), 1, "ÖNCE AÇILIŞ GÖREVLERİ", "Harita ve telefon bu görevlerle açılıyor", [("P",362),("P",425),("P",485),("P",560),("P",700)]),
 (0, 86, 123, None, 2, "FOCUS MODE", "İki analoğa aynı anda bas (L3 + R3)", [("B1",47),("B1",52),("F",1),("F",6)]),
 (0, 123, 153, None, 3, "KOYU MAVİ BİNA = GİRİLEBİLİR", "Açık mavi binalara giriş yok", [("B2",79),("W",2745),("P",288)]),
 (0, 153, 184, None, 4, "NPC'LERİ DİNLE", "Gizli yerler ve yan görevler", [("G",228),("G",245),("P",605),("D",290)]),
 (0, 184, None, None, 5, "PARTNERİNİ ÇAĞIR", "Tek tuşla Jason ya da Lucia", [("P",166),("W",2252),("W",1955)]),
 (1, 0, 32, ("BÖLÜM 2", "ARAÇLAR", ("D",60)), 6, "BENZİN BİTİYOR!", "Benzinlikte doldur ve tamir ettir", [("G",34),("G",44),("G",163),("G",175)]),
 (1, 32, 72, None, 7, "GİZLİ ARAÇ MENÜSÜ", "Radyo tuşu basılı + analog yukarı", [("D",62),("D",146),("D",302),("D",422),("D",650)]),
 (1, 72, 112, None, 8, "ARACI İT • TAKİP CİHAZI", "Yavaş gidersen polisi çağırıyor", [("XC",0),("XC",8),("D",962),("D",1178)]),
 (1, 112, 152, ("BÖLÜM 3", "POLİS", ("P",290)), 9, "POLİS KIYAFETİNİ TANIYOR", "Bagajda yedek kıyafet taşı", [("W",782),("P",946),("P",968),("W",2535),("W",2570)]),
 (1, 152, 183, ("BÖLÜM 4", "SOYGUN, SİLAH VE PARA", ("P",700)), 10, "SOYGUNA MÜŞTERİ GİBİ GİR", "Güvenlikçileri önceden işaretle", [("F",2),("P",706),("P",722),("G",424)]),
 (1, 183, None, None, 11, "SUÇ PROFİLİ + SİLAH SINIRI", "2 tüfek + 2 tabanca", [("P",676),("P",736),("P",845),("P",900)]),
 (2, 0, 25, ("BÖLÜM 5", "HAREKET VE EĞLENCE", ("B2",520)), 12, "EN HIZLI YÜZME", "Analoğa 1 kez = hızlı, 2 kez = maksimum", [("P",872),("P",884),("B1",2)]),
 (2, 25, 65, None, 13, "SADECE SUÇ YOK", "Mini golf, golf, bilardo, atari", [("GO",45),("GO",245),("GO",478),("W",2780)]),
 (2, 65, 96, ("BÖLÜM 6", "BİR NUMARALI TAVSİYE", ("P",1025)), 14, "GÖREVDEN ÖNCE KAYIT AL!", "Biten görevler tekrar oynanamıyor", [("P",1025),("W",2790),("P",1008)]),
 (2, 96, 125, ("BONUS", "GİZLİ SÜRPRİZ", ("B1",60)), 15, "BIGFOOT", "Cottonmouth Gölü'nün güneyi", [("B1",57),("B1",63),("B1",72),("B1",88)]),
 (2, 125, None, None, 0, None, None, [("B2",456),("B2",520),("B2",560)]),
]
INTRO, CARD, PAUSE, END = 1.2, 2.2, 0.35, 8.0

def pcm(path):
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",path,"-f","f32le","-ac","1","-ar",str(SR),"-"])
    return np.frombuffer(raw, np.float32)
parts = [pcm(f"audio/p{i+1}.mp3") for i in range(3)]
def whoosh():
    n = int(0.7*SR); t = np.arange(n)/SR
    noise = np.random.RandomState(1).randn(n).astype(np.float32)
    env = np.sin(np.pi*np.clip(t/0.7,0,1))**2
    # crude band sweep via moving average of varying width
    out = np.convolve(noise, np.ones(6)/6, mode="same") * env * 0.18
    return out.astype(np.float32)
WH = whoosh()

audio = [np.zeros(int(INTRO*SR), np.float32)]
tl = []   # timeline entries
cur = INTRO
whoosh_at = [0.0]
words_tl = []  # (word, start, end, block_index)
for bi, (p, w0, w1, card, no, title, sub, shots) in enumerate(B):
    tm = A[p]["times"]; wd = A[p]["words"]
    if card:
        tl.append(dict(kind="card", t0=cur, t1=cur+CARD, card=card))
        audio.append(np.zeros(int(CARD*SR), np.float32)); whoosh_at.append(cur); cur += CARD
    s = max(0.0, tm[w0][0] - 0.06)
    e = (tm[w1][0] - 0.06) if w1 is not None else A[p]["dur"]
    seg = parts[p][int(s*SR):int(e*SR)]
    audio.append(seg)
    t0 = cur; t1 = cur + len(seg)/SR
    for k in range(w0, w1 if w1 is not None else len(wd)):
        words_tl.append((wd[k], t0 + tm[k][0] - s, t0 + tm[k][1] - s, bi))
    tl.append(dict(kind="block", t0=t0, t1=t1, bi=bi, no=no, title=title, sub=sub, shots=shots))
    cur = t1
    if bi < len(B)-1:
        audio.append(np.zeros(int(PAUSE*SR), np.float32)); tl[-1]["t1"] += PAUSE; cur += PAUSE
tl.append(dict(kind="end", t0=cur, t1=cur+END)); audio.append(np.zeros(int(END*SR), np.float32)); cur += END
TOTAL = cur
mix = np.concatenate(audio)
for t in whoosh_at:
    i = int(t*SR); mix[i:i+len(WH)] += WH[:len(mix)-i]
mix.astype(np.float32).tofile("mix.f32")
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","mix.f32","-af","loudnorm=I=-15:TP=-1.5:LRA=11","-ar","48000","-c:a","aac","-b:a","192k","audio.m4a"], check=True)
print("TOTAL", TOTAL)
json.dump({"tl": tl, "words": words_tl, "total": TOTAL}, open("timeline.json","w"), ensure_ascii=False)

# ---------- base video segments
os.makedirs("seg", exist_ok=True)
def vf_for(key, blur=False):
    path, crop = SRC[key]
    if crop == "VERT":
        vf = ("crop=1080:1700:0:180,split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:2,eq=brightness=-0.18[bg];"
              "[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0")
    else:
        vf = (crop + "," if crop else "") + "scale=1920:1080:flags=lanczos,setsar=1"
        if key in ("D","GO","W","G","B2"): vf += ",unsharp=5:5:0.7"
    if blur: vf += ",boxblur=22:2,eq=brightness=-0.25"
    return path, vf
segs = []
def make(i, key, ss, dur, blur=False):
    path, vf = vf_for(key, blur)
    out = f"seg/{i:03d}.mp4"
    # gentle push-in
    z = f",scale=w='1920*(1+0.04*t/{max(dur,0.1):.2f})':h=-2:eval=frame,crop=1920:1080" if not blur else ""
    cmd = ["ffmpeg","-v","error","-y","-ss",str(ss),"-i",path,"-t",f"{dur:.3f}","-filter_complex",vf+z+f",fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","18",out]
    subprocess.run(cmd, check=True); segs.append(out)
i = 0
for e in tl:
    d = e["t1"] - e["t0"]
    if e["kind"] == "card":
        k, ss = e["card"][2]; make(i, k, ss, d, blur=True); i += 1
    elif e["kind"] == "end":
        make(i, "B2", 580, d, blur=True); i += 1
    else:
        shots = e["shots"]; n = len(shots)
        if e["bi"] == 0:  # prepend intro on first block
            pass
        each = d / n
        for (k, ss) in shots:
            make(i, k, ss, each); i += 1
# intro: first INTRO seconds -> blurred aerial
subprocess.run(["ffmpeg","-v","error","-y","-ss","296","-i","src/bigfoot2.mp4","-t",str(INTRO),"-vf","crop=1216:684:0:18,scale=1920:1080,boxblur=10:2,eq=brightness=-0.2,fps=30,format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","18","seg/intro.mp4"], check=True)
with open("concat.txt","w") as f:
    f.write("file 'seg/intro.mp4'\n")
    for s in segs: f.write(f"file '{s}'\n")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","concat.txt","-c","copy","base.mp4"], check=True)
print("base done")
