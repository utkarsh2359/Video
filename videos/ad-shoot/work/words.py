import json,sys
b,a,z=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
for i,x in enumerate(json.load(open(f'tx/{b}/transcript.json'))):
    if a<=x['start']<=z: print(f"{i:4d} {x['start']:7.2f} {x['end']:7.2f} {x['text']}")
