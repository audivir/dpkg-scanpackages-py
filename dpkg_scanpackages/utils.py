"""Utility functions for dpkg-scanpackages."""

# ruff: noqa: PTH123
from __future__ import annotations

import fileinput
import sys
from contextlib import contextmanager
from typing import IO, TYPE_CHECKING, Protocol

from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence

    from _typeshed import SupportsRead, SupportsWrite
HEADER_ORDER = [
    "Package",
    "Version",
    "Architecture",
    "Built-Using",
    "Multi-Arch",
    "Essential",
    "Source",
    "Origin",
    "Maintainer",
    "Original-Maintainer",
    "Bugs",
    "Installed-Size",
    "Provides",
    "Pre-Depends",
    "Depends",
    "Recommends",
    "Suggests",
    "Conflicts",
    "Breaks",
    "Replaces",
    "Enhances",
    "Filename",
    "Size",
    "MD5sum",
    "SHA1",
    "SHA256",
    "SHA512",
    "Section",
    "Priority",
    "Homepage",
    "Description",
    "Tag",
    "Task",
    "Protected",
    "Important",
    "Description-md5",
    "Build-Essential",
    "Support",
]


class HasHeaders(Protocol):
    """Interface for objects exposing dpkg package headers."""

    headers: dict[str, str]


class DpkgInfoHeaders:
    """Stores the headers of a dpkg package."""

    def __init__(self, headers: dict[str, str]) -> None:
        """Initializes with the given package headers."""
        self.headers = headers


def format_headers(headers: dict[str, str]) -> str:
    """Formats the headers, ordered by `HEADER_ORDER` then alphabetically."""
    pretty = ""
    # write fields in HEADER_ORDER first.
    for key in HEADER_ORDER:
        if key in headers:
            pretty = pretty + (f"{key}: {headers[key]}\n")

    # write remaining fields alphabetically.
    for key in sorted(headers):
        if key not in HEADER_ORDER:
            pretty = pretty + (f"{key}: {headers[key]}\n")
    return pretty


def write_headers(output: IO[str] | str | None, packages: Sequence[HasHeaders]) -> None:
    """Writes the headers."""
    if not packages:
        raise ValueError("No packages to write")

    with multi_open_write(output) as file:
        file.write(format_headers(packages[0].headers))
        for p in packages[1:]:
            file.write("\n")
            file.write(format_headers(p.headers))


class FileInputRead(fileinput.FileInput[str]):
    """Wraps `fileinput.FileInput` to support a single full `read()` call."""

    def __init__(self, files: str | tuple[str, ...], add_newline: bool = False) -> None:
        """Initializes a fresh FileInputRead over the given files."""
        super().__init__(files=files, encoding="utf-8")
        self._sep = "\n" if add_newline else ""
        self._fileno = 0
        self._file_contents: list[str] = []
        self._lines: list[str] | None = None

    def read(self, n: int = -1) -> str:
        """Reads the full contents of all files.

        Raises:
            NotImplementedError: If `n` is not -1, since only full reads are supported.
            ValueError: If called more than once on the same instance.
        """
        if n != -1:
            raise NotImplementedError("can only read fully")
        if self._filelineno > 0 or self._fileno > 0:  # type: ignore[attr-defined]
            raise ValueError("can only read fresh instances")

        self._lines = []
        for line in self:
            self._lines.append(line)
            # nextfile() shifts the accumulated lines into _file_contents
            # whenever a new file is opened.
        # concatenate the contents of all files.
        return self._sep.join(self._file_contents)

    @override
    def nextfile(self) -> None:
        """Closes the current file and opens the next one."""
        if self._lines is not None:  # checks whether read() was called before.
            self._file_contents.append("".join(self._lines))
            self._lines = []
        self._fileno += 1
        super().nextfile()


@contextmanager
def multi_open_read(
    input: IO[str] | str | tuple[str, ...] | None = None,  # noqa: A002
) -> Generator[SupportsRead[str]]:
    """Opens the provided file, file handle, or stdin for reading."""
    if input is None:
        yield sys.stdin
        return

    if isinstance(input, str | tuple):
        if not input:
            raise ValueError("no input data provided")

        with FileInputRead(files=input, add_newline=True) as file:
            yield file
        return
    yield input


@contextmanager
def multi_open_write(
    output: IO[str] | str | None = None,
) -> Generator[SupportsWrite[str]]:
    """Opens the provided file, file handle, or stdout for writing."""
    if output is None:
        yield sys.stdout
    elif isinstance(output, str):
        with open(output, "w") as file:
            yield file
    else:
        yield output
