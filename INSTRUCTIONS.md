# ðŸ› ï¸ WhaleTermux â€” Complete Setup Instructions

> Step-by-step guide to create and host a custom Termux APT repository on Windows.

---

## ðŸ“‹ Prerequisites

- **Windows machine** with Python 3 installed
- **Android device** with [Termux](https://termux.com) installed
- Optional: [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) for better Linux compatibility

---

## ðŸ§­ Setup Overview

```
Step 1: Install Tools         â†’  pip install termux-apt-repo
Step 2: Build .deb Package    â†’  Create control file + scripts â†’ dpkg-deb --build
Step 3: Generate Repo         â†’  termux-apt-repo â†’ dists/stable/main/
Step 4: Host the Repo         â†’  Python HTTP / ngrok / GitHub Pages
Step 5: Install on Termux     â†’  pkg update && pkg install whale-agent
Bonus: Quick Script Install   â†’  curl â†’ chmod +x (no APT needed)
```

---

## Step 1: Set Up Windows as the Build Machine

### Option A: Native Python (Recommended for simplicity)

```cmd
pip3 install termux-apt-repo
```

### Option B: WSL (Better Linux compatibility)

```bash
# Install WSL if not already
wsl --install

# Inside WSL shell:
sudo apt update && sudo apt install python3-pip
pip3 install termux-apt-repo
```
```

---

## Step 2: Create Your Whale Agent .deb Package

### 2.1 Create the directory structure

```bash
mkdir -p whale-agent/DEBIAN
mkdir -p whale-agent/data/data/com.termux/files/usr/bin/
```

### 2.2 Create the control file

Write `whale-agent/DEBIAN/control`:

```
Package: whale-agent
Version: 1.0.0
Architecture: all
Maintainer: Your Name <your@email.com>
Description: Whale agent for Termux
 A custom tool for managing whale operations
```

### 2.3 Create the whale script

Write `whale-agent/data/data/com.termux/files/usr/bin/whale`:

```bash
#!/data/data/com.termux/files/usr/bin/bash
echo "ðŸ‹ Whale Agent v1.0.0"
echo "Welcome to the custom repository!"
# Add your actual whale logic here
```

Make it executable:

```bash
chmod +x whale-agent/data/data/com.termux/files/usr/bin/whale
```

### 2.4 Build the .deb package

```bash
dpkg-deb --build whale-agent
# Output: whale-agent.deb
```

---

## Step 3: Create the APT Repository Structure

```bash
# Create repo directories
mkdir termux-repo
mkdir termux-repo/debs

# Move your .deb into place
mv whale-agent.deb termux-repo/debs/

# Generate APT metadata
termux-apt-repo termux-repo/debs termux-repo/repo stable main
```

This creates the full Debian-style structure:

```
termux-repo/
â””â”€â”€ repo/
    â””â”€â”€ dists/
        â””â”€â”€ stable/
            â””â”€â”€ main/
                â”œâ”€â”€ binary-aarch64/
                â”‚   â”œâ”€â”€ Packages
                â”‚   â”œâ”€â”€ Packages.gz
                â”‚   â””â”€â”€ whale-agent.deb
                â”œâ”€â”€ binary-arm/
                â”œâ”€â”€ binary-x86_64/
                â””â”€â”€ binary-all/
                    â””â”€â”€ whale-agent.deb
```

---

## Step 4: Host the Repository

### Option A: Local Python HTTP Server (Testing)

```cmd
cd termux-repo/repo
python -m http.server 8000
```

Your repo will be available at `http://YOUR_WINDOWS_IP:8000`.
Find your IP with `ipconfig` in another terminal.

> âš ï¸ Only accessible on your local network. Firewall may block port 8000.

---

### Option B: ngrok Tunnel (Public/Demo)

```cmd
# Download ngrok from https://ngrok.com/download
# Then expose your local server
ngrok http 8000
```

You'll get a URL like `https://abc123.ngrok.io` â€” use this in Termux.

> âš ï¸ Free ngrok has rate limits and the URL changes each restart.

---

### Option C: GitHub Pages (Production â€” Recommended)

```bash
# Initialize a Git repo
cd termux-repo/repo
git init
git add .
git commit -m "Initial Termux repository"
git branch -M main

# Create a GitHub repo named "termux-whale-repo"
# (do this on GitHub.com first, don't add README/gitignore)

git remote add origin https://github.com/YOUR_USERNAME/termux-whale-repo.git
git push -u origin main
```

**On GitHub:**
1. Go to your repo â†’ **Settings** â†’ **Pages**
2. Under "Branch", select `main` and folder `/` (root)
3. Click **Save**

Your repo URL will be: `https://YOUR_USERNAME.github.io/termux-whale-repo/`

> âœ… Free, permanent, HTTPS-enabled, worldwide CDN!

---

## Step 5: Configure Termux (Android)

On your Android device, open Termux and run:

```bash
# Create sources list directory (if not exists)
mkdir -p $PREFIX/etc/apt/sources.list.d/

# For GitHub Pages:
echo "deb [trusted=yes] https://YOUR_USERNAME.github.io/termux-whale-repo stable main" \
  > $PREFIX/etc/apt/sources.list.d/whale.list

# For local network (replace IP with your Windows IP):
# echo "deb [trusted=yes] http://192.168.1.100:8000 stable main" \
#   > $PREFIX/etc/apt/sources.list.d/whale.list

# For ngrok:
# echo "deb [trusted=yes] https://abc123.ngrok.io stable main" \
#   > $PREFIX/etc/apt/sources.list.d/whale.list

# Update package lists
pkg update

# Install your whale agent!
pkg install whale-agent

# Test it
whale
```

Expected output:
```
ðŸ‹ Whale Agent v1.0.0
Welcome to the custom repository!
```

---

## ðŸš€ Bonus: Quick Script Installation (No APT)

If setting up a full APT repo is overkill, just serve the script directly:

### On Windows:
```bash
echo '#!/data/data/com.termux/files/usr/bin/bash
echo "ðŸ‹ Whale Agent Running!"
# Your whale logic here' > whale.sh

# Serve it via HTTP
python -m http.server 8000
```

### On Termux (Android):
```bash
curl -o $PREFIX/bin/whale http://YOUR_WINDOWS_IP:8000/whale.sh
chmod +x $PREFIX/bin/whale
whale
```

---

## ðŸ”„ Updating Your Package

When you update your whale agent:

```bash
# 1. Rebuild the .deb with new version in control file
dpkg-deb --build whale-agent

# 2. Copy the new .deb to debs/
copy whale-agent.deb termux-repo/debs/

# 3. Regenerate APT metadata
termux-apt-repo termux-repo/debs termux-repo/repo stable main

# 4. Re-push to GitHub Pages (if using that option)
cd termux-repo/repo
git add .
git commit -m "Update whale-agent to v1.0.1"
git push

# 5. On Termux, update:
pkg update && pkg upgrade
```

---

## ðŸŽ¯ Troubleshooting

| Problem | Solution |
|---------|----------|
| `pkg update` fails to connect | Check your Windows firewall, ensure server is running |
| `dpkg-deb` not found | Install `dpkg` via WSL or use a Linux environment |
| `termux-apt-repo` command not found | Ensure Python Scripts folder is in your PATH |
| GPG key errors | Add `[trusted=yes]` to the sources.list entry |
| Package not found after update | Wait a few minutes, or check `dists/stable/main/binary-all/` exists |
| Permission denied on whale script | Ensure `chmod +x` was run before building .deb |

---

## ðŸ’¡ Pro Tips

- **Architecture**: Use `all` for arch-independent scripts, or build for specific archs (`aarch64`, `arm`, `x86_64`)
- **Trusted Repo**: Add `[trusted=yes]` if you don't sign with GPG â€” keeps setup simple
- **Multiple Packages**: Add multiple `.deb` files to the `debs/` folder before running `termux-apt-repo`
- **CI/CD**: Automate rebuilds with GitHub Actions on each push
- **Testing**: Test your .deb locally before publishing by running `dpkg-deb --info whale-agent.deb`

---

## ðŸ“š Related Resources

- [Termux Wiki: Package Management](https://wiki.termux.com/wiki/Package_Management)
- [termux-apt-repo GitHub](https://github.com/termux/termux-apt-repo)
- [Debian .deb Packaging Guide](https://www.debian.org/doc/debian-policy/ch-controlfields.html)

---

<p align="center">ðŸ‹ Happy packaging!</p>