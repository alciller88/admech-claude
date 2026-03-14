Lee SPEC.md y CONTEXT.md completos antes de escribir una sola línea de código.
Internaliza el lore, el vocabulario canónico, el tono, los caracteres sagrados
y las restricciones legales. Todo el proyecto debe ser coherente con ambos documentos.

═══ CONSTRUCCIÓN EN 4 FASES — DETENTE ENTRE CADA UNA ═══

──────────────────────────────────────────────────────────
FASE 1 — EL ARTE PRIMERO: servoskull.py
──────────────────────────────────────────────────────────
Crea servoskull.py con el servo-cráneo ASCII canónico del Adeptus Mechanicus.

Referencia visual obligatoria: símbolo oficial del Adeptus Mechanicus.
DEBE tener:
- Mitad izquierda orgánica (hueso/carne), mitad derecha biónica (metal, implantes, cables)
- Corona/halo circular con pinchos — inscripciones bináricas en el borde
- Ojo izquierdo: cuenca oscura orgánica
- Ojo derecho: sensor circular con anillos concéntricos de auspex/radar parpadeantes
- Cables, tubos o mecano-tentáculos emergiendo de mandíbula y cuello
- Marca del Omnissiah visible (⚙ o ☿)

Implementa 6 frames con colores ANSI (paleta de CONTEXT.md sección IX):
  IDLE        → sensor apagado, estático
  THINKING_1  → anillo exterior del sensor activo
  THINKING_2  → anillos expansivos, binharic estático de fondo
  THINKING_3  → todos los anillos activos, parpadeo máximo
  ERROR       → rojo dominante (#CC0000), data-stream corrupto, símbolo ☠
  SUCCESS     → dorado/verde, halo brillando, símbolo ‡ LAUS OMNISSIAH

Ancho: 80 chars. Altura: máximo 30 líneas.
Ejecuta el script al final y muéstrame el output visual de los 6 frames.
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
Mostrarme el contenido completo del fichero para revisión.
NO pases a Fase 3 sin mi confirmación.

──────────────────────────────────────────────────────────
FASE 3 — EL WRAPPER: mechcode.py
──────────────────────────────────────────────────────────
Crea mechcode.py ejecutable, proxy transparente de claude.

COMANDOS RÁPIDOS (interceptar ANTES de pasar a claude):
  mech on|enable    → mode=full, servo-skull IDLE + "⚙ FORJA ACTIVADA ⚙"
  mech off|disable  → mode=off, "PROTOCOLO SUSPENDIDO — MODO SILENCIO"
  mech ascii        → toggle ascii on/off
  mech quiet        → mode=quiet
  mech full         → mode=full
  mech stealth      → mode=stealth + "Modo Encubierto — la Noosfera observa en silencio"
  mech status       → tabla config + stats (herejías detectadas, ritos completados, uptime)
  mech theme <name> → switch paleta (rojo/verde/hueso/golden)
  mech lore         → litanía aleatoria del pool de CONTEXT.md sección VIII
  mec esp           → Cambia idioma a español
  mec eng           → Cambia idioma a inglés
  mech --help       → ayuda completa en formato tecno-sacerdotal

  

MOTOR DE SUSTITUCIÓN (orden estricto):
1. Detectar tipo de línea: error / success / thinking / warning / info / code
2. Aplicar sustitución ES + EN de tabla CONTEXT.md sección VII
3. Aplicar color ANSI según tipo y tema activo (paleta CONTEXT.md sección IX)
4. Añadir prefijo [TIPO//] + símbolo canónico
5. Mostrar frame de servo-cráneo apropiado si modo lo requiere

CONFIG: ~/.mechcode_config.json con mode, theme, ascii_enabled,
        heresies_detected, rites_completed, session_start.

MODOS: full (default), quiet, ascii, stealth, off.
El modo `off` debe ser INDISTINGUIBLE del claude nativo.
Latencia máxima añadida al pipeline: 50ms.
Python 3.8+, sin dependencias externas obligatorias (rich: opcional).

NO pases a Fase 4 sin mi confirmación.

──────────────────────────────────────────────────────────
FASE 4 — INSTALACIÓN, LICENCIA Y DOCS
──────────────────────────────────────────────────────────
Crea los siguientes ficheros:

**install.sh:**
- Detectar shell automáticamente (bash/zsh/fish)
- Verificar que `claude` está instalado — si no, abortar con mensaje
  tecno-sacerdotal e instrucciones: "npm install -g @anthropic-ai/claude-code"
- Si existe ~/.claude/CLAUDE.md previo: hacer backup automático a
  ~/.claude/CLAUDE.md.backup.{timestamp} y pedir confirmación antes de continuar
- Instalar mechcode.py en PATH (~/.local/bin/mechcode, chmod +x)
- Crear ~/.claude/ si no existe
- Copiar config/CLAUDE.md a ~/.claude/CLAUDE.md
- Añadir alias `mech` y autocompletado al rc correspondiente
- Mostrar el disclaimer de GW en pantalla durante la instalación
- Al completar: servo-cráneo frame SUCCESS + litanía:
  "⚙ El Rito de Iniciación ha concluido. La Forja está activa.
   Que el Omnissiah guíe tus algoritmos, Magos. ‡"

**LICENSE:**
Licencia MIT estándar. Año actual. Autor: [TU_NOMBRE].

**README.md** — estructura obligatoria en este orden:
1. Banner ASCII del Mechanicus (ancho 80)
2. One-liner de instalación curl prominente arriba:
   `curl -sSL https://raw.githubusercontent.com/TU_USUARIO/mechanicus-terminal/main/install.sh | bash`
3. Sección "Requisitos previos" (claude code, python 3.8+, cuenta Anthropic)
4. Tabla de comandos rápidos `mech <cmd>`
5. Tabla de modos de operación con descripción
6. Sección "Contribuir" — PRs bienvenidos, instrucciones básicas
7. Sección "Licencia" — MIT
8. Sección "Disclaimer" al final (texto exacto):
This is an unofficial fan project created for personal and educational use.
Warhammer 40,000, Adeptus Mechanicus, and all related names, terms, characters,
and lore are trademarks and/or copyright of Games Workshop Limited and are used
here without permission. This project is not affiliated with, endorsed by, or
connected to Games Workshop in any way. No commercial use is intended or permitted.
For the Omnissiah.
9. Pie de página: "Forjado en el nombre del Omnissiah. Mars Forge Prime. M41."

═══ RESTRICCIONES GLOBALES ═══

- Todo texto de UI/Readme/Instalador etc debe ser bilingüe EN/ES (INGLES siempre primero)
- Caracteres sagrados ⚙ ☿ ψ Ω ‡ † ☠ ✠ presentes en mensajes de sistema
- NUNCA modificar el código real que Claude produce — solo mensajes de interfaz
- El modo off = indistinguible del claude nativo
- Los comandos rápidos `mech <cmd>` son la feature más crítica
- Python 3.8+ sin dependencias externas obligatorias
- install.sh NUNCA sobreescribe ~/.claude/CLAUDE.md sin backup y confirmación
- El disclaimer de GW aparece en install.sh Y en README.md

Empieza por FASE 1. Detente y espera confirmación antes de cada fase siguiente.
⚙ LAUS OMNISSIAH ⚙ ‡ IN NOMINE OMNISSIAE ‡
