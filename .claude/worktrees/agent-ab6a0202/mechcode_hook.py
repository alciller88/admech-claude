#!/usr/bin/env python3
"""
mechcode_hook.py — Claude Code hook for Mechanicus Terminal
Reads tool call info from stdin, writes state to ~/.mechcode_state.json
for the servo-skull monitor to display.
"""
import json
import sys
import time
from pathlib import Path

STATE_FILE = Path.home() / ".mechcode_state.json"

# Tool name → (message_es, message_en, skull_frame_hint)
TOOL_MESSAGES = {
    "Read":       ("ESCANEANDO PERGAMINO DE DATOS",        "SCANNING DATA-SCROLL"),
    "Write":      ("INSCRIBIENDO EN EL REGISTRO ETERNO",   "INSCRIBING THE ETERNAL REGISTRY"),
    "Edit":       ("MODIFICANDO ARTEFACTO SAGRADO",        "MODIFYING SACRED ARTIFACT"),
    "Bash":       ("EJECUTANDO RITO BINARIO",              "RITE OF BINARY EXECUTION"),
    "Glob":       ("EXPLORANDO LA NOOSFERA",               "SCOURING THE NOOSPHERE"),
    "Grep":       ("BUSCANDO EN LOS REGISTROS",            "SEARCHING THE ARCHIVES"),
    "Agent":      ("INVOCANDO SERVO-CRANEO",               "SUMMONING SERVO-SKULL"),
    "WebFetch":   ("EXPLORADOR ENVIADO A LA NOOSFERA",     "EXPLORATOR FLEET DISPATCHED"),
    "WebSearch":  ("COMUNION NOOSFERCA INICIADA",          "NOOSPHERIC COMMUNION INITIATED"),
    "Skill":      ("RITO ESPECIALIZADO",                   "SPECIALIZED RITE"),
    "NotebookEdit": ("MODIFICANDO CODEX",                  "MODIFYING CODEX"),
    "TaskCreate": ("CREANDO DIRECTIVA",                    "CREATING DIRECTIVE"),
    "TaskUpdate": ("ACTUALIZANDO DIRECTIVA",               "UPDATING DIRECTIVE"),
}

AGENT_TYPE_NAMES = {
    "Explore":    ("SCRYERSKULL — EXPLORADOR",   "SCRYERSKULL — EXPLORER"),
    "Plan":       ("DATA-SKULL — ESTRATEGA",     "DATA-SKULL — STRATEGIST"),
    "general-purpose": ("MONO-TASK INFOSLAVE",   "MONO-TASK INFOSLAVE"),
    "claude-code-guide": ("LEXMECHANIC",         "LEXMECHANIC"),
}


def load_state():
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return new_state()


def new_state():
    return {
        "main_state": "IDLE",
        "tool": None,
        "tool_detail": None,
        "message_es": "",
        "message_en": "",
        "timestamp": time.time(),
        "agents": {},
        "stats": {
            "heresies_detected": 0,
            "rites_completed": 0,
            "tools_invoked": 0,
            "session_start": time.time(),
        },
    }


def save_state(state):
    try:
        STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def extract_detail(tool, tool_input):
    """Extract a short description from tool input."""
    if tool in ("Read", "Write", "Edit"):
        fp = tool_input.get("file_path", "")
        return fp.split("/")[-1] if fp else ""
    if tool == "Bash":
        cmd = tool_input.get("command", "")
        return (cmd[:35] + "...") if len(cmd) > 35 else cmd
    if tool == "Grep":
        return tool_input.get("pattern", "")[:30]
    if tool == "Glob":
        return tool_input.get("pattern", "")[:30]
    if tool == "Agent":
        return tool_input.get("description", "")[:30]
    if tool == "WebFetch":
        url = tool_input.get("url", "")
        return url.split("/")[-1][:30] if url else ""
    if tool == "WebSearch":
        return tool_input.get("query", "")[:30]
    return ""


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    event = data.get("hook_event_name", "")
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    state = load_state()
    state["timestamp"] = time.time()

    if event == "PreToolUse":
        state["main_state"] = "THINKING"
        state["tool"] = tool
        state["tool_detail"] = extract_detail(tool, tool_input)
        msgs = TOOL_MESSAGES.get(tool, ("EJECUTANDO RITO", "EXECUTING RITE"))
        state["message_es"] = msgs[0]
        state["message_en"] = msgs[1]
        state["stats"]["tools_invoked"] = state["stats"].get("tools_invoked", 0) + 1

    elif event == "PostToolUse":
        state["main_state"] = "SUCCESS"
        state["tool"] = tool
        state["message_es"] = "RITO COMPLETADO"
        state["message_en"] = "RITE COMPLETE"
        state["stats"]["rites_completed"] = state["stats"].get("rites_completed", 0) + 1

    elif event == "PostToolUseFailure":
        state["main_state"] = "ERROR"
        state["tool"] = tool
        state["message_es"] = "HEREJIA DETECTADA"
        state["message_en"] = "TECH-HERESY IDENTIFIED"
        state["stats"]["heresies_detected"] = state["stats"].get("heresies_detected", 0) + 1

    elif event == "SubagentStart":
        agent_id = data.get("agent_id", f"srv-{int(time.time())}")
        agent_type = data.get("agent_type", "unknown")
        names = AGENT_TYPE_NAMES.get(agent_type, (agent_type.upper(), agent_type.upper()))
        state["agents"][agent_id] = {
            "type": agent_type,
            "name_es": names[0],
            "name_en": names[1],
            "state": "active",
            "started": time.time(),
        }

    elif event == "SubagentStop":
        agent_id = data.get("agent_id", "")
        state["agents"].pop(agent_id, None)

    elif event == "SessionStart":
        state = new_state()

    elif event == "Stop":
        state["main_state"] = "IDLE"
        state["tool"] = None
        state["tool_detail"] = None
        state["message_es"] = "AGUARDANDO INSTRUCCIONES"
        state["message_en"] = "AWAITING COMMAND"

    save_state(state)


if __name__ == "__main__":
    main()
