#!/bin/bash
# Update everything — works on macOS and Linux
set -e

echo "=== system packages ==="
if command -v brew &>/dev/null; then
  brew upgrade
  brew upgrade --casks -g 2>/dev/null || true
elif command -v apt &>/dev/null; then
  sudo apt update && sudo apt upgrade -y
  sudo apt autoremove -y
elif command -v dnf &>/dev/null; then
  sudo dnf upgrade -y
elif command -v yum &>/dev/null; then
  sudo yum update -y
elif command -v pacman &>/dev/null; then
  sudo pacman -Syu --noconfirm
elif command -v apk &>/dev/null; then
  sudo apk update && sudo apk upgrade
fi

echo ""
echo "=== rust ==="
command -v rustup &>/dev/null && rustup update
command -v cargo-install-update &>/dev/null && cargo install-update -a

echo ""
echo "=== go ==="
command -v gup &>/dev/null && gup update

echo ""
echo "=== python (uv) ==="
command -v uv &>/dev/null && uv tool upgrade --all

echo ""
echo "=== node ==="
command -v mise &>/dev/null && mise upgrade

echo ""
echo "=== projectdiscovery ==="
command -v pdtm &>/dev/null && pdtm -ua

echo ""
echo "=== exploit-db ==="
command -v getsploit &>/dev/null && getsploit -u

echo ""
echo "=== done ==="
