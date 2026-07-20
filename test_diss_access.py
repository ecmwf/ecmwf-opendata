#!/usr/bin/env python
"""Test script for DISS/SOFF data access via ecmwf-opendata."""

import os
import tempfile

from ecmwf.opendata import Client

# Credentials are loaded automatically from ~/.ecmwf-opendata
client = Client(source="diss")

print("=" * 60)
print("DISS/SOFF Data Access Test")
print("=" * 60)

# --- List available files ---
print("\n1. Listing all files for 2026-06-23...")
files = client.list_files(20260623)
print(f"   Total files: {len(files)}")

print("\n2. Listing by type...")
for ftype in ("model", "pressure", "surface", "amdar"):
    typed_files = client.list_files(20260623, file_type=ftype)
    total_mb = sum(f["size"] for f in typed_files) / 1024 / 1024
    print(f"   {ftype:10s}: {len(typed_files):3d} files, {total_mb:.1f} MB total")

# --- Download a single surface file (smallest, ~4MB) ---
print("\n3. Downloading a single surface file (step=18)...")
with tempfile.TemporaryDirectory() as tmpdir:
    target = os.path.join(tmpdir, "sfc_18h.grib2")
    result = client.download(
        target=target,
        date=20260623,
        file_type="surface",
        step=18,
    )
    size_mb = os.path.getsize(result[0]) / 1024 / 1024
    print(f"   Saved: {result[0]} ({size_mb:.1f} MB)")

# --- Download by exact filename ---
print("\n4. Downloading by exact filename (FSD06230000062303001)...")
with tempfile.TemporaryDirectory() as tmpdir:
    target = os.path.join(tmpdir, "raw.grib2")
    result = client.download(
        target=target,
        date=20260623,
        filename="FSD06230000062303001",
    )
    size_mb = os.path.getsize(result[0]) / 1024 / 1024
    print(f"   Saved: {result[0]} ({size_mb:.1f} MB)")

# --- Download multiple steps to a directory ---
print("\n5. Downloading multiple surface steps (0, 3, 6) to a directory...")
with tempfile.TemporaryDirectory() as tmpdir:
    outdir = os.path.join(tmpdir, "multi")
    result = client.download(
        target=outdir,
        date=20260623,
        file_type="surface",
        steps=[0, 3, 6],
    )
    print(f"   Downloaded {len(result)} files to {outdir}/")
    for path in result:
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"     {os.path.basename(path)} ({size_mb:.1f} MB)")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)
