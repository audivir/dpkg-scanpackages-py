"""Scans packages and creates the Packages file for the apt repository."""

from __future__ import annotations

if __name__ == "__main__":
    from dpkg_scanpackages.cli import main

    main()
