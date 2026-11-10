import os,sys
os.environ.setdefault("S","/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import yt_illus as Y, yt_illus2 as Z
ser,i,c,head,out=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4],sys.argv[5]
L=Y.FACTS if ser=="facts" else Y.GIRLS
L[i]=(head,L[i][1])
Z.make(ser,i,c,f"{os.environ['S']}/ytw/vo_new/{ser}_{i}.wav",out)
