# 아침 영어 한 장 (Vercel + Supabase)

초3 · 초6 · 부모님 · 성인 탭으로 나뉜 매일 아침 영어 홈페이지입니다.
Claude 계정 없이도 **매달 새 대화 내용과 원어민 음성이 자동으로** 만들어집니다.

## 어떻게 돌아가나요

```
[GitHub Actions] 매달 22일 자동 실행 (무료)
   ① OpenAI로 다음 달 30일치 대화·단어·표현 작성   ← 유일한 비용 (월 몇백~몇천 원)
   ② Kokoro로 원어민 음성 만들기 (여성·남성 목소리, 무료)
   ③ Supabase 저장소에 올리기
            ↓
[Supabase Storage] 달별 내용(data.json)과 음성(mp3) 보관 (무료)
            ↓
[Vercel] 홈페이지. 오늘 날짜에 맞는 내용과 음성을 Supabase에서 불러와 보여 줌 (무료)
```

- 그달 내용이 있으면 그달을, 혹시 만들기가 실패하면 있는 달들을 돌려 가며 보여 줍니다. 빈 화면은 나오지 않습니다.
- 12개월이 넘은 달은 자동으로 지웁니다(용량 관리, 한 달 약 23MB).

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `index.html`, `config.js`, `vercel.json` | 홈페이지 (Vercel에 배포되는 것은 이 세 파일뿐) |
| `seed/m/` | 처음 올릴 10월·11월 콘텐츠와 음성 |
| `tools/` | 내용 생성(OpenAI), 형식 검사, 음성 만들기, Supabase 올리기 |
| `prompts/` | 형식 기준(rules.md)과 ChatGPT 반자동용 요청문 |
| `incoming/` | (선택) ChatGPT로 직접 만든 내용을 올리는 곳 |
| `.github/workflows/` | 자동 작업 3개: 처음 설정, 매달 만들기, Supabase 깨워 두기 |

---

## 처음 설정 (한 번만, 30분 정도)

준비물: GitHub, Supabase, Vercel, OpenAI 계정 (Vercel과 Supabase는 GitHub 계정으로 가입하면 편합니다)

### 1. GitHub에 올리기
1. github.com → 오른쪽 위 `+` → `New repository` → 이름 `morning-english` → `Create repository`
2. `uploading an existing file` → 압축 푼 폴더 안 내용을 전부 끌어다 놓기 → `Commit changes`
   - 한 번에 100개까지라 안 되면 `seed` 폴더와 나머지를 나눠 올리세요.
   - `.github` 폴더가 안 보이면(숨김 폴더): `Add file` → `Create new file` → 이름에
     `.github/workflows/monthly.yml` 입력 → 같은 파일 내용 붙여 넣기. `setup.yml`, `keepalive.yml`도 같은 방법.

### 2. Supabase 프로젝트 만들기
1. supabase.com → `New project` → 이름 아무거나, 비밀번호 설정, 지역 `Northeast Asia (Seoul)` → 만들기
2. 왼쪽 `Project Settings` → `API` (또는 `API Keys`) 에서 두 가지를 복사해 둡니다.
   - **Project URL**: `https://abcdefgh.supabase.co` 같은 주소
   - **secret 키** (`sb_secret_...`) 또는 **service_role 키**. 이 키는 비밀번호와 같으니 남에게 보이지 마세요.

### 3. OpenAI API 키 만들기
1. platform.openai.com → 로그인 → `Billing` 에서 결제 수단 등록 (소액 충전, 예: $5)
2. `API keys` → `Create new secret key` → 키 복사

### 4. GitHub에 비밀 값 넣기
저장소 `Settings` → `Secrets and variables` → `Actions` → `New repository secret` 으로 3개 추가:

| Name | 값 |
|---|---|
| `SUPABASE_URL` | 2번의 Project URL |
| `SUPABASE_SECRET_KEY` | 2번의 secret(또는 service_role) 키 |
| `OPENAI_API_KEY` | 3번의 키 |

(선택) 같은 화면 `Variables` 탭: `OPENAI_MODEL`(쓸 모델 이름, 비우면 gpt-4.1), `KEEP_MONTHS`(보관 개월, 기본 12)

### 5. Supabase에 처음 콘텐츠 올리기
저장소 `Actions` 탭 → (처음이면 `I understand... enable` 버튼) → `1. 처음 설정 (Supabase에 올리기)` → `Run workflow`.
1~2분 뒤 초록 체크가 뜨면 성공입니다.

### 6. 홈페이지 주소 연결
1. 저장소에서 `config.js` 를 열고 연필 아이콘으로 수정:
   `https://YOUR-PROJECT-ID.supabase.co` 부분을 **내 Project URL**로 바꿔 저장(Commit).
   결과 예: `window.ENGLISH_BASE = "https://abcdefgh.supabase.co/storage/v1/object/public/english/";`
2. vercel.com → `Add New...` → `Project` → GitHub의 `morning-english` 선택 → `Import`
   - Framework Preset: `Other`, Build 설정은 그대로 → `Deploy`
3. 1분 뒤 `morning-english-xxxx.vercel.app` 주소가 생깁니다. `Settings` → `Domains` 에서 이름을 바꾸거나 내 도메인을 연결할 수 있습니다.

### 7. 바로 시험해 보기 (선택)
`Actions` → `2. 다음 달 콘텐츠 만들기` → `Run workflow` → 달 칸에 아직 없는 달(예: `2026-12`) 입력 → 실행.
30~60분 뒤 초록 체크가 뜨면 홈페이지에서 `내일` 버튼으로 그달 1일로 넘겨 확인합니다.

---

## 그 뒤로는

아무것도 안 하셔도 됩니다. 매달 22일에 다음 달 내용과 음성이 자동으로 올라갑니다.

- 결과 확인: GitHub `Actions` 탭 (초록 체크 = 성공). GitHub 알림 메일로 실패 소식이 옵니다.
- 실패했을 때: 빨간 X → 오류 내용 확인. 대부분 OpenAI 결제 잔액 부족이나 키 오류입니다. 고친 뒤 `Run workflow` 로 다시 실행.
- 비용 확인: platform.openai.com 의 `Usage`.

## (선택) OpenAI 없이 ChatGPT로 직접 만들기
`prompts/gpt_prompt.md` 순서대로 ChatGPT에 요청하고, 결과를 `incoming/YYYY-MM/part1.json`~`part3.json` 으로 저장(Commit)하면
같은 작업이 자동으로 돌아 음성을 만들고 Supabase에 올립니다. ChatGPT가 붙인 ``` 표시나 설명 문장은 자동으로 걸러집니다.

## 알아 둘 점
- Supabase 무료 프로젝트는 오래 사용이 없으면 잠들 수 있어, `3. Supabase 깨워 두기` 작업이 매주 자동으로 깨워 둡니다.
- 원어민 음성은 Kokoro(무료 공개 음성 모델)로 GitHub 서버에서 만듭니다.
- 음성을 못 불러오면 페이지가 기기 음성으로 대신 읽습니다.
- 인쇄: 브라우저에서 Ctrl+P (맥은 ⌘+P). 보고 있는 탭만 인쇄됩니다.
- 탭 바로 열기: 주소 뒤에 `#g3`(초3), `#g6`(초6), `#pa`(부모님), `#ad`(성인).
