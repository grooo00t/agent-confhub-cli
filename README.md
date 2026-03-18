# Nexus CLI (`nxs`)

AI 에이전트(Claude, Gemini, Codex, Cursor, Copilot) 설정을 팀 전체에 중앙 관리하는 CLI 프레임워크.

## 설치

```bash
pipx install nexus-cli
```

## 빠른 시작

```bash
# Registry 초기화
nxs init

# 앱 등록
nxs app add web-frontend --description "React 웹 프론트엔드"

# Claude 에이전트 설정 추가
nxs agent add claude --app web-frontend

# 설정 병합
nxs resolve web-frontend

# 프로젝트에 심볼릭 링크 연결
nxs link web-frontend --target /workspace/my-project
```

## 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `nxs init` | Registry 초기화 |
| `nxs app add/list/show/remove` | 앱 관리 |
| `nxs agent add/list/show/edit/remove` | 에이전트 설정 관리 |
| `nxs resolve <app>` | 설정 병합 빌드 |
| `nxs link <app>` | 프로젝트에 심볼릭 링크 |
| `nxs unlink <app>` | 링크 해제 |
| `nxs sync push/pull` | Git 동기화 |
| `nxs status` | Registry 상태 확인 |
| `nxs install --from-repo <url>` | 회사 레포 설치 |

## 지원 에이전트

| 에이전트 | 링크 대상 |
|----------|----------|
| `claude` | `.claude/` |
| `gemini` | `.gemini/` |
| `codex` | `AGENTS.md` |
| `cursor` | `.cursorrules` |
| `copilot` | `.github/copilot-instructions.md` |

## 팀 공유 워크플로우

```bash
# 설정 관리자
nxs sync pull
nxs agent edit claude --app api-server
nxs resolve api-server --dry-run
nxs sync push --message "feat: Claude 설정 업데이트"

# 팀원
nxs sync pull && nxs resolve --all
# 심볼릭 링크로 연결된 모든 프로젝트에 즉시 반영
```

## 개발

```bash
uv sync --extra dev
pytest tests/ -v
```
