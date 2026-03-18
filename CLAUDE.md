# Nexus CLI

AI 에이전트 설정 중앙 관리 CLI 프레임워크

## 개발 환경 설정

### 의존성 설치

```bash
uv sync
uv sync --extra dev  # 개발 의존성 포함

가상환경 활성화

source .venv/bin/activate

테스트 실행

# 전체 테스트
uv run pytest

# 특정 파일
uv run pytest tests/test_registry.py

# 상세 출력
uv run pytest -v

# 커버리지 포함
uv run pytest --cov=nexus

개발 명령어

# CLI 실행
uv run nxs --help

# 패키지 빌드
uv build