#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import gdown
import re
from pathlib import Path

# ----------------------------
# Configuration
# ----------------------------
DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1nl_VzFqT9mEKZnQXfYehxzeGvp7AeDo2?usp=sharing"
PROJECT_DIR = Path.home() / "third-officer-maintenance-system"
ORIGINALS_DIR = PROJECT_DIR / "data_sources" / "originals"

# Maximum filename length to avoid OS errors
MAX_FILENAME_LENGTH = 100

# ----------------------------
# Utility functions
# ----------------------------
def sanitize_filename(filename):
    """Shorten filename if too long and remove forbidden characters."""
    filename = re.sub(r'[<>:"/\\|?*\n]', '_', filename)  # replace illegal characters
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    return filename

def ensure_directory(path):
    """Create directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Directory ensured: {path}")

# ----------------------------
# Main function
# ----------------------------
def main():
    print("=== Extraction started ===")

    # Step 1: Ensure directories
    ensure_directory(ORIGINALS_DIR)

    # Step 2: Attempt to download folder from Google Drive
    print("Downloading Google Drive folder...")
    try:
        gdown.download_folder(
            url=DRIVE_FOLDER_URL,
            output=str(ORIGINALS_DIR),
            quiet=False,
            use_cookies=False
        )
        print("Folder downloaded successfully.")
    except Exception as e:
        print(f"[WARNING] Some files could not be downloaded automatically: {e}")
        print("[INFO] You may need to download them manually from your browser.")

    # Step 3: Sanitize long filenames
    print("Checking for long filenames...")
    for root, dirs, files in os.walk(ORIGINALS_DIR):
        for fname in files:
            full_path = Path(root) / fname
            safe_name = sanitize_filename(fname)
            if fname != safe_name:
                new_path = Path(root) / safe_name
                os.rename(full_path, new_path)
                print(f"[INFO] Renamed: {fname} -> {safe_name}")

    print("=== Extraction completed ===")
    print(f"Check folder: {ORIGINALS_DIR} for downloaded files.")

if __name__ == "__main__":
    main()
