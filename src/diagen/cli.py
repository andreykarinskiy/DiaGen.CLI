"""CLI entrypoint for DiaGen."""

from typing import Annotated

import typer

from diagen import __version__

app = typer.Typer(help="DiaGen - CLI для запуска автоматизационных сценариев.")


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"DiaGen {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            help="Показать версию DiaGen и завершить работу.",
            is_eager=True,
            callback=version_callback,
        ),
    ] = None,
) -> None:
    """Base application callback."""
    if version:
        return
    typer.echo("DiaGen CLI готов к работе. Используйте --help для списка команд.")


def run() -> None:
    """Console script entrypoint."""
    app()
