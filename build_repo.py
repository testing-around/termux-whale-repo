#!/usr/bin/env python3
"""
build_repo.py -- Manual APT repository generator.
Replaces termux-apt-repo which has compatibility issues with newer dpkg-deb.
"""
import os, sys, hashlib, gzip, subprocess, shutil, json
from datetime import datetime, timezone

DEBS_DIR = "termux-repo/debs"
REPO_DIR = "termux-repo/repo"
SUITE = "stable"
COMPONENT = "main"
ARCHES = ["all", "aarch64", "arm", "x86_64", "i686"]

def get_deb_info(deb_path):
    """Extract package info from .deb using dpkg-deb."""
    result = subprocess.run(
        ["dpkg-deb", "--info", deb_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: dpkg-deb --info failed: {result.stderr}")
        return None
    
    # Parse the output
    info = {}
    for line in result.stdout.split('\n'):
        line = line.strip()
        if ':' in line:
            key, val = line.split(':', 1)
            info[key.strip().lower()] = val.strip()
    
    # Also get file info
    size = os.path.getsize(deb_path)
    info['size'] = str(size)
    
    with open(deb_path, 'rb') as f:
        data = f.read()
    info['md5sum'] = hashlib.md5(data).hexdigest()
    info['sha1'] = hashlib.sha1(data).hexdigest()
    info['sha256'] = hashlib.sha256(data).hexdigest()
    
    filename = os.path.basename(deb_path)
    info['filename'] = filename
    
    return info


def generate_packages_stanza(info):
    """Generate a single Packages stanza."""
    lines = []
    lines.append(f"Package: {info.get('package', 'unknown')}")
    lines.append(f"Version: {info.get('version', '0.0')}")
    lines.append(f"Architecture: {info.get('architecture', 'all')}")
    lines.append(f"Maintainer: {info.get('maintainer', 'unknown')}")
    lines.append(f"Installed-Size: {info.get('installed-size', '1')}")
    lines.append(f"Filename: {info['filename']}")
    lines.append(f"Size: {info['size']}")
    lines.append(f"MD5sum: {info['md5sum']}")
    lines.append(f"SHA1: {info['sha1']}")
    lines.append(f"SHA256: {info['sha256']}")
    if 'description' in info:
        lines.append(f"Description: {info['description']}")
    lines.append("")  # empty line between stanzas
    return '\n'.join(lines)


def main():
    print("=== Building APT Repository ===")
    
    # Find all .deb files
    debs = [f for f in os.listdir(DEBS_DIR) if f.endswith('.deb')]
    if not debs:
        print("ERROR: No .deb files found!")
        sys.exit(1)
    
    print(f"Found {len(debs)} .deb files")
    
    # Process each .deb
    all_info = []
    for deb in debs:
        path = os.path.join(DEBS_DIR, deb)
        print(f"  Processing: {deb}")
        info = get_deb_info(path)
        if info is None:
            print(f"  SKIPPING {deb} (could not read)")
            continue
        print(f"    Package: {info.get('package', '?')} v{info.get('version', '?')}")
        all_info.append(info)
    
    if not all_info:
        print("ERROR: No valid .deb files!")
        sys.exit(1)
    
    # Create architecture directories and write Packages files
    for arch in ARCHES:
        arch_dir = os.path.join(REPO_DIR, "dists", SUITE, COMPONENT, f"binary-{arch}")
        os.makedirs(arch_dir, exist_ok=True)
        
        # Filter packages for this architecture (all matches everything)
        arch_packages = [i for i in all_info if i.get('architecture') == arch or i.get('architecture') == 'all']
        
        if not arch_packages:
            # Still create empty Packages for consistency
            arch_packages = all_info  # all packages go everywhere
        
        # Generate Packages content
        packages_content = ""
        for info in arch_packages:
            packages_content += generate_packages_stanza(info)
        
        # Write Packages
        packages_path = os.path.join(arch_dir, "Packages")
        with open(packages_path, 'w') as f:
            f.write(packages_content)
        print(f"  Written: {packages_path} ({len(packages_content)} bytes)")
        
        # Write Packages.gz
        packages_gz_path = os.path.join(arch_dir, "Packages.gz")
        with gzip.open(packages_gz_path, 'wt', encoding='utf-8') as f:
            f.write(packages_content)
        print(f"  Written: {packages_gz_path}")
        
        # Copy .deb files
        for info in arch_packages:
            src = os.path.join(DEBS_DIR, info['filename'])
            dst = os.path.join(arch_dir, info['filename'])
            shutil.copy2(src, dst)
            print(f"  Copied: {info['filename']} -> {arch_dir}")
    
    # Generate Release file
    release_path = os.path.join(REPO_DIR, "dists", SUITE, "Release")
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    
    # Collect hashes for all files
    md5_lines = []
    sha1_lines = []
    sha256_lines = []
    
    for root, dirs, files in os.walk(os.path.join(REPO_DIR, "dists")):
        for f in files:
            if f == "Release":
                continue
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, os.path.join(REPO_DIR, "dists", SUITE))
            with open(filepath, 'rb') as fh:
                data = fh.read()
            
            md5 = hashlib.md5(data).hexdigest()
            sha1 = hashlib.sha1(data).hexdigest()
            sha256 = hashlib.sha256(data).hexdigest()
            size = len(data)
            
            md5_lines.append(f" {md5} {size:8} {relpath}")
            sha1_lines.append(f" {sha1} {size:8} {relpath}")
            sha256_lines.append(f" {sha256} {size:8} {relpath}")
    
    release_content = f"""Origin: WhaleTermux
Label: WhaleTermux
Suite: {SUITE}
Codename: {SUITE}
Date: {now}
Architectures: {' '.join(ARCHES)}
Components: {COMPONENT}
Description: Custom Termux APT repository for the Whale Agent

MD5Sum:
""" + '\n'.join(md5_lines) + """
SHA1:
""" + '\n'.join(sha1_lines) + """
SHA256:
""" + '\n'.join(sha256_lines) + "\n"
    
    with open(release_path, 'w') as f:
        f.write(release_content)
    print(f"\n  Written: {release_path}")
    
    print("\n=== APT Repository Generated ===")
    print(f"  Packages: {len(all_info)} package(s)")
    print(f"  Arches:   {', '.join(ARCHES)}")
    print(f"  Release:  {release_path}")
    
    # Copy .deb files to repo root too (for APT compatibility)
    for info in all_info:
        src = os.path.join(DEBS_DIR, info['filename'])
        dst = os.path.join(REPO_DIR, info['filename'])
        shutil.copy2(src, dst)
        print(f"  Copied to root: {info['filename']}")

    # List final structure
    print("\n=== Final Structure ===")
    for root, dirs, files in os.walk(REPO_DIR):
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, REPO_DIR)
            size = os.path.getsize(path)
            print(f"  {rel} ({size} bytes)")


if __name__ == "__main__":
    main()
