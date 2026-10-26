# Edição dinâmica ≤30 s com biblioteca de memes originais (sem material de terceiros)
import subprocess, numpy as np, math, random, sys, json, os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
SRC,OUT=sys.argv[1],sys.argv[2]; P=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
R=random.Random(sum(map(ord,OUT))+7)
W,H,FPS,SR=1080,1920,30,44100; MAXD=29.5
GF="/usr/share/fonts/truetype/google-fonts/"
FB=lambda s: ImageFont.truetype(GF+"Poppins-BoldItalic.ttf",s)
FM=lambda s: ImageFont.truetype(GF+"Poppins-Bold.ttf",s)
FR=lambda s: ImageFont.truetype(GF+"Poppins-Medium.ttf",s)
HAAR="/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/g3/haar.xml"
YEL=(255,214,0); WHT=(255,255,255); RED=(255,50,50)
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",SRC],capture_output=True,text=True).stdout)
AU=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",SRC,"-f","f32le","-ac","1","-ar",str(SR),"-"],capture_output=True).stdout,np.float32).astype(np.float64)
step=0.1; win=int(step*SR); e=np.array([np.sqrt((AU[i:i+win]**2).mean()) for i in range(0,len(AU)-win,win)]); ed=20*np.log10(e+1e-9)
sm=np.convolve(e,np.ones(5)/5,'same')
# ---------- janela principal (≤ ~25 s) ----------
BODY=min(dur-0.2,22.0)
if dur-0.2>BODY:
    best,bs=-1,0
    for s in np.arange(0,dur-BODY,0.5):
        sc=sm[int(s/step):int((s+BODY)/step)].sum()
        if sc>best: best,bs=sc,s
    W0,W1=bs,bs+BODY
else: W0,W1=0.0,dur-0.1
i0,i1=int(W0/step)+15,int(W1/step)-25
pk=(i0+int(np.argmax(sm[i0:i1])))*step
# picos secundários
peaks=[]
for i in np.argsort(-sm[i0:i1]):
    t=(i0+i)*step
    if all(abs(t-p)>3.0 for p in peaks+[pk]): peaks.append(t)
    if len(peaks)>=4: break
peaks.sort()
# silêncio
q=np.percentile(ed[i0:i1],22); sil=None; run=0
for i in range(i0,i1):
    run=run+1 if ed[i]<q else 0
    if run==9 and abs(i*step-pk)>2.5: sil=(i-8)*step; break
# ---------- biblioteca ----------
def text(im,s,y,size,col,scale=1.0,font=FB,rot=0,x=None):
    if scale<=0.02: return im
    w=ImageDraw.Draw(Image.new("RGB",(1,1))).textlength(s,font=font(size))
    if w>990: size=int(size*990/w)
    lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((x or W/2,y),s,font=font(max(8,int(size*scale))),fill=col,anchor="mm",stroke_width=int(size*scale*0.09)+4,stroke_fill=(0,0,0))
    if rot: lay=lay.rotate(rot,center=(x or W/2,y),resample=Image.BICUBIC)
    im.paste(lay,(0,0),lay); return im
def pop(t,d=0.15): return 0 if t<0 else (1.0 if t>=d else 0.6+0.55*math.sin(t/d*math.pi/2)-0.15*t/d)
def tint(im,c,a): return Image.blend(im,Image.new("RGB",im.size,c),max(0,min(1,a)))
def zoomc(im,z,cx,cy,dx=0,dy=0):
    cw,ch=W/z,H/z; x0=max(0,min(W-cw,cx-cw/2+dx)); y0=max(0,min(H-ch,cy-ch/2+dy))
    return im.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H),Image.BILINEAR)
FACEC=None
def findface(im):
    import cv2
    arr=np.array(im)[:int(H*0.45)]; gr=cv2.cvtColor(arr,cv2.COLOR_RGB2GRAY)
    fc=cv2.CascadeClassifier(HAAR).detectMultiScale(gr,1.08,4,minSize=(50,50))
    if len(fc): x,y,w_,h_=max(fc,key=lambda r:r[2]*r[3]); return (x+w_/2,y+h_/2)
    return None
def emoji(kind,s):
    im=Image.new("RGBA",(s,s),(0,0,0,0)); d=ImageDraw.Draw(im)
    if kind=="skull":
        d.ellipse((s*.1,0,s*.9,s*.75),fill=(240,240,235),outline=(40,40,40),width=s//30); d.rectangle((s*.3,s*.6,s*.7,s*.92),fill=(240,240,235),outline=(40,40,40),width=s//30)
        d.ellipse((s*.22,s*.28,s*.44,s*.5),fill=(20,20,20)); d.ellipse((s*.56,s*.28,s*.78,s*.5),fill=(20,20,20)); d.polygon([(s*.5,s*.52),(s*.44,s*.62),(s*.56,s*.62)],fill=(20,20,20))
        for x in (0.38,0.5,0.62): d.line((s*x,s*.72,s*x,s*.92),fill=(40,40,40),width=s//30)
        return im
    d.ellipse((0,0,s-1,s-1),fill=(255,204,51),outline=(140,90,0),width=s//40)
    if kind=="laugh":
        d.arc((s*.18,s*.28,s*.42,s*.46),200,340,fill=(80,40,0),width=s//22); d.arc((s*.58,s*.28,s*.82,s*.46),200,340,fill=(80,40,0),width=s//22)
        d.chord((s*.2,s*.45,s*.8,s*.85),0,180,fill=(90,20,20)); d.rectangle((s*.25,s*.62,s*.75,s*.66),fill=WHT)
        for x in (s*.12,s*.78): d.ellipse((x,s*.42,x+s*.12,s*.62),fill=(90,170,255))
    elif kind=="shock":
        for x in (.3,.7): d.ellipse((s*(x-.1),s*.25,s*(x+.1),s*.5),fill=WHT,outline=(80,40,0),width=s//40); d.ellipse((s*(x-.04),s*.33,s*(x+.04),s*.43),fill=(30,30,30))
        d.ellipse((s*.38,s*.58,s*.62,s*.86),fill=(90,20,20))
    elif kind=="side":
        for x in (.3,.7): d.ellipse((s*(x-.1),s*.3,s*(x+.1),s*.45),fill=WHT,outline=(80,40,0),width=s//40); d.ellipse((s*(x+.0),s*.33,s*(x+.08),s*.43),fill=(30,30,30))
        d.line((s*.35,s*.72,s*.65,s*.68),fill=(80,40,0),width=s//18)
    elif kind=="clown":
        d.ellipse((s*.4,s*.45,s*.6,s*.65),fill=(230,30,30)); d.arc((s*.25,s*.5,s*.75,s*.85),20,160,fill=(200,0,0),width=s//14)
        for x in (.3,.7): d.ellipse((s*(x-.07),s*.25,s*(x+.07),s*.4),fill=(30,30,30))
        d.ellipse((-s*.05,-s*.05,s*.3,s*.3),fill=(60,160,255)); d.ellipse((s*.75,-s*.05,s*1.05,s*.3),fill=(60,160,255))
    return im
def phone_banner(app,msg):
    b=Image.new("RGBA",(980,190),(0,0,0,0)); d=ImageDraw.Draw(b)
    d.rounded_rectangle((0,0,979,189),radius=46,fill=(245,245,247,245))
    d.rounded_rectangle((34,40,144,150),radius=26,fill=(40,200,90)); d.text((89,95),app[0],font=FM(60),fill=WHT,anchor="mm")
    d.text((172,62),app,font=FM(38),fill=(20,20,20),anchor="lm"); d.text((940,62),"agora",font=FR(30),fill=(120,120,120),anchor="rm")
    d.text((172,126),msg,font=FR(40),fill=(40,40,40),anchor="lm"); return b
# sons
def nz(n): return np.random.RandomState(R.randint(0,9999)).randn(n)
def boom(d=1.1):
    n=int(SR*d); t=np.arange(n)/SR; f=55*np.exp(-t*0.8)+20; return np.tanh(5*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*2.2)*0.9
def hit(d=0.5):
    n=int(SR*d); t=np.arange(n)/SR; f=40+120*np.exp(-t*15); return np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*6)*0.7
def whoosh(d=0.35):
    n=int(SR*d); x=np.cumsum(nz(n)); x-=np.convolve(x,np.ones(200)/200,'same'); x*=np.hanning(n); return x/np.abs(x).max()*0.5
def scratch(d=0.35):
    n=int(SR*d); t=np.arange(n)/SR; f=900*np.abs(np.sin(2*np.pi*3*t))+200; return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.random.rand(n)*0.3*np.hanning(n)
def blip(f=1200,d=0.08): n=int(SR*d); t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))*0.18*np.hanning(n)
def crickets(d):
    n=int(SR*d); t=np.arange(n)/SR; env=((np.sin(2*np.pi*3.2*t)>0.6)*(np.sin(2*np.pi*28*t)>0)).astype(float); return np.sin(2*np.pi*4300*t)*env*0.16
def ding(): n=int(SR*0.5); t=np.arange(n)/SR; return (np.sin(2*np.pi*1320*t)+0.5*np.sin(2*np.pi*1980*t))*np.exp(-t*7)*0.3
def dun3():
    out=np.zeros(int(SR*1.3))
    for k,f in enumerate((110,98,82)):
        n=int(SR*0.4); t=np.arange(n)/SR; s=np.tanh(3*np.sin(2*np.pi*f*t))*np.exp(-t*4)*0.6; st=int(k*0.42*SR); out[st:st+n]+=s[:len(out[st:st+n])]
    return out
def stamp(): return hit(0.4)*1.2
def tickt(): n=int(SR*0.03); return nz(n)*np.exp(-np.arange(n)/SR*200)*0.25
# ---------- plano ----------
TX=dict(
 rea=["FOI SEM QUERER","ISTO É LEGAL?","PLOT TWIST","NINGUÉM ESPERAVA","MOMENTO HISTÓRICO","TU VISTE ISTO?","ELE DISSE MESMO ISTO","CALMA, CALMA"],
 err=[("CÉREBRO.EXE","deixou de funcionar"),("A CARREGAR PLANO…","3%"),("ERRO 404","plano não encontrado"),("NÍVEL DE CALMA","0%"),("PACIÊNCIA","a acabar…"),("A PROCESSAR…","não compute")],
 sil=["*silêncio constrangedor*","*grilos*","*ninguém disse nada*","*pausa dramática*"],
 notif=[("Mãe","O jantar está na mesa!!"),("Polícia","Onde é que tu estás?"),("Banco","Saldo: 0,37 €"),("Padrinho","Precisamos de falar."),("Advogado","Não digas mais nada."),("Juliette","Visto às 03:12")],
 rate=[("PLANO","2/10"),("ATUAÇÃO","10/10"),("DISCRIÇÃO","0/10"),("CONFIANÇA","100%"),("LÓGICA","1/10")],
 sticker=["?!","LOL","AI AI","OOPS","HEHE","UAU"],
 calm=["ESTOU CALMO","TUDO SOB CONTROLO","ISTO É NORMAL"],
)
pick=lambda k: R.choice(TX[k])
ev=[]  # (t_src, tipo, dados, insere_s)
used=set()
def can(t): return all(abs(t-x[0])>2.0 for x in ev) and W0+1.0<t<W1-1.5
lib_peak=["freeze","zoom3","replay","shake"]
R.shuffle(lib_peak)
if can(pk): ev.append((pk,lib_peak[0],pick("rea"),{"freeze":1.0,"zoom3":1.3,"replay":1.6,"shake":0}[lib_peak[0]]))
other=["notif","sticker","error","stamp","notif","sticker","calm"]
R.shuffle(other)
for t in peaks:
    if not other: break
    if can(t):
        k=other.pop(); ev.append((t,k,None,{"error":1.0}.get(k,0)))
if sil and can(sil): ev.append((sil,"silence",pick("sil"),0))
# mais 1–2 eventos espalhados se houver espaço
for t in np.arange(W0+2,W1-2,3.3):
    if len(ev)>=7 or not other: break
    if can(t): k=other.pop(); ev.append((t,k,None,{"error":1.0}.get(k,0)))
ev.sort()
END=P.get("end") or R.choice(["rate","cta","loop"])
HOOK=P.get("hook","")
# ---------- render ----------
VP=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",OUT+".v.mp4"],stdin=subprocess.PIPE)
AUDIO=[]; NF=[0]
def emit(im): VP.stdin.write(im.tobytes()); NF[0]+=1
def reader(t0,t1):
    p=subprocess.Popen(["ffmpeg","-v","error","-ss",str(max(0,t0)),"-t",str(max(0.05,t1-t0)),"-i",SRC,"-vf",f"fps={FPS},scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield Image.frombytes("RGB",(W,H),b)
    p.stdout.close(); p.kill()
def aseg(t0,t1): return AU[int(t0*SR):int(t1*SR)].copy()
def mixin(a,s,t):
    i=int(max(0,t)*SR); seg=a[i:i+len(s)]; seg+=s[:len(seg)]
# 1) gancho: pico 1.3 s + texto do título
h0=max(0,pk-0.9); h1=min(dur,pk+0.4)
for i,im in enumerate(reader(h0,h1)):
    t=i/FPS; im=zoomc(im,1.1+0.15*t,W/2,H*0.55,R.randint(-12,12),R.randint(-12,12))
    if i<3: im=tint(im,WHT,0.6-0.2*i)
    if HOOK: im=text(im,HOOK,1560,86,YEL,pop(t),rot=-3)
    emit(im)
AUDIO.append(aseg(h0,h1))
# rewind
for k,tt in enumerate(np.linspace(h1,W0+0.2,12)):
    im=next(reader(tt,tt+0.05)); r,g,b=im.split(); r=ImageOps.expand(r,(14,0,0,0)).crop((0,0,W,H)); im=Image.merge("RGB",(r,g,b))
    d=ImageDraw.Draw(im)
    for y in range(0,H,6): d.line([(0,y),(W,y)],fill=(0,0,0),width=2)
    emit(text(im,"<< REWIND",230,70,WHT))
AUDIO.append(whoosh(12/FPS))
# 2) corpo
a=aseg(W0,W1); face=None; evq=list(ev)
over=[]  # overlays ativos: (t_src_ini, tipo, dados)
spd=None
fr_iter=reader(W0,W1); fi=0; acut=[]  # (t_rel_cut, inserted_audio)
skipfr=0
for im in fr_iter:
    t=W0+fi/FPS; fi+=1
    if skipfr>0: skipfr-=1; continue
    # overlays contínuos
    base=im
    for (ts,k,dat) in over:
        u=t-ts
        if k=="notif" and u<2.2:
            b=phone_banner(*dat); y=int(-200+min(1,u/0.18)*260) if u<1.9 else int(60-(u-1.9)/0.3*260); base.paste(b,(50,y),b)
        elif k=="sticker" and u<1.4:
            s=dat; sc=pop(u); 
            if sc>0: base=text(base,s,dat and 980,140,YEL,sc,FB,rot=R.choice([-10,8]))
        elif k=="silence" and u<1.8:
            base=text(base,dat,1250,62,WHT,pop(u),FM)
        elif k=="calm" and u<1.6:
            sh=10; base=base.transform((W,H),Image.AFFINE,(1,0,R.randint(-sh,sh),0,1,R.randint(-sh,sh)))
            base=text(base,dat,1450,96,WHT,pop(u))
        elif k=="stamp" and u<1.6:
            r,sv=dat; lay=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay); sc=max(0.01,2.2-1.2*min(1,u/0.12))
            f1=FM(int(70*sc)); f2=FM(int(120*sc)); cx,cy=W*0.62,H*0.42
            d.rounded_rectangle((cx-300*sc,cy-130*sc,cx+300*sc,cy+130*sc),radius=int(20*sc),outline=RED,width=max(4,int(12*sc)))
            d.text((cx,cy-50*sc),r,font=f1,fill=RED,anchor="mm"); d.text((cx,cy+45*sc),sv,font=f2,fill=RED,anchor="mm")
            lay=lay.rotate(-12,center=(cx,cy),resample=Image.BICUBIC); base.paste(lay,(0,0),lay)
        elif k=="speed" and u<2.0:
            base=text(base,">> x2",300,90,WHT,1,FM,x=880)
    if spd and t<spd: skipfr=1  # 2x: salta 1 frame em cada 2
    emit(base)
    for x in list(evq):
        ts,k,dat,ins=x
        if t>=ts:
            evq.remove(x)
            if k=="notif": over.append((t,k,pick("notif"))); mixin(a,ding(),t-W0)
            elif k=="sticker": over.append((t,k,pick("sticker"))); mixin(a,blip(1500,0.12),t-W0)
            elif k=="silence": over.append((t,k,dat)); c=crickets(1.8); i0_=int((t-W0)*SR); a[i0_:i0_+len(c)]=a[i0_:i0_+len(c)]*0.4+c[:len(a[i0_:i0_+len(c)])]
            elif k=="calm": over.append((t,k,pick("calm"))); mixin(a,hit(0.4),t-W0)
            elif k=="stamp": over.append((t,k,pick("rate"))); mixin(a,stamp(),t-W0)
            elif k=="speed": over.append((t,k,None)); spd=t+2.0  # áudio acelerado tratado abaixo
            elif k in ("freeze","zoom3","replay","error"):
                fc=findface(im) if k in ("freeze","zoom3") else None
                n=int(ins*FPS); ia=np.zeros(int(ins*SR))
                if k=="freeze":
                    g=ImageOps.grayscale(im).convert("RGB"); FX,FY,ZM=(fc[0],fc[1],1.6) if fc else (W/2,H*0.55,0.35); emj=R.choice(["laugh","skull","shock","clown"])
                    for i in range(n):
                        tt=i/FPS; z=1+ZM*min(1,tt/0.12); cw,ch=W/z,H/z; x0=max(0,min(W-cw,FX-cw/2)); y0=max(0,min(H-ch,FY-ch*(0.35 if ZM>1 else 0.5)))
                        f=g.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((W,H)); sh=int(16*math.exp(-tt*6))
                        f=f.transform((W,H),Image.AFFINE,(1,0,R.randint(-sh,sh),0,1,R.randint(-sh,sh))); f=text(f,dat,1450,110,YEL,pop(tt))
                        if tt>0.15: s=int(260*pop(tt-0.15)); e_=emoji(emj,max(8,s)); f.paste(e_,(W-s-60,1000-s//2),e_)
                        emit(f)
                    ia[:len(boom(ins))]+=boom(ins)[:len(ia)]
                elif k=="zoom3":
                    FX,FY=(fc if fc else (W/2,H*0.4))
                    for i in range(n):
                        tt=i/FPS; st=min(2,int(tt/0.42)); z=[1.25,1.6,2.1][st]; f=zoomc(im,z,FX,FY)
                        if st==2: f=tint(f,(150,0,0),0.25)
                        if tt%0.42<0.05: f=tint(f,WHT,0.4)
                        if tt>0.84: f=text(f,dat,1450,110,RED,pop(tt-0.84))
                        emit(f)
                    ia[:len(dun3())]+=dun3()[:len(ia)]
                elif k=="replay":
                    rp=list(reader(t-0.8,t+0.1)); rp=[x for x in rp for _ in (0,1)][:n]
                    for i,f in enumerate(rp):
                        f=ImageEnhance.Contrast(f).enhance(1.2); d=ImageDraw.Draw(f); d.ellipse((60,240,110,290),fill=RED if (i//10)%2==0 else (120,0,0))
                        d.text((130,265),"REPLAY",font=FM(60),fill=WHT,anchor="lm",stroke_width=4,stroke_fill=(0,0,0)); f=zoomc(f,1.15,W/2,H*0.55)
                        if i>n*0.5: f=text(f,dat,1450,100,YEL,pop((i-n*0.5)/FPS))
                        emit(f)
                    sl=aseg(t-0.8,t+0.1); sl=np.interp(np.linspace(0,len(sl)-1,int(len(sl)*2)),np.arange(len(sl)),sl)[:len(ia)]; ia[:len(sl)]+=sl*0.8; ia[:len(whoosh())]+=whoosh()
                elif k=="error":
                    hdr,sub=pick("err")
                    for i in range(n):
                        tt=i/FPS; f=Image.new("RGB",(W,H),(0,0,170))
                        if R.random()<0.25: f=Image.blend(f,ImageEnhance.Brightness(im).enhance(0.6),0.35)
                        d=ImageDraw.Draw(f); d.text((W/2,820),hdr,font=FM(fitw:=min(96,int(96*900/max(1,ImageDraw.Draw(f).textlength(hdr,font=FM(96)))))),fill=WHT,anchor="mm")
                        if "%" in sub:
                            d.rectangle((190,960,890,1020),outline=WHT,width=6); d.rectangle((200,970,200+int(680*min(0.03,tt*0.04)),1010),fill=WHT); d.text((W/2,1100),sub,font=FM(70),fill=WHT,anchor="mm")
                        else: d.text((W/2,980),sub,font=FM(62),fill=WHT,anchor="mm")
                        emit(f)
                    s_=np.concatenate([scratch(),blip(880,0.1),np.zeros(int(SR*0.2)),blip(660,0.1)]); ia[:len(s_)]+=s_[:len(ia)]
                elif k=="shake": pass
                acut.append((t-W0+1/FPS,ia))
            if k=="shake":
                over.append((t,"calm",dat)); mixin(a,boom(0.8),t-W0)
# áudio do corpo com inserções e aceleração 2x
parts=[]; last=0.0
for tc,ia in acut: parts.append(a[int(last*SR):int(tc*SR)]); parts.append(ia); last=tc
parts.append(a[int(last*SR):]); body=np.concatenate(parts)
AUDIO.append(body)
# 3) final
ef=list(reader(W1-0.05,W1))[-1:] or [im]; last=ef[0]; n=int(1.6*FPS); ea=np.zeros(int(1.6*SR))
if END=="rate":
    r,sv=pick("rate")
    for i in range(n):
        tt=i/FPS; f=ImageEnhance.Brightness(last).enhance(0.45); f=text(f,"NOTA FINAL",760,80,WHT,pop(tt))
        if tt>0.35: f=text(f,f"{r}: {sv}",960,130,RED,pop(tt-0.35),rot=-6)
        emit(f)
    mixin(ea,stamp(),0.35)
elif END=="cta":
    q=P.get("cta") or R.choice(["Tu fazias o mesmo?","Quem tem razão?","Parte 2?","Comenta 1 se te ris"])
    for i in range(n):
        tt=i/FPS; f=ImageEnhance.Brightness(last).enhance(0.45); f=text(f,q,880,100,WHT,pop(tt)); f=text(f,"COMENTA 👇".replace(" 👇",""),1040,90,YEL,pop(tt-0.3)); emit(f)
    mixin(ea,ding(),0.0)
else:  # loop: volta ao início com flash, dá vontade de rever
    first=next(reader(W0+0.05,W0+0.1))
    for i in range(n):
        tt=i/FPS; f=Image.blend(last,first,min(1,tt/1.2)); f=text(f,"…E FOI ASSIM QUE COMEÇOU",1500,70,WHT,pop(tt)); emit(f)
    mixin(ea,whoosh(0.6),0.9)
AUDIO.append(ea)
VP.stdin.close(); VP.wait()
mix=np.concatenate(AUDIO); n=int(NF[0]/FPS*SR); mix=np.pad(mix,(0,max(0,n-len(mix))))[:n]; mix=mix/np.abs(mix).max()*0.95
mix.astype(np.float32).tofile(OUT+".m.f32")
subprocess.run(["ffmpeg","-v","error","-y","-i",OUT+".v.mp4","-f","f32le","-ar",str(SR),"-ac","1","-i",OUT+".m.f32","-c:v","copy","-c:a","aac","-b:a","160k","-ac","2","-shortest","-movflags","+faststart",OUT])
os.remove(OUT+".v.mp4"); os.remove(OUT+".m.f32")
print(OUT,round(NF[0]/FPS,1),"win",round(W0,1),round(W1,1),"end",END,[(round(x[0],1),x[1]) for x in ev])
