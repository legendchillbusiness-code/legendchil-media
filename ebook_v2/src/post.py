import re,sys
for f in sys.argv[1:]:
    t=open(f).read()
    t=re.sub(r'\*\*\s+\*\*',' ',t)
    t=re.sub(r'\*\*([^*\n]*?)\s+\*\*',r'**\1** ',t)
    # junta títulos partidos
    t=re.sub(r'^(# .+)\n\n# (?!Cap|Chap|PARTE|PART|Índice|Contents|INTRO|PALAVRAS|FINAL)(.+)$',r'\1 \2',t,flags=re.M)
    t=re.sub(r'^(# .+)\n\n# (?!Cap|Chap|PARTE|PART|Índice|Contents|INTRO|PALAVRAS|FINAL)(.+)$',r'\1 \2',t,flags=re.M)
    t=re.sub(r'\*\n?(\w+)\.\n', lambda m: m.group(0), t)
    t=re.sub(r'^\*(.+)\* (\S+)$',r'*\1 \2*',t,flags=re.M)
    t=t.replace('# Índice\n\n','').replace('# Contents\n\n','')
    open(f,'w').write(t)
