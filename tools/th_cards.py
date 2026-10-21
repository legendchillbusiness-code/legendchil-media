import subprocess,numpy as np,sys
from PIL import Image
W,H,F=1080,1920,30
follow,out=sys.argv[1],sys.argv[2]
fo=Image.open(follow).convert('RGB').resize((W,H))
card=Image.open('/root/th4/img/endcard_dm.png').convert('RGB')
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(F),'-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
for k in range(48):
  t=min(k/5,1);a=(np.asarray(fo).astype(float)*(0.4+0.6*t)).astype(np.uint8);enc.stdin.write(a.tobytes())
for k in range(70):
  t=min(k/6,1);s=1.04-0.04*t
  im=card.resize((int(W*s),int(H*s)),Image.LANCZOS);x=(im.width-W)//2;y=(im.height-H)//2
  a=(np.asarray(im.crop((x,y,x+W,y+H))).astype(float)*(0.35+0.65*t)).astype(np.uint8);enc.stdin.write(a.tobytes())
enc.stdin.close();enc.wait()
