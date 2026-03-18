# 개발자 AI 에이전트 설정 공유 프레임워크 설계 문서

---

## 1. 프레임워크 이름 제안

### 후보 3가지

| 후보 | 이름 | 의미 | 특징 |
|------|------|------|------|
| 1 | **AgentForge** | AI 에이전트를 단조(forge)하는 프레임워크 | 제조/생성의 강인한 이미지, 영어권 친화적 |
| 2 | **Nexus** | 연결점(nexus) 기반 에이전트 설정 관리 | 짧은 CLI 명령어, 연결과 공유의 의미 |
| 3 | **AetherConf** | 에테르(aether)처럼 팀 전체에 퍼지는 설정 | 투명하고 어디서나 접근 가능한 설정의 이미지 |

### 최종 추천: **Nexus** (CLI: `nxs`)

**추천 이유:**
- `nxs init`, `nxs app add`, `nxs agent add`, `nxs link` 등 직관적이고 짧은 CLI
- "연결점"이라는 의미가 루트 설정 상속, 팀 공유, 심볼릭 링크 등 핵심 개념을 잘 대변함
- 회사별 커스텀 CLI(`acme-nxs`)로 확장 시 네이밍 일관성 유지

---

## 2. 구현 기술 스택

### 언어: Python

| 라이브러리 | 용도 |
|-----------|------|
| `typer` | CLI 명령어 정의 (Click 기반, 타입 힌트 지원) |
| `rich` | 터미널 출력 (컬러, 테이블, 프로그레스바) |
| `pathlib` | 파일/디렉토리 조작, 심볼릭 링크 생성 |
| `GitPython` | git 조작 (sync push/pull) |
| `pyyaml` | 설정 파일 파싱 |
| `jinja2` | 마크다운 파일 병합 템플릿 |

### 배포: pipx + PyPI

```bash
# 코어 CLI 설치
pipx install nexus-cli        # → nxs 명령어 등록

# 회사 레포 설치 (두 가지 방법)
pipx install acme-nexus-config
# 또는
nxs install --from-repo https://github.com/acme/nexus-config
```

pipx는 Python 생태계에서 npm의 npx와 동일한 역할을 합니다. 각 패키지를 격리된 가상환경에서 실행하므로 의존성 충돌 없이 여러 회사 레포를 설치할 수 있습니다.

### 프로젝트 구조

```
nexus-cli/
├── pyproject.toml             # 패키지 정의 (pip 배포용)
├── nexus/
│   ├── __init__.py
│   ├── cli.py                 # typer 앱 진입점 (nxs 명령어)
│   ├── commands/
│   │   ├── init.py            # nxs init
│   │   ├── app.py             # nxs app add/list/show/remove
│   │   ├── agent.py           # nxs agent add/edit/show/list
│   │   ├── link.py            # nxs link/unlink
│   │   ├── resolve.py         # nxs resolve
│   │   ├── sync.py            # nxs sync push/pull
│   │   ├── install.py         # nxs install
│   │   └── status.py          # nxs status
│   ├── core/
│   │   ├── registry.py        # Registry 클래스
│   │   ├── merger.py          # 설정 상속/병합 로직
│   │   ├── linker.py          # 심볼릭 링크 관리
│   │   └── agents.py          # 에이전트별 설정 처리
│   └── utils/
│       ├── git.py             # GitPython 래퍼
│       └── console.py         # rich 출력 헬퍼
└── tests/
```

---

## 3. 프레임워크 개요 및 핵심 개념

### 개요

**Nexus**는 팀이 AI 에이전트(Claude, Gemini, Codex 등)의 설정을 중앙에서 관리하고, 프로젝트별로 선택적으로 적용하며, 회사 단위로 공유할 수 있도록 설계된 설정 공유 프레임워크입니다.

개별 개발자가 각자 AI 에이전트 설정을 관리하는 대신, 팀 전체가 일관된 설정을 공유하면서도 프로젝트별 커스터마이징을 허용합니다.

### 핵심 개념

```
┌──────────────────────────────────────────────────────────────┐
│                      Nexus Registry                          │
│   (팀 공유 Git 레포 - 설정의 단일 진실 공급원)                │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Root Config                         │    │
│  │          (모든 앱이 공유하는 기본 설정)                │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │  상속 (inheritance)                  │
│         ┌─────────────┼──────────────┐                      │
│         ▼             ▼              ▼                       │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐                   │
│    │ App: A  │  │ App: B  │  │ App: C  │                   │
│    │ (web)   │  │ (api)   │  │ (data)  │                   │
│    └────┬────┘  └────┬────┘  └────┬────┘                   │
│         │            │             │                         │
│  resolved/        resolved/    resolved/                     │
│  web/claude/      api/claude/  data/gemini/                  │
│    .claude/         .claude/     .gemini/                    │
│         │            │             │                         │
│    심볼릭 링크    심볼릭 링크   심볼릭 링크                    │
│         ▼            ▼             ▼                         │
│  /proj/web/.claude/  /proj/api/.claude/  /proj/data/.gemini/ │
└──────────────────────────────────────────────────────────────┘
```

#### 핵심 개념 용어

| 개념 | 설명 |
|------|------|
| **Registry** | Nexus 프레임워크가 설치된 루트 디렉토리. Git 레포로 관리되는 설정의 중앙 저장소 |
| **Root Config** | 모든 앱이 공통으로 상속받는 기본 에이전트 설정 |
| **App** | 특정 프로젝트 또는 서비스 단위의 설정 묶음. Root Config를 상속하고 오버라이드 가능 |
| **Agent Profile** | Claude, Gemini, Codex 등 특정 AI 에이전트에 대한 설정 |
| **Resolved** | 루트와 앱 설정이 병합된 최종 결과물. 실제 에이전트 디렉토리 구조를 포함 |
| **Link** | 실제 프로젝트의 에이전트 폴더(`.claude/` 등)를 resolved 폴더로 심볼릭 링크하는 작업 |
| **Distribution** | 회사 레포를 PyPI 패키지로 배포하여 팀원이 pipx로 자동 세팅하는 방식 |

---

## 4. 디렉토리 구조

### Nexus Registry 디렉토리 구조

```
~/.nexus/                              # 기본 Registry 위치 (또는 지정 경로)
├── nexus.config.yaml                  # Registry 메타 설정
│
├── root/                              # Root Config
│   └── agents/
│       ├── claude/
│       │   ├── agent.config.yaml      # Claude 루트 병합 설정
│       │   └── .claude/
│       │       ├── CLAUDE.md          # 공통 Claude 지침
│       │       └── settings.json      # 공통 Claude 설정
│       ├── gemini/
│       │   ├── agent.config.yaml
│       │   └── .gemini/
│       │       └── GEMINI.md
│       └── codex/
│           ├── agent.config.yaml
│           └── AGENTS.md
│
├── apps/                              # 등록된 앱 목록
│   ├── web-frontend/
│   │   ├── app.config.yaml            # 앱 메타 설정
│   │   └── agents/
│   │       ├── claude/
│   │       │   ├── agent.config.yaml  # 병합 전략 오버라이드
│   │       │   └── .claude/
│   │       │       ├── CLAUDE.md      # 앱별 Claude 지침 (루트에 추가됨)
│   │       │       └── settings.json  # 앱별 설정 (루트를 deep-merge)
│   │       └── gemini/
│   │           ├── agent.config.yaml
│   │           └── .gemini/
│   │               └── GEMINI.md
│   │
│   └── api-server/
│       ├── app.config.yaml
│       └── agents/
│           └── claude/
│               ├── agent.config.yaml
│               └── .claude/
│                   └── CLAUDE.md
│
├── resolved/                          # 상속 병합 결과 (자동 생성, .gitignore)
│   ├── web-frontend/
│   │   ├── claude/
│   │   │   └── .claude/               # ← 프로젝트/.claude/ 가 이 폴더를 심볼릭 링크
│   │   │       ├── CLAUDE.md          # 루트 + 앱 병합 결과
│   │   │       └── settings.json
│   │   └── gemini/
│   │       └── .gemini/               # ← 프로젝트/.gemini/ 가 이 폴더를 심볼릭 링크
│   │           └── GEMINI.md
│   └── api-server/
│       └── claude/
│           └── .claude/
│               └── CLAUDE.md
│
└── links/
    └── links.json                     # 심볼릭 링크 레지스트리 (링크 추적용)
```

### 실제 프로젝트 디렉토리에서의 구조

```
/workspace/my-web-project/
├── src/
├── package.json
├── .claude/   →  심볼릭 링크  →  ~/.nexus/resolved/web-frontend/claude/.claude/
└── .gemini/   →  심볼릭 링크  →  ~/.nexus/resolved/web-frontend/gemini/.gemini/
```

각 에이전트는 자신의 설정 폴더(`.claude/`, `.gemini/` 등) 단위로 심볼릭 링크됩니다.

---

## 5. CLI 명령어 목록

### 5.1 `nxs init` - Registry 초기화

```bash
# 기본 위치(~/.nexus)에 초기화
nxs init

# 특정 경로에 초기화
nxs init --path /company/shared/nexus

# 기존 Git 레포를 Registry로 초기화
nxs init --from-repo https://github.com/acme/nexus-config
```

**동작:**
1. 지정 경로에 Registry 디렉토리 구조 생성
2. `nexus.config.yaml` 생성
3. `root/agents/` 디렉토리와 기본 에이전트 템플릿 생성
4. Git 레포 초기화 (선택)
5. `~/.nexusrc`에 Registry 경로 등록

---

### 5.2 `nxs app` - 앱 관리

```bash
nxs app add <app-name> [--description "설명"]   # 앱 등록
nxs app list                                    # 앱 목록 조회
nxs app show <app-name>                         # 앱 상세 조회
nxs app remove <app-name>                       # 앱 삭제
nxs app rename <old-name> <new-name>            # 앱 이름 변경
```

**예시:**
```bash
nxs app add web-frontend --description "React 기반 웹 프론트엔드"
nxs app add api-server --description "Node.js REST API 서버"
nxs app add data-pipeline --description "Python 데이터 파이프라인"
```

---

### 5.3 `nxs agent` - 에이전트 설정 관리

```bash
nxs agent add <agent> --app <app> | --root      # 에이전트 추가
nxs agent edit <agent> --app <app> | --root     # 설정 편집 (기본 에디터)
nxs agent show <agent> --app <app>              # 설정 조회
nxs agent show <agent> --app <app> --resolved   # 상속 병합 후 최종값 조회
nxs agent list --app <app> | --root             # 에이전트 목록
nxs agent remove <agent> --app <app>            # 에이전트 설정 삭제
```

**지원 에이전트 및 심볼릭 링크 대상:**

| 식별자 | 에이전트 | 프로젝트 내 심볼릭 링크 대상 | resolved 내 경로 |
|--------|----------|------------------------------|-----------------|
| `claude` | Anthropic Claude | `.claude/` | `resolved/<app>/claude/.claude/` |
| `gemini` | Google Gemini | `.gemini/` | `resolved/<app>/gemini/.gemini/` |
| `codex` | OpenAI Codex | `AGENTS.md` | `resolved/<app>/codex/AGENTS.md` |
| `cursor` | Cursor AI | `.cursorrules` | `resolved/<app>/cursor/.cursorrules` |
| `copilot` | GitHub Copilot | `.github/copilot-instructions.md` | `resolved/<app>/copilot/.github/` |

---

### 5.4 `nxs link` - 심볼릭 링크 관리

```bash
nxs link <app>                                  # 현재 디렉토리에 링크
nxs link <app> --target /path/to/project        # 특정 경로에 링크
nxs link <app> --agent claude                   # 특정 에이전트만 링크
nxs link <app> --agent claude,gemini

nxs unlink <app> [--target /path]               # 링크 해제
nxs link list                                   # 링크 목록
nxs link status                                 # 링크 상태 확인 (깨진 링크 탐지)
```

**링크 생성 예시:**
```bash
nxs link web-frontend --target /workspace/my-project

# 생성되는 심볼릭 링크:
# /workspace/my-project/.claude/  →  ~/.nexus/resolved/web-frontend/claude/.claude/
# /workspace/my-project/.gemini/  →  ~/.nexus/resolved/web-frontend/gemini/.gemini/
```

---

### 5.5 `nxs resolve` - 설정 병합 빌드

```bash
nxs resolve <app>           # 특정 앱 병합 결과 빌드
nxs resolve --all           # 모든 앱 빌드
nxs resolve <app> --dry-run # 결과 미리보기 (파일 미생성)
```

---

### 5.6 `nxs sync` - Git 동기화

```bash
nxs sync push [--message "커밋 메시지"]   # Registry를 원격 레포에 push
nxs sync pull                             # 원격 레포에서 최신 설정 pull
nxs sync remote set <git-url>             # 원격 레포 설정
nxs sync remote show                      # 원격 레포 확인
```

---

### 5.7 `nxs install` - 회사 레포 설치

```bash
nxs install --from-repo https://github.com/acme/nexus-config
nxs install --verify                      # 설치 상태 확인
nxs install --apps web-frontend,api-server  # 특정 앱만 선택 설치
```

---

### 5.8 `nxs status` - 상태 확인

```bash
nxs status                    # Registry 전체 상태
nxs status --app web-frontend # 특정 앱 상태
nxs status --with-links       # 링크 상태 포함
```

---

## 6. 설정 파일 포맷 예시

### 6.1 `nexus.config.yaml` - Registry 메타 설정

```yaml
version: "1.0.0"
registry:
  name: acme-nexus
  description: Acme Corp AI 에이전트 설정 Registry

remote:
  url: https://github.com/acme/nexus-config
  branch: main
  auto_pull: false

defaults:
  inheritance_strategy: deep-merge
  link_mode: symlink
```

---

### 6.2 Root Config - Claude 에이전트 설정

**`root/agents/claude/agent.config.yaml`**

```yaml
agent: claude
version: "1.0.0"
scope: root

merge:
  CLAUDE.md: append        # 앱의 CLAUDE.md를 루트 내용 뒤에 추가
  settings.json: deep-merge  # JSON 필드 단위 병합
```

**`root/agents/claude/.claude/CLAUDE.md`**

```markdown
# 공통 AI 에이전트 규칙

## 코딩 표준
- TypeScript 사용 시 strict 모드 활성화
- 함수 단위 단일 책임 원칙 준수

## 보안 규칙
- 환경 변수는 .env 파일로만 관리
- 민감 정보 로그 출력 금지

## Git 규칙
- 커밋 메시지: [타입]: [내용] 형식
```

**`root/agents/claude/.claude/settings.json`**

```json
{
  "model": "claude-sonnet-4-5",
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

---

### 6.3 App Config - 앱 메타 설정

**`apps/web-frontend/app.config.yaml`**

```yaml
name: web-frontend
version: "1.0.0"
description: React 기반 웹 프론트엔드
inherits: root
agents:
  - claude
  - gemini

metadata:
  team: frontend
  tech_stack: [React, TypeScript, Tailwind CSS]

inheritance:
  strategy: deep-merge
```

---

### 6.4 App-level 에이전트 설정 (오버라이드)

**`apps/web-frontend/agents/claude/agent.config.yaml`**

```yaml
agent: claude
version: "1.0.0"
scope: app
app: web-frontend

merge:
  CLAUDE.md: append          # 기본값, 루트 내용 뒤에 추가
  settings.json: deep-merge  # 루트 settings.json과 deep merge
```

**`apps/web-frontend/agents/claude/.claude/CLAUDE.md`**

```markdown
# Web Frontend 전용 규칙

## 컴포넌트 규칙
- React 컴포넌트는 함수형으로만 작성
- CSS-in-JS 대신 Tailwind CSS 클래스 사용
- 접근성(a11y) 속성 반드시 포함
```

**`apps/web-frontend/agents/claude/.claude/settings.json`**

```json
{
  "model": "claude-opus-4-5",
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(npx *)"]
  }
}
```

---

### 6.5 Resolved 결과물 (자동 생성)

`nxs resolve web-frontend` 실행 후 생성:

**`resolved/web-frontend/claude/.claude/CLAUDE.md`**

```markdown
<!-- AUTO-GENERATED by Nexus - DO NOT EDIT DIRECTLY -->
<!-- Source: root/agents/claude → apps/web-frontend/agents/claude -->
<!-- Generated: 2026-03-18T10:00:00Z -->

# 공통 AI 에이전트 규칙

## 코딩 표준
- TypeScript 사용 시 strict 모드 활성화
...

---
<!-- web-frontend -->

# Web Frontend 전용 규칙

## 컴포넌트 규칙
- React 컴포넌트는 함수형으로만 작성
...
```

**`resolved/web-frontend/claude/.claude/settings.json`** (deep-merge 결과)

```json
{
  "model": "claude-opus-4-5",
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(npx *)"],
    "deny": []
  }
}
```

---

## 7. 상속 메커니즘

### 7.1 병합 전략

```
Root                          App                          Resolved
────────────────────          ──────────────────────       ──────────────────────────────
model: sonnet         +       model: opus            =     model: opus           [app]
permissions.allow: [] +       permissions.allow: [npx] =   permissions.allow: [npx] [app]
CLAUDE.md: [A, B]     +       CLAUDE.md: [C, D]       =     CLAUDE.md: [A, B, —, C, D]  [합산]
```

### 7.2 병합 규칙 상세

| 파일/필드 유형 | 기본 전략 | 설명 |
|---------------|-----------|------|
| `.md` 파일 | `append` | 루트 내용 + 구분선 + 앱 내용 |
| `.json` 파일 | `deep-merge` | JSON 필드 단위 재귀 병합, 스칼라는 앱이 오버라이드 |
| 스칼라 값 | 앱 값으로 오버라이드 | 앱 설정이 루트를 덮어씀 |
| 없는 필드 | 루트 값 유지 | 앱에서 정의하지 않으면 루트 값 사용 |

### 7.3 오버라이드 제어

`agent.config.yaml`에서 병합 전략을 명시적으로 변경:

```yaml
merge:
  CLAUDE.md: replace    # 루트 내용 무시, 앱 내용으로 완전 대체
  settings.json: deep-merge
```

| 전략 | 동작 |
|------|------|
| `append` (기본값) | 루트 내용 뒤에 앱 내용 추가 |
| `replace` | 앱 내용이 루트 내용을 완전 대체 |
| `prepend` | 앱 내용 앞에 루트 내용 추가 |
| `deep-merge` | JSON 필드 단위 재귀 병합 |

### 7.4 상속 시각화

```
$ nxs agent show claude --app web-frontend --resolved

┌─────────────────────────────────────────────────────┐
│  Claude Config (web-frontend) - Resolved             │
├─────────────────────────────────────────────────────┤
│  Source Chain:                                       │
│    root/agents/claude                                │
│    → apps/web-frontend/agents/claude                 │
│                                                      │
│  settings.json:                                      │
│    model:           "claude-opus-4-5"   [app]       │
│    permissions.allow: ["Bash(npm...)"]  [app]       │
│    permissions.deny:  []                [root]      │
│                                                      │
│  .claude/CLAUDE.md:                                  │
│    [root] # 공통 AI 에이전트 규칙                     │
│    [root]   - TypeScript strict 모드...              │
│    [root]   - 보안 규칙...                           │
│    [app]  # Web Frontend 전용 규칙                   │
│    [app]    - React 함수형 컴포넌트...               │
│                                                      │
│  심볼릭 링크 대상:                                   │
│    ~/.nexus/resolved/web-frontend/claude/.claude/    │
└─────────────────────────────────────────────────────┘
```

---

## 8. 팀 공유 워크플로우

### 8.1 전체 흐름

```
설정 관리자                    팀원 A                    팀원 B
────────────                  ────────                  ────────
1. nxs init
2. nxs app add web-frontend
3. nxs agent add claude --app web-frontend
4. [설정 편집]
5. nxs resolve --all
6. nxs sync push
                              7. nxs sync pull          7. nxs sync pull
                              8. nxs resolve --all      8. nxs resolve --all
                              9. nxs link web-frontend  9. nxs link api-server
                             10. [개발 시작]            10. [개발 시작]
                             11. [설정 변경 PR 제안]
12. [PR 리뷰 및 병합]
13. nxs sync push
                             14. nxs sync pull         14. nxs sync pull
                                 nxs resolve --all         nxs resolve --all
                                 (즉시 반영)               (즉시 반영)
```

### 8.2 설정 변경 프로세스

```bash
# 1. 최신 설정 동기화
nxs sync pull

# 2. 변경 작업
nxs agent edit claude --app api-server

# 3. 변경 사항 검증
nxs resolve api-server --dry-run

# 4. 팀 레포에 공유
nxs sync push --message "feat: api-server Claude 설정에 보안 규칙 추가"

# 5. 다른 팀원들: pull 후 자동 반영
nxs sync pull && nxs resolve --all
```

---

## 9. 회사별 레포 배포 방식

### 9.1 배포 구조

```
acme-nexus-config/ (회사 레포)
├── pyproject.toml             # PyPI 패키지 정의
├── nexus.config.yaml          # Registry 설정
├── root/                      # 공통 설정
├── apps/                      # 앱 설정
├── distribution.yaml          # 배포 메타데이터
└── acme_nexus/
    ├── __init__.py
    └── cli.py                 # acme-nxs 진입점 (nxs CLI 확장)
```

---

### 9.2 `pyproject.toml` - PyPI 패키지 정의

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "acme-nexus-config"
version = "2.1.0"
description = "Acme Corp AI 에이전트 설정 Registry"
dependencies = [
    "nexus-cli>=1.0.0",
]

[project.scripts]
acme-nxs = "acme_nexus.cli:app"

[tool.hatch.build.hooks.custom]
# 설치 후 자동으로 nxs install 실행
```

---

### 9.3 `distribution.yaml` - 배포 메타데이터

```yaml
distribution:
  name: acme
  display_name: Acme Corp Nexus
  version: "2.1.0"
  company: Acme Corporation
  registry_url: https://github.com/acme/nexus-config
  cli_alias: acme-nxs

install:
  default_registry_path: ~/.acme-nexus
  auto_link_apps: false
  post_install_message: |
    Acme 에이전트 설정이 완료되었습니다.
    'acme-nxs app list'로 앱 목록을 확인하세요.
  optional_apps:
    - web-frontend
    - api-server
    - data-pipeline
    - mobile-app

apps:
  - name: web-frontend
    description: React 웹 프론트엔드 표준 설정
    agents: [claude, gemini, copilot]
  - name: api-server
    description: Node.js/Python API 서버 표준 설정
    agents: [claude, codex]
```

---

### 9.4 신규 팀원 설치 경험

```bash
# 방법 1: pipx로 직접 설치
pipx install acme-nexus-config

# 방법 2: Git URL로 설치
nxs install --from-repo https://github.com/acme/nexus-config

# 방법 3: pip로 설치 (가상환경 내)
pip install acme-nexus-config
```

**설치 과정 (자동):**

```
$ pipx install acme-nexus-config

Nexus 설치 중... (Acme Corp 배포판)

[1/5] Registry 초기화...          ✅ ~/.acme-nexus/ 생성
[2/5] 설정 파일 다운로드...        ✅ GitHub에서 최신 설정 동기화
[3/5] 설정 병합(resolve)...       ✅ 4개 앱 resolved 완료
[4/5] CLI 설정...                 ✅ `acme-nxs` 명령어 등록
[5/5] 환경 검증...                ✅ Claude, Gemini 에이전트 설정 확인

설치 완료!

사용 가능한 앱:
  - web-frontend  : React 웹 프론트엔드 (Claude, Gemini, Copilot)
  - api-server    : Node.js/Python API (Claude, Codex)
  - data-pipeline : 데이터 파이프라인 (Gemini)
  - mobile-app    : React Native 앱 (Claude, Copilot)

시작하기:
  acme-nxs link web-frontend   # 현재 프로젝트/.claude/ 를 심볼릭 링크
  acme-nxs app list            # 전체 앱 목록 확인
  acme-nxs status              # Registry 상태 확인
```

---

### 9.5 설정 업데이트 배포

```bash
# 설정 관리자: 변경 사항 배포
nxs sync push --message "feat: Claude opus 모델 업데이트"
# PyPI 버전 올리고 배포
python -m build && twine upload dist/*

# 팀원: 최신 설정 적용
pipx upgrade acme-nexus-config
acme-nxs sync pull && acme-nxs resolve --all
# 심볼릭 링크로 연결된 모든 프로젝트에 즉시 반영
```

---

## 10. 심볼릭 링크 동작 방식

### 10.1 링크 생성 메커니즘 (Python)

```python
# linker.py 내부 동작 예시
from pathlib import Path

def link_app(app_name: str, target: Path, agents: list[str]):
    registry = Path("~/.nexus").expanduser()

    for agent in agents:
        resolved_dir = registry / "resolved" / app_name / agent
        agent_dir = resolved_dir / f".{agent}"  # .claude/, .gemini/ 등

        # nxs resolve가 아직 안 된 경우 자동 실행
        if not agent_dir.exists():
            resolve_app(app_name)

        link_path = target / f".{agent}"

        # 기존 파일 백업
        if link_path.exists() and not link_path.is_symlink():
            backup = target / f".nexus-backup" / f".{agent}"
            backup.parent.mkdir(exist_ok=True)
            link_path.rename(backup)

        # 심볼릭 링크 생성
        link_path.symlink_to(agent_dir)
```

### 10.2 자동 반영 원리

`resolved/` 내의 `.claude/` 폴더를 직접 심볼릭 링크하므로, `nxs resolve` 실행 시 모든 링크 프로젝트에 **즉시 자동 반영**됩니다.

```
변경 반영 흐름:
nxs sync pull  →  nxs resolve --all  →  모든 링크 프로젝트 즉시 반영
(원격에서 pull)    (병합 결과 재생성)    (심볼릭 링크로 자동 적용)
```

---

*이 문서는 Nexus 프레임워크 v1.0 설계 기준으로 작성되었습니다.*
