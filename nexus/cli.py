"""Nexus CLI - 진입점 모듈"""
from pathlib import Path
from typing import Optional
import typer
from nexus import __version__
from nexus.commands import app as app_cmd
from nexus.commands import agent as agent_cmd

app = typer.Typer(
    name="nxs",
    help="Nexus CLI - AI 에이전트 설정 관리",
    add_completion=False,
)

app.add_typer(app_cmd.app, name="app")
app.add_typer(agent_cmd.app, name="agent")


def version_callback(value: bool):
    """버전 정보 출력 콜백"""
    if value:
        typer.echo(f"nexus-cli version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="현재 버전을 출력합니다.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Nexus CLI - AI 에이전트 설정 중앙 관리 프레임워크"""


@app.command("init")
def init_command(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Registry 경로"
    ),
    from_repo: Optional[str] = typer.Option(
        None, "--from-repo", help="Git 레포 URL에서 초기화"
    ),
):
    """Nexus Registry를 초기화합니다."""
    from nexus.commands.init import do_init
    do_init(path, from_repo)


@app.command("resolve")
def resolve_command(
    app_name: Optional[str] = typer.Argument(None, help="앱 이름 (생략시 --all 필요)"),
    all_apps: bool = typer.Option(False, "--all", "-a", help="모든 앱 빌드"),
    dry_run: bool = typer.Option(False, "--dry-run", help="결과 미리보기 (파일 미생성)"),
):
    """설정을 병합하여 resolved 디렉토리에 저장합니다."""
    from nexus.commands.resolve import do_resolve
    do_resolve(app_name, all_apps, dry_run)


if __name__ == "__main__":
    app()
