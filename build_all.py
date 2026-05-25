"""
build_all.py -- WhaleTermux Full Build Script
Called by build.bat to build .deb and generate APT repo.
Can also run standalone: python build_all.py

Works on Windows natively (no WSL/dpkg-deb required).
Also works on Linux/macOS if dpkg-deb is available.
"""
import os, shutil, subprocess, sys, tarfile, io, hashlib, gzip, datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(PROJECT_DIR, "whale-agent")
DEBS_DIR = os.path.join(PROJECT_DIR, "termux-repo", "debs")
REPO_DIR = os.path.join(PROJECT_DIR, "termux-repo", "repo")
WHALE_SCRIPT = os.path.join(PKG_DIR, "data", "data", "com.termux", "files", "usr", "bin", "whale")
ARCHES = ["all", "aarch64", "arm", "x86_64", "i686"]

def step(msg):
    print(f"\n{'='*50}\n  {msg}\n{'='*50}")

def build_deb_windows():
    """Build .deb using pure Python (no dpkg-deb needed). Works on Windows."""
    deb_path = os.path.join(PROJECT_DIR, "whale-agent.deb")
    if os.path.exists(deb_path):
        os.remove(deb_path)
    debian_binary = b"2.0\n"
    control_buf = io.BytesIO()
    ctrl_file = os.path.join(PKG_DIR, "DEBIAN", "control")
    if not os.path.exists(ctrl_file):
        print("  [ERROR] DEBIAN/control not found!")
        sys.exit(1)
    with tarfile.open(fileobj=control_buf, mode="w:gz") as tar:
        tar.add(ctrl_file, arcname="control")
    control_data = control_buf.getvalue()
    data_buf = io.BytesIO()
    data_dir = os.path.join(PKG_DIR, "data")
    if not os.path.exists(data_dir):
        print("  [ERROR] data/ directory not found!")
        sys.exit(1)
    with tarfile.open(fileobj=data_buf, mode="w:gz") as tar:
        for root, _dirs, files in os.walk(data_dir):
            for fn in files:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, data_dir).replace("\\", "/")
                tar.add(fp, arcname=rel)
    data_data = data_buf.getvalue()
    with open(deb_path, "wb") as f:
        f.write(b"!<arch>\n")
        for name, content in [
            ("debian-binary", debian_binary),
            ("control.tar.gz", control_data),
            ("data.tar.gz", data_data),
        ]:
            name_b = name.encode("ascii")
            size_val = len(content)
            header = (
                name_b.ljust(16)
                + b"0".rjust(12)
                + b"0".rjust(6)
                + b"0".rjust(6)
                + b"100644".rjust(8)
                + str(size_val).encode("ascii").rjust(10)
                + b"\x60\n"
            )
            assert len(header) == 60
            f.write(header)
            f.write(content)
            if size_val % 2 != 0:
                f.write(b"\n")
    size = os.path.getsize(deb_path)
    print(f"  .deb built natively: {deb_path} ({size} bytes)")
    return deb_path

def compute_hashes(filepath):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
            sha512.update(chunk)
    return {
        "md5": md5.hexdigest(),
        "sha1": sha1.hexdigest(),
        "sha256": sha256.hexdigest(),
        "sha512": sha512.hexdigest(),
    }

def parse_control_from_deb(deb_path):
    with open(deb_path, "rb") as f:
        raw = f.read()
    pos = 8
    while pos < len(raw):
        h = raw[pos:pos+60]
        if len(h) < 60:
            break
        name = h[0:16].decode("ascii").strip()
        sz = int(h[48:58].decode("ascii").strip())
        if name == "control.tar.gz":
            content = raw[pos+60:pos+60+sz]
            tar = tarfile.open(fileobj=io.BytesIO(content))
            fields = {}
            for m in tar.getmembers():
                if m.name == "control":
                    raw_ctrl = tar.extractfile(m).read().decode("utf-8")
                    key = None
                    for line in raw_ctrl.split("\n"):
                        ls = line.strip()
                        if not ls:
                            continue
                        if ":" in line and line[0].isalpha():
                            k, v = line.split(":", 1)
                            key = k.strip()
                            fields[key] = v.strip()
                        elif key and line.startswith(" "):
                            fields[key] += "\n" + line.strip()
                    break
            tar.close()
            return fields
        pos += 60 + sz
        if sz % 2 != 0:
            pos += 1
    return {}

def generate_packages_stanza(deb_filename, deb_path):
    ctrl = parse_control_from_deb(deb_path)
    hashes = compute_hashes(deb_path)
    size = os.path.getsize(deb_path)
    lines = []
    lines.append(f"Package: {ctrl.get('Package', 'unknown')}")
    lines.append(f"Version: {ctrl.get('Version', '0.0')}")
    lines.append(f"Architecture: {ctrl.get('Architecture', 'all')}")
    lines.append(f"Maintainer: {ctrl.get('Maintainer', 'unknown')}")
    lines.append(f"Installed-Size: {(size+1023)//1024}")
    lines.append(f"Filename: {deb_filename}")
    lines.append(f"Size: {size}")
    lines.append(f"MD5sum: {hashes['md5']}")
    lines.append(f"SHA1: {hashes['sha1']}")
    lines.append(f"SHA256: {hashes['sha256']}")
    lines.append(f"SHA512: {hashes['sha512']}")
    desc = ctrl.get("Description", "")
    if desc:
        parts = desc.split("\n", 1)
        lines.append(f"Description: {parts[0]}")
        if len(parts) > 1:
            for dl in parts[1].split("\n"):
                dl = dl.strip()
                if dl:
                    lines.append(f" {dl}")
                else:
                    lines.append(" .")
    lines.append("")
    return "\n".join(lines)

def generate_repo():
    debs = [f for f in os.listdir(DEBS_DIR) if f.endswith(".deb")]
    print(f"  Found {len(debs)} .deb file(s): {debs}")
    for arch in ARCHES:
        binary_dir = os.path.join(REPO_DIR, "dists", "stable", "main", f"binary-{arch}")
        os.makedirs(binary_dir, exist_ok=True)
        entries = []
        for deb_name in debs:
            src = os.path.join(DEBS_DIR, deb_name)
            dst = os.path.join(binary_dir, deb_name)
            shutil.copy2(src, dst)
            entries.append(generate_packages_stanza(deb_name, src))
        pc = "\n".join(entries)
        with open(os.path.join(binary_dir, "Packages"), "w") as f:
            f.write(pc)
        with gzip.open(os.path.join(binary_dir, "Packages.gz"), "wt") as f:
            f.write(pc)
        print(f"  binary-{arch}: Packages ({len(pc)} bytes)")
    md5_e, sha1_e, sha256_e = [], [], []
    ds = os.path.join(REPO_DIR, "dists", "stable")
    for arch in ARCHES:
        base = f"main/binary-{arch}"
        for fn in ("Packages", "Packages.gz"):
            fp = os.path.join(ds, base, fn)
            if os.path.exists(fp):
                h = compute_hashes(fp)
                sz = os.path.getsize(fp)
                r = f"{base}/{fn}"
                md5_e.append(f" {h['md5']} {sz:>8} {r}")
                sha1_e.append(f" {h['sha1']} {sz:>8} {r}")
                sha256_e.append(f" {h['sha256']} {sz:>8} {r}")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S UTC")
    rel_lines = [
        "Origin: WhaleTermux",
        "Label: WhaleTermux",
        "Suite: stable",
        "Codename: stable",
        f"Date: {now}",
        f"Architectures: {' '.join(ARCHES)}",
        "Components: main",
        "Description: Custom Termux APT repository for the Whale Agent",
        "",
        "MD5Sum:",
    ]
    rel_lines.extend(md5_e)
    rel_lines.append("")
    rel_lines.append("SHA1:")
    rel_lines.extend(sha1_e)
    rel_lines.append("")
    rel_lines.append("SHA256:")
    rel_lines.extend(sha256_e)
    rel_lines.append("")
    rel = "\n".join(rel_lines)
    rp = os.path.join(ds, "Release")
    with open(rp, "w") as f:
        f.write(rel)
    print(f"  Release file: {rp} ({len(rel)} bytes)")

def main():
    step("1/3: Building .deb package")
    if not os.path.exists(PKG_DIR):
        print(f"  [ERROR] Package dir not found: {PKG_DIR}")
        sys.exit(1)
    if os.path.exists(WHALE_SCRIPT):
        try:
            os.chmod(WHALE_SCRIPT, 0o755)
        except Exception:
            pass
    use_native = True
    try:
        subprocess.run(["dpkg-deb", "--version"], capture_output=True)
        use_native = False
    except FileNotFoundError:
        pass
    if use_native:
        deb_output = build_deb_windows()
        print("  [info] Used Windows-native .deb builder (dpkg-deb not found)")
    else:
        deb_output = os.path.join(PROJECT_DIR, "whale-agent.deb")
        if os.path.exists(deb_output):
            os.remove(deb_output)
        subprocess.run("dpkg-deb --build whale-agent", shell=True, cwd=PROJECT_DIR, check=True)
        print(f"  .deb built: {deb_output} ({os.path.getsize(deb_output)} bytes)")
    step("2/3: Setting up repo directories")
    os.makedirs(DEBS_DIR, exist_ok=True)
    os.makedirs(REPO_DIR, exist_ok=True)
    shutil.copy(deb_output, os.path.join(DEBS_DIR, "whale-agent.deb"))
    print(f"  .deb copied to {DEBS_DIR}")
    step("3/3: Generating APT repository metadata")
    if use_native:
        generate_repo()
        print("  [info] Used Windows-native APT repo generator (termux-apt-repo not needed)")
    else:
        subprocess.run(
            f"termux-apt-repo {DEBS_DIR} {REPO_DIR} stable main", shell=True, check=True
        )
    rf = os.path.join(REPO_DIR, "dists", "stable", "Release")
    if os.path.exists(rf):
        print(f"  Release file: {rf}")
    sep = "=" * 50
    print(f"\n{sep}\n  BUILD COMPLETE\n{sep}")
    print(f"  .deb:      {deb_output}")
    ppath = os.path.join(REPO_DIR, "dists", "stable", "main", "binary-all", "Packages")
    print(f"  Packages:  {ppath}")
    print(f"  Release:   {rf}")

if __name__ == "__main__":
    main()
