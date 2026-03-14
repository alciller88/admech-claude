#!/usr/bin/env python3
"""
mechcode_hook.py — Claude Code hook for Mechanicus Terminal
Reads tool call info from stdin, writes state to ~/.mechcode_state.json
for the servo-skull monitor to display.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

DEBUG = os.environ.get("MECHCODE_DEBUG") == "1"


def debug_log(msg):
    """Log to stderr only when MECHCODE_DEBUG=1."""
    if DEBUG:
        print(f"[mechcode_hook] {msg}", file=sys.stderr, flush=True)

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
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            debug_log(f"State loaded: main_state={data.get('main_state')}")
            return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[mechcode_hook] Failed to load state: {e}", file=sys.stderr, flush=True)
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
    """Atomic write: temp file + os.rename to prevent corruption mid-read."""
    try:
        content = json.dumps(state, ensure_ascii=False, indent=2)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(STATE_FILE.parent), suffix=".tmp", prefix=".mechstate_"
        )
        try:
            os.write(fd, content.encode("utf-8"))
            os.close(fd)
            os.replace(tmp_path, str(STATE_FILE))
            debug_log(f"State saved: main_state={state.get('main_state')}")
        except OSError as e:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            print(f"[mechcode_hook] Failed to save state: {e}", file=sys.stderr, flush=True)
    except OSError as e:
        print(f"[mechcode_hook] Failed to create temp file: {e}", file=sys.stderr, flush=True)


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
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError, EOFError) as e:
        print(f"[mechcode_hook] Failed to parse stdin: {e}", file=sys.stderr, flush=True)
        return

    event = data.get("hook_event_name", "")
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    debug_log(f"Event received: {event} tool={tool}")

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
    try:
        main()
    except Exception as e:
        print(f"[mechcode_hook] Unexpected error: {e}", file=sys.stderr, flush=True)
    finally:
        sys.exit(0)
