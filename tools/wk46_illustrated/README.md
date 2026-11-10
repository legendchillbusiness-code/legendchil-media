# Pipeline ilustrado (wk46)
Variavel S = pasta de trabalho (scripts leem S/ill, S/posts/build.py, S/ytw/six, S/ytw/vo, S/ytw/tools).
Montar: S/ill <- images/ill_wk46; S/posts/build.py <- tiktok_build.py; S/ytw/tools <- esta pasta; S/ytw/six <- fontes EB Garamond (ver tools/ do repo); S/ytw/vo/<serie>_<i>.wav <- vozes.
- Short individual: python3 yt_illus2.py <facts|girls> <i> <cor> <voz.wav> <out.mp4>  (MUSIC=ambient MVOL=-16, END=0 remove cartao final)
- Short de lista: python3 yt_list2.py '<json spec>' out.mp4  (ver spec nos exemplos do historico: title, intro, intro_text, c0, items [[serie,i],...])
- Voz: ElevenLabs Mark (voice_id u27PQ4R4svuZXlMb7yfu), eleven_v4, 1 geracao; pos: silenceremove, atempo=1.2, loudnorm I=-14
- Carrosseis TikTok: tiktok_build.py (3 slides, cores verde/vermelho/ambar/azul)
- Vozes ja processadas em vo/*.mp3 (converter para wav antes de usar: ffmpeg -i x.mp3 x.wav)
