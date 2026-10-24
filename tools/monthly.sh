#!/usr/bin/env bash
# 월간 작업: Supabase에서 목록을 받고 → (ChatGPT 결과 또는 OpenAI 자동 생성) → 원어민 음성 → Supabase에 올림
set -euo pipefail
python3 tools/supabase_sync.py pull
for M in $(python3 tools/collect_incoming.py); do
  echo "== incoming 폴더의 $M 반영 =="
  bash tools/build_month.sh "$M"
  python3 tools/supabase_sync.py push "$M"
done
if [ "${MODE:-auto}" = "incoming" ]; then exit 0; fi
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY 가 없어 자동 생성은 건너뜁니다 (ChatGPT 반자동 방식 사용 가능)."; exit 0
fi
M=$(python3 tools/generate_openai.py)
if [ -n "$M" ]; then
  echo "== $M 자동 생성분 반영 =="
  bash tools/build_month.sh "$M"
  python3 tools/supabase_sync.py push "$M"
fi
