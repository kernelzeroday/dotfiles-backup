#!/bin/bash
# Bootstrap a fresh machine with core tools before running install.sh
set -e

echo "=== bootstrap ==="

# Homebrew
if ! command -v brew &>/dev/null; then
  echo "installing homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add to current session
  if [ -d /opt/homebrew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -d /home/linuxbrew/.linuxbrew ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  fi
else
  echo "homebrew: already installed"
fi

# Rust
if ! command -v cargo &>/dev/null; then
  echo "installing rust..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
  . "$HOME/.cargo/env"
else
  echo "rust: already installed ($(rustc --version))"
fi

# mise
if ! command -v mise &>/dev/null; then
  echo "installing mise..."
  brew install mise
else
  echo "mise: already installed ($(mise --version))"
fi

# Core brew packages
echo ""
echo "installing core packages..."
brew install bash git gh coreutils ripgrep fd jq

# Set up mise globals
if command -v mise &>/dev/null; then
  echo ""
  echo "setting up mise..."
  mise use --global node@latest
fi

echo ""
echo "bootstrap done. now run ./install.sh"
