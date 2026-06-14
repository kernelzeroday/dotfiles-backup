#!/bin/bash
# Update everything — run periodically
export PATH="/bin:/usr/bin:/sbin:/usr/sbin:$PATH"

echo "=== brew ==="
brew upgrade
brew upgrade --casks -g
brew upgrade --fetch-HEAD kernelzeroday/metasploit/metasploit-framework 2>/dev/null

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


echo "=== done ==="
