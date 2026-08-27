# dpkg-scanpackages-py

A Python implementation of Debian's `dpkg-scanpackages`.

## Prerequisites

Python 3.10 or higher.

## Installation

```shell
pip install git+https://github.com/audivir/dpkg-scanpackages-py.git
```

## Usage

```
Usage: dpkg-scanpackages-py [OPTIONS] {binary_path}

Arguments:
  binary_path      path to the binary directory. [required]

Options:
  --multiversion  -m              allow multiple versions of a single package.
  --arch          -a      <str>   architecture to scan for.
  --type          -t      <str>   scan for <type> packages. [default: deb]
  --output        -o      <path>  write to file instead of stdout.
  --version       -v              show the version.
  --help                          Show this message and exit.
```

On Windows, piping the output to a file results in CRLF line endings. Convert the
file to unix-style (LF) line endings before using it in an apt repository, or use
the `--output` argument to write directly to a file.

## Acknowledgments

This project is a fork of [supermamon/dpkg-scanpackages-py](https://github.com/supermamon/dpkg-scanpackages-py)
by Raymond Velasquez, which is itself a Python implementation of Debian's
`dpkg-scanpackages`.

## License

Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
