#!/bin/bash
# Bootstrap a fresh machine — run this before install.sh
set -e

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

# --- Core brew packages ---
echo ""
echo "installing brew packages..."
brew install \
  bash \
  git \
  gh \
  go \
  rustup \
  uv \
  mise \
  deno \
  bun \
  coreutils \
  ripgrep \
  fd \
  jq \
  aria2 \
  rga

# --- Rust toolchain ---
echo ""
if ! command -v rustc &>/dev/null; then
  echo "initializing rust toolchain..."
  rustup-init -y
  . "$HOME/.cargo/env"
else
  echo "rust: $(rustc --version)"
fi

# --- Cargo package managers ---
echo ""
echo "installing cargo tools..."
cargo install cargo-binstall
cargo binstall -y cargo-update

# --- Go updater ---
echo ""
echo "installing go tools..."
go install github.com/nao1215/gup@latest

# --- pdtm (ProjectDiscovery tool manager) ---
if ! command -v pdtm &>/dev/null; then
  echo ""
  echo "installing pdtm..."
  go install -v github.com/projectdiscovery/pdtm/cmd/pdtm@latest
else
  echo "pdtm: already installed"
fi

# --- mise globals ---
echo ""
echo "setting up mise..."
mise use --global node@latest

# --- Run install.sh ---
echo ""
echo "=== bootstrap done ==="
echo ""
echo "next steps:"
echo "  ./install.sh              # symlink dotfiles"
echo "  cargo binstall <tool>     # install rust CLI tools"
echo "  uv tool install <tool>    # install python CLI tools"
echo "  pdtm -ia                  # install projectdiscovery tools"
echo "  brew bundle               # (if you add a Brewfile later)"
