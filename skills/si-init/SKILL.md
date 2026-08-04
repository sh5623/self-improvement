---
name: si-init
description: >-
  프로젝트에 자가개선 데이터 파일(규약 changelog·라우팅 표)이 없을 때 최초 1회 부트스트랩. "자가개선
  셋업"·"si-init" 요청 시, 또는 si-improve/si-archive/convention-smith 가 데이터 파일을 못 찾았을 때
  사용. **플러그인 업데이트 직후에도 재실행**한다 — 데이터 파일의 버전 스탬프를 대조해 옛 템플릿 문구를
  보수한다(프로젝트 데이터는 불변). 재실행은 안전(멱등) — 기존 시스템 감지 시 덮어쓰지 않고 등록·보수만 한다.
---

# si-init — 프로젝트 부트스트랩 (멱등)

플러그인은 **도구**, 프로젝트에는 **데이터 파일 1개**(`docs/conventions/CHANGELOG.md`)와 상시 로드 문서의 3줄 포인터만 남긴다. FE/BE/스크립트/문서 프로젝트 무관 — 탐지가 지형을 읽고, 표가 그 지형을 기록한다.

## 1. 기존 시스템 감지 — 덮어쓰기 금지

```bash
ls docs/conventions/CHANGELOG.md 2>/dev/null
grep -ril "CONVENTIONS-CHANGELOG\|자가개선\|self-improvement" --include="*.md" docs .claude . 2>/dev/null | grep -v node_modules | head
```

**후보 판별 — 위 grep 은 데이터 파일이 아닌 것까지 잡는다.** 실측: `self-improvement` 라는 단어만 든 README.md 가 첫 후보로 걸렸다. 각 후보에 대해:

```bash
grep -n "^#\+ .*색인\|^#\+ .*라우팅\|si-plugin:\|^### 20[0-9][0-9]-" <후보 파일>   # 표·스탬프·날짜 로그 유무
```

- **이 플러그인 형식의 데이터 파일**: §색인/§라우팅 표 또는 `<!-- si-plugin: v` 스탬프 보유.
- **다른 형태의 기존 시스템**: 위 표는 없지만 **규약 기록이 실제로 담긴 파일**(날짜별 로그 블록·조항 목록). 표·예산·이관표가 없다는 것은 제외 사유가 아니다 — 정본으로 인정하고 등록하되 없는 요소는 아래 셋째 불릿대로 제안만 한다.
- **후보 아님**: 시스템을 **설명만** 하는 문서(README·플러그인 소개 — 기록 0건) · 이름·경로에 `archive`/`ARCHIVE` 가 든 파일(과거 로그 위에 새 블록이 쌓인다).
판별 결과에 따른 처치:

- **이 플러그인 형식의 데이터 파일이 이미 있으면**: §라우팅 표가 현재 지형과 맞는지만 검증·보수(층별 위치 실재 확인)하고 종료.
- **다른 형태의 기존 시스템이면**(자체 규약 changelog·프로토콜 문서 — 예: `docs/**/CONVENTIONS-CHANGELOG.md`): **새로 만들지 않는다. 기존 시스템이 정본이다.** §4 의 배선을 그 시스템의 **실제 경로로 치환해 실행**한다 — 보고로 끝내지 않는다(보고는 세션과 함께 사라지고, 다음 세션은 같은 폴백 grep 을 다시 돌려 README·아카이브를 오선택한다). 그 시스템에 없는 요소(라우팅 표·예산·로테이션·이관표)가 있으면 **제안으로만** 알린다(강제 이식 금지).
- **남은 후보가 0개면 기존 시스템은 없다** — 신설(§2)로 간다. 여기서 오인 등록으로 끝내면 데이터 파일이 생성되지 않고, 다음 세션의 si-improve §0 은 같은 README 를 다시 집는다.

**버전 드리프트 보수 — 재실행의 주 용도.** 플러그인이 업데이트되면 스킬·에이전트(도구)만 새것으로 바뀌고 프로젝트 데이터 파일은 **옛 템플릿 문구 그대로 남는다**(도구/데이터 분리의 대가). 데이터 파일 상단의 `<!-- si-plugin: vX.Y.Z -->` 스탬프를 현재 플러그인 버전(`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`)과 대조한다:

- **스탬프가 현재 버전보다 낮으면**: 템플릿(`templates/CHANGELOG.template.md`)의 **고정 텍스트**(형식 줄·§로그 헤딩·예산·로테이션 문구)만 현재 템플릿과 대조해 갱신하고 스탬프를 올린다. **프로젝트 데이터는 불변** — 라우팅 표의 값·§색인·§로그·§이관표는 건드리지 않는다.
- **스탬프가 없으면**(기존 시스템 등록분): 자동 갱신하지 않는다 — 그 문서는 프로젝트 소유다. 현행 절차와 **모순되는 선언만** 지목해 보고한다(실측: 헤더가 "개선 1건 = 1블록"인데 절차는 "작업 단위 1개 = 1블록" — 다음 세션이 헤더를 따라 로그 본문을 빠뜨린다).
- **스탬프가 현재 버전과 같으면**: 보수 없음.

## 2. 문서 지형 탐지 — 라우팅 표의 재료

| 층 | 찾는 것 | 예시 명령 (있는 것만 잡히면 된다 — 빈 결과도 유효) |
|---|---|---|
| 도구 설정 | linter·formatter·type check·테스트·CI | `ls biome.json eslint.config.* .eslintrc* .prettierrc* tsconfig.json pyproject.toml ruff.toml setup.cfg build.gradle* pom.xml Makefile 2>/dev/null; ls .github/workflows 2>/dev/null` + 패키지 매니저 스크립트(`package.json` scripts 등) |
| 경로 스코프 룰 | `paths:` frontmatter 룰 파일 | `ls .claude/rules/ 2>/dev/null` |
| 태스크·도메인 문서 | 플레이북·스펙 디렉토리 | `ls docs/ 2>/dev/null` |
| 상시 로드 문서 | AGENTS.md / CLAUDE.md (+import 관계) | `ls AGENTS.md CLAUDE.md .claude/CLAUDE.md 2>/dev/null; grep -n '@AGENTS\.md' CLAUDE.md 2>/dev/null` (import 유무가 §4 의 분기를 정한다) |

탐지가 빈 층은 실패가 아니다 — 표에 `없음(필요 시 신설)` 으로 적는다. 그 층이 처음 필요해지는 자가개선 때 신설된다.

## 3. 데이터 파일 생성

이 스킬 폴더의 `templates/CHANGELOG.template.md` 를 `docs/conventions/CHANGELOG.md` 로 복사하고 치환한다:

- `{{DATE}}` → 오늘(YYYY-MM-DD) · `{{VERSION}}` → 현재 플러그인 버전(`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` 의 `version`) · `{{TOOLS}}`/`{{RULES}}`/`{{DOCS}}`/`{{ALWAYS}}` → §2 탐지 결과(**이 프로젝트의 실제 파일명**으로) · `{{ANCHOR_DOC}}` → §4 에서 배선한 문서명.
- 예산 기본값(상시 로드 ≤200줄 · 경로 룰 ≤150줄 · 로그 본문 ≤15블록)은 템플릿에 있다 — 조정은 프로젝트 몫이나 "무제한" 금지.

## 4. 상시 로드 문서 배선 — 범 AI 포인터 3줄

**어느 파일에**: `AGENTS.md` 있으면 AGENTS.md(범 AI 도구 표준 — 이 플러그인 없는 도구·동료도 본다) → 없고 `CLAUDE.md` 만 있으면 CLAUDE.md → 둘 다 없으면 AGENTS.md 신설.

**AGENTS.md 에 썼으면 같은 단계에서 CLAUDE.md 의 import 까지 배선한다.** Claude Code 는 `CLAUDE.md` 만 읽고 `AGENTS.md` 는 읽지 않는다(공식 문서: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`" — https://code.claude.com/docs/en/memory). import 가 없으면 AGENTS.md 에 쓴 포인터는 Claude 세션에 **로드되지 않는다** — 배선했다는 보고만 남고 다음 세션은 폴백 grep 으로 돌아간다.

```bash
ls -l CLAUDE.md 2>/dev/null; grep -n '@AGENTS\.md' CLAUDE.md 2>/dev/null
```

- **유효한 import 로 세는 것**: 백틱·코드펜스 **밖의** `@AGENTS.md` 한 줄. Claude Code 의 import 파서는 코드 스팬·펜스를 건너뛰므로 `` `@AGENTS.md` `` 처럼 감싼 언급은 import 가 아니다(위 grep 은 그런 언급도 잡는다 — 걸린 줄을 눈으로 판정한다).
- `CLAUDE.md` 가 없으면: `@AGENTS.md` 한 줄만 담은 스텁으로 생성.
- 있는데 유효한 import 가 없으면: 파일 **맨 위**에 `@AGENTS.md` 를 백틱 없이 한 줄 가산한다(기존 내용 불변).
- 이미 유효한 import 가 있거나 `CLAUDE.md` 가 `AGENTS.md` 의 심볼릭 링크면(`ls -l` 로 확인) skip — 멱등.
- 검증: 위 grep 이 백틱 밖 `@AGENTS.md` 를 1줄 이상 보여준다. `/context` 의 **Memory files** 에 CLAUDE.md 가 뜨는지는 다음 세션에서 확인된다.

이미 자가개선 절이 있으면 skip(멱등). 넣는 내용은 아래 3줄 — 전체 독트린을 중복하지 않는다(플러그인 사용자는 SessionStart 훅이 이미 주입한다. 이 3줄은 플러그인 없는 도구·사람을 위한 앵커다):

```markdown
## 자가개선
규약·문서가 없거나 틀려서 물리면 그 자리만 고치지 말고 규약 자체를 고친다(일반성+증거 충족 시, 같은 작업 단위 안에서).
절차·라우팅·기록: `docs/conventions/CHANGELOG.md` 헤더. 작업 보고에 "자가개선: N건/해당 없음"을 명시한다.
```

기존 시스템 등록(§1)으로 왔으면 위 3줄의 경로를 그 시스템의 **실제 파일**로 치환한다 — 데이터 파일·프로토콜 문서·아카이브가 갈라져 있으면 각각 명시한다. 다음 세션의 si-improve §0 은 이 선언을 **가장 먼저** 읽으므로, 이 배선이 기존 시스템을 전달하는 유일한 경로다.

## 5. 보고

- 포인터 배선처 + **Claude 로드 경로**: `<파일>` + `CLAUDE.md import: 있음 / 추가 / 해당 없음(포인터가 CLAUDE.md 자체)`. AGENTS.md 에만 썼고 import 가 없는 상태로 종료하면 배선 실패다.
- 결과: `생성` / `기존 등록`(경로) / `보수 N건`(버전 드리프트 보수는 `vX.Y.Z → vA.B.C, 문구 N줄`로 적는다) / `모순 N건`(스탬프 없는 기존 시스템 — 제안만).
- 라우팅 표 전문을 보여준다(사용자가 탐지 오류를 즉시 교정할 수 있게).
- 다음 액션 한 줄: "물리면 `/self-improvement:si-improve`".
