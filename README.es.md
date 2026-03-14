```
===============================================================================
              ⚙  M E C H A N I C U S   T E R M I N A L  ⚙
          Wrapper Adeptus Mechanicus para Claude Code CLI
-------------------------------------------------------------------------------
    ☿ "De la debilidad de la mente, Omnissiah sálvanos." ☿
         — Cánticos del Peregrino, Verso III
===============================================================================
  01001111 01001101 01001110 01001001 01010011 01010011 01001001 01000001 01001000
===============================================================================
```

> **Transforma tu Claude Code CLI en una consola del Adeptus Mechanicus.**
> NO modifica el modelo ni su razonamiento — solo presentación y tono.

[Read in English](README.md)

---

## ⚙ Instalación Rápida

```bash
git clone https://github.com/TU_USUARIO/mechanicus-terminal.git
cd mechanicus-terminal
bash install.sh
```

---

## ‡ Requisitos Previos

| Requisito | Detalles |
|-----------|----------|
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` |
| **Python** | 3.8+ |
| **tmux** | Para el sidebar servo-skull (`sudo apt install tmux` / `brew install tmux`) |
| **Cuenta Anthropic** | Con acceso a Claude Code |
| **Shell** | bash / zsh / fish |

### Compatibilidad de Plataformas

| Plataforma | Estado |
|------------|--------|
| **Linux (nativo)** | Completamente soportado |
| **WSL2 (Ubuntu/Debian/Fedora/Arch)** | Completamente soportado |
| **macOS** | Soportado (instalar tmux via Homebrew) |

---

## ⚙ Comandos

| Comando | Acción |
|---------|--------|
| `mech <claude args>` | Lanzar tmux con claude + sidebar servo-skull |
| `mech on` / `mech enable` | Activar modo Mechanicus |
| `mech off` / `mech disable` | Desactivar — passthrough directo a claude |
| `mech status` | Config y estadísticas |
| `mech theme <name>` | Cambiar paleta (`rojo` / `verde` / `hueso` / `golden`) |
| `mech lore` | Letanía canónica aleatoria |
| `mech esp` | Cambiar idioma a Español |
| `mech eng` | Cambiar idioma a Inglés |
| `mech sidebar <N>` | Ancho del sidebar (20-60 cols) |
| `mech diagnostico` | Diagnóstico del sistema (escaneo auspex) |
| `mech version` | Mostrar versión + info de plataforma |
| `mech kill` | Terminar sesión tmux |
| `mech --help` | Códex completo de comandos |

Todos los demás argumentos lanzan `claude` en una sesión tmux con un sidebar de servo-skull animado.

---

## ψ Cómo Funciona — Arquitectura

```
┌──────────────────────────────────┬──────────────────────┐
│  Claude Code (TUI nativo)        │  Monitor Servo-Skull  │
│                                  │  [skull animado]      │
│  hooks ──────────────────────────│──> estado animado     │
│  escriben a archivo de estado    │  [jerarquía agentes]  │
│                                  │  [stats en vivo]      │
└──────────────────────────────────┴──────────────────────┘
         panel tmux izquierdo        panel derecho (32 cols)
```

Claude Code ejecuta **sin modificar** en su propio panel tmux. Los hooks
se disparan en cada tool call y escriben estado a un archivo JSON compartido
(`~/.mechcode_state.json`). El monitor del servo-skull lee ese archivo y
muestra estado animado — el cráneo cambia según lo que Claude hace, y
múltiples agentes aparecen como Servitors en una jerarquía.

### Componentes Clave

| Archivo | Propósito |
|---------|-----------|
| `mechcode.py` | Lanzador principal — crea sesión tmux, maneja comandos `mech` |
| `servoskull.py` | Renderizador pixel art — genera frames del servo-skull con ANSI true color |
| `servoskull_monitor.py` | Loop del monitor sidebar — lee estado, anima skull en panel derecho |
| `mechcode_hook.py` | Hook de Claude Code — captura eventos de herramientas, escribe estado JSON |
| `shared_config.py` | Constantes compartidas — rutas, parámetros de animación, tipos de agente |
| `config/CLAUDE.md` | Inyección de prompt — tono Mechanicus para respuestas de Claude |

### Hooks

El instalador registra `mechcode_hook.py` como hook de Claude Code en `~/.claude/settings.json`.
Captura estos eventos:

- **PreToolUse** — el cráneo entra en estado THINKING
- **PostToolUse** — el cráneo destella SUCCESS (verde)
- **PostToolUseFailure** — el cráneo destella ERROR (rojo, con efectos de corrupción)
- **SubagentStart/Stop** — agentes aparecen/desaparecen en la jerarquía de Servitors
- **SessionStart** — reinicia contadores de estadísticas
- **Stop** — el cráneo regresa a IDLE

---

## † Solución de Problemas

### `mech: command not found`
Reinicia tu terminal o ejecuta:
```bash
source ~/.bashrc   # o ~/.zshrc
```
Si persiste, verifica que `~/.local/bin` está en tu PATH:
```bash
echo $PATH | grep -q ".local/bin" && echo "OK" || echo "Falta — añadir al perfil del shell"
```

### El sidebar del servo-skull no aparece
1. Verifica que tmux está instalado: `tmux -V`
2. Comprueba que el modo es `full`: `mech status`
3. Ejecuta diagnóstico: `mech diagnostico`

### Los hooks no se disparan (el skull se queda en IDLE)
1. Ejecuta `mech diagnostico` y revisa la línea "Hooks de Claude configurados"
2. Verifica que los hooks están en `~/.claude/settings.json`:
   ```bash
   cat ~/.claude/settings.json | grep mechcode_hook
   ```
3. Si faltan, re-ejecuta `bash install.sh`

### Archivo de estado corrupto
```bash
rm ~/.mechcode_state.json
```
Se creará un nuevo archivo de estado en la próxima sesión.

### Modo debug
Activa `MECHCODE_DEBUG=1` para ver la actividad de hooks en stderr:
```bash
export MECHCODE_DEBUG=1
```

---

## ☠ Desinstalar

```bash
bash uninstall.sh
```

Elimina mechcode del PATH, restaura tu `~/.claude/CLAUDE.md` previo desde backup
(o lo elimina si no había backup), borra la config y limpia los alias del shell.

---

## ◈ Contribuir

Los PRs son bienvenidos en nombre del Omnissiah.

1. Haz fork del repositorio
2. Crea tu rama: `git checkout -b feature/new-litany`
3. Haz commit: `git commit -m "Add new litany to the pool"`
4. Push a la rama: `git push origin feature/new-litany`
5. Abre un Pull Request

Mantén el tono Mechanicus en todo texto de UI. El código sigue convenciones estándar de Python.

---

## Ω Licencia

MIT — Ver [LICENSE](LICENSE) para detalles.

---

## ☠ Disclaimer

Este es un proyecto fan no oficial creado para uso personal y educativo.
Warhammer 40,000, Adeptus Mechanicus, y todos los nombres, términos, personajes
y lore relacionados son marcas y/o copyright de Games Workshop Limited y se usan
aquí sin permiso. Este proyecto no está afiliado, respaldado ni conectado
con Games Workshop de ninguna manera. No se pretende ni se permite uso comercial.
Por el Omnissiah.

---

```
Forjado en el nombre del Omnissiah. Mars Forge Prime. M41.
⚙ 01001100 01000001 01010101 01010011 ⚙
```
