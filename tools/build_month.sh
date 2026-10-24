#!/usr/bin/env bash
# 사용: bash tools/build_month.sh YYYY-MM   (build/YYYY-MM/data.json 이 있어야 함)
set -euo pipefail
M="$1"; OUT="build/$M"
python3 tools/check.py "$OUT/data.json" | tee /tmp/check.txt
grep -qx OK /tmp/check.txt || { echo "::error::형식 검사 실패 ($M)"; exit 1; }
KK="${KOKORO_DIR:-/tmp/kk}"; mkdir -p "$KK"
[ -f "$KK/model.onnx" ] || curl -sSL -o "$KK/model.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f "$KK/voices.bin" ] || curl -sSL -o "$KK/voices.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
P=$(nproc); [ "$P" -gt 6 ] && P=6
step=$(( (30 + P - 1) / P )); pids=()
for ((i=0;i<P;i++)); do
  lo=$(( i*step + 1 )); hi=$(( (i+1)*step )); [ $hi -gt 30 ] && hi=30; [ $lo -gt 30 ] && break
  python3 tools/make_audio.py "$OUT/data.json" "$OUT" $lo $hi & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
python3 tools/merge_idx.py "$OUT"
python3 - "$OUT" <<'PY'
import json,sys
o=sys.argv[1];d=json.load(open(o+'/data.json'))['days'];idx=json.load(open(o+'/idx.json'));miss=0
for n,day in enumerate(d,1):
    k=idx.get(str(n),{});ts=[]
    for g in ('g3','g6','pa'):
        p=day[g];ts+=[w[1] for w in p['w']]+[w[4] for w in p['w']]+[e[0] for e in p['e']]+[x[0] for x in p['d']]
    ts+=[x[0] for x in day['ad']['k']]+[x[0] for x in day['ad']['d']]
    for t in ts:
        if t not in k:miss+=1;print('음성 없음',n,t)
sys.exit(1 if miss else 0)
PY
python3 tools/add_month.py "$M"
