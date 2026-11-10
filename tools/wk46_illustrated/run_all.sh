#!/bin/bash
export S=/tmp/claude-0/-home-claude/c13d6b24-0e07-5236-8288-4698749ad984/scratchpad
cd $S/ytw/tools
python3 - <<'P' | xargs -P 4 -L 1 bash -c 'MUSIC=ambient MVOL=-16 python3 yt_illus2.py $0 $1 $2 ../vo/$0_$1.wav out/short_$0$(( $1 + 1 ))_$2.mp4 >/dev/null 2>>out/log.txt && echo done $0 $1'
import json
for s,i,c in json.load(open("jobs.json")): print(s,i,c)
P
