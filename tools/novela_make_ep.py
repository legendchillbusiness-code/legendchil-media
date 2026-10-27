import json,subprocess,sys,os,numpy as np
D='/tmp/claude-0/-home-claude/9be5d4db-9e4a-5a6b-b6fc-8a267e9a7a31/scratchpad/novela'
ep=sys.argv[1]; os.makedirs(f'{D}/{ep}',exist_ok=True); os.chdir(f'{D}/{ep}')
E=json.load(open('ep.json'))
for i,s in enumerate(E['scenes']):
    subprocess.run(['python3','-m','piper','-m',f'{D}/../tts/tugao.onnx','--length-scale','1.08','-f',f'raw{i}.wav'],input=s['say'].encode(),check=True,capture_output=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'raw{i}.wav','-af','asetrate=22050*0.89,aresample=44100,atempo=1.06,bass=g=4,aecho=0.8:0.6:40:0.10','-ar','44100','-ac','1',f'n{i}.wav'],check=True)
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8'); out=[]
for i,s in enumerate(E['scenes']):
    a=subprocess.run(['ffmpeg','-v','error','-i',f'n{i}.wav','-f','f32le','-ac','1','-ar','16000','-'],capture_output=True).stdout
    segs,_=m.transcribe(np.frombuffer(a,np.float32),language='pt',word_timestamps=True,initial_prompt=s['say'])
    ws=[(w.word.strip(),float(w.start),float(w.end)) for sg in segs for w in sg.words]
    sw=s['say'].split()
    if len(ws)!=len(sw):
        d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'n{i}.wav']))
        L=sum(len(w) for w in sw); t=0.05; ws=[]
        for w in sw: dd=(d-0.1)*len(w)/L; ws.append((w,t,t+dd)); t+=dd
    else: ws=[(sw[k],ws[k][1],ws[k][2]) for k in range(len(sw))]
    out.append(ws)
json.dump(out,open('words.json','w'),ensure_ascii=False)
subprocess.run(['python3',f'{D}/render_novela.py','ep.json','raw.mp4',E['series']],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','raw.mp4','-c:v','copy','-af','loudnorm=I=-14:TP=-1:LRA=9','-c:a','aac','-b:a','192k','-movflags','+faststart',f'{D}/novela_{ep}.mp4'],check=True)
print('done',ep)
