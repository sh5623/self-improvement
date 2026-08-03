# self-improvement — 규약 자가개선 하네스

작업 중 규약·문서·절차에 물렸을 때 그 자리만 우회하지 않고 **규약 자체를 고치게 만드는** Claude Code 플러그인.
어떤 프로젝트(FE·BE·스크립트·문서)에도 설치해 쓸 수 있다 — 절차는 도메인을 모르고, 프로젝트의 문서 지형은 설치 시 탐지해서 기록한다.

> **In short (English)** — A Claude Code plugin that turns "I got bitten by a missing/wrong convention" into a fix of the convention itself, inside the same unit of work. A SessionStart hook injects an 8-line doctrine into every session; three skills run the loop (detect → classify → verify → codify → propagate → record), gate it on evidence, and keep rule docs from growing without bound (per-layer budgets, demotion, archive rotation). Docs and skills are written in Korean.

3원칙:

1. **규약은 얼어있지 않다** — 갭을 발견한 세션이, 같은 작업 단위 안에서, 스스로 고친다.
2. **증거 없으면 규약 없다** — 일반성(재발 지점 실명) + 증거(측정값·file:line) 둘 다 없으면 규약화하지 않는다.
3. **문서에는 예산이 있다** — 규약은 가장 좁은 스코프에 쓰고, 넘치면 아카이브로 이관된다(무한히 자라는 규약 문서는 아무도 안 읽는다).

## 설치

```
/plugin marketplace add sh5623/self-improvement
/plugin install self-improvement@self-improvement
/reload-plugins
```

- 설치는 기본 **user 스코프** — 한 번 설치하면 **모든 프로젝트의 모든 세션**에 적용된다.
- 특정 프로젝트에만 켜려면 `--scope project`, 끄려면 그 프로젝트 `.claude/settings.json` 의 `enabledPlugins` 에서 제외한다.
- 업데이트: `/plugin marketplace update self-improvement` → `/reload-plugins`.

## 구성

| 구성물 | 역할 |
|---|---|
| **SessionStart 훅** (`hooks/doctrine.md`) | 독트린 6조를 매 세션 컨텍스트에 주입 — "물리면 규약을 고친다 · 게이트 · 종료 자문 · 보고 의무". compact 후에도 재주입된다. |
| `/self-improvement:si-improve` | 프로토콜 본체: 감지→분류→검증→규약화→전파→기록 |
| `/self-improvement:si-init` | 프로젝트 부트스트랩(멱등): 문서 지형 탐지 → 데이터 파일 생성 → 상시 로드 문서에 포인터 3줄 |
| `/self-improvement:si-archive` | 비대·사문화 이관: 예산 측정 → 강등/병합/사문화 → 이관표 → changelog 로테이션 |
| `convention-smith` 에이전트 | 라우팅·초안이 애매할 때 위임(READ+DRAFT — 게이트 판정 + 최소 diff 초안, 적용은 호출자) |

**도구 vs 데이터 분리**: 플러그인 = 버전 관리되는 도구. 각 프로젝트에는
**데이터 파일 1개**(`docs/conventions/CHANGELOG.md` — 라우팅 표·예산·이관표·색인·로그)와 상시 로드 문서의
포인터 3줄만 남는다. 플러그인을 업데이트해도 프로젝트 데이터는 그대로다.

## 동작 모델 — 규약의 층과 이동 방향

새 규약은 **위에서부터 처음 맞는 층**에 쓴다(si-improve §4). 넘치거나 죽으면 **아래로만** 이동한다(si-archive).

| 층 | 로드/발동 | 비고 |
|---|---|---|
| 도구 설정 (lint·format·type·test·CI) | 자동 강제 | 도구가 잡을 수 있으면 문서 금지 — 문서 규약은 판단만 |
| 경로 스코프 룰 (`.claude/rules/*.md` + `paths:`) | 매칭 파일을 만질 때만 | 기본 안착지. 신규 파일 = 병렬 충돌 없음 |
| 태스크·도메인 문서 (`docs/**`) | 해당 작업 시 명시적 Read | 플레이북·스펙 |
| 상시 로드 문서 (AGENTS.md/CLAUDE.md) | 모든 세션 | **≤200줄 예산** — 모든 세션에서 참인 것만 |
| 아카이브 (`docs/conventions/archive/`) | 로드 안 됨 | 사문화 규약 + 로테이션된 로그. 삭제가 아니라 보존 |

비대 관리 장치 3개:

- **로그 로테이션**: changelog 본문 블록 15개 캡 — 기록하는 그 자리에서 검산(`grep -c '^### '`), 초과분은 아카이브로. **§색인·§이관표는 전 기간 헤드에 남는다**(중복 확인이 한 파일로 끝나는 근거).
- **이관표**: 층 이동·아카이브 1건 = 1행. 원문서에 개별 포인터를 남발하지 않는다.
- **캡은 절차에 배선**: 예산·캡을 문서 헤더에만 적지 않고, 그것을 실행할 절차 단계(si-improve §6·si-archive)에 박아 둔다 — 헤더에만 있던 캡이 방치된 실사고에서 나온 구조다.

## 빠른 시작

```
# 1) 프로젝트 최초 1회 (기존 유사 시스템이 있으면 그것을 등록하고 끝 — 덮어쓰지 않는다)
/self-improvement:si-init

# 2) 작업 중 규약에 물렸을 때 (또는 훅 독트린이 시키는 대로 세션이 스스로)
/self-improvement:si-improve  <무엇에 물렸는지 + 증거>

# 3) 규약 문서가 길어졌을 때
/self-improvement:si-archive
```

이후 모든 작업 보고에 **"자가개선: N건 + 위치"** 또는 **"자가개선: 해당 없음"** 한 줄이 붙는 것이 정상 동작 신호다.

> **주의** — 훅의 주입은 결정론적이지만, 그다음 행동은 지시 준수의 문제다(실패 시 차단하는 강제 장치가 아니다).
> 그래서 관찰 가능한 신호를 하나 박아 뒀다: 보고 끝의 `자가개선: …` 줄. 그 줄이 없으면 종료 자문을 건너뛴 것이다.

## 실증 유래

이 플러그인은 이론이 아니라 실전 프로젝트(레거시 전환 + API 연동, 규약 개선 40여 건 로그)에서 검증된 규칙의 일반화다. 대표 사고와 그로부터 나온 규칙:

| 실사고 | 일반화된 규칙 (위치) |
|---|---|
| 자가개선이 "사용자가 시키면 하는 작업"으로 방치 | 독트린 1·5조 — 자발 발동 + 보고 의무("이 줄이 없으면 자문을 건너뛴 것") |
| 캡이 헤더에만 있어 로그 42블록·949줄 방치 | "규칙은 실행할 절차 단계에 배선" (si-improve §4, si-archive) |
| "합계는 항상 100" 단언이 정상 13건 오검출 | 무조건 단언 금지 — 조건·예외 명시 (si-improve §4) |
| 적용 범위를 좁히다 다른 영역 반례를 놓침 | 배제 판정에도 근거 (si-improve §4, si-archive §2) |
| 워밍된 캐시 수치로 "성능 해소" 오판 → 같은 날 철회 | 증거의 함정: 콜드 기준 판정 (si-improve §3) |
| 상시 로드 문서 34KB 매 세션 로드 | 층 모델 + 스코프 강등 + 이관표 (si-archive) |

## 이 플러그인 자체도 자가개선 대상

스킬·독트린·에이전트가 부족하면 같은 루프로 고친다 — 이 레포를 수정하고 `.claude-plugin/plugin.json` 의 version 을 올린다. 메타-규약도 얼어있지 않다.

이슈·PR 환영: <https://github.com/sh5623/self-improvement>

## 라이선스

MIT — [LICENSE](LICENSE)
