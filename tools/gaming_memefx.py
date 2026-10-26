import subprocess, numpy as np, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
SRC,OUT=sys.argv[1],sys.argv[2]; random.seed(sum(map(ord,OUT)))
W,H,FPS,SR=1080,1920,30,44100
FB=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf",s)
FM=lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",s)
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",SRC],capture_output=True,text=True).stdout)
au=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",SRC,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
win=int(0.1*SR); e=np.array([np.sqrt((au[i:i+win]**2).mean()) for i in range(0,len(au)-win,win)]); ed=20*np.log10(e+1e-9)
# eventos (evita primeiros 3 s e últimos 3.5 s)
lo,hi=30,len(e)-35
ev=[]
# 1) silêncio >=1.0 s
q=np.percentile(ed[lo:hi],25); run=0
for i in range(lo,hi):
    run=run+1 if ed[i]<q else 0
    if run==10: ev.append(("silencio",(i-9)/10)); break
# 2) pico (reação congelada)
pk=(lo+int(np.argmax(e[lo:hi])))/10; ev.append(("reacao",max(3,pk-0.05)))
# 3) cartão "erro/loading" a meio, longe dos outros
cands=[t for t in np.arange(4,dur-5,0.5) if all(abs(t-x[1])>3 for x in ev)]
if cands: ev.append(("erro",random.choice(cands)))
ev.sort(key=lambda x:x[1])
SIL=["*silêncio constrangedor*","*grilos*","*ninguém disse nada*"]
REA=["MOMENTO HISTÓRICO","NINGUÉM ESPERAVA","ISTO É LEGAL?","PLOT TWIST","FOI SEM QUERER","TU VISTE ISTO?"]
ERR=[("CÉREBRO.EXE","deixou de funcionar"),("A CARREGAR PLANO…","3%"),("ERRO 404","plano não encontrado"),("NÍVEL DE CALMA","0%")]
def crickets(d):
    n=int(SR*d); t=np.arange(n)/SR; env=((np.sin(2*np.pi*3.2*t)>0.6)*(np.sin(2*np.pi*28*t)>0)).astype(float)
    return np.sin(2*np.pi*4300*t)*env*0.18
def boom(d=1.2):
    n=int(SR*d); t=np.arange(n)/SR; f=55*np.exp(-t*0.8)+20; return np.tanh(5*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*2.2)*0.9
def scratch(d=0.35):
    n=int(SR*d); t=np.arange(n)/SR; f=900*np.abs(np.sin(2*np.pi*3*t))+200; return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.random.rand(n)*0.35*np.hanning(n)
def blip(d=0.08,f=1200): n=int(SR*d); t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))*0.2*np.hanning(n)
def face(size):  # emoji original desenhado: cara a chorar a rir
    im=Image.new("RGBA",(size,size),(0,0,0,0)); d=ImageDraw.Draw(im); s=size
    d.ellipse((0,0,s-1,s-1),fill=(255,204,51),outline=(140,90,0),width=s//40)
    d.arc((s*.18,s*.28,s*.42,s*.46),200,340,fill=(80,40,0),width=s//22); d.arc((s*.58,s*.28,s*.82,s*.46),200,340,fill=(80,40,0),width=s//22)
    d.chord((s*.2,s*.45,s*.8,s*.85),0,180,fill=(90,20,20)); d.rectangle((s*.25,s*.62,s*.75,s*.66),fill=(255,255,255))
    for x in (s*.12,s*.78): d.ellipse((x,s*.42,x+s*.12,s*.62),fill=(90,170,255))
    return im
FACE=face(260)
def text(im,s,y,size,col,scale=1.0,font=FB):
    w=ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(s,font=font(size))
    if w>980: size=int(size*980/w)
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((W/2,y),s,font=font(max(8,int(size*scale))),fill=col,anchor="mm",stroke_width=int(size*scale*0.09)+4,stroke_fill=(0,0,0))
    im.paste(lay,(0,0),lay); return im
def pop(t,d=0.15): return 1.0 if t>=d else 0.6+0.55*math.sin(t/d*math.pi/2)-0.15*t/d
# plano de saída: lista de (tipo,t_src,inserção_extra_s)
INS={"reacao":1.0,"erro":1.1}
p=subprocess.Popen(["ffmpeg","-v","error","-i",SRC,"-vf",f"fps={FPS}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
VP=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
A=[]; fi=0; pend=list(ev); cur=0.0; texts={k:random.choice(v) for k,v in (("silencio",SIL),("reacao",REA),("erro",ERR))}
while True:
    b=p.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    im=Image.frombytes("RGB",(W,H),b); t=fi/FPS; fi+=1
    for k,te in ev:
        if k=="silencio" and te<=t<te+1.6:
            im=text(im,texts[k],1250,64,(255,255,255),pop(t-te),FM)
    VP.stdin.write(im.tobytes())
    for k,te in list(pend):
        if k in INS and t>=te:
            pend.remove((k,te)); n=int(INS[k]*FPS)
            A.append(("cut",t))
            if k=="reacao":
                g=ImageOps.grayscale(im).convert("RGB")
                import cv2
                arr=np.array(im)[:int(H*0.45)]; gr=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
                fc=cv2.CascadeClassifier("/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/g3/haar.xml").detectMultiScale(gr,1.08,4,minSize=(50,50))
                if len(fc): x,y,w_,h_=max(fc,key=lambda r:r[2]*r[3]); FX,FY=x+w_/2,y+h_/2; ZM=1.6
                else: FX,FY=W/2,H*0.55; ZM=0.35
                for i in range(n):
                    tt=i/FPS; z=1+ZM*min(1,tt/0.12); cw,ch=W/z,H/z
                    x0=max(0,min(W-cw,FX-cw/2)); y0=max(0,min(H-ch,FY-ch*(0.35 if ZM>1 else 0.5)))
                    fr=g.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H))
                    sh=int(16*math.exp(-tt*6)); fr=fr.transform((W,H),Image.AFFINE,(1,0,random.randint(-sh,sh),0,1,random.randint(-sh,sh)))
                    fr=text(fr,texts[k],1450,110,(255,214,0),pop(tt))
                    if tt>0.15: fs=int(260*pop(tt-0.15)); f2=FACE.resize((fs,fs)); fr.paste(f2,(W-fs-60,1000-fs//2),f2)
                    VP.stdin.write(fr.tobytes())
                A.append(("ins",boom(INS[k])))
            else:
                h,s=texts[k]
                for i in range(n):
                    tt=i/FPS; fr=Image.new("RGB",(W,H),(0,0,170)); d=ImageDraw.Draw(fr)
                    if random.random()<0.25: fr=Image.blend(fr,ImageEnhance.Brightness(im).enhance(0.6),0.35); d=ImageDraw.Draw(fr)
                    d.text((W/2,820),h,font=FM(96),fill=(255,255,255),anchor="mm")
                    if "%" in s:
                        d.rectangle((190,960,890,1020),outline=(255,255,255),width=6); pct=0.03 if tt<0.8 else 0.0
                        d.rectangle((200,970,200+680*min(pct,tt*0.04),1010),fill=(255,255,255)); d.text((W/2,1100),s,font=FM(70),fill=(255,255,255),anchor="mm")
                    else: d.text((W/2,980),s,font=FM(62),fill=(255,255,255),anchor="mm")
                    VP.stdin.write(fr.tobytes())
                A.append(("ins",np.concatenate([scratch(),blip(0.1,880),np.zeros(int(SR*0.2)),blip(0.1,660),np.zeros(max(0,int(INS[k]*SR)-int(SR*0.75)))])[:int(INS[k]*SR)]))
p.stdout.close(); VP.stdin.close(); VP.wait()
# áudio: original cortado nos pontos de inserção + sfx
a=au.copy()
for k,te in ev:
    if k=="silencio": s=int(te*SR); c=crickets(1.6); a[s:s+len(c)]=a[s:s+len(c)]*0.4+c[:len(a[s:s+len(c)])]
parts=[]; last=0.0; i=0
while i<len(A):
    _,tc=A[i]; _,ins=A[i+1]; parts.append(a[int(last*SR):int((tc+1/FPS)*SR)]); parts.append(ins); last=tc+1/FPS; i+=2
parts.append(a[int(last*SR):]); mix=np.concatenate(parts); mix=mix/np.abs(mix).max()*0.95
mix.astype(np.float32).tofile(OUT+".m.f32")
subprocess.run(["ffmpeg","-v","error","-y","-i",OUT+".v.mp4","-f","f32le","-ar",str(SR),"-ac","1","-i",OUT+".m.f32","-c:v","copy","-c:a","aac","-b:a","160k","-ac","2","-shortest","-movflags","+faststart",OUT])
import os; os.remove(OUT+".v.mp4"); os.remove(OUT+".m.f32"); print(OUT,[(k,round(t,1)) for k,t in ev])
