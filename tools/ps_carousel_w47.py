# Slide 2 sem cabecalho "DID YOU KNOW?" (mantem cor e frases). Saida: tiktok_ps/w47_N.jpg
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));T=f"{R}/tiktok_ps"
W,H=1080,1023;Y=(236,221,30);K=(10,10,10);WH=(255,255,255);PH=702
PB=lambda s:ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",s)
def wrap(d,words,font,maxw):
    L,c=[],[]
    for w in words:
        t=c+[w]
        if d.textlength(" ".join(x for x,_ in t),font=font)<=maxw:c=t
        else:L.append(c);c=[w]
    return L+[c]
POSTS=[("02","People who hold eye contact too long aren't *confident.* They're *testing* you."),
("06","If someone pays for everything early on, find out what they *expect* later."),
("08","People who pause before they answer are choosing what you get to *know.*"),
("09","People who laugh at everything you say want *something* from you."),
("04","People who keep saying \"trust me\" already know you *shouldn't.*"),
("12","In any group, the one everyone checks before laughing is the one in *control.*")]
for i,(n,t) in enumerate(POSTS,1):
    ph=Image.open(f"{T}/s2_{n}.jpg").convert("RGB").crop((12,110,1068,710))
    ph=ImageOps.fit(ph,(W-24,PH-12),Image.LANCZOS)
    im=Image.new("RGB",(W,H),Y);d=ImageDraw.Draw(im)
    im.paste(ph,(12,12));d.rectangle((12,PH,W-12,H),fill=K)
    words=[(w.strip("*"),w.startswith("*")) for w in t.split()]
    for size in (62,58,54,50):
        f=PB(size);L=wrap(d,words,f,960)
        if len(L)<=3:break
    lh=int(size*1.22);y0=PH+(H-PH-lh*len(L))/2
    for j,ln in enumerate(L):
        x=(W-d.textlength(" ".join(x for x,_ in ln),font=f))/2;y=y0+j*lh
        for w,k in ln:
            d.text((x,y),w,font=f,fill=Y if k else WH);x+=d.textlength(w+" ",font=f)
    im.save(f"{T}/w47_{i}.jpg",quality=93)
