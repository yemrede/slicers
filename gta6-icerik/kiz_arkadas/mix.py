import json, subprocess
M=json.load(open("marks.json")); total=sum(m[1] for m in M)
inputs=[]; filt=[]; labs=[]; n=0
for i,(t,od,src,st,dur,sp,au) in enumerate(M):
    if au!="game": continue
    inputs+=["-ss",str(st),"-t",str(dur),"-i",f"src/{src}.mp4"]
    filt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,volume=6.5,afade=t=in:d=0.05,afade=t=out:st={dur-0.06}:d=0.06,adelay={int(t*1000)}|{int(t*1000)}[g{n}]"); labs.append(f"[g{n}]"); n+=1
tA=M[3][0]  # phone shot start = end of part A
tm=[m[0] for m in M if m[6]=="music"][0]
inputs+=["-ss","8.0","-t",str(tA),"-i","music/hw.mp4"]
filt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.5,afade=t=in:d=0.3,afade=t=out:st={tA-0.25}:d=0.25[ma]"); labs.append("[ma]"); n+=1
mdur=total-tm
inputs+=["-ss","36.55","-t",str(mdur),"-i","music/hw.mp4"]
filt.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,afade=t=in:d=0.05,afade=t=out:st={mdur-1.3}:d=1.3,volume=0.6,adelay={int(tm*1000)}|{int(tm*1000)}[mu]"); labs.append("[mu]"); n+=1
filt.append("".join(labs)+f"amix=inputs={len(labs)}:normalize=0,alimiter=limit=0.95,atrim=0:{total}[a]")
cmd=["ffmpeg","-loglevel","error","-y"]+inputs+["-i","v_noaudio.mp4","-filter_complex",";".join(filt),"-map",f"{n}:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart","GTA6_kiz_arkadas.mp4"]
subprocess.run(cmd,check=True); print("ok",total,tA,tm)
