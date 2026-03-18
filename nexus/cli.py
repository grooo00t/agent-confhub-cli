"""Nexus CLI - 진입점 모듈"""
from typing import Optional
import typer
from nexus import __version__

app = typer.Typer(
    name="nxs",
    help="Nexus CLI - AI 에이전트 설정 관리",
    add_completion=False,
)


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


# commands 서브앱 등록 플레이스홀더
# 추후 각 커맨드 모듈이 추가될 예정입니다.
# 예시:
# from nexus.commands import init, app as app_cmd, agent, sync
# app.add_typer(init.app, name="init")
# app.add_typer(app_cmd.app, name="app")
# app.add_typer(agent.app, name="agent")
# app.add_typer(sync.app, name="sync")


if __name__ == "__main__":
    app()
