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
| **Anthropic Account** | With Claude Code access |
| **Shell** | bash / zsh / fish |

---

## ⚙ Quick Commands / Comandos Rápidos

| Command | Action / Acción |
|---------|----------------|
| `mech on` / `mech enable` | Activate full Mechanicus mode / Activa modo completo |
| `mech off` / `mech disable` | Deactivate — native Claude output / Output nativo |
| `mech ascii` | Toggle servo-skull ASCII on/off |
| `mech quiet` | Substitutions + color only / Solo sustituciones y color |
| `mech full` | Full mode: ASCII + color + substitutions + litanies / Modo completo |
| `mech stealth` | Stealth mode for hostile environments / Modo encubierto |
| `mech status` | Show config + stats / Config y estadísticas |
| `mech theme <name>` | Switch palette / Cambiar paleta (`rojo` / `verde` / `hueso` / `golden`) |
| `mech lore` | Random canonical litany / Litanía aleatoria |
| `mech esp` | Switch language to Spanish / Cambiar a español |
| `mech eng` | Switch language to English / Cambiar a inglés |
| `mech --help` | Full command codex / Códex de comandos |

All other arguments are passed directly to `claude` — the proxy is transparent.

Todos los demás argumentos se pasan directamente a `claude` — el proxy es transparente.

---

## † Operation Modes / Modos de Operación

| Mode | ASCII | Colors | Substitutions | Litanies | Use / Uso |
|------|:-----:|:------:|:-------------:|:--------:|-----------|
| **full** | ✓ | ✓ | ✓ | ✓ | Default — full experience / Experiencia completa |
| **quiet** | ✗ | ✓ | ✓ | ✗ | No art, with color + text / Sin arte, con color |
| **ascii** | ✓ | ✓ | ✓ | ✗ | Art yes, litanies no / Arte sí, litanías no |
| **stealth** | ✗ | ✗ | minimal | ✗ | Hostile environments / Entornos hostiles |
| **off** | ✗ | ✗ | ✗ | ✗ | Indistinguishable from native `claude` |

---

## ψ How It Works / Cómo Funciona

```
[User] → [mechcode intercepts mech commands] → passes rest to [claude]
                                                            ↓
[Terminal] ← [ANSI colors] ← [substitutions] ← [raw stdout]
                ↑
         [servo-skull frame by state]
```

The substitution engine transforms system messages into Adeptus Mechanicus
Cant — errors become heresies, successes become completed rites, and the
Omnissiah guides all operations.

El motor de sustitución transforma mensajes del sistema en Cant Mechanicus
— los errores se convierten en herejías, los éxitos en ritos completados,
y el Omnissiah guía todas las operaciones.

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
