#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

deploy() {
  src="$DIR/$1"
  dst="$HOME/$2"
  if [ -L "$dst" ]; then
    rm "$dst"
  elif [ -e "$dst" ]; then
    echo "  backing up $dst -> ${dst}.bak"
    mv "$dst" "${dst}.bak"
  fi
  cp "$src" "$dst"
  echo "  $src -> $dst"
}

echo "installing dotfiles..."
deploy dotfiles/bashrc       .bashrc
deploy dotfiles/bash_profile .bash_profile
deploy dotfiles/inputrc      .inputrc
deploy dotfiles/zshrc        .zshrc
deploy dotfiles/zshenv       .zshenv
deploy dotfiles/profile      .profile
deploy dotfiles/gitconfig    .gitconfig
deploy dotfiles/gpg.conf     .gnupg/gpg.conf
deploy dotfiles/vimrc        .vimrc

mkdir -p "$HOME/ansi_art/sh_out"
deploy dotfiles/ansi_art/gengar.sh ansi_art/sh_out/gengar.sh

echo ""
echo "installing mise config..."
mkdir -p "$HOME/.config/mise"
deploy dotfiles/config/mise/config.toml .config/mise/config.toml

echo ""
echo "installing scripts to ~/bin..."
mkdir -p "$HOME/bin"
deploy scripts/update.sh bin/update.sh
deploy scripts/update.osx.sh bin/update.osx.sh

echo ""
if command -v cargo &>/dev/null; then
  echo "building subversivequote..."
  cargo install --path "$DIR/subversive" --quiet
  echo "  installed subversivequote"
else
  echo "cargo not found, skipping subversivequote (install rust first)"
fi

echo ""
echo "done. open a new shell."
