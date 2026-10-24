"""python3 check.py <data.json> : 형식 검사. 문제 없으면 OK 출력."""
import sys,json
d=json.load(open(sys.argv[1]));days=d['days'];err=[]
if len(days)!=30:err.append('days must be 30, got %d'%len(days))
spec={'g3':(3,3,2),'g6':(5,3,6),'pa':(5,5,6)}
for i,x in enumerate(days,1):
    for key in ('theme','sub'):
        if not x.get(key):err.append(f'{i} {key}')
    for g,(nw,ne,nd) in spec.items():
        p=x[g]
        if len(p['w'])!=nw or any(len(w)!=7 for w in p['w']):err.append(f'{i} {g}.w')
        if len(p['e'])!=ne or any(len(e)!=3 for e in p['e']):err.append(f'{i} {g}.e')
        if len(p['d'])!=nd or any(len(e)!=2 for e in p['d']):err.append(f'{i} {g}.d')
    a=x['ad']
    if not a.get('t') or not a.get('s'):err.append(f'{i} ad.t/s')
    if len(a['k'])!=5 or any(len(e)!=3 for e in a['k']):err.append(f'{i} ad.k')
    if len(a['d'])!=14 or any(len(e)!=2 for e in a['d']):err.append(f'{i} ad.d')
print('OK' if not err else '\n'.join(err))
