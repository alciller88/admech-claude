#!/usr/bin/env python3
# === MECHCODE.PY — El Envoltorio de la Forja ===
# Launches Claude Code in a tmux session with a servo-skull sidebar monitor.
"""
Mechanicus Terminal — tmux-based wrapper for Claude Code CLI.
- Left pane: claude (full TUI, unmodified)
- Right pane: servo-skull monitor (animated status display)
- Claude Code hooks update shared state file for the monitor

Python 3.8+ — no external dependencies.
"""

import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# === VERSION ===
VERSION = "1.0.0-beta"

# === PATHS ===
CONFIG_PATH = Path.home() / ".mechcode_config.json"
STATE_FILE = Path.home() / ".mechcode_state.json"
SCRIPT_DIR = Path(__file__).resolve().parent
MONITOR_SCRIPT = SCRIPT_DIR / "servoskull_monitor.py"

# === TMUX CONFIG ===
TMUX_SESSION = "mechanicus"
SIDEBAR_WIDTH = 32  # columns for the right pane

# === LANGUAGE DETECTION ===

def detect_system_language():
    """Detect language from system locale. Returns 'es' or 'en'."""
    for var in ("LANG", "LC_ALL", "LANGUAGE", "LC_MESSAGES"):
        val = os.environ.get(var, "")
        if val.lower().startswith("es"):
            return "es"
    return "en"


def get_lang(cfg):
    """Get active language. Config overrides system detection."""
    lang = cfg.get("language")
    if lang and lang != "auto":
        return lang
    return detect_system_language()


# === I18N STRINGS ===

I18N = {
    "en": {
        "forge_activated": "\u2699 FORGE ACTIVATED \u2699",
        "protocol_suspended": "PROTOCOL SUSPENDED \u2014 SILENCE MODE",
        "lang_set": "\u2699 Language: English \u2699",
        "unknown_theme": "Unknown theme: '{}'. Available: {}",
        "theme_set": "\u2699 Theme: {} \u2699",
        "sidebar_range": "Sidebar width must be between 20 and 60",
        "sidebar_invalid": "Invalid width: '{}'",
        "sidebar_set": "\u2699 Sidebar width: {} cols (restart session to apply) \u2699",
        "session_killed": "Session terminated.",
        "no_session": "No active Mechanicus session.",
        "help_header": "\u2550\u2550\u2550\u2699 MECHANICUS TERMINAL \u2014 COMMANDS \u2699\u2550\u2550\u2550",
        "help_footer_1": "All other args are passed to claude in a tmux session",
        "help_footer_2": "with an animated servo-skull sidebar monitor.",
        "help_cmds": [
            ("mech on|enable",          "Activate Mechanicus mode",       "mech on"),
            ("mech off|disable",        "Deactivate \u2014 native claude output",  "mech off"),
            ("mech status",             "Show config + stats",            "mech status"),
            ("mech theme <name>",       "Switch palette",                 "mech theme verde"),
            ("mech lore",               "Random canonical litany",        "mech lore"),
            ("mech esp | eng",          "Switch language",                "mech esp"),
            ("mech sidebar <N>",        "Set sidebar width (20-60)",      "mech sidebar 40"),
            ("mech diagnose",           "Run system diagnostics",         "mech diagnose"),
            ("mech version",            "Show version",                   "mech version"),
            ("mech kill",               "Kill tmux session",              "mech kill"),
            ("mech --help",             "This codex",                     "mech --help"),
        ],
        "help_quickstart_header": "QUICK START",
        "help_quickstart": [
            "1. mech on          \u2192 Enable Mechanicus mode",
            "2. mech <prompt>    \u2192 Launch claude with servo-skull sidebar",
            "3. mech diagnose    \u2192 Check system readiness",
        ],
        "claude_not_found": "HERESY \u2014 Claude Code not found in PATH",
        "claude_install": "Install: npm install -g @anthropic-ai/claude-code",
        "tmux_required": "tmux is required for Mechanicus Terminal",
        "tmux_install": "Install: sudo apt install tmux  /  brew install tmux",
        "status_header": "\u2550\u2550\u2550\u2699\u2550\u2550\u2550 MECHANICUS STATUS \u2550\u2550\u2550\u2699\u2550\u2550\u2550",
        "version_label": "Mechanicus Terminal",
        # Diagnose strings
        "diag_header": "\u2550\u2550\u2550\u2699 SYSTEM DIAGNOSTICS \u2014 AUSPEX SCAN \u2699\u2550\u2550\u2550",
        "diag_footer": "\u2550\u2550\u2550\u2699 SCAN COMPLETE \u2699\u2550\u2550\u2550",
        "diag_python_ver": "Python version",
        "diag_python_ok": "Python {ver} (3.8+ required)",
        "diag_python_fail": "Python {ver} is below 3.8. Upgrade your Python installation.",
        "diag_tmux": "tmux installed",
        "diag_tmux_ok": "tmux {ver}",
        "diag_tmux_fail": "tmux not found. Install: sudo apt install tmux / brew install tmux",
        "diag_claude": "claude command",
        "diag_claude_ok": "Found at {path}",
        "diag_claude_fail": "Not found. Install: npm install -g @anthropic-ai/claude-code",
        "diag_hooks": "Claude hooks configured",
        "diag_hooks_ok": "mechcode_hook.py registered in settings.json",
        "diag_hooks_fail": "Hooks not configured. Run: install.sh",
        "diag_hooks_no_file": "~/.claude/settings.json not found. Run: install.sh",
        "diag_state": "State file (~/.mechcode_state.json)",
        "diag_state_ok": "Valid JSON, last updated {age}s ago",
        "diag_state_missing": "Not found (created on first session launch)",
        "diag_state_invalid": "Contains invalid JSON. Delete and relaunch: rm ~/.mechcode_state.json",
        "diag_config": "Config file (~/.mechcode_config.json)",
        "diag_config_ok": "Valid JSON",
        "diag_config_missing": "Not found (defaults will be used)",
        "diag_config_invalid": "Contains invalid JSON. Delete to reset: rm ~/.mechcode_config.json",
        "diag_scripts": "Scripts in ~/.local/bin",
        "diag_scripts_ok": "All {n} scripts found",
        "diag_scripts_fail": "Missing: {missing}. Run: install.sh",
        "diag_session": "tmux session '{name}'",
        "diag_session_ok": "Running",
        "diag_session_warn": "Not running (will start on next launch)",
        "diag_path": "~/.local/bin in PATH",
        "diag_path_ok": "PATH includes ~/.local/bin",
        "diag_path_fail": "~/.local/bin not in PATH. Add to your shell profile: export PATH=\"$HOME/.local/bin:$PATH\"",
        "diag_summary_ok": "All systems operational. The Machine Spirit is pleased.",
        "diag_summary_warn": "{n} warning(s) detected. Non-critical, but review recommended.",
        "diag_summary_fail": "{n} failure(s) detected. Purge required before operation.",
    },
    "es": {
        "forge_activated": "\u2699 FORJA ACTIVADA \u2699",
        "protocol_suspended": "PROTOCOLO SUSPENDIDO \u2014 MODO SILENCIO",
        "lang_set": "\u2699 Idioma: Espa\u00f1ol \u2699",
        "unknown_theme": "Tema desconocido: '{}'. Disponibles: {}",
        "theme_set": "\u2699 Tema: {} \u2699",
        "sidebar_range": "El ancho del sidebar debe estar entre 20 y 60",
        "sidebar_invalid": "Ancho no v\u00e1lido: '{}'",
        "sidebar_set": "\u2699 Ancho sidebar: {} cols (reiniciar sesi\u00f3n para aplicar) \u2699",
        "session_killed": "Sesi\u00f3n terminada.",
        "no_session": "No hay sesi\u00f3n Mechanicus activa.",
        "help_header": "\u2550\u2550\u2550\u2699 MECHANICUS TERMINAL \u2014 COMANDOS \u2699\u2550\u2550\u2550",
        "help_footer_1": "El resto de args se pasan a claude en una sesi\u00f3n tmux",
        "help_footer_2": "con un monitor de servo-cr\u00e1neo animado.",
        "help_cmds": [
            ("mech on|enable",          "Activar modo Mechanicus",        "mech on"),
            ("mech off|disable",        "Desactivar \u2014 output nativo de claude", "mech off"),
            ("mech status",             "Config y estad\u00edsticas",            "mech status"),
            ("mech theme <name>",       "Cambiar paleta",                 "mech theme verde"),
            ("mech lore",               "Letan\u00eda can\u00f3nica aleatoria",       "mech lore"),
            ("mech esp | eng",          "Cambiar idioma",                 "mech esp"),
            ("mech sidebar <N>",        "Ancho del sidebar (20-60)",      "mech sidebar 40"),
            ("mech diagnostico",        "Diagn\u00f3stico del sistema",         "mech diagnostico"),
            ("mech version",            "Mostrar versi\u00f3n",                 "mech version"),
            ("mech kill",               "Terminar sesi\u00f3n tmux",            "mech kill"),
            ("mech --help",             "Este c\u00f3dex",                      "mech --help"),
        ],
        "help_quickstart_header": "INICIO R\u00c1PIDO",
        "help_quickstart": [
            "1. mech on          \u2192 Activar modo Mechanicus",
            "2. mech <prompt>    \u2192 Lanzar claude con sidebar servo-cr\u00e1neo",
            "3. mech diagnostico \u2192 Verificar estado del sistema",
        ],
        "claude_not_found": "HEREJ\u00cdA \u2014 Claude Code no encontrado en PATH",
        "claude_install": "Instalar: npm install -g @anthropic-ai/claude-code",
        "tmux_required": "tmux es necesario para Mechanicus Terminal",
        "tmux_install": "Instalar: sudo apt install tmux  /  brew install tmux",
        "status_header": "\u2550\u2550\u2550\u2699\u2550\u2550\u2550 ESTADO MECHANICUS \u2550\u2550\u2550\u2699\u2550\u2550\u2550",
        "version_label": "Mechanicus Terminal",
        # Diagnose strings
        "diag_header": "\u2550\u2550\u2550\u2699 DIAGN\u00d3STICO DEL SISTEMA \u2014 ESCANEO AUSPEX \u2699\u2550\u2550\u2550",
        "diag_footer": "\u2550\u2550\u2550\u2699 ESCANEO COMPLETO \u2699\u2550\u2550\u2550",
        "diag_python_ver": "Versi\u00f3n de Python",
        "diag_python_ok": "Python {ver} (se requiere 3.8+)",
        "diag_python_fail": "Python {ver} es inferior a 3.8. Actualice su instalaci\u00f3n de Python.",
        "diag_tmux": "tmux instalado",
        "diag_tmux_ok": "tmux {ver}",
        "diag_tmux_fail": "tmux no encontrado. Instalar: sudo apt install tmux / brew install tmux",
        "diag_claude": "Comando claude",
        "diag_claude_ok": "Encontrado en {path}",
        "diag_claude_fail": "No encontrado. Instalar: npm install -g @anthropic-ai/claude-code",
        "diag_hooks": "Hooks de Claude configurados",
        "diag_hooks_ok": "mechcode_hook.py registrado en settings.json",
        "diag_hooks_fail": "Hooks no configurados. Ejecutar: install.sh",
        "diag_hooks_no_file": "~/.claude/settings.json no encontrado. Ejecutar: install.sh",
        "diag_state": "Archivo de estado (~/.mechcode_state.json)",
        "diag_state_ok": "JSON v\u00e1lido, \u00faltima actualizaci\u00f3n hace {age}s",
        "diag_state_missing": "No encontrado (se crea al iniciar la primera sesi\u00f3n)",
        "diag_state_invalid": "JSON inv\u00e1lido. Eliminar y relanzar: rm ~/.mechcode_state.json",
        "diag_config": "Archivo de config (~/.mechcode_config.json)",
        "diag_config_ok": "JSON v\u00e1lido",
        "diag_config_missing": "No encontrado (se usar\u00e1n valores por defecto)",
        "diag_config_invalid": "JSON inv\u00e1lido. Eliminar para reiniciar: rm ~/.mechcode_config.json",
        "diag_scripts": "Scripts en ~/.local/bin",
        "diag_scripts_ok": "Los {n} scripts encontrados",
        "diag_scripts_fail": "Faltan: {missing}. Ejecutar: install.sh",
        "diag_session": "Sesi\u00f3n tmux '{name}'",
        "diag_session_ok": "En ejecuci\u00f3n",
        "diag_session_warn": "No activa (se iniciar\u00e1 en el pr\u00f3ximo lanzamiento)",
        "diag_path": "~/.local/bin en PATH",
        "diag_path_ok": "PATH incluye ~/.local/bin",
        "diag_path_fail": "~/.local/bin no est\u00e1 en PATH. A\u00f1adir al perfil del shell: export PATH=\"$HOME/.local/bin:$PATH\"",
        "diag_summary_ok": "Todos los sistemas operativos. El Esp\u00edritu de M\u00e1quina est\u00e1 complacido.",
        "diag_summary_warn": "{n} advertencia(s) detectada(s). No cr\u00edtico, pero se recomienda revisar.",
        "diag_summary_fail": "{n} fallo(s) detectado(s). Purga necesaria antes de operar.",
    },
}


# === DEFAULT CONFIG ===
DEFAULT_CONFIG = {
    "mode": "full",
    "theme": "rojo",
    "ascii_enabled": True,
    "language": "auto",
    "sidebar_width": SIDEBAR_WIDTH,
    "heresies_detected": 0,
    "rites_completed": 0,
    "session_start": datetime.now(timezone.utc).isoformat(),
}

# === COLOR PALETTES ===
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

# === LITANIES ===
LITANIES = [
    "Behold thou corruption, and unthinking, end it. \u2014 Maxims Mechanicus",
    "Knowledge will ever be a blessing and a curse. \u2014 Maxims Mechanicus",
    "Blessed is the mind too small for doubt. \u2014 Maxims Mechanicus",
    "The circuits are complete. The engine of fate is primed.",
    "From the weakness of the mind, Omnissiah save us.",
    "The Omnissiah directs our footsteps along the path of knowledge.",
    "Strike down your foes without mercy. \u2014 Canticle 0101",
    "We are the executors of your Grand Design. \u2014 Canticles of Mars, 79.12",
    "Wheresoever the blasphemer writes, obliterate.",
    "I aspired to the purity of the Blessed Machine.",
]


# === CONFIG MANAGEMENT ===

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"\033[31m[HERESY//] Error writing config: {e}\033[0m", file=sys.stderr)


def get_theme(cfg):
    return THEMES.get(cfg.get("theme", "rojo"), THEMES["rojo"])


def reset_state():
    """Reset the shared state file for a new session."""
    state = {
        "main_state": "IDLE",
        "tool": None,
        "tool_detail": None,
        "message_es": "AGUARDANDO INSTRUCCIONES",
        "message_en": "AWAITING COMMAND",
        "timestamp": time.time(),
        "agents": {},
        "stats": {
            "heresies_detected": 0,
            "rites_completed": 0,
            "tools_invoked": 0,
            "session_start": time.time(),
        },
    }
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    except OSError:
        pass


# === TMUX OPERATIONS ===

def has_tmux():
    return shutil.which("tmux") is not None


def tmux_session_exists():
    result = subprocess.run(
        ["tmux", "has-session", "-t", TMUX_SESSION],
        capture_output=True,
    )
    return result.returncode == 0


def find_claude():
    claude_path = shutil.which("claude")
    if claude_path:
        return claude_path
    for candidate in [
        "/usr/local/bin/claude",
        str(Path.home() / ".npm-global" / "bin" / "claude"),
        str(Path.home() / ".local" / "bin" / "claude"),
    ]:
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def find_python():
    for cmd in ["python3", "python"]:
        path = shutil.which(cmd)
        if path:
            return path
    return "python3"


def launch_tmux_session(claude_args, cfg):
    """Launch a tmux session with claude on the left, monitor on the right."""
    claude_path = find_claude()
    if not claude_path:
        theme = get_theme(cfg)
        t = I18N[get_lang(cfg)]
        print(f"{theme['error']}{t['claude_not_found']}\033[0m")
        print(f"{theme['warning']}{t['claude_install']}\033[0m")
        sys.exit(1)

    python_path = find_python()
    monitor_path = str(MONITOR_SCRIPT)
    width = cfg.get("sidebar_width", SIDEBAR_WIDTH)

    # Reset state for new session
    reset_state()

    # Build claude command with args
    claude_cmd = claude_path
    if claude_args:
        # Escape args for shell
        escaped_args = " ".join(
            f"'{a}'" if " " in a or "'" not in a else f'"{a}"'
            for a in claude_args
        )
        claude_cmd = f"{claude_path} {escaped_args}"

    if tmux_session_exists():
        # Attach to existing session
        os.execvp("tmux", ["tmux", "attach-session", "-t", TMUX_SESSION])
        return

    # Create new tmux session with claude in the main pane
    # -d: detached initially so we can set up panes
    subprocess.run([
        "tmux", "new-session",
        "-d",                          # detached
        "-s", TMUX_SESSION,            # session name
        "-x", "200", "-y", "50",       # initial size (will adapt)
        claude_cmd,                    # command for left pane
    ], check=True)

    # Split right pane for the monitor
    subprocess.run([
        "tmux", "split-window",
        "-t", TMUX_SESSION,
        "-h",                          # horizontal split (side by side)
        "-l", str(width),              # width of the right pane
        f"{python_path} {monitor_path}",
    ], check=True)

    # Focus back on the left pane (claude)
    subprocess.run([
        "tmux", "select-pane",
        "-t", f"{TMUX_SESSION}:0.0",
    ], check=True)

    # Set pane border style
    subprocess.run([
        "tmux", "set-option", "-t", TMUX_SESSION,
        "pane-border-style", "fg=colour240",
    ], capture_output=True)
    subprocess.run([
        "tmux", "set-option", "-t", TMUX_SESSION,
        "pane-active-border-style", "fg=colour214",
    ], capture_output=True)

    # Disable status bar for cleaner look (optional, can be toggled)
    subprocess.run([
        "tmux", "set-option", "-t", TMUX_SESSION,
        "status", "off",
    ], capture_output=True)

    # Attach to the session
    os.execvp("tmux", ["tmux", "attach-session", "-t", TMUX_SESSION])


# === MECH COMMANDS ===

def cmd_on(cfg):
    cfg["mode"] = "full"
    cfg["ascii_enabled"] = True
    save_config(cfg)
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    print(f"{theme['gold']}{t['forge_activated']}{theme['reset']}")

def cmd_off(cfg):
    cfg["mode"] = "off"
    save_config(cfg)
    t = I18N[get_lang(cfg)]
    print(t["protocol_suspended"])

def cmd_status(cfg):
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    g, i, d, r = theme["gold"], theme["info"], theme["dim"], theme["reset"]
    print(f"{g}{t['status_header']}{r}")
    print(f"{i}  Mode:     {g}{cfg.get('mode', 'full')}{r}")
    print(f"{i}  Theme:    {g}{cfg.get('theme', 'rojo')}{r}")
    print(f"{i}  Language: {g}{cfg.get('language', 'auto')}{r}")
    print(f"{i}  Sidebar:  {g}{cfg.get('sidebar_width', SIDEBAR_WIDTH)} cols{r}")
    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            stats = state.get("stats", {})
            print(f"{i}  Rites:    {g}{stats.get('rites_completed', 0)}{r}")
            print(f"{i}  Heresies: {g}{stats.get('heresies_detected', 0)}{r}")
            print(f"{i}  Tools:    {g}{stats.get('tools_invoked', 0)}{r}")
    except (json.JSONDecodeError, OSError):
        pass
    print(f"{g}\u2550\u2550\u2550\u2699 LAUS OMNISSIAH \u2699\u2550\u2550\u2550{r}")

def cmd_theme(cfg, theme_name):
    theme_name = theme_name.lower().strip()
    t = I18N[get_lang(cfg)]
    if theme_name not in THEMES:
        print(f"\033[31m{t['unknown_theme'].format(theme_name, ', '.join(THEMES.keys()))}\033[0m")
        return
    cfg["theme"] = theme_name
    save_config(cfg)
    theme = get_theme(cfg)
    print(f"{theme['gold']}{t['theme_set'].format(theme_name)}{theme['reset']}")

def cmd_lore(_cfg):
    theme = get_theme(_cfg)
    litany = random.choice(LITANIES)
    print(f"\n{theme['gold']}   \u2550\u2550\u2550\u2699 LITANY \u2699\u2550\u2550\u2550{theme['reset']}")
    print(f"{theme['info']}   \"{litany}\"{theme['reset']}")
    print(f"{theme['dim']}   01001100 01000001 01010101 01010011{theme['reset']}\n")

def cmd_lang(cfg, lang):
    lang = lang.lower().strip()
    if lang not in ("es", "en"):
        print(f"Unknown language: '{lang}'. Options: es, en")
        return
    cfg["language"] = lang
    save_config(cfg)
    t = I18N[lang]
    print(t["lang_set"])

def cmd_sidebar(cfg, width_str):
    t = I18N[get_lang(cfg)]
    try:
        width = int(width_str)
        if width < 20 or width > 60:
            print(t["sidebar_range"])
            return
    except ValueError:
        print(t["sidebar_invalid"].format(width_str))
        return
    cfg["sidebar_width"] = width
    save_config(cfg)
    print(t["sidebar_set"].format(width))

def cmd_kill(_cfg):
    t = I18N[get_lang(_cfg)]
    if tmux_session_exists():
        subprocess.run(["tmux", "kill-session", "-t", TMUX_SESSION])
        print(t["session_killed"])
    else:
        print(t["no_session"])

def cmd_version(cfg):
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    g, i, d, r = theme["gold"], theme["info"], theme["dim"], theme["reset"]
    print(f"{g}\u2699 {t['version_label']} v{VERSION} \u2699{r}")
    print(f"{i}  Python:   {d}{platform.python_version()}{r}")
    print(f"{i}  Platform: {d}{platform.system()} {platform.machine()}{r}")

def cmd_help(cfg):
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    g, i, d, w, s, r = (theme["gold"], theme["info"], theme["dim"],
                         theme["warning"], theme["success"], theme["reset"])
    print(f"{g}{t['help_header']}{r}")
    print()
    # Quick start section
    print(f"  {g}\u250c\u2500 {t['help_quickstart_header']} \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500{r}")
    for line in t["help_quickstart"]:
        print(f"  {g}\u2502{r} {s}{line}{r}")
    print(f"  {g}\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500{r}")
    print()
    for cmd, desc, example in t["help_cmds"]:
        print(f"{i}  {cmd:<24}{d}\u2192{i} {desc}")
        print(f"{d}{'':>26}ex: {example}{r}")
    print()
    print(f"{w}  {t['help_footer_1']}{r}")
    print(f"{w}  {t['help_footer_2']}{r}")
    print()
    print(f"{d}  \"From the weakness of the mind, Omnissiah save us.\"{r}")
    print(f"{g}\u2550\u2550\u2550\u2699 LAUS OMNISSIAH \u2699\u2550\u2550\u2550{r}")


def cmd_diagnose(cfg):
    """Run comprehensive system diagnostics."""
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    g, i, d, r = theme["gold"], theme["info"], theme["dim"], theme["reset"]
    sc = theme["success"]
    er = theme["error"]
    wr = theme["warning"]

    # Symbols
    SYM_OK = f"{sc}\u2713{r}"
    SYM_FAIL = f"{er}\u2717{r}"
    SYM_WARN = f"{wr}\u2020{r}"

    failures = 0
    warnings = 0

    def print_check(symbol, label, detail):
        print(f"  {symbol} {i}{label:<38}{d}{detail}{r}")

    print(f"{g}{t['diag_header']}{r}")
    print()

    # 1. Python version
    pyver = platform.python_version()
    pymajor, pyminor = sys.version_info[:2]
    if pymajor >= 3 and pyminor >= 8:
        print_check(SYM_OK, t["diag_python_ver"],
                    t["diag_python_ok"].format(ver=pyver))
    else:
        print_check(SYM_FAIL, t["diag_python_ver"],
                    t["diag_python_fail"].format(ver=pyver))
        failures += 1

    # 2. tmux installed + version
    tmux_path = shutil.which("tmux")
    if tmux_path:
        try:
            result = subprocess.run(["tmux", "-V"], capture_output=True, text=True)
            tmux_ver = result.stdout.strip()
        except OSError:
            tmux_ver = "unknown"
        print_check(SYM_OK, t["diag_tmux"],
                    t["diag_tmux_ok"].format(ver=tmux_ver))
    else:
        print_check(SYM_FAIL, t["diag_tmux"], t["diag_tmux_fail"])
        failures += 1

    # 3. claude command
    claude_path = find_claude()
    if claude_path:
        print_check(SYM_OK, t["diag_claude"],
                    t["diag_claude_ok"].format(path=claude_path))
    else:
        print_check(SYM_FAIL, t["diag_claude"], t["diag_claude_fail"])
        failures += 1

    # 4. Claude hooks in settings.json
    settings_path = Path.home() / ".claude" / "settings.json"
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            hooks = settings.get("hooks", {})
            hook_str = json.dumps(hooks)
            if "mechcode_hook" in hook_str:
                print_check(SYM_OK, t["diag_hooks"], t["diag_hooks_ok"])
            else:
                print_check(SYM_FAIL, t["diag_hooks"], t["diag_hooks_fail"])
                failures += 1
        except (json.JSONDecodeError, OSError):
            print_check(SYM_FAIL, t["diag_hooks"], t["diag_hooks_fail"])
            failures += 1
    else:
        print_check(SYM_FAIL, t["diag_hooks"], t["diag_hooks_no_file"])
        failures += 1

    # 5. State file
    if STATE_FILE.exists():
        try:
            state_data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            ts = state_data.get("timestamp", 0)
            age = int(time.time() - ts) if ts else "?"
            print_check(SYM_OK, t["diag_state"],
                        t["diag_state_ok"].format(age=age))
        except json.JSONDecodeError:
            print_check(SYM_FAIL, t["diag_state"], t["diag_state_invalid"])
            failures += 1
    else:
        print_check(SYM_WARN, t["diag_state"], t["diag_state_missing"])
        warnings += 1

    # 6. Config file
    if CONFIG_PATH.exists():
        try:
            json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            print_check(SYM_OK, t["diag_config"], t["diag_config_ok"])
        except json.JSONDecodeError:
            print_check(SYM_FAIL, t["diag_config"], t["diag_config_invalid"])
            failures += 1
    else:
        print_check(SYM_WARN, t["diag_config"], t["diag_config_missing"])
        warnings += 1

    # 7. Scripts in ~/.local/bin
    local_bin = Path.home() / ".local" / "bin"
    expected_scripts = [
        "mechcode.py", "servoskull.py", "servoskull_monitor.py", "mechcode_hook.py"
    ]
    missing_scripts = [s for s in expected_scripts if not (local_bin / s).exists()]
    if not missing_scripts:
        print_check(SYM_OK, t["diag_scripts"],
                    t["diag_scripts_ok"].format(n=len(expected_scripts)))
    else:
        print_check(SYM_FAIL, t["diag_scripts"],
                    t["diag_scripts_fail"].format(missing=", ".join(missing_scripts)))
        failures += 1

    # 8. tmux session running
    if tmux_path:
        if tmux_session_exists():
            print_check(SYM_OK,
                        t["diag_session"].format(name=TMUX_SESSION),
                        t["diag_session_ok"])
        else:
            print_check(SYM_WARN,
                        t["diag_session"].format(name=TMUX_SESSION),
                        t["diag_session_warn"])
            warnings += 1
    else:
        print_check(SYM_FAIL,
                    t["diag_session"].format(name=TMUX_SESSION),
                    t["diag_tmux_fail"])
        # Already counted in tmux check above

    # 9. PATH includes ~/.local/bin
    local_bin_str = str(local_bin)
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if local_bin_str in path_dirs:
        print_check(SYM_OK, t["diag_path"], t["diag_path_ok"])
    else:
        print_check(SYM_FAIL, t["diag_path"], t["diag_path_fail"])
        failures += 1

    # Summary
    print()
    if failures == 0 and warnings == 0:
        print(f"  {sc}{t['diag_summary_ok']}{r}")
    elif failures == 0:
        print(f"  {wr}{t['diag_summary_warn'].format(n=warnings)}{r}")
    else:
        print(f"  {er}{t['diag_summary_fail'].format(n=failures)}{r}")
        if warnings > 0:
            print(f"  {wr}{t['diag_summary_warn'].format(n=warnings)}{r}")

    print(f"{g}{t['diag_footer']}{r}")


MECH_COMMANDS = {
    "on":          lambda cfg, _: cmd_on(cfg),
    "enable":      lambda cfg, _: cmd_on(cfg),
    "off":         lambda cfg, _: cmd_off(cfg),
    "disable":     lambda cfg, _: cmd_off(cfg),
    "status":      lambda cfg, _: cmd_status(cfg),
    "theme":       lambda cfg, a: cmd_theme(cfg, a[0] if a else ""),
    "lore":        lambda cfg, _: cmd_lore(cfg),
    "esp":         lambda cfg, _: cmd_lang(cfg, "es"),
    "eng":         lambda cfg, _: cmd_lang(cfg, "en"),
    "sidebar":     lambda cfg, a: cmd_sidebar(cfg, a[0] if a else "32"),
    "kill":        lambda cfg, _: cmd_kill(cfg),
    "diagnose":    lambda cfg, _: cmd_diagnose(cfg),
    "diagnostico": lambda cfg, _: cmd_diagnose(cfg),
    "version":     lambda cfg, _: cmd_version(cfg),
    "--help":      lambda cfg, _: cmd_help(cfg),
    "-h":          lambda cfg, _: cmd_help(cfg),
    "help":        lambda cfg, _: cmd_help(cfg),
}


# === MAIN ===

def main():
    cfg = load_config()

    if "session_start" not in cfg or not cfg["session_start"]:
        cfg["session_start"] = datetime.now(timezone.utc).isoformat()
        save_config(cfg)

    args = sys.argv[1:]

    # No args: show help
    if not args:
        cmd_help(cfg)
        return

    # Check for mech commands
    first = args[0].lower()
    if first in MECH_COMMANDS:
        handler = MECH_COMMANDS[first]
        handler(cfg, args[1:])
        return

    # Mode off: pure passthrough to claude, no tmux
    if cfg.get("mode") == "off":
        claude_path = find_claude()
        if claude_path:
            os.execvp(claude_path, [claude_path] + args)
        else:
            print("Claude Code not found in PATH", file=sys.stderr)
            sys.exit(1)
        return

    # Check prerequisites
    if not has_tmux():
        theme = get_theme(cfg)
        t = I18N[get_lang(cfg)]
        print(f"{theme['error']}{t['tmux_required']}{theme['reset']}")
        print(f"{theme['info']}{t['tmux_install']}{theme['reset']}")
        sys.exit(1)

    # Launch tmux session with claude + monitor
    launch_tmux_session(args, cfg)


if __name__ == "__main__":
    main()
