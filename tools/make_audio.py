"""월별 음성 만들기: python3 make_audio.py <data.json> <출력폴더> [시작일 끝일]
- Kokoro TTS 모델 필요: /tmp/kk/model.onnx, /tmp/kk/voices.bin
  curl -L -o /tmp/kk/model.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
  curl -L -o /tmp/kk/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
  pip install kokoro-onnx soundfile --break-system-packages
- 날짜별로 dNN.mp3 와 idxNN.json 을 만든다. 모두 끝나면 merge_idx.py 로 idx.json 하나로 합친다.
- 대화 줄: 짝수번째(0,2,..)=af_heart(여성), 홀수번째=am_michael(남성). 나머지는 af_heart.
"""
import sys,json,subprocess,numpy as np,soundfile as sf,os
import onnxruntime as ort
KK=os.environ.get('KOKORO_DIR','/tmp/kk')
from kokoro_onnx import Kokoro
data=json.load(open(sys.argv[1]));out=sys.argv[2];os.makedirs(out,exist_ok=True)
lo=int(sys.argv[3]) if len(sys.argv)>3 else 1;hi=int(sys.argv[4]) if len(sys.argv)>4 else len(data['days'])
so=ort.SessionOptions();so.intra_op_num_threads=1
k=Kokoro.from_session(ort.InferenceSession(KK+'/model.onnx',so,providers=['CPUExecutionProvider']),KK+'/voices.bin')
def texts(day):
    m={}
    def add(t,v='af_heart'):
        if t and t not in m:m[t]=v
    for g in ('g3','g6','pa'):
        p=day[g]
        for w in p['w']:add(w[1]);add(w[4])
        for e in p['e']:add(e[0])
        for n,x in enumerate(p['d']):add(x[0],'am_michael' if n%2 else 'af_heart')
    for x in day['ad']['k']:add(x[0])
    for n,x in enumerate(day['ad']['d']):add(x[0],'am_michael' if n%2 else 'af_heart')
    return m
sr=24000;gap=np.zeros(int(sr*0.3),dtype=np.float32)
for n in range(lo,hi+1):
    parts=[];idx={};pos=0.0
    for t,v in texts(data['days'][n-1]).items():
        a,_=k.create(t,voice=v,speed=0.92,lang='en-us');a=np.concatenate([a.astype(np.float32),gap])
        idx[t]=[round(pos,3),round(len(a)/sr-0.3,3)];pos+=len(a)/sr;parts.append(a)
    sf.write(f'{out}/_d{n}.wav',np.concatenate(parts),sr)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'{out}/_d{n}.wav','-ac','1','-b:a','40k','-codec:a','libmp3lame',f'{out}/d{n:02d}.mp3'],check=True)
    os.remove(f'{out}/_d{n}.wav')
    json.dump(idx,open(f'{out}/idx{n:02d}.json','w'),ensure_ascii=False)
    print('done',n,flush=True)
