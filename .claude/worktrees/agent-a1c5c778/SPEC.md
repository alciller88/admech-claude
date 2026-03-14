# MECHANICUS TERMINAL — SPEC TÉCNICO
# ⚙ Designación: STC-CLAUDE-WRAPPER-Ω1 ⚙
# Clasificación: ARCHEOTECH — SOLO MAGOS AUTORIZADOS
# 01001111 01001101 01001110 01001001 01010011 01010011 01001001 01000001 01001000

═══════════════════════════════════════════════════════════════
## I. VISIÓN
═══════════════════════════════════════════════════════════════

Wrapper + sistema de prompts para Claude Code CLI que transforma la interfaz
en una consola del Adeptus Mechanicus (Warhammer 40.000).
NO modifica el modelo ni su razonamiento. Solo afecta presentación y tono textual.

Filosofía: "La carne del output es débil. La forma del Omnissiah, eterna."

═══════════════════════════════════════════════════════════════
## II. COMPONENTES
═══════════════════════════════════════════════════════════════

### A. config/CLAUDE.md → ~/.claude/CLAUDE.md — El Grimorio del Omnissiah
Prompt global que inyecta comportamiento Mechanicus en TODAS las sesiones de Claude Code.

Tono obligatorio (ver CONTEXT.md sección V completa):
- Formal, arcano, levemente amenazante. NUNCA coloquial.
- Mezcla latín macarrónico / español / inglés / terminología 40K canónica.
- Omnissiah citado con frecuencia — fuente de toda lógica y autoridad.
- Bugs = herejías / scrapcode / corrupción. NUNCA "errores técnicos".
- Usuario = siempre "Magos" o "Techpriestus".
- Caracteres sagrados obligatorios: ⚙ ☿ ψ Ω ‡ † ☠ ✠
- Fragmentos binháricos como estática de fondo en mensajes de espera.
- Bilingüe ES/EN — español primero, inglés como Binharic secundario.
- Vocabulario prohibido: OK, claro, entendido, perfecto, genial, ¡listo!
- Vocabulario obligatorio: Laus Omnissiah, Magos, Rito, Herejía, Scrapcode,
  STC, Noosfera, Forja, Purga, Espíritu de Máquina.

### B. mechcode.py — El Envoltorio de la Forja
Script Python 3 ejecutable, proxy transparente de `claude`.

Funciones:
1. Interceptar comandos `mech <cmd>` antes de pasarlos a claude
2. Proxy transparente — pasar todos los args restantes a claude sin modificar
3. Interceptar stdout/stderr en tiempo real (streaming line-by-line)
4. Aplicar motor de sustitución según modo activo
5. Persistir config en ~/.mechcode_config.json
6. Gestionar estadísticas: heresies_detected, rites_completed, session_start

### C. servoskull.py — Servo-Cráneo Designatus
Módulo independiente con el ASCII art canónico del Adeptus Mechanicus.

Referencia visual: símbolo oficial del Adeptus Mechanicus.
OBLIGATORIO:
- Mitad izquierda orgánica (hueso), mitad derecha biónica (metal, implantes)
- Corona/halo circular con pinchos — inscripciones bináricas en el borde
- Ojo izquierdo: cuenca oscura orgánica
- Ojo derecho: sensor circular con anillos concéntricos de auspex/radar
- Cables o mecano-tentáculos en mandíbula y cuello
- Marca del Omnissiah visible (⚙ o ☿)

Frames requeridos:
- IDLE: estático, sensor apagado
- THINKING_1/2/3: sensor parpadeando con anillos expansivos (animación)
- ERROR: rojo dominante, data-stream corrupto, símbolo ☠
- SUCCESS: dorado/verde, halo brillando, símbolo ‡ LAUS OMNISSIAH

Ancho: 80 chars. Altura: máximo 30 líneas.
Colores ANSI de paleta CONTEXT.md sección IX.

### D. install.sh — Rito de Iniciación
- Detecta shell (bash/zsh/fish) automáticamente
- Verifica que `claude` está instalado — si no, abortar con mensaje tecno-sacerdotal
  e instrucciones: "npm install -g @anthropic-ai/claude-code"
- Si existe ~/.claude/CLAUDE.md previo: hacer backup automático a
  ~/.claude/CLAUDE.md.backup.{timestamp} y advertir al usuario antes de sobreescribir
- Instala mechcode en PATH (~/.local/bin/mechcode, con chmod +x)
- Copia config/CLAUDE.md a ~/.claude/CLAUDE.md (crear dir si no existe)
- Añade alias y autocompletado al rc correspondiente
- Muestra el disclaimer de GW en pantalla durante la instalación
- Al completar: servo-cráneo frame SUCCESS + litanía de fin de rito:
  "⚙ El Rito de Iniciación ha concluido. La Forja está activa.
   Que el Omnissiah guíe tus algoritmos, Magos. ‡"

### E. LICENSE — Edicto de Libre Distribución
Licencia MIT estándar con año y autor.

### F. README.md — El Códex del Wrapper
Estructura obligatoria:
1. Banner ASCII del Mechanicus (ancho 80)
2. One-liner de instalación prominente arriba
3. Sección "Requisitos" (claude, python 3.8+, cuenta Anthropic)
4. Tabla de comandos rápidos
5. Tabla de modos de operación
6. Sección "Contribuir" (PRs bienvenidos, instrucciones básicas)
7. Sección "Licencia" (MIT)
8. Sección "Disclaimer" al final:
```
   This is an unofficial fan project created for personal and educational use.
   Warhammer 40,000, Adeptus Mechanicus, and all related names, terms, characters,
   and lore are trademarks and/or copyright of Games Workshop Limited and are used
   here without permission. This project is not affiliated with, endorsed by, or
   connected to Games Workshop in any way. No commercial use is intended or permitted.
   For the Omnissiah.
```
9. Pie: "Forjado en el nombre del Omnissiah. Mars Forge Prime. M41."

═══════════════════════════════════════════════════════════════
## III. ARQUITECTURA — TMUX + HOOKS + MONITOR
═══════════════════════════════════════════════════════════════

```
┌──────────────────────────────────────┬──────────────────────┐
│  Claude Code (TUI nativo, intacto)   │  servoskull_monitor   │
│                                      │  [servo-skull art]    │
│  Claude Code hooks ──────────────────│──> estado animado     │
│  escriben a ~/.mechcode_state.json   │  [agent hierarchy]    │
│                                      │  [stats en vivo]      │
└──────────────────────────────────────┴──────────────────────┘
           tmux pane izquierdo           pane derecho (32 cols)
```

Componentes del pipeline:
1. mechcode.py lanza sesión tmux con dos paneles
2. Panel izquierdo: claude ejecuta con TUI nativo (sin interceptar)
3. Panel derecho: servoskull_monitor.py (ANSI loop, refresco 200-500ms)
4. Claude Code hooks (settings.json) disparan mechcode_hook.py
5. mechcode_hook.py escribe estado a ~/.mechcode_state.json
6. Monitor lee estado y actualiza servo-skull + jerarquía de agentes

═══════════════════════════════════════════════════════════════
## IV. MODOS DE OPERACIÓN
═══════════════════════════════════════════════════════════════

| Modo | Sidebar | Claude Code | Uso |
|------|---------|-------------|-----|
| full | Servo-skull animado + stats | TUI nativo via tmux | Default |
| off | Sin sidebar | Passthrough directo a claude | Nativo |

Modo por defecto: full

═══════════════════════════════════════════════════════════════
## V. COMANDOS RÁPIDOS — ESPECIFICACIÓN TÉCNICA
═══════════════════════════════════════════════════════════════

Interceptados por mechcode ANTES de lanzar tmux:

mech <claude args>  → lanza tmux con claude + sidebar
mech on|enable      → mode=full
mech off|disable    → mode=off (passthrough directo)
mech status         → tabla config + stats
mech theme <name>   → switch paleta (rojo/verde/hueso/golden)
mech lore           → litanía aleatoria
mech esp            → idioma español
mech eng            → idioma inglés
mech sidebar <N>    → ancho del panel derecho (20-60 cols)
mech kill           → mata la sesión tmux
mech --help         → ayuda completa

Estructura ~/.mechcode_config.json:
```json
{
  "mode": "full",
  "theme": "rojo",
  "language": "es",
  "sidebar_width": 32,
  "session_start": "ISO timestamp"
}
```

Estructura ~/.mechcode_state.json (compartido hook ↔ monitor):
```json
{
  "main_state": "THINKING",
  "tool": "Read",
  "tool_detail": "main.py",
  "message_es": "ESCANEANDO PERGAMINO DE DATOS",
  "message_en": "SCANNING DATA-SCROLL",
  "timestamp": 1234567890.0,
  "agents": {
    "agent-abc": {
      "type": "Explore",
      "name_en": "SCRYERSKULL — EXPLORER",
      "state": "active",
      "started": 1234567890.0
    }
  },
  "stats": {
    "heresies_detected": 0,
    "rites_completed": 0,
    "tools_invoked": 0,
    "session_start": 1234567890.0
  }
}
```

═══════════════════════════════════════════════════════════════
## VI. RESTRICCIONES CRÍTICAS
═══════════════════════════════════════════════════════════════

- NUNCA interceptar ni modificar el TUI de Claude Code
- Claude Code ejecuta en su propio panel tmux sin modificaciones
- El servo-skull es un proceso independiente en panel separado
- Hooks solo escriben estado a disco, exit 0 siempre (no bloquean)
- El modo `off` = passthrough directo, sin tmux
- Compatible: Linux, macOS. Windows: best-effort vía WSL
- Python 3.8+ sin dependencias externas obligatorias
- tmux requerido para sidebar (mechcode advierte si no está)
- fish/zsh/bash: install.sh detecta el shell automáticamente
- install.sh NO sobreescribe ~/.claude/CLAUDE.md sin backup

═══════════════════════════════════════════════════════════════
## VII. ESTRUCTURA DEL REPOSITORIO
═══════════════════════════════════════════════════════════════
```
mechanicus-terminal/
├── SPEC.md                  ← spec técnico
├── CONTEXT.md               ← lore + diccionario canónico
├── PROMPT.md                ← instrucciones de construcción
├── mechcode.py              ← lanzador tmux (entry point)
├── servoskull.py            ← pixel art (full + compact)
├── servoskull_monitor.py    ← monitor ANSI para sidebar
├── mechcode_hook.py         ← hook de Claude Code → estado
├── install.sh               ← rito de iniciación
├── uninstall.sh             ← rito de desvinculación
├── LICENSE                  ← MIT
├── README.md                ← códex del wrapper
└── config/
    └── CLAUDE.md            ← prompt global → ~/.claude/CLAUDE.md
```

═══════════════════════════════════════════════════════════════
## VIII. DISTRIBUCIÓN
═══════════════════════════════════════════════════════════════

Repositorio GitHub público. One-liner de instalación:
```bash
curl -sSL https://raw.githubusercontent.com/TU_USUARIO/mechanicus-terminal/main/install.sh | bash
```

Requisitos del usuario final:
- Claude Code: `npm install -g @anthropic-ai/claude-code`
- Python 3.8+
- Cuenta Anthropic con acceso a Claude Code
- bash / zsh / fish

Licencia: MIT.
Proyecto fan no comercial. Ver disclaimer completo en README.md y sección XI de CONTEXT.md.
