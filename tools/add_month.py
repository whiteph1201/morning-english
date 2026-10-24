"""python3 tools/add_month.py YYYY-MM : build/YYYY-MM 결과를 m/YYYY-MM 으로 옮기고 months.json, history.json 갱신.
KEEP 개월보다 오래된 달은 지운다(용량 관리)."""
import sys,json,os,shutil,glob
KEEP=int(os.environ.get('KEEP_MONTHS') or '12')
month=sys.argv[1];src=f'build/{month}';dst=f'm/{month}'
os.makedirs(dst,exist_ok=True)
for f in glob.glob(src+'/*'):shutil.move(f,dst+'/'+os.path.basename(f))
mj=json.load(open('m/months.json'));ms=sorted(set(mj['months']+[month]))
removed=[]
while len(ms)>KEEP:
    old=ms.pop(0);shutil.rmtree(f'm/{old}',ignore_errors=True);removed.append(old);print('removed',old)
os.makedirs('build',exist_ok=True);open('build/removed.txt','w').write('\n'.join(removed))
json.dump({'months':ms},open('m/months.json','w'))
h=json.load(open('m/history.json'));d=json.load(open(dst+'/data.json'))['days']
h[month]={'kids':[x['theme'] for x in d],'adult':[x['ad']['t'] for x in d]}
json.dump(h,open('m/history.json','w'),ensure_ascii=False)
print('added',month,ms)
