# ðŸ‹ WhaleTermux â€” Custom Termux APT Repository

[![Platform](https://img.shields.io/badge/Platform-Android-3DDC84?logo=android)](https://termux.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/your-username/termux-whale-repo/graphs/commit-activity)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/your-username/termux-whale-repo/pulls)

> **Host your own custom Termux APT repository on Windows** â€” distribute your whale agent (or any tool) to Android Termux users with `pkg install`!

---

## ðŸ” Overview

**WhaleTermux** is a complete starter kit for creating and hosting a **custom Termux APT repository** from your Windows machine. Whether you want to distribute a personal tool like the **Whale Agent** or build a full-fledged package repository, this guide has you covered.

### âœ¨ What You Get

| Feature | Description |
|---------|-------------|
| ðŸ“¦ **Custom .deb Packages** | Build Termux-compatible packages with ease |
| ðŸ—‚ï¸ **APT Repository Structure** | Full Debian-style `dists/` layout |
| ðŸŒ **Multiple Hosting Options** | Local HTTP, ngrok tunnel, or GitHub Pages |
| ðŸ“± **One-Liner Install** | Users install with `pkg install whale-agent` |
| ðŸš€ **Quick Alternative** | Direct script download if APT is overkill |

---

## ðŸ“ Project Structure

```
whaletermux/
â”œâ”€â”€ README.md              â† You are here
â”œâ”€â”€ INDEX.md               â† File structure map & navigation
â”œâ”€â”€ INSTRUCTIONS.md        â† Complete step-by-step setup guide
â”œâ”€â”€ termux-repo-guide.md   â† Raw chat export reference
â”œâ”€â”€ whale-agent/           â† .deb package workspace
â”‚   â”œâ”€â”€ DEBIAN/
â”‚   â”‚   â””â”€â”€ control        â† Package metadata
â”‚   â””â”€â”€ data/              â† Installable files
â””â”€â”€ termux-repo/           â† Generated APT repository
    â””â”€â”€ repo/
        â””â”€â”€ dists/
            â””â”€â”€ stable/
                â””â”€â”€ main/
                    â”œâ”€â”€ binary-aarch64/
                    â”œâ”€â”€ binary-arm/
                    â”œâ”€â”€ binary-x86_64/
                    â””â”€â”€ binary-all/
```

---

## ðŸš€ Quick Start

```bash
# 1. Install tools on Windows
pip3 install termux-apt-repo

# 2. Build your .deb package
mkdir -p whale-agent/DEBIAN
mkdir -p whale-agent/data/data/com.termux/files/usr/bin/
# ... add your control file and scripts
dpkg-deb --build whale-agent

# 3. Create repo & serve locally
mkdir termux-repo/debs
mv whale-agent.deb termux-repo/debs/
termux-apt-repo termux-repo/debs termux-repo/repo stable main
cd termux-repo/repo && python -m http.server 8000

# 4. On Android (Termux), add the repo & install
echo "deb [trusted=yes] http://YOUR_WINDOWS_IP:8000 stable main" \
  > $PREFIX/etc/apt/sources.list.d/whale.list
pkg update && pkg install whale-agent
```

> ðŸ“– **Full instructions â†’ [INSTRUCTIONS.md](INSTRUCTIONS.md)**

---

## ðŸ“¦ Hosting Options

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Local Python HTTP** | Zero config, instant | Local network only | Testing & development |
| **ngrok Tunnel** | Public URL, HTTPS | Temporary URL, rate limits | Demos & sharing |
| **GitHub Pages** | Free, permanent, HTTPS | Public by default | Production release |

---

## ðŸ” Security Notes

- Add `[trusted=yes]` for unsigned repos, or sign with GPG for production
- GitHub Pages repos are **public** â€” don't put sensitive data in packages
- For private distribution, use ngrok with authentication or a local VPN

---

## ðŸ¤ Contributing

Found a bug? Want to add a package? PRs welcome!

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-package`)
3. Build and test your .deb
4. Commit and push
5. Open a Pull Request

---

## ðŸ“„ License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

---

## ðŸ™ Acknowledgments

- [Termux](https://termux.com) â€” The amazing Android terminal emulator
- [termux-apt-repo](https://github.com/termux/termux-apt-repo) â€” APT repo tooling

---

<p align="center">Built with ðŸ‹ by Carbon</p>