#!/bin/bash
# Bootstrap a fresh machine — run this before install.sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== bootstrap ==="

# --- Homebrew ---
if ! command -v brew &>/dev/null; then
  echo "installing homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -d /opt/homebrew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -d /home/linuxbrew/.linuxbrew ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi
else
  echo "homebrew: $(brew --version | head -1)"
fi

# --- Brew packages from list ---
echo ""
echo "installing brew packages..."
grep -v '^#' "$DIR/packages/brew.txt" | grep -v '^$' | xargs brew install

# --- Rust toolchain ---
echo ""
if ! command -v rustc &>/dev/null; then
  echo "initializing rust toolchain..."
  rustup-init -y
  . "$HOME/.cargo/env"
else
  echo "rust: $(rustc --version)"
fi

# --- Cargo package managers + published crates ---
echo ""
echo "installing cargo tools..."
cargo install cargo-binstall
cargo binstall -y cargo-update
echo "installing cargo packages from list..."
grep -v '^#' "$DIR/packages/cargo.txt" | grep -v '^$' | xargs cargo binstall -y

# --- uv tools from list ---
echo ""
echo "installing uv tools..."
grep -v '^#' "$DIR/packages/uv.txt" | grep -v '^$' | while read -r pkg; do
  uv tool install "$pkg" 2>/dev/null || echo "  warning: $pkg failed"
done

# --- Go tools ---
echo ""
echo "installing go tools..."
go install github.com/nao1215/gup@latest
go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest

# --- mise globals ---
echo ""
echo "setting up mise..."
mise use --global node@latest

# --- Cleanup ---
echo ""
echo "cleaning up..."
brew cleanup -s

echo ""
echo "=== bootstrap done ==="
echo ""
echo "next steps:"
echo "  ./install.sh                    # symlink dotfiles + build subversivequote"
echo "  pdtm -ia                        # install projectdiscovery tools"
echo ""
echo "local rust projects (if you have ~/code cloned):"
echo "  cat packages/cargo-local.txt    # list of local-only rust projects"
echo "  cargo install --path ~/code/X   # install one"
