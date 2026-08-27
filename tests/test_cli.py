"""Tests for the command-line interface."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import TYPE_CHECKING

import doctyper
import pytest
from doctyper.testing import CliRunner

from dpkg_scanpackages import __version__
from dpkg_scanpackages.cli import get_version, main, print_error, scan_packages, version_callback

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch
    from conftest import Helpers

runner = CliRunner()


def build_app() -> doctyper.Typer:
    app = doctyper.DocTyper()
    app.command()(scan_packages)
    return app


def test_get_version_installed() -> None:
    assert get_version() == __version__


def test_get_version_fallback(monkeypatch: MonkeyPatch) -> None:
    def raise_not_found(unused_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr("dpkg_scanpackages.cli.version", raise_not_found)
    assert get_version() == __version__


def test_version_callback_true(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(doctyper.Exit):
        version_callback(True)
    out = capsys.readouterr().out
    assert f"Debian dpkg-scanpackages-py version {__version__}." in out


def test_version_callback_false(capsys: CaptureFixture[str]) -> None:
    version_callback(False)
    assert capsys.readouterr().out == ""


def test_print_error(capsys: CaptureFixture[str]) -> None:
    print_error(ValueError("boom"))
    out = capsys.readouterr().out
    assert "boom" in out
    assert "Use --help for program usage information." in out


def test_scan_packages_bad_path(capsys: CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        scan_packages(binary_path=Path("/nonexisting"))
    assert exc_info.value.code == 1

    out = capsys.readouterr().out
    assert "binary path /nonexisting not found" in out


def test_scan_packages_writes_output(tmp_path: Path, helpers: Helpers) -> None:
    from conftest import CURR_DIR

    output = tmp_path / "Packages"
    with helpers.change_cwd(str(CURR_DIR)):
        scan_packages(binary_path=CURR_DIR, output=output)

    assert output.read_text("utf-8")


def test_main_wires_scan_packages_into_doctyper_app(monkeypatch: MonkeyPatch) -> None:
    registered: dict[str, object] = {}

    class FakeApp:
        def command(self) -> object:
            def decorator(func: object) -> object:
                registered["func"] = func
                return func

            return decorator

        def __call__(self) -> None:
            registered["called"] = True

    monkeypatch.setattr("dpkg_scanpackages.cli.doctyper.DocTyper", FakeApp)

    main()

    assert registered["func"] is scan_packages
    assert registered["called"] is True


def test_cli_version_end_to_end() -> None:
    result = runner.invoke(build_app(), ["--version"])
    assert result.exit_code == 0
    assert f"Debian dpkg-scanpackages-py version {__version__}." in result.output


def test_cli_scan_end_to_end(tmp_path: Path, helpers: Helpers) -> None:
    from conftest import CURR_DIR

    output = tmp_path / "Packages"
    with helpers.change_cwd(str(CURR_DIR)):
        result = runner.invoke(build_app(), ["-o", str(output), str(CURR_DIR)])

    assert result.exit_code == 0
    assert output.read_text("utf-8")


def test_cli_bad_path_end_to_end() -> None:
    result = runner.invoke(build_app(), ["/nonexisting"])
    assert result.exit_code == 1
    assert "binary path /nonexisting not found" in result.output
