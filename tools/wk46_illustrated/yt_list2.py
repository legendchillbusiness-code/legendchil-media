import os,sys,subprocess,json
os.environ.setdefault("S","/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yt_illus as Y
import yt_illus2 as Z
from PIL import Image
W,H,FPS=Z.W,Z.H,30
COL=["verde","vermelho","ambar","azul"]
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode())
def make(spec,out):
    S=os.environ["S"]; vo=f"{S}/ytw/vo"
    items=spec["items"]; N=len(items); GAP=0.28
    segs=[]  # (wav, base, base_ill, text_for_captions)
    # intro
    s0,i0=items[0]
    ser0=s0; ill0=Y.ILL[(s0,i0)]
    tag="PSYCHOLOGY SAYS" if s0=="facts" else "PSYCHOLOGY ABOUT GIRLS"
    base_i,_=Z.slide_v2(tag,spec["title"],"",COL[spec["c0"]%4],ill0)
    segs.append((f"{vo}/{spec['intro']}.wav",base_i,spec["intro_text"]))
    for k,(ser,i) in enumerate(items):
        h,b=(Y.FACTS if ser=="facts" else Y.GIRLS)[i]
        tg=f"#{k+1} OF {N}"
        base,_=Z.slide_v2(tg,h,b,COL[(spec["c0"]+k+1)%4],Y.ILL[(ser,i)])
        segs.append((f"{vo}/{ser}_{i}.wav",base,h+" "+b))
    durs=[dur(w) for w,_,_ in segs]
    # audio concat with gaps
    ins=[]; fl=[]
    for n,(w,_,_) in enumerate(segs):
        ins+=["-i",w]; fl.append(f"[{n}]apad=pad_dur={GAP}[a{n}]")
    fl.append("".join(f"[a{n}]" for n in range(len(segs)))+f"concat=n={len(segs)}:v=0:a=1[voice]")
    voice=out.replace(".mp4","_voice.wav")
    subprocess.check_call(["ffmpeg","-nostdin","-v","error","-y"]+ins+["-filter_complex",";".join(fl),"-map","[voice]",voice])
    T=sum(durs)+GAP*len(segs)
    END=float(os.environ.get("END","3.0")); TOT=T+END
    fc=f"[1:a]apad[v];[2:a]aloop=loop=-1:size=2e9,volume=-16dB[m];[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{TOT},afade=t=out:st={TOT-0.5}:d=0.5[a]"
    cmd=["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",voice,"-i",f"{S}/ytw/tools/ambient.wav","-filter_complex",fc,"-map","0:v","-map","[a]","-t",str(TOT),"-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    t0=0.0
    for (w,base,txt),d in zip(segs,durs):
        L=d+GAP; gs=Z.groups(txt,3); ch=[len(g) for g in gs]; tot=sum(ch); acc=0; tcs=[]
        for c in ch: tcs.append((acc/tot*d,(acc+c)/tot*d)); acc+=c
        for k in range(int(round(L*FPS))):
            t=k/FPS; z=1.0+0.07*(t/L); ww,hh=W/z,H/z; x=(W-ww)/2; y=(H-hh)/2
            im=base.crop((int(x),int(y),int(x+ww),int(y+hh))).resize((W,H),Image.BILINEAR)
            for (a,b2),g in zip(tcs,gs):
                if a<=t<b2+0.02: Z.caption(im,g); break
            p.stdin.write(im.tobytes())
    for k in range(int(END*FPS)): p.stdin.write(Y.endcard(k/FPS).tobytes())
    p.stdin.close(); p.wait(); print(out,TOT)
if __name__=="__main__":
    make(json.loads(sys.argv[1]),sys.argv[2])
