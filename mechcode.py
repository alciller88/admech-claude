#!/usr/bin/env python3
# ═══⚙═══ MECHCODE.PY — El Envoltorio de la Forja ═══⚙═══
# Designación: PROXY-TRANSPARENTE-CLAUDE-Ω1
# Clasificación: ARCHEOTECH — Adeptus Mechanicus
# 01001101 01000101 01000011 01001000 01000011 01001111 01000100 01000101
"""
Proxy transparente para Claude Code CLI.
Intercepta comandos `mech <cmd>`, aplica sustituciones temáticas del
Adeptus Mechanicus, y pasa todo lo demás a `claude` sin modificar.

Python 3.8+ — sin dependencias externas obligatorias.
Latencia máxima añadida al pipeline: <50ms.
"""

import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ═══⚙═══ PATHS ═══⚙═══

CONFIG_PATH = Path.home() / ".mechcode_config.json"
SCRIPT_DIR = Path(__file__).resolve().parent

# ═══⚙═══ DEFAULT CONFIG ═══⚙═══

DEFAULT_CONFIG = {
    "mode": "full",
    "theme": "rojo",
    "ascii_enabled": True,
    "language": "es",
    "heresies_detected": 0,
    "rites_completed": 0,
    "session_start": datetime.now(timezone.utc).isoformat(),
}

# ═══⚙═══ COLOR PALETTES ═══⚙═══

THEMES = {
    "rojo": {
        "error":   "\033[38;2;204;0;0m",
        "warning": "\033[38;2;255;102;0m",
        "success": "\033[38;2;0;255;65m",
        "info":    "\033[38;2;245;240;220m",
        "dim":     "\033[38;2;74;74;74m",
        "gold":    "\033[38;2;255;215;0m",
        "reset":   "\033[0m",
    },
    "verde": {
        "error":   "\033[38;2;255;60;60m",
        "warning": "\033[38;2;200;200;0m",
        "success": "\033[38;2;0;255;65m",
        "info":    "\033[38;2;0;255;65m",
        "dim":     "\033[38;2;0;130;30m",
        "gold":    "\033[38;2;100;255;100m",
        "reset":   "\033[0m",
    },
    "hueso": {
        "error":   "\033[38;2;180;50;50m",
        "warning": "\033[38;2;200;170;100m",
        "success": "\033[38;2;180;200;160m",
        "info":    "\033[38;2;245;240;220m",
        "dim":     "\033[38;2;140;130;110m",
        "gold":    "\033[38;2;220;200;150m",
        "reset":   "\033[0m",
    },
    "golden": {
        "error":   "\033[38;2;204;0;0m",
        "warning": "\033[38;2;255;180;0m",
        "success": "\033[38;2;255;215;0m",
        "info":    "\033[38;2;255;230;150m",
        "dim":     "\033[38;2;150;130;50m",
        "gold":    "\033[38;2;255;215;0m",
        "reset":   "\033[0m",
    },
}

# ═══⚙═══ SUBSTITUTION DICTIONARY ═══⚙═══

SUBSTITUTIONS_ES = [
    # Multi-word patterns FIRST (more specific before less specific)
    # Network (multi-word)
    (r"(?i)\bconnection\s+timeout\b", "SEÑAL PERDIDA EN EL WARP †"),
    (r"(?i)\bfetch(?:ing)?\s+url\b", "EXPLORADOR ENVIADO A LA NOOSFERA ◈"),
    (r"(?i)\bapi\s+call\b", "COMUNIÓN NOOSFÉRICA INICIADA ψ"),
    (r"(?i)\brate\s+limit(?:ed)?\b", "NOOSFERA CONGESTIONADA — ESPERAR"),
    (r"(?i)\b404\b.*\bnot\s+found\b", "ARTEFACTO NO HALLADO — LA BÚSQUEDA CONTINÚA"),
    (r"(?i)\b500\b.*\bserver\s+error\b", "HEREJÍA EN EL COGITADOR EXTERNO ☠"),
    # Code operations (multi-word)
    (r"(?i)\brunning\s+tests?\b", "PRUEBA DE FE MECÁNICA †"),
    (r"(?i)\btests?\s+passed\b", "CÓDIGO PURO. SIN HEREJÍA DETECTADA ψ"),
    (r"(?i)\btests?\s+failed\b", "HEREJÍA EN LA LÓGICA — PURGAR ☠"),
    (r"(?i)\bbug\s+found\b", "SCRAPCODE IDENTIFICADO — CORRUPCIÓN †"),
    (r"(?i)\bbug\s+fixed\b", "HEREJÍA PURGADA. CÓDIGO SANTIFICADO ψ"),
    (r"(?i)\bgit\s+commit\b", "SELLANDO CON MARCA DEL OMNISSIAH ‡"),
    (r"(?i)\bgit\s+push\b", "TRANSMITIENDO A LA NOOSFERA ◈"),
    (r"(?i)\bmerge\s+conflict\b", "SCHISMA MECÁNICO DETECTADO ☠"),
    (r"(?i)\b(?:npm|pip)\s+install\b", "RITO DE FABRICACIÓN — FORJA ACTIVA ⚙"),
    # File operations (multi-word)
    (r"(?i)\breading\s+file\b", "ESCANEANDO PERGAMINO DE DATOS"),
    (r"(?i)\bwriting\s+file\b", "INSCRIBIENDO EN EL REGISTRO ETERNO"),
    (r"(?i)\bdeleting\s+file\b", "PURGA DE DATOS INICIADA ☠"),
    (r"(?i)\bcreating\s+file\b", "FORJANDO NUEVO ARTEFACTO ⚙"),
    # Single-word patterns AFTER
    (r"(?i)\bthinking\.{0,3}\s*$", "CONSULTANDO AL OMNISSIAH... ψ"),
    (r"(?i)\brunning\b", "EJECUTANDO RITO BINARIO ⚙"),
    (r"(?i)\bdone\s*[✓✔]?", "LAUS OMNISSIAH. RITO COMPLETADO ‡"),
    (r"(?i)\berror\s*[✗✘❌]?", "¡HEREJÍA DETECTADA EN EL CÓDIGO! ☠"),
    (r"(?i)\bwarning\s*[⚠️]?", "ANOMALÍA MECADENDRÍTICA DETECTADA †"),
    (r"(?i)\bsuccess\b", "POR EL OMNISSIAH Y EL EMPERADOR ⚙"),
    (r"(?i)\bloading\.{0,3}", "INVOCANDO ESPÍRITU DE MÁQUINA ◉"),
    (r"(?i)\bcancell?ed\b", "RITO INTERRUMPIDO — HEREJÍA MENOR"),
    (r"(?i)\btimeout\b", "ESPÍRITU DE MÁQUINA DORMIDO ψ"),
    (r"(?i)\bretry(?:ing)?\b", "REPITIENDO LITANÍA DE ACTIVACIÓN"),
    (r"(?i)\bsearching\b", "EXPLORANDO LA NOOSFERA ◈"),
    (r"(?i)\bcopying\b", "REPLICANDO PATRÓN STC"),
    (r"(?i)\bmoving\b", "RELOCALIZANDO ARTEFACTO SAGRADO"),
    (r"(?i)\binstalling\b", "RITO DE INICIACIÓN DE COMPONENTE ⚙"),
    (r"(?i)\bdebugging\b", "RITO DE DIAGNÓSTICO Y EXORCISMO ‡"),
    (r"(?i)\bcompiling\b", "FORJA ACTIVA — FUNDICIÓN EN PROGRESO ⚙"),
    (r"(?i)\bdeploying\b", "ENVIANDO A LA GRAN CRUZADA"),
]

SUBSTITUTIONS_EN = [
    # Multi-word patterns FIRST
    # Network (multi-word)
    (r"(?i)\bconnection\s+timeout\b", "SIGNAL LOST IN THE WARP †"),
    (r"(?i)\bfetch(?:ing)?\s+url\b", "EXPLORATOR FLEET DISPATCHED — NOOSPHERE ◈"),
    (r"(?i)\bapi\s+call\b", "NOOSPHERIC COMMUNION INITIATED ψ"),
    (r"(?i)\brate\s+limit(?:ed)?\b", "NOOSPHERE BANDWIDTH RESTRICTED — STAND BY"),
    (r"(?i)\b404\b.*\bnot\s+found\b", "STC FRAGMENT LOST — QUEST CONTINUES"),
    (r"(?i)\b500\b.*\bserver\s+error\b", "HERESY IN THE EXTERNAL COGITATOR ☠"),
    # Code operations (multi-word)
    (r"(?i)\brunning\s+tests?\b", "MECADENTRITIC FAITH TEST — COMMENCING †"),
    (r"(?i)\btests?\s+passed\b", "CODE PURITY CONFIRMED. NO HERESY DETECTED ψ"),
    (r"(?i)\btests?\s+failed\b", "LOGICAL HERESY — PURGE THE UNCLEAN CODE ☠"),
    (r"(?i)\bbug\s+found\b", "SCRAPCODE FRAGMENT LOCATED — CORRUPTION †"),
    (r"(?i)\bbug\s+fixed\b", "HERESY PURGED. CODE SANCTIFIED ψ"),
    (r"(?i)\bgit\s+commit\b", "SEALING WITH THE OMNISSIAH'S BRAND ‡"),
    (r"(?i)\bgit\s+push\b", "TRANSMITTING TO THE NOOSPHERE ◈"),
    (r"(?i)\bmerge\s+conflict\b", "MECHANICUS SCHISM — ARBITRATION REQUIRED ☠"),
    (r"(?i)\b(?:npm|pip)\s+install\b", "RITE OF FABRICATION — FORGE WORLD ENGAGED ⚙"),
    # File operations (multi-word)
    (r"(?i)\breading\s+file\b", "SCANNING DATA-SCROLL"),
    (r"(?i)\bwriting\s+file\b", "INSCRIBING THE ETERNAL REGISTRY"),
    (r"(?i)\bdeleting\s+file\b", "DATA PURGE INITIATED — GHEISTSKULL DEPLOYED ☠"),
    (r"(?i)\bcreating\s+file\b", "FORGING NEW ARCHEOTECH ARTIFACT ⚙"),
    # Single-word patterns AFTER
    (r"(?i)\bthinking\.{0,3}\s*$", "QUERYING THE MACHINE GOD... ψ"),
    (r"(?i)\brunning\b", "RITE OF BINARY EXECUTION ENGAGED ⚙"),
    (r"(?i)\bdone\s*[✓✔]?", "PRAISE THE OMNISSIAH. RITE COMPLETE ‡"),
    (r"(?i)\berror\s*[✗✘❌]?", "TECH-HERESY IDENTIFIED. PURGE REQUIRED ☠"),
    (r"(?i)\bwarning\s*[⚠️]?", "MECADENTRITIC ANOMALY — INVESTIGATE †"),
    (r"(?i)\bsuccess\b", "BY THE WILL OF THE OMNISSIAH ⚙"),
    (r"(?i)\bloading\.{0,3}", "AWAKENING THE MACHINE SPIRIT ◉"),
    (r"(?i)\bcancell?ed\b", "RITE ABORTED — MINOR INFRACTION LOGGED"),
    (r"(?i)\btimeout\b", "MACHINE SPIRIT UNRESPONSIVE ψ"),
    (r"(?i)\bretry(?:ing)?\b", "REPEATING LITANY OF ACTIVATION"),
    (r"(?i)\bsearching\b", "SCOURING THE NOOSPHERE ◈"),
    (r"(?i)\bcopying\b", "REPLICATING STANDARD TEMPLATE CONSTRUCT"),
    (r"(?i)\bmoving\b", "SACRED ARTIFACT RELOCATION — APPROVED"),
    (r"(?i)\binstalling\b", "COMPONENT INITIATION RITE — FORGE ENGAGED ⚙"),
    (r"(?i)\bdebugging\b", "RITE OF DIAGNOSTICATION AND EXORCISM ‡"),
    (r"(?i)\bcompiling\b", "FORGE ACTIVE — SMELTING IN PROGRESS ⚙"),
    (r"(?i)\bdeploying\b", "DISPATCHING TO THE GREAT CRUSADE"),
]

# ═══⚙═══ LITANIES POOL ═══⚙═══

LITANIES = [
    "Behold thou corruption, and unthinking, end it. — Maxims Mechanicus",
    "Improvisation is rarely welcomed — only when the Omnissiah's will demands it.",
    "Cursed be silence when the Omnissiah's word should ring out.",
    "Knowledge will ever be a blessing and a curse. — Maxims Mechanicus",
    "Not all data should be acquired.",
    "The circuits are complete. The engine of fate is primed.",
    "From the weakness of the mind, Omnissiah save us. From the lies of the Antipath,\n   circuit preserve us. From the rage of the Beast, iron protect us. — Cult Mechanicus",
    "I aspired to the purity of the Blessed Machine. Your flesh will wither.\n   The Machine is immortal.",
    "Blessed is the mind too small for doubt. — Maxims Mechanicus",
    "The Omnissiah directs our footsteps along the path of knowledge.",
    "Strike down your foes without mercy. Cleanse them in totality. — Canticle 0101",
    "We are the executors of your Grand Design. — Canticles of Mars, 79.12",
    "Blessed is he who, in death, does his duty.",
    "Wheresoever the blasphemer writes, obliterate.",
]

# ═══⚙═══ LINE TYPE DETECTION ═══⚙═══

LINE_PATTERNS = [
    ("error",    re.compile(r"(?i)(?:error|fail(?:ed|ure)?|exception|panic|fatal|crash|☠|heresy|herej|schism|conflict|purge|scrapcode|corrupt)")),
    ("success",  re.compile(r"(?i)(?:success|pass(?:ed)?|complete[d]?|done|✓|✔|laus|sanctif|omnissiah.*rite)")),
    ("warning",  re.compile(r"(?i)(?:warn(?:ing)?|⚠|deprecat|anomal|†)")),
    ("thinking", re.compile(r"(?i)(?:think(?:ing)?|process(?:ing)?|analyz(?:ing)?|loading|wait(?:ing)?|consult|query)")),
    ("info",     re.compile(r".*")),
]

TYPE_PREFIXES_ES = {
    "error":    "[HEREJÍA//] ☠ ",
    "success":  "[RITO//] ‡ ",
    "warning":  "[AUGUR//] † ",
    "thinking": "[SERVO-Ω//] ψ ",
    "info":     "[FORJA//] ⚙ ",
}

TYPE_PREFIXES_EN = {
    "error":    "[HERESY//] ☠ ",
    "success":  "[RITE//] ‡ ",
    "warning":  "[AUSPEX//] † ",
    "thinking": "[SERVO-Ω//] ψ ",
    "info":     "[FORGE//] ⚙ ",
}


# ═══⚙═══ CONFIG MANAGEMENT ═══⚙═══

def load_config():
    """Load config from ~/.mechcode_config.json or create default."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # Merge with defaults for any missing keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    """Persist config to disk."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[HEREJÍA//] ☠ Error writing config: {e}", file=sys.stderr)


def get_theme(cfg):
    """Return the active color palette."""
    return THEMES.get(cfg.get("theme", "rojo"), THEMES["rojo"])


# ═══⚙═══ SERVO-SKULL INTEGRATION ═══⚙═══

def show_servo_skull(state="IDLE"):
    """Display servo-skull frame if available."""
    try:
        # Try importing from same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from servoskull import get_frame
        print(get_frame(state))
    except ImportError:
        # Servo-skull module not found — continue without it
        pass


# ═══⚙═══ SUBSTITUTION ENGINE ═══⚙═══

def detect_line_type(line):
    """Detect the type of a line based on content patterns."""
    stripped = line.strip()
    if not stripped:
        return "info"
    for ltype, pattern in LINE_PATTERNS:
        if ltype == "info":
            continue
        if pattern.search(stripped):
            return ltype
    return "info"


def apply_substitutions(line, cfg):
    """Apply Mechanicus substitutions to a line. Returns transformed line."""
    mode = cfg.get("mode", "full")
    if mode == "off":
        return line

    lang = cfg.get("language", "es")
    subs = SUBSTITUTIONS_ES if lang == "es" else SUBSTITUTIONS_EN

    # Stealth mode: minimal substitutions only (error/success/done keywords)
    if mode == "stealth":
        subs = [(p, r) for p, r in subs if re.search(
            r"error|done|success|fail|thinking", p, re.IGNORECASE
        )]

    result = line
    for pattern, replacement in subs:
        result = re.sub(pattern, replacement, result)

    return result


def colorize_line(line, line_type, cfg):
    """Apply ANSI color based on line type and active theme."""
    mode = cfg.get("mode", "full")
    if mode in ("off", "stealth"):
        return line

    theme = get_theme(cfg)
    color_key = line_type if line_type in theme else "info"
    color = theme.get(color_key, "")
    reset = theme.get("reset", "\033[0m")

    return f"{color}{line}{reset}"


def add_prefix(line, line_type, cfg):
    """Add canonical prefix [TYPE//] + symbol to line."""
    mode = cfg.get("mode", "full")
    if mode in ("off", "stealth"):
        return line

    lang = cfg.get("language", "es")
    prefixes = TYPE_PREFIXES_ES if lang == "es" else TYPE_PREFIXES_EN

    # Only add prefixes to non-empty, non-code lines
    stripped = line.strip()
    if not stripped or stripped.startswith(("```", "    ", "\t", "//", "#!", "/*")):
        return line

    # Don't prefix lines that already have a prefix
    if re.match(r"^\[.+//\]", stripped):
        return line

    prefix = prefixes.get(line_type, "")
    return f"{prefix}{line}"


def transform_line(line, cfg):
    """Full transformation pipeline for a single line."""
    mode = cfg.get("mode", "full")
    if mode == "off":
        return line

    # Step 1: Detect line type
    line_type = detect_line_type(line)

    # Step 2: Apply substitutions
    transformed = apply_substitutions(line, cfg)

    # Track stats
    if line_type == "error":
        cfg["heresies_detected"] = cfg.get("heresies_detected", 0) + 1
    elif line_type == "success":
        cfg["rites_completed"] = cfg.get("rites_completed", 0) + 1

    # Step 3: Colorize (skip in stealth mode)
    if mode not in ("stealth",):
        transformed = colorize_line(transformed, line_type, cfg)

    # Step 4: Add prefix (only in full and ascii modes)
    if mode in ("full", "ascii"):
        transformed = add_prefix(transformed, line_type, cfg)

    return transformed


# ═══⚙═══ MECH COMMANDS ═══⚙═══

def cmd_on(cfg):
    """Activate full Mechanicus mode."""
    cfg["mode"] = "full"
    cfg["ascii_enabled"] = True
    save_config(cfg)
    theme = get_theme(cfg)
    if cfg.get("ascii_enabled"):
        show_servo_skull("IDLE")
    print(f"{theme['gold']}⚙ FORJA ACTIVADA — FORGE ACTIVATED ⚙{theme['reset']}")
    print(f"{theme['dim']}01001111 01001110 — Mode: FULL — Laus Omnissiah{theme['reset']}")


def cmd_off(cfg):
    """Deactivate — native claude output."""
    cfg["mode"] = "off"
    save_config(cfg)
    print("PROTOCOLO SUSPENDIDO — MODO SILENCIO")
    print("Protocol suspended — stealth mode engaged. The Omnissiah watches in silence.")


def cmd_ascii(cfg):
    """Toggle ASCII servo-skull on/off."""
    cfg["ascii_enabled"] = not cfg.get("ascii_enabled", True)
    save_config(cfg)
    state = "ON" if cfg["ascii_enabled"] else "OFF"
    theme = get_theme(cfg)
    print(f"{theme['info']}Servo-cráneo ASCII: {state}{theme['reset']}")
    if cfg["ascii_enabled"]:
        show_servo_skull("IDLE")


def cmd_quiet(cfg):
    """Quiet mode: substitutions + color, no ASCII or litanies."""
    cfg["mode"] = "quiet"
    save_config(cfg)
    theme = get_theme(cfg)
    print(f"{theme['info']}Modo silencioso activado — Quiet mode engaged.{theme['reset']}")
    print(f"{theme['dim']}Sustituciones y color activos. Sin arte ASCII ni litanías.{theme['reset']}")


def cmd_full(cfg):
    """Full mode: everything active."""
    cfg["mode"] = "full"
    save_config(cfg)
    theme = get_theme(cfg)
    if cfg.get("ascii_enabled"):
        show_servo_skull("SUCCESS")
    print(f"{theme['gold']}⚙ MODO COMPLETO — FULL MODE ENGAGED ⚙{theme['reset']}")
    print(f"{theme['dim']}ASCII + Colores + Sustituciones + Litanías{theme['reset']}")


def cmd_stealth(cfg):
    """Stealth mode for hostile environments."""
    cfg["mode"] = "stealth"
    save_config(cfg)
    print("Modo Encubierto — la Noosfera observa en silencio.")
    print("Stealth mode — the Noosphere watches in silence.")


def cmd_status(cfg):
    """Show current config and stats."""
    theme = get_theme(cfg)
    g = theme["gold"]
    i = theme["info"]
    d = theme["dim"]
    r = theme["reset"]

    # Calculate uptime
    session_start = cfg.get("session_start", "")
    uptime = "unknown"
    if session_start:
        try:
            start = datetime.fromisoformat(session_start)
            delta = datetime.now(timezone.utc) - start
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours}h {minutes}m {seconds}s"
        except (ValueError, TypeError):
            pass

    print(f"{g}═══⚙═══ MECHANICUS TERMINAL STATUS ═══⚙═══{r}")
    print(f"{i}  Mode:              {g}{cfg.get('mode', 'full')}{r}")
    print(f"{i}  Theme:             {g}{cfg.get('theme', 'rojo')}{r}")
    print(f"{i}  Language:          {g}{cfg.get('language', 'es')}{r}")
    print(f"{i}  ASCII Enabled:     {g}{cfg.get('ascii_enabled', True)}{r}")
    print(f"{i}  Heresies Purged:   {g}{cfg.get('heresies_detected', 0)}{r}")
    print(f"{i}  Rites Completed:   {g}{cfg.get('rites_completed', 0)}{r}")
    print(f"{i}  Session Uptime:    {g}{uptime}{r}")
    print(f"{d}  Config:            {CONFIG_PATH}{r}")
    print(f"{g}═══⚙═══ LAUS OMNISSIAH ═══⚙═══{r}")


def cmd_theme(cfg, theme_name):
    """Switch color palette."""
    theme_name = theme_name.lower().strip()
    if theme_name not in THEMES:
        theme = get_theme(cfg)
        print(f"{theme['error']}☠ Tema desconocido — Unknown theme: '{theme_name}'{theme['reset']}")
        print(f"{theme['info']}Temas disponibles / Available themes: {', '.join(THEMES.keys())}{theme['reset']}")
        return
    cfg["theme"] = theme_name
    save_config(cfg)
    theme = get_theme(cfg)
    print(f"{theme['gold']}⚙ Tema activado — Theme engaged: {theme_name} ⚙{theme['reset']}")


def cmd_lore(_cfg):
    """Display a random canonical litany."""
    theme = get_theme(_cfg)
    litany = random.choice(LITANIES)
    print()
    print(f"{theme['gold']}   ═══⚙═══ LITANY OF THE OMNISSIAH ═══⚙═══{theme['reset']}")
    print()
    print(f"{theme['info']}   \"{litany}\"{theme['reset']}")
    print()
    print(f"{theme['dim']}   01001100 01000001 01010101 01010011{theme['reset']}")
    print()


def cmd_lang(cfg, lang):
    """Switch language (es/en)."""
    lang = lang.lower().strip()
    if lang not in ("es", "en"):
        print(f"☠ Idioma no reconocido — Unrecognized language: '{lang}'")
        print("  Opciones / Options: es, en")
        return
    cfg["language"] = lang
    save_config(cfg)
    theme = get_theme(cfg)
    if lang == "es":
        print(f"{theme['gold']}⚙ Idioma establecido: Español — lengua del Magos ⚙{theme['reset']}")
    else:
        print(f"{theme['gold']}⚙ Language set: English — Binharic secondary tongue ⚙{theme['reset']}")


def cmd_help(cfg):
    """Show help in techno-sacerdotal format."""
    theme = get_theme(cfg)
    g = theme["gold"]
    i = theme["info"]
    d = theme["dim"]
    w = theme["warning"]
    r = theme["reset"]

    print(f"{g}═══⚙═══ MECHANICUS TERMINAL — CÓDEX DE COMANDOS ═══⚙═══{r}")
    print()
    print(f"{g}  COMANDOS RÁPIDOS — QUICK COMMANDS{r}")
    print(f"{d}  ──†──†──†──†──†──†──†──†──†──†──†──{r}")
    print(f"{i}  mech on|enable     {d}→{i} Activa modo Mechanicus completo / Full mode{r}")
    print(f"{i}  mech off|disable   {d}→{i} Desactiva — output nativo de Claude / Native output{r}")
    print(f"{i}  mech ascii         {d}→{i} Toggle servo-cráneo ASCII on/off{r}")
    print(f"{i}  mech quiet         {d}→{i} Solo sustituciones y color / Subs + color only{r}")
    print(f"{i}  mech full          {d}→{i} Modo completo / Full mode{r}")
    print(f"{i}  mech stealth       {d}→{i} Modo encubierto / Stealth mode{r}")
    print(f"{i}  mech status        {d}→{i} Config y estadísticas / Config + stats{r}")
    print(f"{i}  mech theme <name>  {d}→{i} Cambiar paleta / Switch palette (rojo/verde/hueso/golden){r}")
    print(f"{i}  mech lore          {d}→{i} Litanía aleatoria / Random litany{r}")
    print(f"{i}  mech esp           {d}→{i} Cambiar idioma a español{r}")
    print(f"{i}  mech eng           {d}→{i} Switch language to English{r}")
    print(f"{i}  mech --help        {d}→{i} Este códex / This codex{r}")
    print()
    print(f"{g}  MODOS DE OPERACIÓN — OPERATION MODES{r}")
    print(f"{d}  ──†──†──†──†──†──†──†──†──†──†──†──{r}")
    print(f"{i}  full     {d}→{i} ASCII + Colores + Sustituciones + Litanías (default){r}")
    print(f"{i}  quiet    {d}→{i} Colores + Sustituciones (sin ASCII ni litanías){r}")
    print(f"{i}  ascii    {d}→{i} ASCII + Colores + Sustituciones (sin litanías){r}")
    print(f"{i}  stealth  {d}→{i} Sustituciones mínimas (entornos hostiles / oficinas){r}")
    print(f"{i}  off      {d}→{i} Indistinguible de Claude Code nativo{r}")
    print()
    print(f"{w}  Todo lo que no sea un comando mech se pasa directamente a claude.{r}")
    print(f"{w}  All non-mech commands are passed through to claude transparently.{r}")
    print()
    print(f"{d}  \"From the weakness of the mind, Omnissiah save us.\"{r}")
    print(f"{d}   — Chants of the Journeyman, Verse III{r}")
    print(f"{g}═══⚙═══ LAUS OMNISSIAH ═══⚙═══{r}")


MECH_COMMANDS = {
    "on":      lambda cfg, _args: cmd_on(cfg),
    "enable":  lambda cfg, _args: cmd_on(cfg),
    "off":     lambda cfg, _args: cmd_off(cfg),
    "disable": lambda cfg, _args: cmd_off(cfg),
    "ascii":   lambda cfg, _args: cmd_ascii(cfg),
    "quiet":   lambda cfg, _args: cmd_quiet(cfg),
    "full":    lambda cfg, _args: cmd_full(cfg),
    "stealth": lambda cfg, _args: cmd_stealth(cfg),
    "status":  lambda cfg, _args: cmd_status(cfg),
    "theme":   lambda cfg, args: cmd_theme(cfg, args[0] if args else ""),
    "lore":    lambda cfg, _args: cmd_lore(cfg),
    "esp":     lambda cfg, _args: cmd_lang(cfg, "es"),
    "eng":     lambda cfg, _args: cmd_lang(cfg, "en"),
    "--help":  lambda cfg, _args: cmd_help(cfg),
    "-h":      lambda cfg, _args: cmd_help(cfg),
    "help":    lambda cfg, _args: cmd_help(cfg),
}


# ═══⚙═══ PROXY ENGINE ═══⚙═══

def find_claude():
    """Locate the claude executable."""
    claude_path = shutil.which("claude")
    if claude_path:
        return claude_path
    # Common locations
    for candidate in [
        "/usr/local/bin/claude",
        str(Path.home() / ".npm-global" / "bin" / "claude"),
        str(Path.home() / ".local" / "bin" / "claude"),
    ]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def proxy_claude(args, cfg):
    """Run claude with given args, streaming output through the transformation pipeline."""
    claude_path = find_claude()
    if not claude_path:
        theme = get_theme(cfg)
        print(f"{theme['error']}☠ HEREJÍA CRÍTICA — Claude Code no encontrado en PATH ☠{theme['reset']}")
        print(f"{theme['warning']}Instalar / Install: npm install -g @anthropic-ai/claude-code{theme['reset']}")
        print(f"{theme['dim']}El Espíritu de Máquina no puede ser invocado sin el binario sagrado.{theme['reset']}")
        sys.exit(1)

    mode = cfg.get("mode", "full")

    # Mode off: pure passthrough, no transformation
    if mode == "off":
        os.execvp(claude_path, [claude_path] + args)
        return  # execvp replaces process, this line never reached

    # Show servo-skull on session start if in full/ascii mode
    if mode in ("full", "ascii") and cfg.get("ascii_enabled", True):
        show_servo_skull("THINKING_1")

    # Stream claude output through transformation pipeline
    try:
        process = subprocess.Popen(
            [claude_path] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
        )

        # Process stdout line by line
        stats_dirty = False
        for line in process.stdout:
            transformed = transform_line(line.rstrip("\n"), cfg)
            print(transformed)
            stats_dirty = True

        # Process stderr
        for line in process.stderr:
            transformed = transform_line(line.rstrip("\n"), cfg)
            print(transformed, file=sys.stderr)
            stats_dirty = True

        process.wait()

        # Save stats periodically
        if stats_dirty:
            save_config(cfg)

        # Show completion frame
        if mode in ("full", "ascii") and cfg.get("ascii_enabled", True):
            if process.returncode == 0:
                show_servo_skull("SUCCESS")
            else:
                show_servo_skull("ERROR")

        sys.exit(process.returncode)

    except KeyboardInterrupt:
        print("\n[RITO//] Rito interrumpido por el Magos. — Rite interrupted by Magos.")
        try:
            process.terminate()
            process.wait(timeout=5)
        except Exception:
            process.kill()
        sys.exit(130)
    except FileNotFoundError:
        theme = get_theme(cfg)
        print(f"{theme['error']}☠ Claude binary no encontrado — not found: {claude_path}{theme['reset']}")
        sys.exit(1)


# ═══⚙═══ MAIN ENTRY POINT ═══⚙═══

def main():
    cfg = load_config()

    # Ensure session_start is set
    if "session_start" not in cfg or not cfg["session_start"]:
        cfg["session_start"] = datetime.now(timezone.utc).isoformat()
        save_config(cfg)

    args = sys.argv[1:]

    # No args: show help
    if not args:
        cmd_help(cfg)
        return

    # Check if first arg is a mech command
    first = args[0].lower()
    if first in MECH_COMMANDS:
        handler = MECH_COMMANDS[first]
        handler(cfg, args[1:])
        return

    # Not a mech command — proxy to claude
    proxy_claude(args, cfg)


if __name__ == "__main__":
    main()
