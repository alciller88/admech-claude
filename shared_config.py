#!/usr/bin/env python3
"""
shared_config.py — Shared constants for Mechanicus Terminal
Single source of truth for paths, animation parameters, and hook events.
"""
import os
from pathlib import Path

# === PATHS ===
STATE_FILE = Path.home() / ".mechcode_state.json"
CONFIG_FILE = Path.home() / ".mechcode_config.json"
CLAUDE_DIR = Path.home() / ".claude"

# === SIDEBAR ===
SIDEBAR_WIDTH = 32
SIDEBAR_MIN = 20
SIDEBAR_MAX = 60

# === ANIMATION PARAMETERS ===
THINKING_INTERVAL = 0.15
IDLE_INTERVAL = 0.12
ERROR_INTERVAL = 0.18
DEFAULT_INTERVAL = 0.5

BREATH_SPEED = 0.08
BREATH_MIN = 0.65
BREATH_MAX = 1.0

THINKING_PHASE_SPEED = 0.05
ERROR_FRAME_TICKS = 4

# === HOOK EVENTS ===
HOOK_PRE_TOOL_USE = "PreToolUse"
HOOK_POST_TOOL_USE = "PostToolUse"
HOOK_POST_TOOL_FAILURE = "PostToolUseFailure"
HOOK_SUBAGENT_START = "SubagentStart"
HOOK_SUBAGENT_STOP = "SubagentStop"
HOOK_SESSION_START = "SessionStart"
HOOK_STOP = "Stop"

# === AGENT TYPES (shared registry) ===
AGENT_TYPES = {
    "Explore": {
        "name_es": "SCRYERSKULL \u2014 EXPLORADOR",
        "name_en": "SCRYERSKULL \u2014 EXPLORER",
        "icon": "\u03c8",
    },
    "Plan": {
        "name_es": "DATA-SKULL \u2014 ESTRATEGA",
        "name_en": "DATA-SKULL \u2014 STRATEGIST",
        "icon": "\u2021",
    },
    "general-purpose": {
        "name_es": "MONO-TASK INFOSLAVE",
        "name_en": "MONO-TASK INFOSLAVE",
        "icon": "\u2620",
    },
    "claude-code-guide": {
        "name_es": "LEXMECHANIC",
        "name_en": "LEXMECHANIC",
        "icon": "\u2638",
    },
}


def get_agent_name(agent_type, lang="en"):
    """Get localized agent name."""
    key = "name_en" if lang == "en" else "name_es"
    info = AGENT_TYPES.get(agent_type)
    if info:
        return info[key]
    return agent_type.upper()


def get_agent_icon(agent_type):
    """Get agent icon character."""
    info = AGENT_TYPES.get(agent_type)
    if info:
        return info["icon"]
    return "\u2020"


# === LANGUAGE DETECTION ===

def detect_system_language():
    """Detect language from system locale. Returns 'es' or 'en'."""
    for var in ("LANG", "LC_ALL", "LANGUAGE", "LC_MESSAGES"):
        val = os.environ.get(var, "")
        if val.lower().startswith("es"):
            return "es"
    return "en"


def get_active_language(config=None):
    """Get language with config override."""
    if config:
        lang = config.get("language")
        if lang and lang != "auto":
            return lang
    return detect_system_language()
