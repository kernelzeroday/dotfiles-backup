#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"

link() {
  src="$DIR/$1"
  dst="$HOME/$2"
  if [ -e "$dst" ] && [ ! -L "$dst" ]; then
    echo "  backing up $dst -> ${dst}.bak"
    mv "$dst" "${dst}.bak"
  fi
  ln -sf "$src" "$dst"
  echo "  $dst -> $src"
}

echo "linking dotfiles..."
link dotfiles/bashrc       .bashrc
link dotfiles/bash_profile .bash_profile
link dotfiles/inputrc      .inputrc
link dotfiles/zshrc        .zshrc
link dotfiles/zshenv       .zshenv
link dotfiles/profile      .profile
link dotfiles/gitconfig    .gitconfig
link dotfiles/gpg.conf     .gnupg/gpg.conf
link dotfiles/vimrc        .vimrc

mkdir -p "$HOME/ansi_art/sh_out"
link dotfiles/ansi_art/gengar.sh ansi_art/sh_out/gengar.sh

echo ""
echo "linking mise config..."
mkdir -p "$HOME/.config/mise"
link dotfiles/config/mise/config.toml .config/mise/config.toml

echo ""
echo "linking scripts to ~/bin..."
mkdir -p "$HOME/bin"
link scripts/update.sh bin/update.sh

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
