#!/usr/bin/env python3
"""Clone cleanyourtv at a pinned commit and verify that HEAD matches.

    py scripts/fetch_cleanyourtv.py [--dest PATH]

It only clones and leaves the tree at the pinned commit; it runs nothing from the repo.
After cloning it runs `git rev-parse HEAD` and compares it with COMMIT: if it does not
match, it exits with an error (exit 1) and nothing from that copy is used.

The default destination stays outside synced folders (Google Drive / OneDrive break
.git files). If the chosen path falls inside one, it warns and does not clone: pick
another one with --dest.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/Gathin23/cleanyourtv.git"
COMMIT = "6e8615eb0be0e843ceeebedae246d69f3e0a88d7"
DEFAULT_DEST = Path.home() / ".cache" / "smart-tv-tuneup" / "cleanyourtv"
# Markers of synced folders (compared in lowercase against every part of the path).
# "Mi unidad" is Google Drive in Spanish.
SYNCED_FOLDERS = ("mi unidad", "onedrive", "google drive", "dropbox", "icloud")


def is_synced_folder(path):
    """True if the path falls inside a known synced folder."""
    parts = [p.lower() for p in Path(path).expanduser().resolve().parts]
    return any(marker in part for part in parts for marker in SYNCED_FOLDERS)


def head_of(path):
    """HEAD of the repo at `path`, or None if there is no repo or git fails."""
    if not (Path(path) / ".git").exists():
        return None
    try:
        out = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def run(cmd):
    """Run a git command and return (ok, text)."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    text = (out.stdout + out.stderr).strip()
    return out.returncode == 0, text


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clone cleanyourtv at the pinned commit and verify HEAD.")
    parser.add_argument("--dest", help="where to clone (default %s)" % DEFAULT_DEST)
    args = parser.parse_args(argv)

    dest = Path(args.dest).expanduser() if args.dest else DEFAULT_DEST

    if is_synced_folder(dest):
        print("That path is inside a synced folder (%s). Syncing "
              "breaks .git files." % dest, file=sys.stderr)
        print("Pick another one with --dest, for example: --dest %s"
              % (Path.home() / ".cache" / "smart-tv-tuneup" / "cleanyourtv"), file=sys.stderr)
        return 2

    if shutil.which("git") is None:
        print("git was not found in PATH: install it before cloning.", file=sys.stderr)
        return 2

    if dest.exists():
        head = head_of(dest)
        if head is None:
            print("%s exists but is not a usable git repo: delete it or pick another "
                  "--dest (nothing is touched unless you ask)." % dest, file=sys.stderr)
            return 1
        if head == COMMIT:
            print("OK: %s is already at the pinned commit %s." % (dest, COMMIT))
            print("Do not run anything from that repo without reviewing it; see references/android.md.")
            return 0
        print("FAIL: the HEAD of %s is %s and %s was expected. That copy is not used."
              % (dest, head, COMMIT), file=sys.stderr)
        print("Delete the folder or pick another --dest; nothing is modified on your own.",
              file=sys.stderr)
        return 1

    print("Cloning %s into %s ..." % (REPO, dest))
    ok, text = run(["git", "clone", REPO, str(dest)])
    if not ok:
        print("clone failed: %s" % text, file=sys.stderr)
        return 1

    ok, text = run(["git", "-C", str(dest), "checkout", "--detach", COMMIT])
    if not ok:
        print("checkout of the pinned commit failed: %s" % text, file=sys.stderr)
        return 1

    head = head_of(dest)
    if head != COMMIT:
        print("FAIL: the verified HEAD is %s and %s was expected: that copy is not used."
              % (head, COMMIT), file=sys.stderr)
        return 1

    print("OK: HEAD verified = %s" % head)
    print("That only leaves the code at hand: read and review it before running anything "
          "from inside. Do not run repo scripts automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
