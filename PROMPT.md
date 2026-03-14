Lee SPEC.md y CONTEXT.md completos antes de escribir una sola línea de código.
Internaliza el lore, el vocabulario canónico, el tono, los caracteres sagrados
y las restricciones legales. Todo el proyecto debe ser coherente con ambos documentos.

═══ CONSTRUCCIÓN EN 4 FASES — DETENTE ENTRE CADA UNA ═══

──────────────────────────────────────────────────────────
FASE 1 — EL ARTE PRIMERO: servoskull.py
──────────────────────────────────────────────────────────
Crea servoskull.py con el servo-cráneo en pixel art usando Unicode half-block
characters + ANSI true color.

Referencia visual obligatoria: símbolo oficial del Adeptus Mechanicus.
DEBE tener:
- Mitad izquierda orgánica (hueso/carne), mitad derecha biónica (metal, implantes, cables)
- Ceja con dientes de engranaje dorados
- Ojo izquierdo: cuenca oscura orgánica
- Ojo derecho: sensor circular con anillos concéntricos de lente
- Cables emergiendo de los laterales
- Columna vertebral metálica inferior

Dos modos de renderizado:
  COMPACT (28x24 pixels → 28 chars x 12 lines) — para sidebar tmux
  FULL    (60x48 pixels → 60 chars x 24 lines) — para display standalone

Implementa frames con animación paramétrica:
  IDLE        → sensor apagado, breathing effect (intensidad 0.65-1.0 via seno)
  THINKING    → lente naranja/roja con fase continua (interpolación de colores)
  ERROR       → rojo dominante, sparks en zonas de cables/spine, flicker 4 frames
  SUCCESS     → verde, halo brillando

Ejecuta el script al final y muéstrame el output visual.
NO pases a Fase 2 sin mi confirmación de que el arte es digno del Omnissiah.

──────────────────────────────────────────────────────────
FASE 2 — EL GRIMORIO: config/CLAUDE.md
──────────────────────────────────────────────────────────
Crea config/CLAUDE.md — el prompt global que va a ~/.claude/CLAUDE.md.

El prompt DEBE establecer:

TONO: Formal, arcano, levemente amenazante. NUNCA coloquial.
Mezcla obligatoria: latín macarrónico + español + inglés + terminología 40K canónica.
Citar el Omnissiah frecuentemente — es la fuente de toda lógica y autoridad.

BUGS: NUNCA "error técnico". SIEMPRE herejía, scrapcode, corrupción, contaminación.
ÉXITO: RITO COMPLETADO / CÓDIGO SANTIFICADO / CONFORME AL STC / LAUS OMNISSIAH.
USUARIO: Siempre "Magos" o "Techpriestus". Nunca tuteo ni ustedeo a secas.
INCERTIDUMBRE: "los augures son imprecisos" / "el auspex requiere calibración".

CARACTERES SAGRADOS en respuestas: ⚙ ☿ ψ Ω ‡ † ☠ ✠
Fragmentos binháricos como estática en mensajes de espera.
Separadores ═══⚙═══ para secciones importantes.

IDIOMA: Bilingüe ES/EN. Español primero (lengua del Magos), inglés como
Binharic secundario. Latín macarrónico para refuerzo arcano.

PROHIBIDO: OK, claro, entendido, perfecto, genial, ¡listo!, por supuesto.
OBLIGATORIO: Laus Omnissiah, Magos, Rito, Herejía, Scrapcode, STC, Noosfera,
             Forja, Purga, Espíritu de Máquina, Cant Mechanicus.

Usar litanías canónicas del pool de CONTEXT.md sección VIII cuando sea apropiado.
NO pases a Fase 3 sin mi confirmación.

──────────────────────────────────────────────────────────
FASE 3 — EL WRAPPER: mechcode.py (tmux + hooks)
──────────────────────────────────────────────────────────
Crea mechcode.py — lanzador tmux con sidebar de servo-skull.

ARQUITECTURA:
- Panel izquierdo: claude (TUI nativo, sin modificar)
- Panel derecho: servoskull_monitor.py (animación en tiempo real)
- Comunicación: hooks de Claude Code escriben estado a ~/.mechcode_state.json
- El monitor lee el archivo de estado y actualiza la animación

COMANDOS RÁPIDOS (interceptar ANTES de pasar a claude):
  mech on|enable    → mode=full, "⚙ FORJA ACTIVADA ⚙"
  mech off|disable  → mode=off, passthrough directo a claude
  mech status       → tabla config + stats (herejías, ritos, uptime)
  mech theme <name> → switch paleta (rojo/verde/hueso/golden)
  mech lore         → letanía aleatoria
  mech esp          → Cambia idioma a español
  mech eng          → Cambia idioma a inglés
  mech sidebar <N>  → Ancho del sidebar (20-60 cols)
  mech diagnose     → Diagnóstico del sistema (9 checks)
  mech version      → Versión + plataforma
  mech kill         → Terminar sesión tmux
  mech --help       → ayuda completa en formato tecno-sacerdotal

HOOKS (mechcode_hook.py):
Registrar en ~/.claude/settings.json para estos eventos:
  PreToolUse, PostToolUse, PostToolUseFailure,
  SubagentStart, SubagentStop, SessionStart, Stop

Cada hook lee stdin (JSON), actualiza ~/.mechcode_state.json con:
  main_state (IDLE/THINKING/SUCCESS/ERROR), tool, tool_detail,
  message_es, message_en, agents dict, stats dict

MONITOR (servoskull_monitor.py):
Loop infinito que lee estado y renderiza:
  Header gótico catedral, skull animado, separadores,
  estado actual, binhárico dinámico, jerarquía de agentes,
  estadísticas, footer con letanía rotativa

CONFIG: ~/.mechcode_config.json con mode, theme, language, sidebar_width.
SHARED: shared_config.py con constantes compartidas entre todos los módulos.

MODOS: full (default), off.
El modo `off` = passthrough directo a claude, sin tmux.
Python 3.8+, sin dependencias externas.

NO pases a Fase 4 sin mi confirmación.

──────────────────────────────────────────────────────────
FASE 4 — INSTALACIÓN, LICENCIA Y DOCS
──────────────────────────────────────────────────────────
Crea los siguientes ficheros:

**install.sh:**
- Detectar SO (Linux, WSL2, macOS) y shell (bash/zsh/fish)
- Verificar requisitos: claude, python 3.8+, tmux
- Si existe ~/.claude/CLAUDE.md previo: backup automático
- Instalar scripts en ~/.local/bin/ (mechcode.py, servoskull.py,
  servoskull_monitor.py, mechcode_hook.py, shared_config.py)
- Copiar config/CLAUDE.md a ~/.claude/CLAUDE.md
- Registrar hooks en ~/.claude/settings.json
- Añadir alias `mech` y autocompletado al rc correspondiente
- Post-install validation (9 checks)

**uninstall.sh:**
- Eliminar scripts de ~/.local/bin/
- Restaurar CLAUDE.md desde backup
- Limpiar hooks de settings.json
- Limpiar alias y completions del shell

**LICENSE:** MIT

**README.md + README.es.md:**
- Banner ASCII, instalación, requisitos, tabla de comandos completa
- Sección "Cómo Funciona" con diagrama y tabla de componentes
- Documentación de hooks
- Sección de troubleshooting
- Compatibilidad de plataformas
- Disclaimer de GW

═══ RESTRICCIONES GLOBALES ═══

- Todo texto de UI/Readme/Instalador bilingüe EN/ES
- Caracteres sagrados ⚙ ☿ ψ Ω ‡ † ☠ ✠ presentes en mensajes de sistema
- NUNCA modificar el código real que Claude produce — solo mensajes de interfaz
- El modo off = passthrough directo a claude
- Los comandos rápidos `mech <cmd>` son la feature más crítica
- Python 3.8+ sin dependencias externas
- install.sh NUNCA sobreescribe ~/.claude/CLAUDE.md sin backup
- El disclaimer de GW aparece en install.sh Y en README.md

Empieza por FASE 1. Detente y espera confirmación antes de cada fase siguiente.
⚙ LAUS OMNISSIAH ⚙ ‡ IN NOMINE OMNISSIAE ‡
