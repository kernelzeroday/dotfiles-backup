#!/bin/bash
# Update everything — run periodically
export PATH="/bin:/usr/bin:/sbin:/usr/sbin:$PATH"

echo "=== brew ==="
brew upgrade
brew upgrade --casks -g

echo "=== rust ==="
rustup update
cargo install-update -a

echo "=== go ==="
command -v gup &>/dev/null && gup update

echo "=== python (uv) ==="
command -v uv &>/dev/null && uv tool upgrade --all

echo "=== projectdiscovery ==="
command -v pdtm &>/dev/null && pdtm -ua

echo "=== exploit-db ==="
command -v getsploit &>/dev/null && getsploit -u

echo "=== metasploit ==="
command -v msfupdate &>/dev/null && msfupdate

echo "=== done ==="
