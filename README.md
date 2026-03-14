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
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/mechanicus-terminal/main/install.sh | bash
```

Or clone and install manually:

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

---

## ⚙ Quick Commands

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
| `mech kill` | Kill tmux session |
| `mech --help` | Full command codex |

All other arguments launch `claude` in a tmux session with an animated servo-skull sidebar.

---

## ψ How It Works

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
tool call and write state to a shared JSON file. The servo-skull monitor
reads that file and displays animated status — the skull changes based on
what Claude is doing, and multiple agents appear as Servitors in a hierarchy.

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
