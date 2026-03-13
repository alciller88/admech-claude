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
## III. ARQUITECTURA DE TRANSFORMACIÓN
═══════════════════════════════════════════════════════════════

[Usuario] → [mechcode intercepta cmd mech] → pasa resto a [claude]
                                                       ↓
[Terminal] ← [colores ANSI] ← [sustituciones] ← [stdout raw]
                ↑
         [servo-skull frame según estado]

Motor de sustitución (orden estricto):
1. Detectar tipo de línea: error / success / thinking / warning / info / code
2. Aplicar sustitución ES + EN de tabla CONTEXT.md sección VII
3. Aplicar color ANSI según tipo y tema activo (paleta sección IX)
4. Añadir prefijo [TIPO//] + símbolo canónico
5. Mostrar frame de servo-cráneo apropiado si modo lo requiere

═══════════════════════════════════════════════════════════════
## IV. MODOS DE OPERACIÓN
═══════════════════════════════════════════════════════════════

| Modo | ASCII | Colores | Sustituciones | Litanías | Uso |
|------|-------|---------|--------------|---------|-----|
| full | ✓ | ✓ | ✓ | ✓ | Default — experiencia completa |
| quiet | ✗ | ✓ | ✓ | ✗ | Sin arte, con color y texto |
| ascii | ✓ | ✓ | ✓ | ✗ | Arte sí, litanías no |
| stealth | ✗ | ✗ | mínimas | ✗ | Entornos hostiles / oficinas |
| off | ✗ | ✗ | ✗ | ✗ | Indistinguible de claude nativo |

Modo por defecto: full

═══════════════════════════════════════════════════════════════
## V. COMANDOS RÁPIDOS — ESPECIFICACIÓN TÉCNICA
═══════════════════════════════════════════════════════════════

Interceptados por mechcode ANTES de pasar args a claude:

mech on|enable      → mode=full, servo-skull IDLE + "⚙ FORJA ACTIVADA ⚙"
mech off|disable    → mode=off, "PROTOCOLO SUSPENDIDO — MODO SILENCIO"
mech ascii          → toggle ascii on/off
mech quiet          → mode=quiet
mech full           → mode=full
mech stealth        → mode=stealth + "Modo Encubierto — la Noosfera observa en silencio"
mech status         → tabla config + stats (herejías, ritos, uptime de sesión)
mech theme <name>   → switch paleta (rojo/verde/hueso/golden)
mech lore           → litanía aleatoria del pool CONTEXT.md sección VIII
mech --help         → ayuda completa en formato tecno-sacerdotal

Estructura ~/.mechcode_config.json:
```json
{
  "mode": "full",
  "theme": "rojo",
  "ascii_enabled": true,
  "heresies_detected": 0,
  "rites_completed": 0,
  "session_start": "ISO timestamp"
}
```

═══════════════════════════════════════════════════════════════
## VI. RESTRICCIONES CRÍTICAS
═══════════════════════════════════════════════════════════════

- NUNCA romper el pipe de Claude Code
- NUNCA modificar el código real que Claude produce — solo mensajes de UI
- NUNCA añadir latencia >50ms al pipeline de streaming
- El modo `off` debe ser INDISTINGUIBLE del claude nativo
- Compatible: Linux, macOS. Windows: best-effort vía WSL
- Python 3.8+ sin dependencias externas obligatorias (rich: opcional)
- fish/zsh/bash: install.sh detecta el shell automáticamente
- install.sh NO sobreescribe ~/.claude/CLAUDE.md sin backup y confirmación previa

═══════════════════════════════════════════════════════════════
## VII. ESTRUCTURA DEL REPOSITORIO
═══════════════════════════════════════════════════════════════
```
mechanicus-terminal/
├── SPEC.md
├── CONTEXT.md
├── mechcode.py              ← ejecutable principal
├── servoskull.py            ← módulo ASCII art
├── install.sh               ← rito de iniciación
├── LICENSE                  ← MIT
├── README.md                ← códex del wrapper
├── config/
│   └── CLAUDE.md            ← prompt global → ~/.claude/CLAUDE.md
└── themes/
    ├── theme_rojo.py        ← paleta Marte (default)
    ├── theme_verde.py       ← paleta Biónica
    ├── theme_hueso.py       ← paleta Pergamino
    └── theme_golden.py      ← paleta Omnissiah
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
