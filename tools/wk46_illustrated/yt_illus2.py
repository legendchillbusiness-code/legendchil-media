import os,sys,subprocess,re
os.environ.setdefault("S","/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yt_illus as Y
from PIL import Image,ImageDraw,ImageFont,ImageChops
W,H,FPS=Y.W2,Y.H2,30
def slide_v2(tag,head,body,c,ill,notext=False):
    p=Y.PAL[c]; im=Image.new("RGB",(W,H),p["bg"]); d=ImageDraw.Draw(im)
    ft=Y.PB(34); tw=d.textlength(tag,font=ft)+80
    f1=Y.PB(104); f2=ImageFont.truetype(Y.M,50)
    l1=Y.wrap(d,head,f1,W-140); l2=Y.wrap(d,body,f2,W-140); y=330
    if not notext:
        d.rectangle((W/2-tw/2,200,W/2+tw/2,270),fill=(15,15,15)); d.text((W/2,235),tag,font=ft,fill=(255,255,255),anchor="mm")
    for ln in l1:
        if not notext: d.text((70,y),ln,font=f1,fill=p["fg"])
        y+=124
    y+=30
    for ln in l2:
        if not notext: d.text((70,y),ln,font=f2,fill=p["fg"])
        y+=66
    g=Y.prep_ill(ill); top=y+30; bh=1500-top; bw=W-60
    k=min(bh/g.height,bw/g.width); g=g.resize((int(g.width*k),int(g.height*k)),Image.LANCZOS)
    x=(W-g.width)//2; yy=top+(bh-g.height)//2
    reg=im.crop((x,yy,x+g.width,yy+g.height)); im.paste(ImageChops.multiply(reg,g.convert("RGB")),(x,yy))
    return im,(x,yy,g.width,g.height)
def groups(text,n=3):
    import math,re
    out=[]
    for sent in re.findall(r"[^.?!]+[.?!]?",text):
        w=sent.split()
        if not w: continue
        k=math.ceil(len(w)/n); sz=math.ceil(len(w)/k)
        out+= [" ".join(w[i:i+sz]) for i in range(0,len(w),sz)]
    return out
def caption(im,txt):
    d=ImageDraw.Draw(im); sz=92
    while d.textlength(txt.upper(),font=Y.PB(sz))>W-110 and sz>50: sz-=4
    f=Y.PB(sz)
    d.text((W/2,1560),txt.upper(),font=f,fill=(255,255,255),anchor="mm",stroke_width=8,stroke_fill=(0,0,0))
def make(ser,i,c,voice,out,n=3):
    tag="PSYCHOLOGY SAYS" if ser=="facts" else "PSYCHOLOGY ABOUT GIRLS"
    h,b=(Y.FACTS if ser=="facts" else Y.GIRLS)[i]
    base,(bx,by,bw,bh)=slide_v2(tag,h,b,c,Y.ILL[(ser,i)])
    base_ill,_=slide_v2(tag,h,b,c,Y.ILL[(ser,i)],notext=True)
    T=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",voice]).decode())+0.35
    END=float(os.environ.get("END","3.0")); TOT=T+END
    scenes=[(0,0.34,(W/2,H/2),1.0,1.07),(0.34,0.60,(bx+bw*0.30,by+bh*0.5),1.75,1.95),(0.60,0.84,(bx+bw*0.72,by+bh*0.5),1.75,1.95),(0.84,1.0,(W/2,by+bh/2),1.0,1.08)]
    words=(h+" "+b).split(); gs=groups(h+" "+b,n); chars=[len(g) for g in gs]; tot=sum(chars)
    tcs=[];acc=0
    for ch in chars: tcs.append((acc/tot*(T-0.35),(acc+ch)/tot*(T-0.35))); acc+=ch
    music=os.environ.get("MUSIC","phonk")
    ins=["-i",voice] if music=="none" else ["-i",voice,"-i",f"{os.environ['S']}/ytw/tools/{music}.wav"]
    fc=(f"[1:a]apad,atrim=0:{TOT},afade=t=out:st={TOT-0.5}:d=0.5[a]" if music=="none" else f"[1:a]apad[v];[2:a]volume={os.environ.get('MVOL','-21')}dB[m];[v][m]amix=inputs=2:duration=first:normalize=0,atrim=0:{TOT},afade=t=out:st={TOT-0.5}:d=0.5[a]")
    cmd=["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-"]+ins+[
      "-filter_complex",fc,
      "-map","0:v","-map","[a]","-t",str(TOT),"-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out]
    # voice shorter than TOT -> apad then amix duration=first would stop at voice; use longest instead
    cmd[cmd.index("-filter_complex")+1]=cmd[cmd.index("-filter_complex")+1].replace("duration=first","duration=longest")
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    N=int(T*FPS)
    for k in range(N):
        t=k/FPS; fr=t/T
        for si,(s0,s1,(cx,cy),z0,z1) in enumerate(scenes):
            if s0<=fr<s1 or (s1==1.0 and fr>=s0):
                u=(fr-s0)/(s1-s0); z=z0+(z1-z0)*u; break
        w,hh=W/z,H/z; x=min(max(cx-w/2,0),W-w); y=min(max(cy-hh/2,0),H-hh)
        src=base if si in (0,3) else base_ill
        im=src.crop((int(x),int(y),int(x+w),int(y+hh))).resize((W,H),Image.BILINEAR)
        for (a,b2),g in zip(tcs,gs):
            if a<=t<b2+0.02: caption(im,g); break
        p.stdin.write(im.tobytes())
    for k in range(int(END*FPS)): p.stdin.write(Y.endcard(k/FPS).tobytes())
    p.stdin.close(); p.wait(); print(out,TOT)
if __name__=="__main__":
    make(sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5])
