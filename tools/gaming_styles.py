import subprocess, numpy as np, math, random, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
SRC,OUT,STYLE=sys.argv[1],sys.argv[2],sys.argv[3]; P=json.loads(sys.argv[4])
W,H,FPS,SR=1080,1920,30,44100; random.seed(hash(OUT)%999)
SIX="/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/six"
FB=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf",s)
FM=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",s)
FG=lambda s: ImageFont.truetype(f"{SIX}/ebg-500-normal.ttf",s)
FGI=lambda s: ImageFont.truetype(f"{SIX}/ebg-500-italic.ttf",s)
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",SRC],capture_output=True,text=True).stdout)
au=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",SRC,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
win=int(0.25*SR); e=np.array([np.sqrt((au[i:i+win]**2).mean()) for i in range(0,len(au)-win,win)])
lo,hi=8,max(9,len(e)-10); pk=(lo+int(np.argmax(e[lo:hi])))*0.25
thr=np.percentile(e,70); B=[]
for i in range(1,len(e)-1):
    if e[i]>thr and e[i]>=e[i-1] and e[i]>e[i+1] and (not B or i*0.25-B[-1]>=1.2): B.append(i*0.25)
def reader(t0,t1):
    p=subprocess.Popen(["ffmpeg","-v","error","-ss",str(max(0,t0)),"-t",str(t1-t0),"-i",SRC,"-vf",f"fps={FPS},scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield Image.frombytes("RGB",(W,H),b)
    p.stdout.close(); p.kill()
def one(t): return next(reader(t,t+0.05))
def zoom(im,z,dx=0,dy=0,cx=0.5,cy=0.55):
    cw,ch=W/z,H/z; x0=max(0,min(W-cw,cx*W-cw/2+dx)); y0=max(0,min(H-ch,cy*H-ch/2+dy))
    return im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.BILINEAR)
def tint(im,c,a): return Image.blend(im,Image.new("RGB",im.size,c),max(0,min(1,a)))
def pop(t,d=0.18): return 1.0 if t>=d else 0.6+0.55*math.sin(t/d*math.pi/2)-0.15*t/d
def fit(font,s,size,maxw):
    w=ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(s,font=font(size)); return size if w<=maxw else int(size*maxw/w)
def text(im,s,y,size,col,scale=1,rot=0,font=FB,stroke=True):
    size=fit(font,s,size,1000); f=font(max(8,int(size*scale))); lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((W/2,y),s,font=f,fill=col,anchor="mm",**({"stroke_width":int(size*scale*0.09)+4,"stroke_fill":(0,0,0)} if stroke else {}))
    if rot: lay=lay.rotate(rot,center=(W/2,y),resample=Image.BICUBIC)
    im.paste(lay,(0,0),lay); return im
def rgbsplit(im,o):
    r,g,b=im.split(); r=ImageOps.expand(r,(o,0,0,0)).crop((0,0,W,H)); b=ImageOps.expand(b,(0,0,o,0)).crop((o,0,W+o,H)); return Image.merge("RGB",(r,g,b))
def whoosh(d=0.4):
    n=int(SR*d); x=np.cumsum(np.random.randn(n)); x-=np.convolve(x,np.ones(200)/200,'same'); x*=np.hanning(n); return x/np.abs(x).max()*0.5
def hit(d=0.6):
    n=int(SR*d); t=np.arange(n)/SR; f=40+120*np.exp(-t*15); return np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*6)*0.7
def vboom(d=1.4):  # boom grave tipo meme
    n=int(SR*d); t=np.arange(n)/SR; f=55*np.exp(-t*0.8)+20
    return np.tanh(5*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*2.2)*0.95
def heart(n_beats=3):
    out=[]
    for _ in range(n_beats):
        for d,a in ((0.12,0.9),(0.1,0.6)):
            n=int(SR*d); t=np.arange(n)/SR; out.append(np.sin(2*np.pi*50*t)*np.exp(-t*30)*a); out.append(np.zeros(int(SR*0.08)))
        out.append(np.zeros(int(SR*0.35)))
    return np.concatenate(out)
def tick(): n=int(SR*0.03); return np.random.randn(n)*np.exp(-np.arange(n)/SR*200)*0.25
VP=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
A=[]; NF=[0]
def emit(im): VP.stdin.write(im.tobytes()); NF[0]+=1
def add(a,arr,t):
    s=int(max(0,t)*SR); seg=a[s:s+len(arr)]; seg+=arr[:len(seg)]
# ---------------- ESTILOS ----------------
if STYLE=="acao":
    h0,h1=max(0,pk-1.0),min(dur,pk+0.8)
    for i,im in enumerate(reader(h0,h1)):
        t=i/FPS; im=zoom(im,1.08+0.12*t/(h1-h0),random.randint(-10,10),random.randint(-10,10))
        if i<3: im=tint(im,(255,255,255),0.6-0.2*i)
        emit(text(im,P["hook"],1560,84,(255,214,0),pop(t),-3))
    A.append(au[int(h0*SR):int(h1*SR)])
    for tt in np.linspace(h1,0.3,15):
        im=rgbsplit(one(tt),14); d=ImageDraw.Draw(im)
        for y in range(0,H,6): d.line([(0,y),(W,y)],fill=(0,0,0),width=2)
        emit(im)
    A.append(whoosh(15/FPS))
    a=au.copy()
    for i,im in enumerate(reader(0,dur)):
        t=i/FPS; past=[b for b in B if b<=t]; dt=t-past[-1] if past else 9; z=1.0+0.07*math.exp(-dt*8)
        u=t-(pk-0.1)
        if -0.8<u<0.9:
            sh=int(22*math.exp(-u*3)) if u>=0 else 0; z=max(z,1.12 if u>=0 else 1+0.12*(1+u/0.8))
            im=zoom(im,z,random.randint(-sh,sh) if sh else 0,random.randint(-sh,sh) if sh else 0)
            if 0<=u<0.1: im=tint(im,(255,255,255),0.5)
        else: im=zoom(im,z)
        if dt<0.05: im=tint(im,(255,255,255),0.18)
        emit(im)
    for b in B: add(a,whoosh(0.3)*0.35,b-0.15)
    add(a,hit(),pk-0.1); A.append(a)
elif STYLE=="meme":
    BAR=230
    def memeframe(im,top):
        out=Image.new("RGB",(W,H),(255,255,255)); out.paste(im.crop((0,0,W,H-BAR)),(0,BAR)); d=ImageDraw.Draw(out)
        lines=top.split("\n"); size=min(fit(FM,l,64,1000) for l in lines)
        for k,l in enumerate(lines): d.text((40,BAR/2+(k-(len(lines)-1)/2)*size*1.15),l,font=FM(size),fill=(0,0,0),anchor="lm")
        return out
    a=au.copy(); fz=pk; A2=[]
    # parte 1: até ao pico
    for i,im in enumerate(reader(0,fz)): emit(memeframe(im,P["top"]))
    A2.append(a[:int(fz*SR)])
    # congela: zoom à cara + P&B + boom
    fr=one(fz); face=fr.crop((140,0,940,450)).resize((W,int(450*W/800)))
    n=int(1.6*FPS)
    for i in range(n):
        t=i/FPS; base=ImageOps.grayscale(fr).convert("RGB")
        z=1+0.9*min(1,t/0.25); im=zoom(base,z,0,0,0.5,0.09)
        if i<2: im=tint(im,(255,255,255),0.6)
        im=text(im,P.get("freeze",""),1450,110,(255,255,255),pop(t),0) if P.get("freeze") else im
        emit(memeframe(im,P["top"]))
    v=np.zeros(int(1.6*SR)); v[:len(vboom())]+=vboom()[:len(v)]; A2.append(v)
    for i,im in enumerate(reader(fz,dur)): emit(memeframe(im,P["top"]))
    A2.append(a[int(fz*SR):]); A.extend(A2)
elif STYLE=="doc":
    def grade(im,t):
        im=ImageEnhance.Color(im).enhance(0.55); im=Image.blend(im,Image.new("RGB",(W,H),(112,84,50)),0.16)
        g=Image.effect_noise((W//3,H//3),28).resize((W,H)).convert("RGB"); im=Image.blend(im,g,0.06)
        d=ImageDraw.Draw(im); d.rectangle((0,0,W,150),fill=(0,0,0)); d.rectangle((0,H-150,W,H),fill=(0,0,0)); return im
    intro=P["intro"]; a=au.copy()
    # intro: escreve tipo máquina por cima do 1.º frame
    n0=int(max(2.4,0.06*len(intro)+1.0)*FPS); fr=one(0.5)
    for i in range(n0):
        t=i/FPS; k=min(len(intro),int(t/0.055)); im=grade(ImageEnhance.Brightness(fr.filter(ImageFilter.GaussianBlur(18))).enhance(0.4),t)
        lines=intro[:k].split("|"); y0=H/2-(len(lines)-1)*45
        d=ImageDraw.Draw(im)
        for j,l in enumerate(lines): d.text((W/2,y0+j*90),l,font=FG(70),fill=(240,232,216),anchor="mm")
        emit(im)
    ia=np.zeros(int(n0/FPS*SR))
    for c in range(len(intro)):
        if intro[c] not in " |": add(ia,tick(),c*0.055)
    A.append(ia)
    for i,im in enumerate(reader(0,dur)):
        t=i/FPS; z=1.0+0.06*t/dur; emit(grade(zoom(im,z),t))
    A.append(a)
    q,src=P["quote"],P.get("src","Provérbio português"); n1=int(3.0*FPS)
    for i in range(n1):
        t=i/FPS; al=min(1,t/0.6); im=Image.new("RGB",(W,H),(8,8,8)); d=ImageDraw.Draw(im)
        c=tuple(int(x*al) for x in (240,232,216)); g=tuple(int(x*al) for x in (184,151,90))
        lines=q.split("|"); y0=H/2-80-(len(lines)-1)*50
        for j,l in enumerate(lines): d.text((W/2,y0+j*100),l,font=FGI(fit(FGI,l,84,940)),fill=c,anchor="mm")
        d.text((W/2,y0+len(lines)*100+40),"— "+src,font=FG(44),fill=g,anchor="mm"); emit(im)
    qa=np.zeros(int(3.0*SR)); add(qa,hit(1.0)*0.5,0.0); A.append(qa)
elif STYLE=="drama":
    a=au.copy(); hb=heart(3); hbd=len(hb)/SR
    for i,im in enumerate(reader(0,dur)):
        t=i/FPS; u=t-(pk-hbd)
        if u>0:
            k=min(1,u/hbd); z=1+0.55*k; im=zoom(im,z,0,0,0.5,0.09+0.46*(1-k))
            v=Image.new("L",(W,H),0); dv=ImageDraw.Draw(v); dv.ellipse((-200,-150,W+200,H+150),fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
            im=Image.composite(im,tint(im,(120,0,0),0.75),v)
            if t>=pk and t<pk+0.12: im=tint(im,(255,255,255),0.6)
            if t>=pk: im=text(im,P["peak"],1180,120,(255,60,60),pop(t-pk),-3)
        emit(im)
    add(a,hb*0.8,pk-hbd); add(a,hit(0.9),pk); A.append(a)
    q=P["quote"]; n1=int(2.8*FPS); last=one(dur-0.1)
    for i in range(n1):
        t=i/FPS; im=ImageEnhance.Brightness(ImageOps.grayscale(last).convert("RGB")).enhance(0.25)
        lines=q.split("|"); y0=H/2-(len(lines)-1)*55
        for j,l in enumerate(lines): im=text(im,l,y0+j*115,96,(255,255,255) if j<len(lines)-1 else (255,214,0),pop(t-0.25*j) if t>0.25*j else 0.01)
        emit(im)
    A.append(np.zeros(int(2.8*SR)))
VP.stdin.close(); VP.wait()
mix=np.concatenate(A); n=int(NF[0]/FPS*SR); mix=np.pad(mix,(0,max(0,n-len(mix))))[:n]; mix=mix/np.abs(mix).max()*0.95
mix.astype(np.float32).tofile(OUT+".m.f32")
subprocess.run(["ffmpeg","-v","error","-y","-i",OUT+".v.mp4","-f","f32le","-ar",str(SR),"-ac","1","-i",OUT+".m.f32","-c:v","copy","-c:a","aac","-b:a","160k","-ac","2","-shortest","-movflags","+faststart",OUT])
import os; os.remove(OUT+".v.mp4"); os.remove(OUT+".m.f32"); print(OUT,STYLE,round(NF[0]/FPS,1))
