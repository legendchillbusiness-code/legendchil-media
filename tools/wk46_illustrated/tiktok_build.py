import os, json
from PIL import Image, ImageDraw, ImageFont, ImageOps
W,H=1080,1023
B="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
M="/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
if not os.path.exists(M): M=B
PAL={"verde":dict(mid=(22,58,52),bg=(60,190,170),fg=(10,20,20),ac=(70,214,200)),
"vermelho":dict(mid=(92,12,18),bg=(200,40,48),fg=(255,255,255),ac=(235,70,80)),
"ambar":dict(mid=(88,66,8),bg=(240,170,50),fg=(20,20,20),ac=(245,200,40)),
"azul":dict(mid=(14,34,78),bg=(70,120,230),fg=(255,255,255),ac=(120,175,255))}
ORDER=["verde","vermelho","ambar","azul"]
FACTS=[("Words fade. Feelings stay.","Emotional moments stick in memory far longer than plain facts. People remember how you made them feel."),
("You judge yourself by your intentions.","You judge others by their actions. It's called the actor-observer bias, and most people do it."),
("The first thing you hear sticks.","Whatever you learn first about a person colors everything you learn after. It's called the primacy effect."),
("Talk less. Be liked more.","People tend to enjoy a conversation more when they are the ones doing most of the talking."),
("You copy people you like.","Without noticing, we tend to mirror the posture and gestures of people we get along with."),
("Silence makes people talk.","Most people feel the urge to fill a pause. That's often when they say more than they planned."),
("People judge by the peak and the end.","Not the average. How an experience peaked and how it ended decides how it is remembered.")]
GIRLS=[("She keeps checking where you are.","If her eyes find you again and again across the room, she has already noticed you."),
("She asks about your life.","Interest shows up as real questions, not just small talk."),
("Feet point where interest is.","People tend to turn their feet toward who they want to talk to, even when their eyes look away."),
("She remembers the small things.","A detail you mentioned once and she brings back later is attention. Not luck."),
("Fast replies mean nothing.","Detailed replies do. Effort in the message shows interest."),
("She stops asking questions.","When the questions stop, the conversation is usually already over for her."),
("She laughs, then repeats the joke.","Bringing your joke back later means she is still thinking about it.")]
TF=["#2 is the one almost everyone misses.","#3 changes how you read every first meeting.","#4 is why the best listeners win.","#5 happens to you every day. You never notice.","#6 is what silence does to people.","#7 decides how people remember you.","That was 7. The rest people only notice too late."]
TG=["#2 is the one she never says out loud.","#3 is body language. Her feet give her away.","#4 is the one that means she's invested.","#5 is why a fast reply means nothing.","#6 is when it's already over.","#7 is the one most guys miss.","That's 7. She's giving you more signs than you think."]
def wrap(d,t,f,mw):
    out=[];l=""
    for w in t.split():
        x=(l+" "+w).strip()
        if d.textlength(x,font=f)<=mw: l=x
        else: out.append(l); l=w
    out.append(l); return out
def cover_man(c):
    g=ImageOps.autocontrast(Image.open("/home/claude/legendchil-media/images/psych_says/cover_en.jpg").convert("L"),cutoff=1)
    return ImageOps.colorize(g,black=(0,0,0),mid=PAL[c]["mid"],white=(255,255,255),midpoint=110)
def cover_girl(c):
    s=Image.open("/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad/woman_ref.jpg").convert("L").crop((0,170,1438,1532))
    g=ImageOps.fit(s,(W,H),Image.LANCZOS,centering=(0.5,0.5))
    g=ImageOps.autocontrast(g,cutoff=0.5)
    g=g.point(lambda v:min(255,int(v*1.35)))
    im=ImageOps.colorize(g,black=(0,0,0),mid=PAL[c]["mid"],white=(255,255,255),midpoint=110)
    d=ImageDraw.Draw(im); f=ImageFont.truetype(M,66)
    d.text((W//2,800),"Psychology about girls...",font=f,fill=(255,255,255),anchor="mm")
    return im
ILLD="/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad/ill/"
ILL={("facts",0):"facts1.jpg",("facts",1):"facts2.jpg",("facts",2):"facts3.jpg",("facts",3):"facts4.jpg",("facts",4):"facts5.jpg",("facts",5):"facts6.jpg",("facts",6):"facts7.jpg",("girls",0):"girls1.jpg",("girls",1):"girls2.jpg",("girls",2):"girls3.jpg",("girls",3):"girls4.jpg",("girls",4):"girls5.jpg",("girls",5):"girls6.jpg",("girls",6):"girls7.jpg"}
def prep_ill(fn):
    g=Image.open(ILLD+fn).convert("L")
    g=g.point(lambda v:255 if v>=165 else int(v*255/165))  # skin tone -> white, lines stay
    bb=g.point(lambda v:255 if v<200 else 0).getbbox()
    return g.crop(bb)
def slide2(tag,head,body,c,ill=None):
    p=PAL[c]; im=Image.new("RGB",(W,H),p["bg"]); d=ImageDraw.Draw(im)
    ft=ImageFont.truetype(B,26); tw=d.textlength(tag,font=ft)+60
    d.rectangle((W/2-tw/2,60,W/2+tw/2,118),fill=(15,15,15)); d.text((W/2,89),tag,font=ft,fill=(255,255,255),anchor="mm")
    if ill:
        hs,bs,hl,bl=70,40,84,56
    else: hs,bs,hl,bl=78,44,96,62
    f1=ImageFont.truetype(B,hs); f2=ImageFont.truetype(M,bs)
    l1=wrap(d,head,f1,W-140); l2=wrap(d,body,f2,W-140)
    th=len(l1)*hl+30+len(l2)*bl
    y=160 if ill else max(170,(H+118-th)//2)
    for ln in l1: d.text((70,y),ln,font=f1,fill=p["fg"]); y+=hl
    y+=30
    for ln in l2: d.text((70,y),ln,font=f2,fill=p["fg"]); y+=bl
    if ill:
        g=prep_ill(ill); top=y+20; bh=H-30-top; bw=W-100
        k=min(bh/g.height,bw/g.width); g=g.resize((int(g.width*k),int(g.height*k)),Image.LANCZOS)
        x=(W-g.width)//2; yy=top+(bh-g.height)//2
        reg=im.crop((x,yy,x+g.width,yy+g.height)); col=Image.new("RGB",g.size,p["bg"])
        from PIL import ImageChops
        im.paste(ImageChops.multiply(reg,g.convert("RGB")),(x,yy))
    return im
def slide3(t,c):
    p=PAL[c]; im=Image.new("RGB",(W,H),(12,12,12)); d=ImageDraw.Draw(im)
    f=ImageFont.truetype(B,84); ls=wrap(d,t,f,W-160); y=(H-len(ls)*104)//2
    for i,ln in enumerate(ls): d.text((80,y),ln,font=f,fill=(255,255,255) if i<len(ls)-1 else p["ac"]); y+=104
    d.rectangle((80,H-90,80+120,H-82),fill=p["ac"])
    return im
posts=[]
for i in range(7):
    posts.append(("facts",i,"PSYCHOLOGY SAYS",FACTS[i],TF[i])); posts.append(("girls",i,"PSYCHOLOGY ABOUT GIRLS",GIRLS[i],TG[i]))
for n,(ser,i,tag,(h,b),t3) in enumerate(posts):
    c=ORDER[i%4] if ser=="facts" else ORDER[(i+2)%4]; od=f"p{n+1:02d}_{ser}{i+1}_{c}"; os.makedirs(od,exist_ok=True)
    (cover_man(c) if ser=="facts" else cover_girl(c)).convert("RGB").save(f"{od}/1.jpg",quality=92)
    slide2(tag,h,b,c,ILL.get((ser,i))).save(f"{od}/2.jpg",quality=92); slide3(t3,c).save(f"{od}/3.jpg",quality=92)
print(len(posts))
