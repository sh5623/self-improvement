---
name: si-init
description: >-
  프로젝트에 자가개선 데이터 파일(규약 changelog·라우팅 표)이 없을 때 최초 1회 부트스트랩. "자가개선
  셋업"·"si-init" 요청 시, 또는 si-improve/si-archive/convention-smith 가 데이터 파일을 못 찾았을 때
  사용. 재실행은 안전(멱등) — 기존 시스템 감지 시 덮어쓰지 않고 등록·보수만 한다.
---

# si-init — 프로젝트 부트스트랩 (멱등)

플러그인은 **도구**, 프로젝트에는 **데이터 파일 1개**(`docs/conventions/CHANGELOG.md`)와 상시 로드 문서의 3줄 포인터만 남긴다. FE/BE/스크립트/문서 프로젝트 무관 — 탐지가 지형을 읽고, 표가 그 지형을 기록한다.

## 1. 기존 시스템 감지 — 덮어쓰기 금지

```bash
ls docs/conventions/CHANGELOG.md 2>/dev/null
grep -ril "CONVENTIONS-CHANGELOG\|자가개선\|self-improvement" --include="*.md" docs .claude . 2>/dev/null | grep -v node_modules | head
```

- **이 플러그인 형식의 데이터 파일이 이미 있으면**: §라우팅 표가 현재 지형과 맞는지만 검증·보수(층별 위치 실재 확인)하고 종료.
- **다른 형태의 유사 시스템이 있으면**(자체 규약 changelog·프로토콜 문서 — 예: `docs/**/CONVENTIONS-CHANGELOG.md`): **새로 만들지 않는다. 기존 시스템이 정본이다.** 그 위치를 보고하고, 그 시스템에 없는 요소(라우팅 표·예산·로테이션·이관표)가 있으면 **제안으로만** 알린다(강제 이식 금지).
- 둘 다 없으면 §2 로.

## 2. 문서 지형 탐지 — 라우팅 표의 재료

| 층 | 찾는 것 | 예시 명령 (있는 것만 잡히면 된다 — 빈 결과도 유효) |
|---|---|---|
| 도구 설정 | linter·formatter·type check·테스트·CI | `ls biome.json eslint.config.* .eslintrc* .prettierrc* tsconfig.json pyproject.toml ruff.toml setup.cfg build.gradle* pom.xml Makefile 2>/dev/null; ls .github/workflows 2>/dev/null` + 패키지 매니저 스크립트(`package.json` scripts 등) |
| 경로 스코프 룰 | `paths:` frontmatter 룰 파일 | `ls .claude/rules/ 2>/dev/null` |
| 태스크·도메인 문서 | 플레이북·스펙 디렉토리 | `ls docs/ 2>/dev/null` |
| 상시 로드 문서 | AGENTS.md / CLAUDE.md (+import 관계) | `ls AGENTS.md CLAUDE.md 2>/dev/null; head -5 CLAUDE.md 2>/dev/null` |

탐지가 빈 층은 실패가 아니다 — 표에 `없음(필요 시 신설)` 으로 적는다. 그 층이 처음 필요해지는 자가개선 때 신설된다.

## 3. 데이터 파일 생성

이 스킬 폴더의 `templates/CHANGELOG.template.md` 를 `docs/conventions/CHANGELOG.md` 로 복사하고 치환한다:

- `{{DATE}}` → 오늘(YYYY-MM-DD) · `{{TOOLS}}`/`{{RULES}}`/`{{DOCS}}`/`{{ALWAYS}}` → §2 탐지 결과(**이 프로젝트의 실제 파일명**으로) · `{{ANCHOR_DOC}}` → §4 에서 배선한 문서명.
- 예산 기본값(상시 로드 ≤200줄 · 경로 룰 ≤150줄 · 로그 본문 ≤15블록)은 템플릿에 있다 — 조정은 프로젝트 몫이나 "무제한" 금지.

## 4. 상시 로드 문서 배선 — 범 AI 포인터 3줄

**어느 파일에**: `AGENTS.md` 있으면 AGENTS.md(범 AI 도구 표준 — 이 플러그인 없는 도구·동료도 본다) → 없고 `CLAUDE.md` 만 있으면 CLAUDE.md → **둘 다 없으면 AGENTS.md 신설 + CLAUDE.md 는 `@AGENTS.md` 한 줄 스텁**으로 생성.

이미 자가개선 절이 있으면 skip(멱등). 넣는 내용은 아래 3줄 — 전체 독트린을 중복하지 않는다(플러그인 사용자는 SessionStart 훅이 이미 주입한다. 이 3줄은 플러그인 없는 도구·사람을 위한 앵커다):

```markdown
## 자가개선
규약·문서가 없거나 틀려서 물리면 그 자리만 고치지 말고 규약 자체를 고친다(일반성+증거 충족 시, 같은 작업 단위 안에서).
절차·라우팅·기록: `docs/conventions/CHANGELOG.md` 헤더. 작업 보고에 "자가개선: N건/해당 없음"을 명시한다.
```

## 5. 보고

- 결과: `생성` / `기존 등록`(경로) / `보수 N건`.
- 라우팅 표 전문을 보여준다(사용자가 탐지 오류를 즉시 교정할 수 있게).
- 다음 액션 한 줄: "물리면 `/self-improvement:si-improve`".
