"""incoming/YYYY-MM/ 안의 *.json 조각(파일 이름 순서)을 합쳐 build/YYYY-MM/data.json 을 만든다.
조각은 {"days":[...]} 또는 [...] (하루치 목록) 형식 모두 가능. 30일이 모이면 그달 이름을 출력한다.
사용: python3 tools/collect_incoming.py  → 처리할 달을 한 줄씩 출력 (이미 m/ 에 있는 달은 건너뜀)"""
import json,glob,os,re,sys
ready=[]
have=set(json.load(open('m/months.json'))['months']) if os.path.exists('m/months.json') else set()
for d in sorted(glob.glob('incoming/[0-9][0-9][0-9][0-9]-[0-9][0-9]')):
    month=os.path.basename(d)
    if month in have or os.path.exists(f'm/{month}/data.json'):continue
    days=[]
    for f in sorted(glob.glob(d+'/*.json')):
        try:
            raw=open(f,encoding='utf-8-sig').read()
            # ChatGPT가 붙이는 ``` 표시나 앞뒤 설명 문장을 걷어 냄
            raw=re.sub(r'```(json)?','',raw)
            s=min([i for i in (raw.find('{'),raw.find('[')) if i>=0] or [0]);e=max(raw.rfind('}'),raw.rfind(']'))+1
            x=json.loads(raw[s:e])
        except Exception as e:
            print(f'::error::{f} JSON 형식 오류: {e}',file=sys.stderr);continue
        days+= x['days'] if isinstance(x,dict) else x
    if len(days)<30:
        print(f'{month}: 아직 {len(days)}일치만 있음 (30일 필요)',file=sys.stderr);continue
    os.makedirs(f'build/{month}',exist_ok=True)
    json.dump({'month':month,'days':days[:30]},open(f'build/{month}/data.json','w'),ensure_ascii=False)
    ready.append(month)
print('\n'.join(ready))
