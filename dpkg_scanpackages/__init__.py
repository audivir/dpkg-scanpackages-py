"""Scans packages and creates the Packages file for the apt repository."""

from __future__ import annotations

from dpkg_scanpackages.cli import main, scan_packages
from dpkg_scanpackages.scan_packages import DpkgInfo, DpkgScanPackages, add_4mb_sha256
from dpkg_scanpackages.utils import FileInputRead

__all__ = [
    "DpkgInfo",
    "DpkgScanPackages",
    "FileInputRead",
    "add_4mb_sha256",
    "main",
    "scan_packages",
]

__version__ = "0.4.1"
