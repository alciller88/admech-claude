```
===============================================================================
              ⚙  M E C H A N I C U S   T E R M I N A L  ⚙
          Wrapper Adeptus Mechanicus para Claude Code CLI
-------------------------------------------------------------------------------
    ☿ "De la debilidad de la mente, Omnissiah salvanos." ☿
         — Canticos del Peregrino, Verso III
===============================================================================
  01001111 01001101 01001110 01001001 01010011 01010011 01001001 01000001 01001000
===============================================================================
```

> **Transforma tu Claude Code CLI en una consola del Adeptus Mechanicus.**
> NO modifica el modelo ni su razonamiento — solo presentacion y tono.

[Read in English](README.md)

---

## ⚙ Instalacion Rapida

```bash
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/mechanicus-terminal/main/install.sh | bash
```

O clonar e instalar manualmente:

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

---

## ⚙ Comandos Rapidos

| Comando | Accion |
|---------|--------|
| `mech <claude args>` | Lanzar tmux con claude + sidebar servo-skull |
| `mech on` / `mech enable` | Activar modo Mechanicus |
| `mech off` / `mech disable` | Desactivar — passthrough directo a claude |
| `mech status` | Config y estadisticas |
| `mech theme <name>` | Cambiar paleta (`rojo` / `verde` / `hueso` / `golden`) |
| `mech lore` | Letania canonica aleatoria |
| `mech esp` | Cambiar idioma a Espanol |
| `mech eng` | Cambiar idioma a Ingles |
| `mech sidebar <N>` | Ancho del sidebar (20-60 cols) |
| `mech kill` | Terminar sesion tmux |
| `mech --help` | Codex completo de comandos |

Todos los demas argumentos lanzan `claude` en una sesion tmux con un sidebar de servo-skull animado.

---

## ψ Como Funciona

```
┌──────────────────────────────────┬──────────────────────┐
│  Claude Code (TUI nativo)        │  Monitor Servo-Skull  │
│                                  │  [skull animado]      │
│  hooks ──────────────────────────│──> estado animado     │
│  escriben a archivo de estado    │  [jerarquia agentes]  │
│                                  │  [stats en vivo]      │
└──────────────────────────────────┴──────────────────────┘
         panel tmux izquierdo        panel derecho (32 cols)
```

Claude Code ejecuta **sin modificar** en su propio panel tmux. Los hooks
se disparan en cada tool call y escriben estado a un archivo JSON compartido.
El monitor del servo-skull lee ese archivo y muestra estado animado — el
craneo cambia segun lo que Claude hace, y multiples agentes aparecen como
Servitors en una jerarquia.

---

## ☠ Desinstalar

```bash
bash uninstall.sh
```

Elimina mechcode del PATH, restaura tu `~/.claude/CLAUDE.md` previo desde backup
(o lo elimina si no habia backup), borra la config y limpia los alias del shell.

---

## ◈ Contribuir

Los PRs son bienvenidos en nombre del Omnissiah.

1. Haz fork del repositorio
2. Crea tu rama: `git checkout -b feature/new-litany`
3. Haz commit: `git commit -m "Add new litany to the pool"`
4. Push a la rama: `git push origin feature/new-litany`
5. Abre un Pull Request

Manten el tono Mechanicus en todo texto de UI. El codigo sigue convenciones estandar de Python.

---

## Ω Licencia

MIT — Ver [LICENSE](LICENSE) para detalles.

---

## ☠ Disclaimer

Este es un proyecto fan no oficial creado para uso personal y educativo.
Warhammer 40,000, Adeptus Mechanicus, y todos los nombres, terminos, personajes
y lore relacionados son marcas y/o copyright de Games Workshop Limited y se usan
aqui sin permiso. Este proyecto no esta afiliado, respaldado ni conectado
con Games Workshop de ninguna manera. No se pretende ni se permite uso comercial.
Por el Omnissiah.

---

```
Forjado en el nombre del Omnissiah. Mars Forge Prime. M41.
⚙ 01001100 01000001 01010101 01010011 ⚙
```
