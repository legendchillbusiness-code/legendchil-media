# Narrativa com memes ligados ao que é dito + freeze frames; sons originais ao estilo meme
import subprocess, numpy as np, math, random, sys, json, os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
SRC,OUT=sys.argv[1],sys.argv[2]; S=json.loads(sys.argv[3]); HOOK=sys.argv[4]
R=random.Random(sum(map(ord,OUT)))
W,H,FPS,SR=1080,1920,30,44100
GF="/usr/share/fonts/truetype/google-fonts/"
FB=lambda s: ImageFont.truetype(GF+"Poppins-BoldItalic.ttf",s)
FM=lambda s: ImageFont.truetype(GF+"Poppins-Bold.ttf",s)
HAAR="/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/g3/haar.xml"
YEL=(255,214,0); WHT=(255,255,255); RED=(255,50,50)
AU=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",SRC,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
W0,W1=S["w"]; dur=len(AU)/SR; W1=min(W1,dur-0.05)
def fitsize(font,s,size,maxw=990):
    w=ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(s,font=font(size)); return size if w<=maxw else int(size*maxw/w)
def text(im,s,y,size,col,scale=1.0,font=FB,rot=0):
    if scale<=0.02: return im
    size=fitsize(font,s,size); lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((W/2,y),s,font=font(max(8,int(size*scale))),fill=col,anchor="mm",stroke_width=int(size*scale*0.09)+4,stroke_fill=(0,0,0))
    if rot: lay=lay.rotate(rot,center=(W/2,y),resample=Image.BICUBIC)
    im.paste(lay,(0,0),lay); return im
def caption_box(im,s,y,a):  # legenda de narrador estilo meme: caixa branca, texto preto
    if a<=0: return im
    size=fitsize(FM,s,54,920); f=FM(size); d0=ImageDraw.Draw(Image.new("RGB",(1,1))); tw=d0.textlength(s,font=f)
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    x0=(W-tw)/2-30; d.rounded_rectangle((x0,y-48,x0+tw+60,y+48),radius=18,fill=(255,255,255,int(240*a)))
    d.text((W/2,y),s,font=f,fill=(0,0,0,int(255*a)),anchor="mm"); im.paste(lay,(0,0),lay); return im
def pop(t,d=0.15): return 0 if t<0 else (1.0 if t>=d else 0.6+0.55*math.sin(t/d*math.pi/2)-0.15*t/d)
def tint(im,c,a): return Image.blend(im,Image.new("RGB",im.size,c),max(0,min(1,a)))
def zoomc(im,z,cx,cy):
    cw,ch=W/z,H/z; x0=max(0,min(W-cw,cx-cw/2)); y0=max(0,min(H-ch,cy-ch/2))
    return im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.BILINEAR)
def findface(im):
    import cv2
    gr=cv2.cvtColor(np.array(im)[:int(H*0.45)],cv2.COLOR_RGB2GRAY)
    fc=cv2.CascadeClassifier(HAAR).detectMultiScale(gr,1.08,4,minSize=(50,50))
    if len(fc): x,y,w_,h_=max(fc,key=lambda r:r[2]*r[3]); return (x+w_/2,y+h_/2)
    return None
# ---- sons originais (estilo meme, sintetizados) ----
rs=np.random.RandomState(1)
def env(n,a=0.005,r=0.2): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/r)
def tone(f,d,kind="saw",vib=0):
    n=int(SR*d); t=np.arange(n)/SR; ph=2*np.pi*np.cumsum(f*(1+vib*np.sin(2*np.pi*5.5*t)))/SR
    x=np.sin(ph) if kind=="sin" else 2*((ph/(2*np.pi))%1)-1
    return x
def lp(x,k=12): return np.convolve(x,np.ones(k)/k,'same')
def sfx(kind):
    if kind=="boom":
        n=int(SR*1.0); t=np.arange(n)/SR; f=55*np.exp(-t*0.8)+20; return np.tanh(5*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*2.4)*0.55
    if kind=="trombone":  # wah-wah descendente (motivo genérico)
        out=[]
        for f,d,v in ((233,0.32,0),(220,0.32,0),(208,0.32,0),(196,0.9,0.03)):
            x=lp(tone(f,d,"saw",v),18)*np.minimum(1,np.arange(int(SR*d))/(SR*0.03))*np.exp(-np.arange(int(SR*d))/(SR*(1.2 if d>0.5 else 0.5))); out.append(x*0.35)
        return np.concatenate(out)
    if kind=="sting":  # dun-dun-DUN
        out=np.zeros(int(SR*1.3))
        for k,(f,d) in enumerate(((98,0.22),(92,0.22),(73,0.85))):
            n=int(SR*d); x=(lp(tone(f,d),8)+0.5*lp(tone(f*1.5,d),8))*env(n,0.004,0.5 if k==2 else 0.15)*0.35; s=int(k*0.25*SR); out[s:s+n]+=x[:len(out[s:s+n])]
        return out
    if kind=="scratch":
        n=int(SR*0.35); t=np.arange(n)/SR; f=900*np.abs(np.sin(2*np.pi*3*t))+200; return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*rs.rand(n)*0.22*np.hanning(n)
    if kind=="bonk":
        n=int(SR*0.35); t=np.arange(n)/SR; return (np.sin(2*np.pi*(420*np.exp(-t*6))*t)+0.4*np.sin(2*np.pi*1100*t))*np.exp(-t*14)*0.5
    if kind=="cash":
        out=np.zeros(int(SR*0.8))
        for k,f in enumerate((1568,2093)):
            n=int(SR*0.5); t=np.arange(n)/SR; x=(np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*7)*0.22; s=int(k*0.09*SR); out[s:s+n]+=x[:len(out[s:s+n])]
        return out
    if kind=="ding":
        n=int(SR*0.6); t=np.arange(n)/SR; return (np.sin(2*np.pi*1320*t)+0.5*np.sin(2*np.pi*1980*t))*np.exp(-t*6)*0.22
    if kind=="heart":
        out=[]
        for _ in range(2):
            for d,a in ((0.12,0.7),(0.1,0.45)):
                n=int(SR*d); t=np.arange(n)/SR; out.append(np.sin(2*np.pi*50*t)*np.exp(-t*30)*a); out.append(np.zeros(int(SR*0.08)))
            out.append(np.zeros(int(SR*0.3)))
        return np.concatenate(out)
    if kind=="whoosh":
        n=int(SR*0.35); x=np.cumsum(rs.randn(n)); x-=np.convolve(x,np.ones(200)/200,'same'); x*=np.hanning(n); return x/np.abs(x).max()*0.22
    return np.zeros(1)
def emoji(kind,s):
    im=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(im)
    if kind=="skull":
        d.ellipse((s*.1,0,s*.9,s*.75),fill=(240,240,235),outline=(40,40,40),width=s//30); d.rectangle((s*.3,s*.6,s*.7,s*.92),fill=(240,240,235),outline=(40,40,40),width=s//30)
        d.ellipse((s*.22,s*.28,s*.44,s*.5),fill=(20,20,20)); d.ellipse((s*.56,s*.28,s*.78,s*.5),fill=(20,20,20)); d.polygon([(s*.5,s*.52),(s*.44,s*.62),(s*.56,s*.62)],fill=(20,20,20)); return im
    d.ellipse((0,0,s-1,s-1),fill=(255,204,51),outline=(140,90,0),width=s//40)
    if kind=="laugh":
        d.arc((s*.18,s*.28,s*.42,s*.46),200,340,fill=(80,40,0),width=s//22); d.arc((s*.58,s*.28,s*.82,s*.46),200,340,fill=(80,40,0),width=s//22)
        d.chord((s*.2,s*.45,s*.8,s*.85),0,180,fill=(90,20,20)); d.rectangle((s*.25,s*.62,s*.75,s*.66),fill=WHT)
        for x in (s*.12,s*.78): d.ellipse((x,s*.42,x+s*.12,s*.62),fill=(90,170,255))
    else:  # shock
        for x in (.3,.7): d.ellipse((s*(x-.1),s*.25,s*(x+.1),s*.5),fill=WHT,outline=(80,40,0),width=s//40); d.ellipse((s*(x-.04),s*.33,s*(x+.04),s*.43),fill=(30,30,30))
        d.ellipse((s*.38,s*.58,s*.62,s*.86),fill=(90,20,20))
    return im
EMO={"trombone":"skull","boom":"shock","bonk":"laugh","sting":None,"scratch":"laugh","cash":None,"ding":None,"heart":None}
# ---- render ----
VP=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
NF=[0]
def emit(im): VP.stdin.write(im.tobytes()); NF[0]+=1
p=subprocess.Popen(["ffmpeg","-v","error","-ss",str(W0),"-t",str(W1-W0),"-i",SRC,"-vf",f"fps={FPS},scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
ev=sorted([e for e in S["ev"] if W0<=e[1]<W1],key=lambda e:e[1]); pend=list(ev)
a=AU[int(W0*SR):int(W1*SR)].copy(); cuts=[]; labels=[]; last=None; fi=0
def mix(buf,x,t):
    i=int(max(0,t)*SR); seg=buf[i:i+len(x)]; seg+=x[:len(seg)]
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    im=Image.frombytes("RGB",(W,H),b); t=W0+fi/FPS; fi+=1; last=im
    base=im
    if t-W0<1.7 and HOOK: base=text(base,HOOK,1560,86,YEL,pop(t-W0),rot=-3)
    for (ts,s) in labels:
        u=t-ts
        if 0<=u<2.0: base=caption_box(base,s,1290,min(1,u/0.12,(2.0-u)/0.2))
    emit(base)
    for e in list(pend):
        if t>=e[1]:
            pend.remove(e)
            if e[0]=="label": labels.append((t,e[2])); mix(a,sfx("whoosh")*0.6,t-W0)
            elif e[0]=="freeze":
                _,_,txt,snd,style=e; n=int((1.1 if snd!="trombone" else 1.6)*FPS)
                fc=findface(im) if style=="zoom" else None
                g=ImageOps.grayscale(im).convert("RGB") if style in("bw","zoom") else im
                if style=="dark": g=ImageEnhance.Brightness(ImageOps.grayscale(im).convert("RGB")).enhance(0.55)
                FX,FY,ZM=(fc[0],fc[1],1.6) if fc else (W/2,H*0.55,0.25)
                emo=EMO.get(snd)
                for i in range(n):
                    tt=i/FPS; z=1+ZM*min(1,tt/0.12)
                    f=zoomc(g,z,FX,FY+(H*0.12 if fc else 0)) if style!="plain" else zoomc(g,1+0.06*min(1,tt/0.2),W/2,H*0.55)
                    if style=="plain": f=tint(f,(0,0,0),0.25)
                    if i<2: f=tint(f,WHT,0.5)
                    f=text(f,txt,1450,104,YEL if snd!="trombone" else WHT,pop(tt))
                    if emo and tt>0.2: s_=int(230*pop(tt-0.2)); ej=emoji(emo,max(8,s_)); f.paste(ej,(W-s_-60,1060-s_//2),ej)
                    emit(f)
                x=sfx(snd); ia=np.zeros(n*SR//FPS); ia[:len(x)]+=x[:len(ia)]; cuts.append((t-W0+1/FPS,ia))
            elif e[0]=="card":
                _,_,txt,snd=e; n=int(1.0*FPS); lines=txt.split("|")
                for i in range(n):
                    tt=i/FPS; f=ImageEnhance.Brightness(ImageOps.grayscale(im).convert("RGB")).enhance(0.2)
                    for k,l in enumerate(lines): f=text(f,l,H/2-70+k*150,120 if k else 90,YEL if k else WHT,pop(tt-0.2*k))
                    emit(f)
                x=sfx(snd); ia=np.zeros(n*SR//FPS); ia[:len(x)]+=x[:len(ia)]; cuts.append((t-W0+1/FPS,ia))
p.stdout.close(); p.kill()
parts=[]; lt=0.0
for tc,ia in cuts: parts.append(a[int(lt*SR):int(tc*SR)]); parts.append(ia); lt=tc
parts.append(a[int(lt*SR):]); body=np.concatenate(parts)
# final
END=S.get("end","tbc"); n=int(1.6*FPS); ea=np.zeros(int(1.6*SR))
if END=="tbc":  # congela com tom sépia e "CONTINUA…" com seta (genérico)
    sep=ImageOps.colorize(ImageOps.grayscale(last),(40,25,10),(235,215,170))
    for i in range(n):
        tt=i/FPS; f=sep.copy(); d=ImageDraw.Draw(f); x0=60+int(40*(1-min(1,tt/0.2)))
        d.polygon([(x0,1660),(x0+520,1660),(x0+600,1720),(x0+520,1780),(x0,1780),(x0+50,1720)],fill=(30,20,10)); d.text((x0+300,1720),"CONTINUA…",font=FM(64),fill=(235,215,170),anchor="mm")
        emit(f)
    mix(ea,sfx("sting")*0.7,0)
elif END=="cta":
    q=S.get("q") or R.choice(["Tu fazias o mesmo?","Quem tem razão?","Comenta 1 se te ris"])
    for i in range(n):
        tt=i/FPS; f=ImageEnhance.Brightness(last).enhance(0.4); f=text(f,q,880,96,WHT,pop(tt)); f=text(f,"COMENTA",1030,90,YEL,pop(tt-0.3)); emit(f)
    mix(ea,sfx("ding"),0)
elif END=="era":
    sep=ImageOps.colorize(ImageOps.grayscale(last),(20,20,20),(200,200,200))
    for i in range(int(2.2*FPS)):
        tt=i/FPS; f=ImageEnhance.Brightness(sep).enhance(max(0.25,1-tt/1.2)); f=text(f,"FIM DE UMA ERA",H/2,110,WHT,pop(tt-0.3)); emit(f)
    ea=np.zeros(int(2.2*SR)); mix(ea,sfx("trombone")*0.6,0.2)
else:  # loop
    p2=subprocess.run(["ffmpeg","-v","error","-ss",str(W0+0.05),"-i",SRC,"-frames:v","1","-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    first=Image.frombytes("RGB",(W,H),p2)
    for i in range(n):
        tt=i/FPS; f=Image.blend(last,first,min(1,tt/1.2)); f=text(f,"…E FOI ASSIM QUE COMEÇOU",1500,70,WHT,pop(tt)); emit(f)
    mix(ea,sfx("whoosh"),0.9)
VP.stdin.close(); VP.wait()
mixa=np.concatenate([body,ea]); N=int(NF[0]/FPS*SR); mixa=np.pad(mixa,(0,max(0,N-len(mixa))))[:N]; mixa=mixa/np.abs(mixa).max()*0.95
mixa.astype(np.float32).tofile(OUT+".m.f32")
subprocess.run(["ffmpeg","-v","error","-y","-i",OUT+".v.mp4","-f","f32le","-ar",str(SR),"-ac","1","-i",OUT+".m.f32","-c:v","copy","-c:a","aac","-b:a","160k","-ac","2","-shortest","-movflags","+faststart",OUT])
os.remove(OUT+".v.mp4"); os.remove(OUT+".m.f32"); print(OUT,round(NF[0]/FPS,1),len(ev))
