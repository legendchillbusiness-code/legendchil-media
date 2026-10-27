import json,subprocess,sys,numpy as np,random
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance,ImageFilter
W,H,FPS,SR=1080,1920,30,44100
EPJ,OUT,SERIES=sys.argv[1],sys.argv[2],sys.argv[3]
IMG='/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/novela/img/'
E=json.load(open(EPJ)); WORDS=json.load(open('words.json'))
PB=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',s)
SERIF=lambda s: ImageFont.truetype('/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/six/ebg-600-normal.ttf',s)
GOLD=(232,190,100); WHITE=(250,248,242); RED=(214,30,30)
PAUSE=0.35
def grade(p,bw=False):
    im=ImageOps.autocontrast(Image.open(IMG+p).convert('L'),cutoff=0.5)
    im=im.convert('RGB') if bw else ImageOps.colorize(im,(0,0,0),(255,212,150)).convert('RGB')
    im=ImageEnhance.Contrast(im).enhance(1.15)
    if bw: im=ImageEnhance.Brightness(im).enhance(0.6)
    sc=max(W*1.2/im.width,H*1.2/im.height); return im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
def kb(big,p,dirn,shake=0):
    z=1.0+0.10*p if dirn==0 else 1.10-0.10*p
    cw,ch=int(big.width/1.2/z*1.0),int(big.height/1.2/z)
    cw,ch=int(W/ (W*1.2/big.width) /z), int(H/(H*1.2/big.height)/z)
    x0=(big.width-cw)//2+int(shake*random.uniform(-1,1)); y0=(big.height-ch)//2+int(shake*random.uniform(-1,1))
    return big.crop((x0,y0,x0+cw,y0+ch)).resize((W,H),Image.BILINEAR)
VIG=Image.new('L',(W,H),0); dv=ImageDraw.Draw(VIG)
for i in range(50): dv.rectangle((i*5,i*8,W-i*5,H-i*8),fill=int(255*min(1,0.45+i/35)))
VIG=VIG.filter(ImageFilter.GaussianBlur(90)); BLACK=Image.new('RGB',(W,H),(0,0,0))
def shadow_text(im,xy,s,font,fill,anchor='mm',stroke=0):
    sh=Image.new('RGBA',im.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
    ds.text((xy[0]+3,xy[1]+5),s,font=font,fill=(0,0,0,230),anchor=anchor,stroke_width=stroke,stroke_fill=(0,0,0,230))
    sh=sh.filter(ImageFilter.GaussianBlur(5)); im.paste(sh,(0,0),sh)
    ImageDraw.Draw(im).text(xy,s,font=font,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=(0,0,0))
FC=PB(74)
def caption(im,words,t):
    # chunks of up to 3 words; show chunk containing current word; active word gold
    chunks=[];cur=[]
    dd=ImageDraw.Draw(im)
    for w in words:
        if cur and dd.textlength(' '.join(x[0].upper() for x in cur+[w]),font=FC)>960: chunks.append(cur);cur=[]
        cur.append(w)
        if len(cur)==3 or w[0][-1] in '.,?!': chunks.append(cur);cur=[]
    if cur: chunks.append(cur)
    ch=None
    for c in chunks:
        if t>=c[0][1]-0.05: ch=c
    if ch is None or t>ch[-1][2]+0.35 and ch is chunks[-1]: 
        if ch is None: return
    d=ImageDraw.Draw(im)
    txt=[w[0].upper() for w in ch]; widths=[d.textlength(x+' ',font=FC) for x in txt]
    x=W/2-sum(widths)/2; y=1360
    for (w,s,e),tx,wd in zip(ch,txt,widths):
        col=GOLD if s-0.02<=t<=e+0.05 else WHITE
        shadow_text(im,(x,y),tx,FC,col,anchor='lm',stroke=4); x+=wd
def header(im):
    d=ImageDraw.Draw(im); f=PB(30)
    shadow_text(im,(W/2,165),SERIES,f,(225,200,150))
# timeline
segs=[];t=0
for i,s in enumerate(E['scenes']):
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'n{i}.wav']))
    lead=0.45 if s.get('freeze') else 0.0
    segs.append((t,lead,d)); t+=lead+d+PAUSE
END=2.4; TOTAL=t+END
bigs=[grade(s['img'],bool(s.get('freeze'))) for s in E['scenes']]
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-preset','medium','vid.mp4'],stdin=subprocess.PIPE)
FT,FS=SERIF(150),PB(56)
N=int(TOTAL*FPS)
for n in range(N):
    gt=n/FPS
    k=max(i for i,(st,_,_) in enumerate(segs) if st<=gt) if gt<t else None
    if k is not None:
        st,lead,d=segs[k]; s=E['scenes'][k]; lt=gt-st; prog=lt/(lead+d+PAUSE)
        fr=s.get('freeze')
        if fr:
            shake=18*max(0,1-lt/0.35)
            im=kb(bigs[k],0.5+0.1*prog,0,shake)
        else:
            im=kb(bigs[k],prog,k%2)
        im=Image.composite(im,BLACK,VIG)
        if lt<0.12: im=Image.blend(im,Image.new('RGB',(W,H),(255,255,255) if fr else (0,0,0)),(0.4 if fr else 0.6)*(1-lt/0.12))
        header(im)
        if fr:
            band=Image.new('L',(W,H),0); db=ImageDraw.Draw(band); db.rectangle((0,430,W,790),fill=170); band=band.filter(ImageFilter.GaussianBlur(60))
            im=Image.composite(BLACK,im,band)
            a=min(1,lt/0.15)
            shadow_text(im,(W/2,560),fr[0],FT,RED if a>0 else RED)
            shadow_text(im,(W/2,700),fr[1],FS,WHITE)
        caption(im,WORDS[k],lt-lead)
    else:
        lt=gt-t; im=kb(bigs[-1],1.0,0); im=ImageEnhance.Brightness(Image.composite(im,BLACK,VIG)).enhance(0.35)
        header(im)
        sc=1+0.04*np.sin(lt*6)
        shadow_text(im,(W/2,830),E['end'][0],SERIF(int(170*sc)),GOLD)
        shadow_text(im,(W/2,990),E['end'][1],SERIF(120),WHITE)
        if lt>0.6: shadow_text(im,(W/2,1250),'Segue para não perderes.',PB(48),WHITE)
    p.stdin.write(im.tobytes())
p.stdin.close();p.wait()
# ---- audio
A=np.zeros(int((TOTAL+0.5)*SR),np.float32)
def load(f):
    r=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','f32le','-ac','1','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(r,np.float32).copy()
bed=load('/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/g2/phonk40.wav')
bedmask=np.full(len(A),0.16,np.float32)
for i,(st,lead,d) in enumerate(segs):
    v=load(f'n{i}.wav'); a=int((st+lead)*SR); A[a:a+len(v)]+=v*1.15
    if E['scenes'][i].get('freeze'):
        a0=int(st*SR); bedmask[a0:a0+int((lead+0.8)*SR)]=0.0
        tt=np.arange(int(1.1*SR))/SR; f=55*np.exp(-tt*1.5)+35
        boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3.2)*0.9+np.random.randn(len(tt)).astype(np.float32)*np.exp(-tt*18)*0.25
        A[a0:a0+len(boom)]+=boom.astype(np.float32)
# riser into end + hard cut
r0=int((t-1.6)*SR); tt=np.arange(int(1.6*SR))/SR
riser=(np.random.randn(len(tt))*0.18*(tt/1.6)**2+np.sin(2*np.pi*(200+600*(tt/1.6)**2)*tt)*0.08*(tt/1.6)).astype(np.float32)
A[r0:r0+len(riser)]+=riser
# end: ticking
for k in range(int(END/0.5)):
    a=int((t+k*0.5)*SR); tk=np.sin(2*np.pi*2400*np.arange(800)/SR)*np.exp(-np.arange(800)/80)*0.35; A[a:a+800]+=tk
sm=np.convolve(bedmask,np.ones(2205)/2205,mode='same').astype(np.float32)
A[:len(A)]+=np.resize(bed,len(A))*sm
A=np.clip(A/max(1,np.abs(A).max()*1.05),-1,1)
subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(SR),'-ac','1','-i','-','-c:a','pcm_s16le','aud.wav'],input=A.tobytes(),check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','vid.mp4','-i','aud.wav','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',OUT],check=True)
print(OUT,round(TOTAL,1))
