#!/data/data/com.termux/files/usr/bin/bash
# install.sh -- Whale Agent one-liner installer for Termux
# Usage: curl -sL https://testing-around.github.io/termux-whale-repo/install.sh | bash

set -e
REPO_URL="https://testing-around.github.io/termux-whale-repo"
PACKAGE_NAME="whale-agent"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
info() { printf "${CYAN}%s${NC}\n" "$*"; }
ok()   { printf "${GREEN}%s${NC}\n" "$*"; }
warn() { printf "${YELLOW}%s${NC}\n" "$*"; }
error(){ printf "${RED}%s${NC}\n" "$*"; }

echo "=== Checking Environment ==="
if [ -z "$PREFIX" ]; then error "Not in Termux!"; exit 1; fi
ok "Termux detected: $PREFIX"

echo "=== Adding Whale Repo ==="
mkdir -p $PREFIX/etc/apt/sources.list.d
echo "deb [trusted=yes] $REPO_URL stable main" > $PREFIX/etc/apt/sources.list.d/whale.list
ok "Repo added"

echo "=== Updating Package Lists ==="
pkg update -y || { error "Update failed"; exit 1; }
ok "Updated"

echo "=== Installing $PACKAGE_NAME ==="
pkg install -y "$PACKAGE_NAME" || { error "Install failed"; exit 1; }
ok "Installed!"

echo ""
echo "  __        __   _    "
echo "  \ \      / /__| |__ "
echo "   \ \ /\ / / _ \ '_ \\"
echo "    \ V  V /  __/ | | |"
echo "     \_/\_/ \___|_| |_|"
echo ""
echo -e "${GREEN}Whale Agent installed! Run: whale${NC}"
