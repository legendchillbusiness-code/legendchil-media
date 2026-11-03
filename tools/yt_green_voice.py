"""Listas verdes com voz (sem musica). uso: python3 -I yt_green_voice.py slug=URL_MP3 ...
MP3 vem do ElevenLabs (voz Mark, eleven_v4). Fala 1.3x, saida em /tmp/vo/out."""
import os
os.makedirs("/tmp/vo/out",exist_ok=True)
import sys, json, subprocess, os
sys.path.insert(0,'/home/claude/legendchil-media/tools')
import yt_green_render as R
root='/home/claude/legendchil-media'
w46={d['slug']:d for d in json.load(open(f'{root}/tools/yt_green_w46.json'))}
w45={d['slug']:d for d in json.load(open(f'{root}/tools/yt_green_w45.json'))}
BG={'using_you':'face'}
def make(slug,url):
    d=w46.get(slug) or w45[slug]
    bg=d.get('bg') or BG.get(slug,'face')
    mp3=f'/tmp/vo/{slug}.mp3'
    subprocess.run(['curl','-s','-m','40','-o',mp3,url],check=True)
    png=f'/tmp/vo/{slug}.png'; wav=f'/tmp/vo/{slug}.wav'
    old=f'{root}/videos/yt_green/{slug}.mp4'
    if os.path.exists(old):
        subprocess.run(['ffmpeg','-v','error','-y','-ss','5','-i',old,'-frames:v','1',png],check=True)
    else:
        im,y=R.card(f'{root}/images/yt_c/bg_{bg}.jpg',d['head'],d['items'])
        if y>R.H-230: print('WARN overflow',slug,y)
        im.save(png)
    subprocess.run(['ffmpeg','-v','error','-y','-i',mp3,'-af','silenceremove=start_periods=1:start_threshold=-45dB,atempo=1.3,loudnorm=I=-14',wav],check=True)
    dur=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',wav]).decode().strip()
    out=f'/tmp/vo/out/{slug}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',png,'-i',wav,'-t',dur,'-r','30','-vf','format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','20','-tune','stillimage','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',out],check=True)
    print(slug,bg,dur)
if __name__=='__main__':
    for a in sys.argv[1:]:
        s,u=a.split('=',1); make(s,u)
