from typer.testing import CliRunner

from diagen import __version__
from diagen.cli import app


class TestCli:
    def test_show_version(self) -> None:
        # arrange
        runner = CliRunner()
        sut = app

        # act
        result = runner.invoke(sut, ["--version"])

        # assert
        assert result.exit_code == 0
        assert f"DiaGen {__version__}" in result.stdout

    def test_show_help(self) -> None:
        # arrange
        runner = CliRunner()
        sut = app

        # act
        result = runner.invoke(sut, ["--help"])

        # assert
        assert result.exit_code == 0
        assert "DiaGen" in result.stdout
        assert "--version" in result.stdout

    def test_default_run(self) -> None:
        # arrange
        runner = CliRunner()
        sut = app

        # act
        result = runner.invoke(sut, [])

        # assert
        assert result.exit_code == 0
        assert "готов к работе" in result.stdout
