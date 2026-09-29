import json,sys
# print transcript as lines, breaking on gaps > 0.6s, with start/end times
for b in sys.argv[1:]:
    w=json.load(open(f'tx/{b}/transcript.json'))
    print(f'==== {b}')
    line=[];ls=None;prev=None
    for x in w:
        if prev is not None and x['start']-prev>0.6:
            print(f"[{ls:6.2f}-{prev:6.2f}] "+" ".join(line)); line=[];ls=None
        if ls is None: ls=x['start']
        line.append(x['text']); prev=x['end']
    if line: print(f"[{ls:6.2f}-{prev:6.2f}] "+" ".join(line))
