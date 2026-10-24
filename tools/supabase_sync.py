"""Supabase Storage 동기화.
환경 변수: SUPABASE_URL (예: https://abcd.supabase.co), SUPABASE_SECRET_KEY (service_role 또는 sb_secret_ 키), BUCKET(기본 english)
사용:
  python3 tools/supabase_sync.py init         버킷 만들고 seed/m 의 콘텐츠를 올림 (처음 한 번)
  python3 tools/supabase_sync.py pull         months.json, history.json, 가장 최근 달 data.json 을 ./m 으로 받음
  python3 tools/supabase_sync.py push YYYY-MM m/YYYY-MM 와 목록 파일을 올리고, build/removed.txt 에 적힌 달은 지움
  python3 tools/supabase_sync.py ping         일주일 넘게 안 쓰면 잠드는 무료 프로젝트를 깨워 둠
"""
import os,sys,json,glob,urllib.request,urllib.error,mimetypes
URL=os.environ['SUPABASE_URL'].rstrip('/');KEY=os.environ['SUPABASE_SECRET_KEY'];B=os.environ.get('BUCKET') or 'english'
def hdr(extra=None):
    h={'apikey':KEY}
    if not KEY.startswith('sb_'):h['Authorization']='Bearer '+KEY
    h.update(extra or {});return h
def req(method,path,data=None,headers=None,ok404=False):
    r=urllib.request.Request(URL+path,data=data,method=method,headers=hdr(headers))
    try:
        with urllib.request.urlopen(r,timeout=120) as f:return f.status,f.read()
    except urllib.error.HTTPError as e:
        body=e.read()
        if ok404 and e.code in (400,404,409):return e.code,body
        raise SystemExit(f'Supabase 오류 {e.code} {method} {path}: {body[:300]!r}')
def ctype(p):
    return 'application/json' if p.endswith('.json') else ('audio/mpeg' if p.endswith('.mp3') else (mimetypes.guess_type(p)[0] or 'application/octet-stream'))
def upload(remote,local):
    cache='60' if remote.endswith(('months.json','history.json')) else '86400'
    req('POST',f'/storage/v1/object/{B}/{remote}',open(local,'rb').read(),{'Content-Type':ctype(remote),'x-upsert':'true','cache-control':f'max-age={cache}'})
    print('올림',remote,flush=True)
def download(remote,local):
    s,b=req('GET',f'/storage/v1/object/{B}/{remote}',ok404=True)
    if s!=200:return False
    os.makedirs(os.path.dirname(local) or '.',exist_ok=True);open(local,'wb').write(b);return True
def delete_month(m):
    s,b=req('POST',f'/storage/v1/object/list/{B}',json.dumps({'prefix':f'm/{m}','limit':1000}).encode(),{'Content-Type':'application/json'})
    names=[f'm/{m}/'+x['name'] for x in json.loads(b) if x.get('name')]
    if names:req('DELETE',f'/storage/v1/object/{B}',json.dumps({'prefixes':names}).encode(),{'Content-Type':'application/json'})
    print('지움',m,len(names),'개')
cmd=sys.argv[1]
if cmd=='init':
    s,b=req('POST','/storage/v1/bucket',json.dumps({'id':B,'name':B,'public':True}).encode(),{'Content-Type':'application/json'},ok404=True)
    print('버킷',B,'만듦' if s==200 else '이미 있음')
    s,_=req('GET',f'/storage/v1/object/{B}/m/months.json',ok404=True)
    if s==200:raise SystemExit('이미 설정되어 있어 건너뜁니다 (기존 콘텐츠 보호).')
    for f in sorted(glob.glob('seed/m/**/*',recursive=True)):
        if os.path.isfile(f):upload(f[len('seed/'):],f)
elif cmd=='pull':
    os.makedirs('m',exist_ok=True)
    if not download('m/months.json','m/months.json'):raise SystemExit('months.json 이 없습니다. 먼저 "처음 설정" 작업을 실행하세요.')
    if not download('m/history.json','m/history.json'):json.dump({},open('m/history.json','w'))
    ms=sorted(json.load(open('m/months.json'))['months'])
    download(f'm/{ms[-1]}/data.json',f'm/{ms[-1]}/data.json');print('받음',ms)
elif cmd=='push':
    m=sys.argv[2]
    for f in sorted(glob.glob(f'm/{m}/*')):upload(f,f)
    upload('m/history.json','m/history.json');upload('m/months.json','m/months.json')
    if os.path.exists('build/removed.txt'):
        for old in open('build/removed.txt').read().split():delete_month(old)
elif cmd=='ping':
    req('GET','/rest/v1/',ok404=True)
    req('POST',f'/storage/v1/object/list/{B}',json.dumps({'prefix':'m','limit':1}).encode(),{'Content-Type':'application/json'},ok404=True)
    print('ok')
