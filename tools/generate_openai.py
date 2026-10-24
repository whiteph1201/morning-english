"""완전 자동 방식: OpenAI API로 다음 달 30일치를 만들어 build/YYYY-MM/data.json 에 저장하고 달 이름을 출력.
환경 변수: OPENAI_API_KEY (필수), OPENAI_MODEL (선택, 기본 gpt-4.1), TARGET_MONTH (선택, 예: 2026-12)"""
import os,json,sys,datetime,urllib.request,time
KEY=os.environ['OPENAI_API_KEY'];MODEL=os.environ.get('OPENAI_MODEL') or 'gpt-4.1'
def target():
    t=os.environ.get('TARGET_MONTH')
    if t:return t
    now=datetime.datetime.utcnow()+datetime.timedelta(hours=9)
    y,m=now.year,now.month+1
    if m==13:y,m=y+1,1
    return f'{y}-{m:02d}'
M=target()
if M in json.load(open('m/months.json'))['months']:print(f'{M} 이미 있음',file=sys.stderr);sys.exit(0)
rules=open('prompts/rules.md',encoding='utf-8').read()
hist=json.load(open('m/history.json',encoding='utf-8'))
used_k=sorted({t for v in hist.values() for t in v['kids']});used_a=sorted({t for v in hist.values() for t in v['adult']})
latest=sorted(json.load(open('m/months.json'))['months'])[-1]
example=json.load(open(f'm/{latest}/data.json',encoding='utf-8'))['days'][0]
def chat(msg):
    body=json.dumps({'model':MODEL,'response_format':{'type':'json_object'},'temperature':0.8,
      'messages':[{'role':'system','content':'You write content for a Korean family English-learning page. Output JSON only.'},{'role':'user','content':msg}]}).encode()
    for a in range(4):
        try:
            req=urllib.request.Request((os.environ.get('OPENAI_BASE_URL') or 'https://api.openai.com/v1').rstrip('/')+'/chat/completions',data=body,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
            r=json.load(urllib.request.urlopen(req,timeout=300));return json.loads(r['choices'][0]['message']['content'])
        except Exception as e:
            print('retry',a,e,file=sys.stderr);time.sleep(10*(a+1))
    raise SystemExit('OpenAI 호출 실패')
SPEC={'g3':(3,3,2),'g6':(5,3,6),'pa':(5,5,6)}
def ok(d):
    try:
        if not d['theme'] or not d['sub']:return False
        for g,(nw,ne,nd) in SPEC.items():
            p=d[g]
            if len(p['w'])!=nw or any(len(w)!=7 for w in p['w']):return False
            if len(p['e'])!=ne or any(len(e)!=3 for e in p['e']):return False
            if len(p['d'])!=nd or any(len(e)!=2 for e in p['d']):return False
        a=d['ad'];return bool(a['t'] and a['s']) and len(a['k'])==5 and all(len(e)==3 for e in a['k']) and len(a['d'])==14 and all(len(e)==2 for e in a['d'])
    except Exception:return False
plan=chat(f'''{rules}

지난 어린이 주제(겹치지 말 것): {used_k}
지난 성인 상황(겹치지 말 것): {used_a}
30일치 계획을 만들어. 형식: {{"plan":[{{"theme":"...","sub":"...","ad_t":"...","ad_s":"..."}}, ... 30개]}}''')['plan'][:30]
days=[]
for s in range(0,30,5):
    part=plan[s:s+5]
    for a in range(3):
        r=chat(f'''{rules}

예시 하루치(형식 참고용, 내용은 따라 하지 말 것):
{json.dumps(example,ensure_ascii=False)}

아래 계획대로 {len(part)}일치를 만들어. 각 날의 theme, sub, ad.t, ad.s 는 계획 값을 그대로 쓴다.
계획: {json.dumps(part,ensure_ascii=False)}
형식: {{"days":[ ... {len(part)}개 ... ]}}''')
        got=r.get('days',[])
        if len(got)==len(part) and all(ok(d) for d in got):days+=got;break
        print('형식 불일치, 다시 시도',s,a,file=sys.stderr)
    else:raise SystemExit(f'{s+1}일차부터 만들기 실패')
os.makedirs(f'build/{M}',exist_ok=True)
json.dump({'month':M,'days':days},open(f'build/{M}/data.json','w'),ensure_ascii=False)
print(M)
