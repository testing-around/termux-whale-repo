"""
build_all.py -- WhaleTermux Full Build Script
Called by build.bat to build .deb and generate APT repo.
Can also run standalone: python build_all.py

Requirements:
  pip install termux-apt-repo
  apt install dpkg xz-utils (Linux/WSL)
"""
import os, shutil, subprocess, sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(PROJECT_DIR, "whale-agent")
DEBS_DIR = os.path.join(PROJECT_DIR, "termux-repo", "debs")
REPO_DIR = os.path.join(PROJECT_DIR, "termux-repo", "repo")
WHALE_SCRIPT = os.path.join(PKG_DIR, "data", "data", "com.termux", "files", "usr", "bin", "whale")

def step(msg):
    print(f"\n{'='*50}\n  {msg}\n{'='*50}")

def run(cmd, cwd=None):
    print(f"  $ {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_DIR)
    if r.returncode != 0:
        print(f"  [ERROR] Command failed: {cmd}")
        sys.exit(1)

def main():
    step("1/3: Building .deb package")
    if not os.path.exists(PKG_DIR):
        print(f"  [ERROR] Package dir not found: {PKG_DIR}")
        sys.exit(1)
    if os.path.exists(WHALE_SCRIPT):
        os.chmod(WHALE_SCRIPT, 0o755)
        print("  whale script executable")
    deb_output = os.path.join(PROJECT_DIR, "whale-agent.deb")
    if os.path.exists(deb_output):
        os.remove(deb_output)
    run("dpkg-deb --build whale-agent")
    if not os.path.exists(deb_output):
        print("  [ERROR] .deb not created!")
        sys.exit(1)
    size = os.path.getsize(deb_output)
    print(f"  .deb built: {deb_output} ({size} bytes)")

    step("2/3: Setting up repo directories")
    os.makedirs(DEBS_DIR, exist_ok=True)
    os.makedirs(REPO_DIR, exist_ok=True)
    shutil.copy(deb_output, os.path.join(DEBS_DIR, "whale-agent.deb"))
    print(f"  .deb copied to {DEBS_DIR}")

    step("3/3: Generating APT repository metadata")
    run(f"termux-apt-repo {DEBS_DIR} {REPO_DIR} stable main")

    release_file = os.path.join(REPO_DIR, "dists", "stable", "Release")
    if os.path.exists(release_file):
        print(f"  Release file: {release_file}")
    print(f"\nBUILD COMPLETE")
    print(f"  .deb:      {deb_output}")
    print(f"  Packages:  {REPO_DIR}\\dists\\stable\\main\\binary-all\\Packages")
    print(f"  Release:   {release_file}")

if __name__ == "__main__":
    main()
