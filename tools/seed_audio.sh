#!/usr/bin/env bash
# 처음 설정용: seed/m/ 의 달 중 음성이 없는 달의 원어민 음성을 만든다
set -euo pipefail
KK="${KOKORO_DIR:-/tmp/kk}"; mkdir -p "$KK"
[ -f "$KK/model.onnx" ] || curl -sSL -o "$KK/model.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f "$KK/voices.bin" ] || curl -sSL -o "$KK/voices.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
P=$(nproc); [ "$P" -gt 6 ] && P=6
for d in seed/m/*/; do
  d=${d%/}; [ -f "$d/data.json" ] || continue
  if [ -f "$d/d01.mp3" ] && [ -f "$d/idx.json" ]; then echo "$d 음성 있음"; continue; fi
  echo "== $d 음성 만들기 =="
  step=$(( (30 + P - 1) / P )); pids=()
  for ((i=0;i<P;i++)); do
    lo=$(( i*step + 1 )); hi=$(( (i+1)*step )); [ $hi -gt 30 ] && hi=30; [ $lo -gt 30 ] && break
    python3 tools/make_audio.py "$d/data.json" "$d" $lo $hi & pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p"; done
  python3 tools/merge_idx.py "$d"
done
