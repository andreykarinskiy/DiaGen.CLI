from typer.testing import CliRunner

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
        assert "DiaGen 0.1.0" in result.stdout

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
