```
===============================================================================
              ⚙  M E C H A N I C U S   T E R M I N A L  ⚙
          Adeptus Mechanicus Wrapper for Claude Code CLI
-------------------------------------------------------------------------------
    ☿ "From the weakness of the mind, Omnissiah save us." ☿
         — Chants of the Journeyman, Verse III
===============================================================================
  01001111 01001101 01001110 01001001 01010011 01010011 01001001 01000001 01001000
===============================================================================
```

> **Transforms your Claude Code CLI into a console of the Adeptus Mechanicus.**
> Does NOT modify the model or its reasoning — only presentation and tone.

[Leer en Español](README.es.md)

---

## ⚙ Quick Install

```bash
git clone https://github.com/TU_USUARIO/mechanicus-terminal.git
cd mechanicus-terminal
bash install.sh
```

---

## ‡ Prerequisites

| Requirement | Details |
|-------------|---------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Python** | 3.8+ |
| **tmux** | For servo-skull sidebar (`sudo apt install tmux` / `brew install tmux`) |
| **Anthropic Account** | With Claude Code access |
| **Shell** | bash / zsh / fish |

### Platform Compatibility

| Platform | Status |
|----------|--------|
| **Linux (native)** | Fully supported |
| **WSL2 (Ubuntu/Debian/Fedora/Arch)** | Fully supported |
| **macOS** | Supported (install tmux via Homebrew) |

---

## ⚙ Commands

| Command | Action |
|---------|--------|
| `mech <claude args>` | Launch tmux with claude + servo-skull sidebar |
| `mech on` / `mech enable` | Activate Mechanicus mode |
| `mech off` / `mech disable` | Deactivate — direct passthrough to claude |
| `mech status` | Show config + stats |
| `mech theme <name>` | Switch palette (`rojo` / `verde` / `hueso` / `golden`) |
| `mech lore` | Random canonical litany |
| `mech esp` | Switch language to Spanish |
| `mech eng` | Switch language to English |
| `mech sidebar <N>` | Set sidebar width (20-60 cols) |
| `mech diagnose` | Run system diagnostics (auspex scan) |
| `mech version` | Show version + platform info |
| `mech kill` | Kill tmux session |
| `mech --help` | Full command codex |

All other arguments launch `claude` in a tmux session with an animated servo-skull sidebar.

---

## ψ How It Works — Architecture

```
┌──────────────────────────────────┬──────────────────────┐
│  Claude Code (native TUI)        │  Servo-Skull Monitor  │
│                                  │  [animated skull]     │
│  hooks ──────────────────────────│──> state updates      │
│  write to state file             │  [agent hierarchy]    │
│                                  │  [live stats]         │
└──────────────────────────────────┴──────────────────────┘
         tmux left pane              right pane (32 cols)
```

Claude Code runs **unmodified** in its own tmux pane. Hooks fire on every
tool call and write state to a shared JSON file (`~/.mechcode_state.json`).
The servo-skull monitor reads that file and displays animated status — the
skull changes based on what Claude is doing, and multiple agents appear as
Servitors in a hierarchy.

### Key Components

| File | Purpose |
|------|---------|
| `mechcode.py` | Main launcher — creates tmux session, handles `mech` commands |
| `servoskull.py` | Pixel art renderer — generates servo-skull frames with ANSI true color |
| `servoskull_monitor.py` | Sidebar monitor loop — reads state, animates skull in right pane |
| `mechcode_hook.py` | Claude Code hook — captures tool events, writes state JSON |
| `shared_config.py` | Shared constants — paths, animation params, agent types |
| `config/CLAUDE.md` | Prompt injection — Mechanicus tone for Claude responses |

### Hooks

The installer registers `mechcode_hook.py` as a Claude Code hook in `~/.claude/settings.json`.
It captures these events:

- **PreToolUse** — skull enters THINKING state
- **PostToolUse** — skull flashes SUCCESS (green)
- **PostToolUseFailure** — skull flashes ERROR (red, with corruption effects)
- **SubagentStart/Stop** — agents appear/disappear in the Servitor hierarchy
- **SessionStart** — resets stats counter
- **Stop** — skull returns to IDLE

---

## † Troubleshooting

### `mech: command not found`
Restart your terminal or run:
```bash
source ~/.bashrc   # or ~/.zshrc
```
If it still fails, check that `~/.local/bin` is in your PATH:
```bash
echo $PATH | grep -q ".local/bin" && echo "OK" || echo "Missing — add to your shell profile"
```

### Servo-skull sidebar not appearing
1. Verify tmux is installed: `tmux -V`
2. Check that mode is `full`: `mech status`
3. Run diagnostics: `mech diagnose`

### Hooks not firing (skull stays IDLE)
1. Run `mech diagnose` and check the "Claude hooks configured" line
2. Verify hooks are in `~/.claude/settings.json`:
   ```bash
   cat ~/.claude/settings.json | grep mechcode_hook
   ```
3. If missing, re-run `bash install.sh`

### State file corrupted
```bash
rm ~/.mechcode_state.json
```
A fresh state file will be created on the next session.

### Debug mode
Set `MECHCODE_DEBUG=1` to see hook activity on stderr:
```bash
export MECHCODE_DEBUG=1
```

---

## ☠ Uninstall

```bash
bash uninstall.sh
```

Removes mechcode from PATH, restores your previous `~/.claude/CLAUDE.md` from backup
(or removes it if no backup exists), deletes config, and cleans shell aliases.

---

## ◈ Contributing

PRs are welcome in the name of the Omnissiah.

1. Fork the repository
2. Create your branch: `git checkout -b feature/new-litany`
3. Commit your changes: `git commit -m "Add new litany to the pool"`
4. Push to branch: `git push origin feature/new-litany`
5. Open a Pull Request

Please keep the Mechanicus tone in all UI text. Code follows standard Python conventions.

---

## Ω License

MIT — See [LICENSE](LICENSE) for details.

---

## ☠ Disclaimer

This is an unofficial fan project created for personal and educational use.
Warhammer 40,000, Adeptus Mechanicus, and all related names, terms, characters,
and lore are trademarks and/or copyright of Games Workshop Limited and are used
here without permission. This project is not affiliated with, endorsed by, or
connected to Games Workshop in any way. No commercial use is intended or permitted.
For the Omnissiah.

---

```
Forged in the name of the Omnissiah. Mars Forge Prime. M41.
⚙ 01001100 01000001 01010101 01010011 ⚙
```
