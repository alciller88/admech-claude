#!/usr/bin/env python3
"""
servoskull_monitor.py — Servo-Skull sidebar monitor
Runs in the right tmux pane. Reads state from ~/.mechcode_state.json
and displays animated servo-skull + agent hierarchy + stats.
"""
import json
import math
import os
import random
import string
import sys
import time
from pathlib import Path

# Add script directory to path for servoskull import
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from servoskull import (
    get_frame, RESET, BOLD, DIM, GREY_COGIT, GOLD_OMNI,
    GREEN_BIONIC, RED_MARS, ORANGE_FORGE, BONE_SACRED,
)

STATE_FILE = Path.home() / ".mechcode_state.json"
CONFIG_FILE = Path.home() / ".mechcode_config.json"


def detect_language():
    """Detect active language from config or system locale."""
    try:
        if CONFIG_FILE.exists():
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            lang = cfg.get("language")
            if lang and lang != "auto":
                return lang
    except (json.JSONDecodeError, OSError):
        pass
    for var in ("LANG", "LC_ALL", "LANGUAGE", "LC_MESSAGES"):
        val = os.environ.get(var, "")
        if val.lower().startswith("es"):
            return "es"
    return "en"


# Animation timing constants
THINKING_INTERVAL = 0.15   # faster tick for smooth animation
IDLE_INTERVAL = 0.12       # breathing tick
ERROR_INTERVAL = 0.18      # error flicker tick
DEFAULT_INTERVAL = 0.5     # fallback for SUCCESS and other states

# Breathing sine wave parameters
BREATH_SPEED = 0.08        # radians per tick
BREATH_MIN = 0.65          # minimum intensity
BREATH_MAX = 1.0           # maximum intensity

# Thinking smooth phase speed
THINKING_PHASE_SPEED = 0.05  # radians per tick

# Error flicker cycle
ERROR_FRAME_TICKS = 4      # ticks per error frame

# Binharic fragments for background static
BINHARIC_FRAGMENTS = [
    "01001101 01000001 01010010",
    "10110100 01011010 11001001",
    "01001111 01001101 01001110",
    "11010010 00101101 10010110",
    "01010011 01010100 01000011",
    "10001001 01110100 00110101",
    "01001100 01000001 01010101",
    "11100101 00011010 01101100",
]

# Hex fragments for mixed binharic display
HEX_FRAGMENTS = [
    "0x4D415253 FORGE",
    "0xDEAD C0DE PURGE",
    "0x0MN1 5514H",
    "0xFF41 B10C",
    "0xC0G1 7470R",
    "0xAD3P 7U5",
    "0x53RV 0SKL",
    "0xM3CH 4N1C",
]

# Mixed binharic patterns for dynamic display
BINHARIC_PATTERNS = [
    "{b0} {b1} {b2}",
    ">{b0}< >{b1}<",
    "[{b0}]{b1}",
    "{b0}:{b1}:{b2}",
    "||{b0}||{b1}||",
    "<<{b0}>>{b1}",
]

# Glitch characters for corrupt_text
GLITCH_CHARS = "░▒▓█▀▄╳╬╫╪⌐¬¡«»┼┤├┬┴╡╞╥╨▌▐▀▄"

LITANIES = {
    "en": [
        "The Omnissiah protects.",
        "Flesh is weak.",
        "Knowledge is power.",
        "Logic is divine.",
        "In code we trust.",
        "The Machine endures.",
        "Iron within.",
        "Data is sacred.",
        "Purge the unclean code.",
        "The circuit is eternal.",
        "Praise the Machine God.",
        "Beware the scrapcode.",
    ],
    "es": [
        "El Omnissiah protege.",
        "La carne es debil.",
        "El conocimiento es poder.",
        "La logica es divina.",
        "En el codigo confiamos.",
        "La Maquina perdura.",
        "Hierro interior.",
        "Los datos son sagrados.",
        "Purga el codigo impuro.",
        "El circuito es eterno.",
        "Alabad al Dios Maquina.",
        "Temed al scrapcode.",
    ],
}

# Localized UI strings for the monitor
MONITOR_I18N = {
    "en": {
        "idle": "IDLE",
        "thinking": "THINKING",
        "rite_complete": "RITE COMPLETE",
        "heresy": "HERESY!",
        "servitors": "SERVITORS",
        "stats": "STATS",
        "rites": "Rites:",
        "heresies": "Heresies:",
        "tools": "Tools:",
        "uptime": "Uptime:",
        "awaiting": "AWAITING COMMAND",
        "title": "MECHANICUS",
        "footer_title": "OMNISSIAH",
        "corruption": "CORRUPTION",
    },
    "es": {
        "idle": "INACTIVO",
        "thinking": "PROCESANDO",
        "rite_complete": "RITO COMPLETO",
        "heresy": "HEREJIA!",
        "servitors": "SERVITORES",
        "stats": "ESTADISTICAS",
        "rites": "Ritos:",
        "heresies": "Herejias:",
        "tools": "Herram.:",
        "uptime": "Activo:",
        "awaiting": "AGUARDANDO INSTRUCCIONES",
        "title": "MECHANICUS",
        "footer_title": "OMNISSIAH",
        "corruption": "CORRUPCION",
    },
}

# Agent type icons (small servo-skull representations)
AGENT_ICONS = {
    "Explore":    "\u03c8",  # psi
    "Plan":       "\u2021",  # double dagger
    "general-purpose": "\u2620",  # skull
    "claude-code-guide": "\u2638",  # wheel
}

# Color codes for states
STATE_COLORS = {
    "IDLE":     GREY_COGIT,
    "THINKING": ORANGE_FORGE,
    "SUCCESS":  GREEN_BIONIC,
    "ERROR":    RED_MARS,
}


def load_state():
    """Load current state from the shared state file."""
    try:
        if STATE_FILE.exists():
            text = STATE_FILE.read_text(encoding="utf-8")
            if text.strip():
                return json.loads(text)
    except (json.JSONDecodeError, OSError):
        pass
    return None


def get_terminal_size():
    """Get the current terminal dimensions."""
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows
    except (ValueError, OSError):
        return 30, 24


def truncate(text, width):
    """Truncate text to fit width."""
    if len(text) <= width:
        return text
    return text[:width - 2] + ".."


def center(text, width):
    """Center text within width (approximate, ignoring ANSI)."""
    import re
    clean = re.sub(r'\033\[[^m]*m', '', text)
    pad = max(0, (width - len(clean)) // 2)
    return " " * pad + text


def visible_len(text):
    """Get visible length of text, ignoring ANSI escape codes."""
    import re
    return len(re.sub(r'\033\[[^m]*m', '', text))


def format_uptime(seconds):
    """Format seconds into human-readable uptime."""
    hours, rem = divmod(int(seconds), 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def corrupt_text(text, intensity=0.3):
    """Corrupt text by randomly replacing characters with glitch symbols.

    Used during ERROR state to simulate data corruption / scrapcode.
    Each character has `intensity` probability of being replaced.
    """
    result = []
    for ch in text:
        if ch in (' ', '\n', '\t'):
            result.append(ch)
        elif random.random() < intensity:
            result.append(random.choice(GLITCH_CHARS))
        else:
            result.append(ch)
    return "".join(result)


# ═══ GOTHIC CATHEDRAL FRAME ═══

def draw_header(w, lang="en"):
    """Draw the gothic cathedral-style header with arch and cog symbols."""
    t = MONITOR_I18N.get(lang, MONITOR_I18N["en"])
    title = t["title"]
    inner = w - 2  # inside the frame walls ║...║
    lines = []

    # Top pinnacle
    arch_top = "╔" + "═" * inner + "╗"
    lines.append(f"{GOLD_OMNI}{arch_top}{RESET}")

    # Gothic arch row with cog symbols
    # ║  ═══⚙ MECHANICUS ⚙═══  ║
    label = f"═══⚙ {title} ⚙═══"
    pad_total = max(0, inner - len(label))
    pad_l = pad_total // 2
    pad_r = pad_total - pad_l
    arch_label = "║" + " " * pad_l + label + " " * pad_r + "║"
    lines.append(f"{GOLD_OMNI}{arch_label}{RESET}")

    # Ornamental sub-arch: ╠═╦═══════════╦═╣
    if inner >= 10:
        mid = inner - 4  # space between the two ╦
        sub_arch = "╠═╦" + "═" * mid + "╦═╣"
    else:
        sub_arch = "╠" + "═" * inner + "╣"
    lines.append(f"{GOLD_OMNI}{sub_arch}{RESET}")

    return "\n".join(lines)


def draw_frame_sides(content_line, w):
    """Wrap a content line with gothic frame side walls ║."""
    import re
    clean = re.sub(r'\033\[[^m]*m', '', content_line)
    inner = w - 2
    pad = max(0, inner - len(clean))
    return f"{GOLD_OMNI}║{RESET}{content_line}{' ' * pad}{GOLD_OMNI}║{RESET}"


def draw_section_separator(w, style="cog"):
    """Draw a separator inside the frame."""
    inner = w - 2
    if style == "cog":
        # ║ ──⚙──⚙──⚙── ║
        unit = "──⚙"
        repeats = max(1, inner // 3)
        sep = (unit * repeats)[:inner]
    elif style == "cross":
        # ║ ──†──†──†── ║
        unit = "──†"
        repeats = max(1, inner // 3)
        sep = (unit * repeats)[:inner]
    elif style == "heavy":
        # ║ ═══⚙═══⚙═══ ║
        unit = "═══⚙"
        repeats = max(1, inner // 4)
        sep = (unit * repeats)[:inner]
    else:
        sep = "─" * inner
    return draw_frame_sides(f"{GREY_COGIT}{sep}{RESET}", w)


def draw_footer(w, litany="", lang="en"):
    """Draw the ornamental gothic footer with rotating litany."""
    t = MONITOR_I18N.get(lang, MONITOR_I18N["en"])
    title = t["footer_title"]
    inner = w - 2
    lines = []

    # Litany row
    if litany:
        lit_trunc = truncate(litany, inner)
        pad_total = max(0, inner - len(lit_trunc))
        pad_l = pad_total // 2
        pad_r = pad_total - pad_l
        lit_line = " " * pad_l + lit_trunc + " " * pad_r
        lines.append(f"{GOLD_OMNI}║{GREY_COGIT}{DIM}{lit_line}{RESET}{GOLD_OMNI}║{RESET}")

    # Sub-arch: ╠═╩═══════════╩═╣
    if inner >= 10:
        mid = inner - 4
        sub_arch = "╠═╩" + "═" * mid + "╩═╣"
    else:
        sub_arch = "╠" + "═" * inner + "╣"
    lines.append(f"{GOLD_OMNI}{sub_arch}{RESET}")

    # Footer label: ║  ═══⚙ OMNISSIAH ⚙═══  ║
    label = f"═══⚙ {title} ⚙═══"
    pad_total = max(0, inner - len(label))
    pad_l = pad_total // 2
    pad_r = pad_total - pad_l
    footer_label = "║" + " " * pad_l + label + " " * pad_r + "║"
    lines.append(f"{GOLD_OMNI}{footer_label}{RESET}")

    # Bottom
    bottom = "╚" + "═" * inner + "╝"
    lines.append(f"{GOLD_OMNI}{bottom}{RESET}")

    return "\n".join(lines)


def draw_separator(w, char="\u2500", color=GREY_COGIT):
    """Draw a horizontal separator (legacy, used inside framed content)."""
    return f"{color}{char * min(w - 2, 28)}{RESET}"


def draw_status(state_data, w, lang="en"):
    """Draw the current status section with box framing."""
    t = MONITOR_I18N.get(lang, MONITOR_I18N["en"])
    msg_key = "message_es" if lang == "es" else "message_en"

    if state_data is None:
        main_state = "IDLE"
        msg = t["awaiting"]
        tool = None
        detail = None
    else:
        main_state = state_data.get("main_state", "IDLE")
        msg = state_data.get(msg_key) or state_data.get("message_en", t["awaiting"])
        tool = state_data.get("tool")
        detail = state_data.get("tool_detail")

    color = STATE_COLORS.get(main_state, GREY_COGIT)
    lines = []

    if main_state == "THINKING":
        state_display = f"{t['thinking']} \u03c8"
    elif main_state == "SUCCESS":
        state_display = f"{t['rite_complete']} \u2021"
    elif main_state == "ERROR":
        state_display = f"{t['heresy']} \u2620"
    else:
        state_display = f"{t['idle']} \u2699"

    # Apply glitch corruption in ERROR state
    display_msg = msg or ""
    if main_state == "ERROR":
        state_display = corrupt_text(state_display, 0.3)
        display_msg = corrupt_text(display_msg, 0.3)

    inner = w - 2
    lines.append(draw_frame_sides(
        f"{color}{BOLD}{truncate(state_display, inner)}{RESET}", w))

    if display_msg:
        lines.append(draw_frame_sides(
            f"{color}{truncate(display_msg, inner)}{RESET}", w))

    if tool:
        tool_line = f"[{tool}]"
        if detail:
            tool_line += f" {detail}"
        if main_state == "ERROR":
            tool_line = corrupt_text(tool_line, 0.15)
        lines.append(draw_frame_sides(
            f"{GREY_COGIT}{truncate(tool_line, inner)}{RESET}", w))

    return "\n".join(lines)


def draw_agents(state_data, w, lang="en"):
    """Draw the agent hierarchy section."""
    if state_data is None:
        return ""

    agents = state_data.get("agents", {})
    if not agents:
        return ""

    t = MONITOR_I18N.get(lang, MONITOR_I18N["en"])
    name_key = "name_es" if lang == "es" else "name_en"

    lines = []
    lines.append(draw_section_separator(w, "cross"))
    count = len(agents)
    header = f" {t['servitors']} [{count}]"
    lines.append(draw_frame_sides(
        f"{GOLD_OMNI}{truncate(header, w - 2)}{RESET}", w))

    for agent_id, info in list(agents.items())[:5]:
        atype = info.get("type", "unknown")
        icon = AGENT_ICONS.get(atype, "\u2020")
        name = info.get(name_key) or info.get("name_en", atype.upper())
        elapsed = time.time() - info.get("started", time.time())
        time_str = format_uptime(elapsed)

        line = f" {icon} {name}"
        lines.append(draw_frame_sides(
            f"{ORANGE_FORGE}{truncate(line, w - 2)}{RESET}", w))
        lines.append(draw_frame_sides(
            f"{GREY_COGIT}   {time_str}{RESET}", w))

    if count > 5:
        lines.append(draw_frame_sides(
            f"{GREY_COGIT} +{count - 5} ...{RESET}", w))

    return "\n".join(lines)


def draw_stats(state_data, w, lang="en"):
    """Draw statistics section."""
    t = MONITOR_I18N.get(lang, MONITOR_I18N["en"])

    if state_data is None:
        stats = {}
    else:
        stats = state_data.get("stats", {})

    heresies = stats.get("heresies_detected", 0)
    rites = stats.get("rites_completed", 0)
    tools = stats.get("tools_invoked", 0)
    session_start = stats.get("session_start", time.time())
    uptime = format_uptime(time.time() - session_start)

    lines = []
    lines.append(draw_section_separator(w, "cog"))
    lines.append(draw_frame_sides(
        f"{GOLD_OMNI} {t['stats']}{RESET}", w))
    lines.append(draw_frame_sides(
        f"{GREY_COGIT} {t['rites']:<10}{GREEN_BIONIC}{rites}{RESET}", w))
    lines.append(draw_frame_sides(
        f"{GREY_COGIT} {t['heresies']:<10}{RED_MARS}{heresies}{RESET}", w))
    lines.append(draw_frame_sides(
        f"{GREY_COGIT} {t['tools']:<10}{BONE_SACRED}{tools}{RESET}", w))
    lines.append(draw_frame_sides(
        f"{GREY_COGIT} {t['uptime']:<10}{BONE_SACRED}{uptime}{RESET}", w))

    return "\n".join(lines)


def draw_binharic(w, cycle_count=0):
    """Draw dynamic binharic static with mixed hex fragments.

    Each cycle produces a different pattern. Occasionally shows hex
    fragments instead of pure binary for variety.
    """
    inner = w - 2
    # Every 3rd cycle, mix in a hex fragment
    if cycle_count % 3 == 2:
        frag = random.choice(HEX_FRAGMENTS)
    elif cycle_count % 5 == 0:
        # Use a pattern template
        bits = [format(random.randint(0, 255), '08b') for _ in range(3)]
        pattern = random.choice(BINHARIC_PATTERNS)
        frag = pattern.format(b0=bits[0], b1=bits[1], b2=bits[2])
    else:
        # Standard binary fragment but regenerated each time
        frag = " ".join(format(random.randint(0, 255), '08b')
                        for _ in range(random.randint(2, 3)))

    return draw_frame_sides(
        f"{GREY_COGIT}{DIM}{truncate(frag, inner)}{RESET}", w)


def draw_litany(w, lang="en"):
    """Draw a random litany."""
    pool = LITANIES.get(lang, LITANIES["en"])
    litany = random.choice(pool)
    return f"{GREY_COGIT}{DIM}{truncate(litany, w)}{RESET}"


def clear_screen():
    """Clear terminal and move cursor to top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def main():
    hide_cursor()
    lang = detect_language()
    litany_timer = time.time()
    litany_pool = LITANIES.get(lang, LITANIES["en"])
    current_litany = random.choice(litany_pool)
    cycle_count = 0

    # Animation state
    breath_angle = 0.0          # sine wave angle for IDLE breathing
    thinking_angle = 0.0        # sine wave angle for THINKING phase
    error_tick = 0              # tick counter for ERROR frame cycling
    last_main_state = None      # track state transitions

    try:
        while True:
            w, h = get_terminal_size()
            state_data = load_state()

            main_state = "IDLE"
            if state_data:
                main_state = state_data.get("main_state", "IDLE")

            # Auto-decay: if state is SUCCESS/ERROR and >3 seconds old, go IDLE
            if state_data and main_state in ("SUCCESS", "ERROR"):
                ts = state_data.get("timestamp", 0)
                if time.time() - ts > 3.0:
                    main_state = "IDLE"

            # Reset animation counters on state transition
            if main_state != last_main_state:
                if main_state == "IDLE":
                    breath_angle = 0.0
                elif main_state == "THINKING":
                    thinking_angle = 0.0
                elif main_state == "ERROR":
                    error_tick = 0
                last_main_state = main_state

            # Compute animation parameters per state
            intensity = 1.0
            error_frame = 0
            thinking_phase = None

            if main_state == "IDLE":
                # Breathing effect: sine wave cycling intensity 0.65..1.0
                breath_val = math.sin(breath_angle) * 0.5 + 0.5  # 0..1
                intensity = BREATH_MIN + breath_val * (BREATH_MAX - BREATH_MIN)
                breath_angle += BREATH_SPEED
                skull_state = "IDLE"

            elif main_state == "THINKING":
                # Smooth thinking phase: continuous sine cycle 0..1
                thinking_phase = (math.sin(thinking_angle) * 0.5 + 0.5)
                thinking_angle += THINKING_PHASE_SPEED
                skull_state = "THINKING"

            elif main_state == "ERROR":
                # Flickering error: cycle through frames 0-3
                error_frame = (error_tick // ERROR_FRAME_TICKS) % 4
                error_tick += 1
                skull_state = "ERROR"

            elif main_state == "SUCCESS":
                skull_state = "SUCCESS"

            else:
                skull_state = "IDLE"

            # Generate skull frame with animation params
            last_skull = get_frame(
                skull_state, compact=True,
                intensity=intensity,
                error_frame=error_frame,
                thinking_phase=thinking_phase,
            )

            # Rotate litany every 30s
            if time.time() - litany_timer > 30:
                current_litany = random.choice(litany_pool)
                litany_timer = time.time()

            cycle_count += 1

            # Build full display with gothic cathedral frame
            output_parts = []
            output_parts.append(draw_header(w, lang))

            # Skull section — wrap each line in frame sides
            if last_skull:
                for skull_line in last_skull.split("\n"):
                    output_parts.append(draw_frame_sides(skull_line, w))
            else:
                output_parts.append(draw_frame_sides("", w))

            # Separator between skull and status
            output_parts.append(draw_section_separator(w, "heavy"))

            output_parts.append(draw_status(state_data, w, lang))
            output_parts.append(draw_binharic(w, cycle_count))

            agents_section = draw_agents(state_data, w, lang)
            if agents_section:
                output_parts.append(agents_section)

            output_parts.append(draw_stats(state_data, w, lang))

            # Empty framed line before footer
            output_parts.append(draw_frame_sides("", w))

            output_parts.append(draw_footer(w, current_litany, lang))

            # Clear and draw
            clear_screen()
            full_output = "\n".join(output_parts)
            sys.stdout.write(full_output)
            sys.stdout.flush()

            # Sleep interval depends on state — faster for animated states
            if main_state == "THINKING":
                time.sleep(THINKING_INTERVAL)
            elif main_state == "IDLE":
                time.sleep(IDLE_INTERVAL)
            elif main_state == "ERROR":
                time.sleep(ERROR_INTERVAL)
            else:
                time.sleep(DEFAULT_INTERVAL)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()


if __name__ == "__main__":
    main()
