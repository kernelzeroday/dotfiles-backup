# dotfiles

15 years of bash configuration, finally cleaned up and optimized.

## The Big Win: 825ms → 31ms Shell Startup

The single biggest improvement came from removing **one line**:

```bash
[[ -r "/opt/homebrew/etc/profile.d/bash_completion.sh" ]] && . "/opt/homebrew/etc/profile.d/bash_completion.sh"
```

Homebrew's `bash-completion@2` eagerly loads **178 completion scripts** at startup. Every single shell open paid a 760ms tax for tab-completions you mostly never use. Removing it brought startup from 825ms to ~65ms. The rest of the gains came from switching nvm to mise shims.

If you use Homebrew bash-completion and your shell feels slow, this is probably why.

## New Machine Setup

```bash
git clone https://github.com/kernelzeroday/dotfiles-backup
cd dotfiles-backup
./bootstrap.sh    # install homebrew, rust, go, uv, mise, all packages
./install.sh      # symlink dotfiles, build subversivequote, link update.sh
```

`bootstrap.sh` installs everything through Homebrew where possible (rustup, go, uv, mise, deno, bun, mpv, etc.), then sets up cargo-binstall, gup, and pdtm. Package lists are data-driven — edit a text file, not a script.

`install.sh` symlinks all dotfiles into `$HOME`, backs up anything that already exists as `.bak`, builds subversivequote from source, and links `scripts/update.sh` into `~/bin`.

Both scripts work on macOS and Linux.

## Keeping Things Updated

```bash
update.sh    # symlinked to ~/bin by install.sh
```

Detects the system package manager (brew/apt/dnf/yum/pacman/apk) and updates everything: system packages, rust toolchain + cargo bins, go bins, uv tools, mise, projectdiscovery tools, and exploit-db. Cleans package manager caches between steps to save disk on tight boxes.

## Design Decisions

### bash over zsh

zsh has better built-in completion and globbing. bash has readline, `.inputrc`, POSIX compatibility, and 15 years of muscle memory. The actual language differences don't matter at the prompt — the things zsh does better (arrays, floating point) belong in scripts, which are better written in Python or Rust anyway.

Both shells are configured identically here. bash is the daily driver.

### nvm → mise (shims mode)

nvm's lazy-loading hack (wrapping `node`, `npm`, `npx` in shell functions) is clever but fragile. mise with `shims` mode just adds a directory to `$PATH` — zero shell overhead, no function wrappers, no prompt hooks. The tradeoff is that mise shims don't auto-switch versions on `cd` into a project directory (you'd need `eval "$(mise activate bash)"` for that, which adds ~48ms). Shims + a global `node = "latest"` is the right call unless you're constantly switching Node versions between projects.

### No bash-completion, no oh-my-zsh

Both are startup time disasters that solve problems most people don't have. bash-completion eagerly sources 178 scripts. oh-my-zsh loads a plugin framework. If you need completion for a specific tool, add that one completion — don't load all of them.

zsh's built-in `compinit` with `-C` (cached) is fast and good enough. It loads lazily and caches the dump file, only regenerating every 24 hours.

### Cross-OS compatibility

**Shell init files:** macOS terminals open login shells (reads `.bash_profile`). Linux terminals open non-login interactive shells (reads `.bashrc`). If your config is in `.bash_profile`, Linux gets a bare shell. The fix:

- `.bashrc` — everything, with `[[ $- != *i* ]] && return` to guard interactive-only stuff
- `.bash_profile` — one line: `[ -f ~/.bashrc ] && . ~/.bashrc`

Non-interactive shells (scp, rsync, cron) get PATH and env vars but skip the prompt, art, and quotes.

**Homebrew detection:** PATH auto-detects Homebrew's location (`/opt/homebrew` on macOS, `/home/linuxbrew/.linuxbrew` on Linux) instead of hardcoding. Missing directories are skipped cleanly.

**Guarded dependencies:** mise shims, gengar art, subversivequote, iTerm2 integration, and cargo env are all checked before loading. The shell works on a bare machine with nothing installed — no errors, no missing command noise.

### Vi mode in both shells

bash uses readline (`.inputrc`). zsh uses ZLE (`bindkey`). They're completely different systems that do the same thing. The config translates between them:

| Feature | bash (.inputrc) | zsh (.zshrc) |
|---------|----------------|--------------|
| Enable vi mode | `set editing-mode vi` | `bindkey -v` |
| Mode indicator | `vi-ins-mode-string` / `vi-cmd-mode-string` | `zle-keymap-select` widget |
| Clear screen | `Control-l: clear-screen` per keymap | `bindkey -M viins/vicmd '^L'` |
| Fast Escape | (readline default is fine) | `KEYTIMEOUT=1` |
| Cursor shape | not supported in readline | `\e[2 q` / `\e[6 q` in ZLE hooks |

Both show green `(i)` for insert and blue `(c)` for command mode.

### Minimal vimrc

9 lines, zero plugins. Just built-in settings that vim ships with but doesn't enable by default:

- `syntax on` — syntax highlighting
- `hlsearch` + `incsearch` — highlight matches, search as you type
- `ignorecase` + `smartcase` — case-insensitive unless you type a capital
- `scrolloff=5` — never edit at the screen edge
- `wildmenu` — tab-completion for `:e` and friends
- `ttimeoutlen=10` — snappy Escape key
- `backspace=indent,eol,start` — fixes backspace on some systems

No line numbers (they break terminal copy-paste and the cursor position is already in the status bar).

### Package management philosophy

Instead of dumping every installed package into a Brewfile (815 formulas, most installed as dependencies), package lists are curated to what's actually used:

- `packages/brew.txt` — core tools installed via Homebrew (languages, runtimes, CLI essentials)
- `packages/cargo.txt` — published Rust crates, installed via `cargo binstall` for speed
- `packages/cargo-local.txt` — local Rust projects in `~/code` that aren't on crates.io (reference only, not auto-installed)
- `packages/uv.txt` — Python CLI tools installed via `uv tool install`

Go tools come from two sources: `gup` for standalone Go binaries and `pdtm` for ProjectDiscovery's security tools. Both are installed by bootstrap and updated by `update.sh`.

## What's Here

```
dotfiles/
  bash_profile        # sources .bashrc
  bashrc              # the real config (everything lives here)
  inputrc             # readline vi mode (green (i) / blue (c))
  zshrc               # zsh equivalent of bashrc
  zshenv              # cargo env (runs for all zsh sessions)
  profile             # legacy sh profile
  gitconfig            # git identity + lfs
  gpg.conf            # gpg settings
  vimrc               # minimal vim config (9 lines)
  ansi_art/
    gengar.sh          # terminal art displayed on login
  config/
    mise/
      config.toml      # node = "latest"
packages/
  brew.txt             # Homebrew packages
  cargo.txt            # crates.io packages (cargo binstall)
  cargo-local.txt      # local Rust projects (reference)
  uv.txt               # Python CLI tools
scripts/
  update.sh            # cross-platform updater (symlinked to ~/bin)
  update.osx.sh        # original macOS-only update script
subversive/            # subversivequote — random quote CLI (Rust)
bootstrap.sh           # new machine setup (homebrew → everything)
install.sh             # symlink dotfiles + build subversivequote
```

## What's NOT here

- `.ssh/config` — contains internal network topology
- `.secrets` — API keys and tokens (gitignored)
- Anything that can be derived from the code or installed via a package manager
