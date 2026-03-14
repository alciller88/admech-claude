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
import random
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

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
            ("mech on|enable",    "Activate Mechanicus mode"),
            ("mech off|disable",  "Deactivate \u2014 native claude output"),
            ("mech status",       "Show config + stats"),
            ("mech theme <name>", "Switch palette (rojo/verde/hueso/golden)"),
            ("mech lore",         "Random canonical litany"),
            ("mech esp",          "Language: Spanish"),
            ("mech eng",          "Language: English"),
            ("mech sidebar <N>",  "Set sidebar width (20-60 cols)"),
            ("mech kill",         "Kill tmux session"),
            ("mech --help",       "This codex"),
        ],
        "claude_not_found": "HERESY \u2014 Claude Code not found in PATH",
        "claude_install": "Install: npm install -g @anthropic-ai/claude-code",
        "tmux_required": "tmux is required for Mechanicus Terminal",
        "tmux_install": "Install: sudo apt install tmux  /  brew install tmux",
        "status_header": "\u2550\u2550\u2550\u2699\u2550\u2550\u2550 MECHANICUS STATUS \u2550\u2550\u2550\u2699\u2550\u2550\u2550",
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
            ("mech on|enable",    "Activar modo Mechanicus"),
            ("mech off|disable",  "Desactivar \u2014 output nativo de claude"),
            ("mech status",       "Config y estad\u00edsticas"),
            ("mech theme <name>", "Cambiar paleta (rojo/verde/hueso/golden)"),
            ("mech lore",         "Letan\u00eda can\u00f3nica aleatoria"),
            ("mech esp",          "Idioma: Espa\u00f1ol"),
            ("mech eng",          "Idioma: Ingl\u00e9s"),
            ("mech sidebar <N>",  "Ancho del sidebar (20-60 cols)"),
            ("mech kill",         "Terminar sesi\u00f3n tmux"),
            ("mech --help",       "Este c\u00f3dex"),
        ],
        "claude_not_found": "HEREJ\u00cdA \u2014 Claude Code no encontrado en PATH",
        "claude_install": "Instalar: npm install -g @anthropic-ai/claude-code",
        "tmux_required": "tmux es necesario para Mechanicus Terminal",
        "tmux_install": "Instalar: sudo apt install tmux  /  brew install tmux",
        "status_header": "\u2550\u2550\u2550\u2699\u2550\u2550\u2550 ESTADO MECHANICUS \u2550\u2550\u2550\u2699\u2550\u2550\u2550",
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

def cmd_help(cfg):
    theme = get_theme(cfg)
    t = I18N[get_lang(cfg)]
    g, i, d, w, r = theme["gold"], theme["info"], theme["dim"], theme["warning"], theme["reset"]
    print(f"{g}{t['help_header']}{r}")
    print()
    for cmd, desc in t["help_cmds"]:
        print(f"{i}  {cmd:<22}{d}\u2192{i} {desc}{r}")
    print()
    print(f"{w}  {t['help_footer_1']}{r}")
    print(f"{w}  {t['help_footer_2']}{r}")
    print()
    print(f"{d}  \"From the weakness of the mind, Omnissiah save us.\"{r}")
    print(f"{g}\u2550\u2550\u2550\u2699 LAUS OMNISSIAH \u2699\u2550\u2550\u2550{r}")


MECH_COMMANDS = {
    "on":      lambda cfg, _: cmd_on(cfg),
    "enable":  lambda cfg, _: cmd_on(cfg),
    "off":     lambda cfg, _: cmd_off(cfg),
    "disable": lambda cfg, _: cmd_off(cfg),
    "status":  lambda cfg, _: cmd_status(cfg),
    "theme":   lambda cfg, a: cmd_theme(cfg, a[0] if a else ""),
    "lore":    lambda cfg, _: cmd_lore(cfg),
    "esp":     lambda cfg, _: cmd_lang(cfg, "es"),
    "eng":     lambda cfg, _: cmd_lang(cfg, "en"),
    "sidebar": lambda cfg, a: cmd_sidebar(cfg, a[0] if a else "32"),
    "kill":    lambda cfg, _: cmd_kill(cfg),
    "--help":  lambda cfg, _: cmd_help(cfg),
    "-h":      lambda cfg, _: cmd_help(cfg),
    "help":    lambda cfg, _: cmd_help(cfg),
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
