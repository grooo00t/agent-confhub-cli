# ConfHub CLI (`confhub`)

AI 에이전트(Claude, Gemini, Codex, Cursor, Copilot) 설정을 팀 전체에 중앙 관리하는 CLI 프레임워크.

## 개념 구조

```mermaid
graph TD
    R["~/.confhub (Registry)"]
    ROOT["root/agents/claude/\n팀 공통 기본 설정"]
    APP["apps/api-server/agents/claude/\n프로젝트별 설정"]
    RESOLVED["resolved/api-server/claude/\n병합 결과 (자동 생성)"]
    REMOTE["confhub-config\n(private git repo)"]
    PROJECT["api-server 프로젝트\n.nexus-config/ (submodule)"]
    SYMLINK[".claude/ 심볼릭 링크"]

    ROOT -->|"상속 + 오버라이드"| RESOLVED
    APP -->|"confhub resolve"| RESOLVED
    RESOLVED -->|"confhub sync push"| REMOTE
    REMOTE -->|"git submodule"| PROJECT
    PROJECT -->|"confhub submodule init"| SYMLINK
```

## 설치

```bash
pipx install agent-confhub-cli
```

## 빠른 시작

```bash
# Registry 초기화
confhub init

# 앱 등록
confhub app add web-frontend

# Claude 에이전트 설정 추가
confhub agent add claude --app web-frontend

# 설정 병합
confhub resolve web-frontend

# 프로젝트에 심볼릭 링크 연결
confhub link web-frontend --target /workspace/my-project
```

## 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `confhub init` | Registry 초기화 |
| `confhub app add/list/show/remove` | 앱 관리 |
| `confhub agent add/list/show/remove` | 에이전트 설정 관리 |
| `confhub resolve <app>` | 설정 병합 빌드 |
| `confhub link <app>` | 프로젝트에 심볼릭 링크 |
| `confhub unlink <app>` | 링크 해제 |
| `confhub submodule add <app>` | 프로젝트에 git submodule + sparse-checkout으로 설정 적용 |
| `confhub submodule init <app>` | 클론 후 sparse-checkout 및 심볼릭 링크 설정 (팀원용) |
| `confhub submodule remove <app>` | submodule 설정 제거 |
| `confhub sync push/pull` | Git 동기화 |
| `confhub status` | Registry 상태 확인 |
| `confhub install --from-repo <url>` | 회사 레포 설치 |

## 지원 에이전트

| 에이전트 | 링크 대상 |
|----------|----------|
| `claude` | `.claude/` |
| `gemini` | `.gemini/` |
| `codex` | `AGENTS.md` |
| `cursor` | `.cursorrules` |
| `copilot` | `.github/copilot-instructions.md` |

## 팀 공유 워크플로우

### 심볼릭 링크 방식 (개인 머신 로컬 적용)

```mermaid
sequenceDiagram
    participant A as 설정 관리자
    participant R as ~/.confhub (Registry)
    participant G as confhub-config (git)
    participant T as 팀원

    A->>R: confhub app add / confhub agent add
    A->>R: 파일 직접 편집
    A->>R: confhub resolve <app>
    A->>G: confhub sync push
    T->>G: confhub sync pull
    T->>R: confhub resolve --all
    Note over T: 심볼릭 링크로<br/>연결된 프로젝트에 즉시 반영
```

```bash
# 설정 관리자 - 설정 변경 후 push
confhub sync push --message "feat: Claude 설정 업데이트"

# 팀원 - pull 후 resolve로 로컬 반영
confhub sync pull && confhub resolve --all
```

### Git Submodule 방식 (sparse-checkout으로 앱 설정만 적용)

confhub-config 레포 전체가 아닌 해당 앱의 `resolved/<app>/` 만 체크아웃합니다.

```mermaid
sequenceDiagram
    participant A as 설정 관리자
    participant N as ~/.confhub (Registry)
    participant G as confhub-config (git)
    participant P as api-server 프로젝트
    participant T as 팀원

    A->>N: confhub app add api-server
    A->>N: confhub agent add claude --app api-server
    A->>N: 파일 직접 편집
    A->>G: confhub submodule add api-server --target ./api-server
    Note over A,G: resolve → push → submodule add<br/>→ sparse-checkout 자동 수행
    A->>P: .nexus-config/ submodule + .claude/ 심볼릭 링크 생성
    A->>P: git push (프로젝트 레포)

    T->>P: git clone api-server
    T->>P: confhub submodule init api-server
    Note over T,P: sparse-checkout + 심볼릭 링크 자동 설정
```

**설정 관리자 (최초 1회):**

```bash
# 1. Registry를 private 레포와 연결
confhub sync remote set https://github.com/your-team/confhub-config.git

# 2. 앱 및 에이전트 설정 준비
confhub app add api-server
confhub agent add claude --app api-server
# ~/.confhub/apps/api-server/agents/claude/ 에서 직접 파일 편집

# 3. 프로젝트에 submodule 적용
#    resolve → remote push → git submodule add → sparse-checkout 자동 수행
confhub submodule add api-server --target /workspace/api-server
```

**프로젝트 레포에 생성되는 구조:**

```
api-server/
├── .nexus-config/    ← confhub-config submodule (resolved/api-server/ 만 sparse-checkout)
├── .claude/          ← symlink → .nexus-config/resolved/api-server/claude/.claude/
├── .gemini/          ← symlink → .nexus-config/resolved/api-server/gemini/.gemini/
└── ...
```

개발자는 `.claude/`, `.gemini/` 등 프로젝트 루트의 심볼릭 링크만 사용하면 됩니다. `.nexus-config/` 내부 구조는 신경 쓸 필요 없습니다.

**팀원 (레포 클론 후):**

```bash
# 심볼릭 링크는 레포에 이미 커밋되어 있어 별도 생성 불필요
git clone --recurse-submodules https://github.com/your-team/api-server.git
cd api-server

# sparse-checkout 적용 (resolved/api-server/ 만 체크아웃)
confhub submodule init api-server
```

**설정 업데이트:**

```mermaid
flowchart LR
    E["파일 직접 편집\n~/.confhub/apps/api-server/..."]
    S["confhub submodule add api-server\n--target ./api-server"]
    GP["git push\n(프로젝트 레포)"]
    T["팀원: git pull\n+ git submodule update\n+ confhub submodule init api-server"]

    E --> S --> GP --> T
```

```bash
# ~/.confhub/apps/api-server/agents/claude/ 파일 직접 수정 후
confhub submodule add api-server --target /workspace/api-server
# resolve → confhub push → submodule ref + 심볼릭 링크 커밋

# 팀원은 프로젝트에서 반영
git pull && git submodule update
confhub submodule init api-server  # sparse-checkout 재적용
```

## 개발

```bash
uv sync --extra dev
pytest tests/ -v
```
