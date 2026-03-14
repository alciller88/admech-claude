```
═══════════════════════════════════════════════════════════════════════════════
              ⚙  M E C H A N I C U S   T E R M I N A L  ⚙
          Adeptus Mechanicus Wrapper for Claude Code CLI
───────────────────────────────────────────────────────────────────────────────
    ☿ "From the weakness of the mind, Omnissiah save us." ☿
         — Chants of the Journeyman, Verse III
═══════════════════════════════════════════════════════════════════════════════
  01001111 01001101 01001110 01001001 01010011 01010011 01001001 01000001 01001000
═══════════════════════════════════════════════════════════════════════════════
```

> **Transforms your Claude Code CLI into a console of the Adeptus Mechanicus.**
> Does NOT modify the model or its reasoning — only presentation and tone.
>
> **Transforma tu Claude Code CLI en una consola del Adeptus Mechanicus.**
> NO modifica el modelo ni su razonamiento — solo presentación y tono.

---

## ⚙ Quick Install / Instalación Rápida

```bash
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/mechanicus-terminal/main/install.sh | bash
```

Or clone and install manually / O clonar e instalar manualmente:

```bash
git clone https://github.com/TU_USUARIO/mechanicus-terminal.git
cd mechanicus-terminal
bash install.sh
```

---

## ‡ Prerequisites / Requisitos Previos

| Requirement | Details |
|-------------|---------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Python** | 3.8+ |
| **tmux** | For servo-skull sidebar (`sudo apt install tmux` / `brew install tmux`) |
| **Anthropic Account** | With Claude Code access |
| **Shell** | bash / zsh / fish |

---

## ⚙ Quick Commands / Comandos Rápidos

| Command | Action / Acción |
|---------|----------------|
| `mech <claude args>` | Launch tmux with claude + servo-skull sidebar |
| `mech on` / `mech enable` | Activate Mechanicus mode / Activa modo |
| `mech off` / `mech disable` | Deactivate — direct passthrough to claude |
| `mech status` | Show config + stats / Config y estadísticas |
| `mech theme <name>` | Switch palette (`rojo` / `verde` / `hueso` / `golden`) |
| `mech lore` | Random canonical litany / Litanía aleatoria |
| `mech esp` | Switch language to Spanish / Cambiar a español |
| `mech eng` | Switch language to English / Cambiar a inglés |
| `mech sidebar <N>` | Set sidebar width (20-60 cols) |
| `mech kill` | Kill tmux session |
| `mech --help` | Full command codex / Códex de comandos |

All other arguments launch `claude` in a tmux session with an animated servo-skull sidebar.

Todos los demás argumentos lanzan `claude` en una sesión tmux con un sidebar de servo-skull animado.

---

## ψ How It Works / Cómo Funciona

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

Claude Code ejecuta **sin modificar** en su propio panel tmux. Los hooks
se disparan en cada tool call y escriben estado a un archivo JSON compartido.
El monitor del servo-skull lee ese archivo y muestra estado animado — el
cráneo cambia según lo que Claude hace, y múltiples agentes aparecen como
Servitors en una jerarquía.

---

## ☠ Uninstall / Desinstalar

```bash
bash uninstall.sh
```

Removes mechcode from PATH, restores your previous `~/.claude/CLAUDE.md` from backup
(or removes it if no backup exists), deletes config, and cleans shell aliases.

Elimina mechcode del PATH, restaura tu `~/.claude/CLAUDE.md` previo desde backup
(o lo elimina si no había backup), borra la config y limpia los alias del shell.

---

## ◈ Contributing / Contribuir

PRs are welcome in the name of the Omnissiah.

Los PRs son bienvenidos en nombre del Omnissiah.

1. Fork the repository / Haz fork del repositorio
2. Create your branch / Crea tu rama: `git checkout -b feature/new-litany`
3. Commit your changes / Haz commit: `git commit -m "Add new litany to the pool"`
4. Push to branch / Push a la rama: `git push origin feature/new-litany`
5. Open a Pull Request / Abre un Pull Request

Please keep the Mechanicus tone in all UI text. Code follows standard Python conventions.

Mantén el tono Mechanicus en todo texto de UI. El código sigue convenciones estándar de Python.

---

## Ω License / Licencia

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
Forjado en el nombre del Omnissiah. Mars Forge Prime. M41.
⚙ 01001100 01000001 01010101 01010011 ⚙
```
