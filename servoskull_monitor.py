#!/usr/bin/env python3
"""
servoskull_monitor.py — Servo-Skull sidebar monitor
Runs in the right tmux pane. Reads state from ~/.mechcode_state.json
and displays animated servo-skull + agent hierarchy + stats.
"""
import json
import os
import random
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

# Thinking animation cycles through these frames
THINKING_FRAMES = ["THINKING", "THINKING_2", "THINKING_3", "THINKING_2"]
THINKING_INTERVAL = 0.6  # seconds per frame

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

LITANIES = [
    "The Omnissiah protects.",
    "Flesh is weak.",
    "Knowledge is power.",
    "Logic is divine.",
    "In code we trust.",
    "The Machine endures.",
    "Iron within.",
    "Data is sacred.",
]

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
    # Strip ANSI for length calculation
    import re
    clean = re.sub(r'\033\[[^m]*m', '', text)
    pad = max(0, (width - len(clean)) // 2)
    return " " * pad + text


def format_uptime(seconds):
    """Format seconds into human-readable uptime."""
    hours, rem = divmod(int(seconds), 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def draw_separator(w, char="\u2500", color=GREY_COGIT):
    """Draw a horizontal separator."""
    return f"{color}{char * min(w, 28)}{RESET}"


def draw_header(w):
    """Draw the Mechanicus header."""
    lines = []
    lines.append(f"{GOLD_OMNI}{center('\u2550\u2550\u2550\u2699 MECHANICUS \u2699\u2550\u2550\u2550', w)}{RESET}")
    return "\n".join(lines)


def draw_status(state_data, w):
    """Draw the current status section."""
    if state_data is None:
        main_state = "IDLE"
        msg = "AWAITING COMMAND"
        tool = None
        detail = None
    else:
        main_state = state_data.get("main_state", "IDLE")
        msg = state_data.get("message_en", "AWAITING COMMAND")
        tool = state_data.get("tool")
        detail = state_data.get("tool_detail")

    color = STATE_COLORS.get(main_state, GREY_COGIT)
    lines = []

    # State line
    state_display = main_state
    if main_state == "THINKING":
        state_display = "THINKING \u03c8"
    elif main_state == "SUCCESS":
        state_display = "RITE COMPLETE \u2021"
    elif main_state == "ERROR":
        state_display = "HERESY! \u2620"
    elif main_state == "IDLE":
        state_display = "IDLE \u2699"

    lines.append(f"{color}{BOLD}{truncate(state_display, w)}{RESET}")

    # Message
    if msg:
        lines.append(f"{color}{truncate(msg, w)}{RESET}")

    # Tool + detail
    if tool:
        tool_line = f"[{tool}]"
        if detail:
            tool_line += f" {detail}"
        lines.append(f"{GREY_COGIT}{truncate(tool_line, w)}{RESET}")

    return "\n".join(lines)


def draw_agents(state_data, w):
    """Draw the agent hierarchy section."""
    if state_data is None:
        return ""

    agents = state_data.get("agents", {})
    if not agents:
        return ""

    lines = []
    lines.append(draw_separator(w))
    count = len(agents)
    header = f" SERVITORS [{count}]"
    lines.append(f"{GOLD_OMNI}{truncate(header, w)}{RESET}")

    for agent_id, info in list(agents.items())[:5]:  # max 5 displayed
        atype = info.get("type", "unknown")
        icon = AGENT_ICONS.get(atype, "\u2020")
        name = info.get("name_en", atype.upper())
        elapsed = time.time() - info.get("started", time.time())
        time_str = format_uptime(elapsed)

        line = f" {icon} {name}"
        lines.append(f"{ORANGE_FORGE}{truncate(line, w)}{RESET}")
        lines.append(f"{GREY_COGIT}   {time_str}{RESET}")

    if count > 5:
        lines.append(f"{GREY_COGIT} +{count - 5} more...{RESET}")

    return "\n".join(lines)


def draw_stats(state_data, w):
    """Draw statistics section."""
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
    lines.append(draw_separator(w))
    lines.append(f"{GOLD_OMNI} STATS{RESET}")
    lines.append(f"{GREY_COGIT} Rites:    {GREEN_BIONIC}{rites}{RESET}")
    lines.append(f"{GREY_COGIT} Heresies: {RED_MARS}{heresies}{RESET}")
    lines.append(f"{GREY_COGIT} Tools:    {BONE_SACRED}{tools}{RESET}")
    lines.append(f"{GREY_COGIT} Uptime:   {BONE_SACRED}{uptime}{RESET}")

    return "\n".join(lines)


def draw_binharic(w):
    """Draw random binharic static line."""
    frag = random.choice(BINHARIC_FRAGMENTS)
    return f"{GREY_COGIT}{DIM}{truncate(frag, w)}{RESET}"


def draw_footer(w):
    """Draw the footer."""
    return f"{GOLD_OMNI}{center('\u2550\u2550\u2550\u2699 OMNISSIAH \u2699\u2550\u2550\u2550', w)}{RESET}"


def draw_litany(w):
    """Draw a random litany."""
    litany = random.choice(LITANIES)
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
    thinking_idx = 0
    last_state = None
    last_skull = None
    litany_timer = time.time()
    current_litany = random.choice(LITANIES)

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

            # Determine skull frame
            if main_state == "THINKING":
                skull_state = THINKING_FRAMES[thinking_idx % len(THINKING_FRAMES)]
                thinking_idx += 1
            elif main_state == "ERROR":
                skull_state = "ERROR"
                thinking_idx = 0
            elif main_state == "SUCCESS":
                skull_state = "SUCCESS"
                thinking_idx = 0
            else:
                skull_state = "IDLE"
                thinking_idx = 0

            # Only regenerate skull if state changed
            if skull_state != last_state:
                last_skull = get_frame(skull_state, compact=True)
                last_state = skull_state

            # Rotate litany every 30s
            if time.time() - litany_timer > 30:
                current_litany = random.choice(LITANIES)
                litany_timer = time.time()

            # Build full display
            output_parts = []
            output_parts.append(draw_header(w))
            output_parts.append("")
            output_parts.append(last_skull)
            output_parts.append("")
            output_parts.append(draw_status(state_data, w))
            output_parts.append(draw_binharic(w))

            agents_section = draw_agents(state_data, w)
            if agents_section:
                output_parts.append(agents_section)

            output_parts.append(draw_stats(state_data, w))
            output_parts.append("")
            output_parts.append(f"{GREY_COGIT}{DIM}{truncate(current_litany, w)}{RESET}")
            output_parts.append("")
            output_parts.append(draw_footer(w))

            # Clear and draw
            clear_screen()
            full_output = "\n".join(output_parts)
            sys.stdout.write(full_output)
            sys.stdout.flush()

            # Sleep interval depends on state
            if main_state == "THINKING":
                time.sleep(THINKING_INTERVAL)
            else:
                time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear_screen()


if __name__ == "__main__":
    main()
