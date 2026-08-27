"""Command-line interface for dpkg-scanpackages.

Usage:
    dpkg-scanpackages [-m] [-a <arch>] [-t <type>] [-o <output>] <binary_path>
"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, version

# doctyper needs the real Path type at runtime for CLI introspection.
from pathlib import Path  # noqa: TC003
from typing import Annotated

import doctyper

from dpkg_scanpackages.scan_packages import DpkgScanPackages


def get_version() -> str:
    """Gets the installed package version, falling back to `__version__`."""
    try:
        return version("dpkg_scanpackages")
    except PackageNotFoundError:
        from dpkg_scanpackages import __version__

        return __version__


def version_callback(show_version: bool) -> None:
    """Prints the version and exits, if `show_version` is set."""
    if show_version:
        doctyper.echo(f"Debian dpkg-scanpackages-py version {get_version()}.")
        raise doctyper.Exit


def print_error(err: ValueError) -> None:
    """Prints an error message."""
    print(f"{sys.argv[0]}: {err}")  # noqa: T201
    print()  # noqa: T201
    print("Use --help for program usage information.")  # noqa: T201


def scan_packages(
    binary_path: Annotated[Path, doctyper.Argument(help="path to the binary directory.")],
    multiversion: Annotated[
        bool,
        doctyper.Option(
            "--multiversion", "-m", help="allow multiple versions of a single package."
        ),
    ] = False,
    arch: Annotated[
        str | None, doctyper.Option("--arch", "-a", help="architecture to scan for.")
    ] = None,
    package_type: Annotated[
        str, doctyper.Option("--type", "-t", help="scan for <type> packages.")
    ] = "deb",
    output: Annotated[
        Path | None, doctyper.Option("--output", "-o", help="write to file instead of stdout.")
    ] = None,
    unused_version: Annotated[
        bool | None,
        doctyper.Option(
            "--version", "-v", callback=version_callback, is_eager=True, help="show the version."
        ),
    ] = None,
) -> None:
    """Scans `binary_path` for packages and writes their headers to `output`."""
    try:
        DpkgScanPackages(
            binary_path=str(binary_path),
            multiversion=multiversion,
            arch=arch,
            package_type=package_type,
            output=str(output) if output is not None else None,
            previous=None,
        ).scan()
    except ValueError as err:
        print_error(err)
        raise SystemExit(1) from None


def main() -> None:
    """Entry point for the `dpkg-scanpackages-py` console script."""
    app = doctyper.DocTyper()
    app.command()(scan_packages)
    app()
