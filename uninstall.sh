#!/usr/bin/env bash
# === RITO DE DESVINCULACION — MECHANICUS TERMINAL ===
set -euo pipefail

# === LANGUAGE DETECTION ===
detect_lang() {
    local val=""
    for var in LANG LC_ALL LANGUAGE LC_MESSAGES; do
        val="${!var:-}"
        if [[ "${val,,}" == es* ]]; then
            echo "es"
            return
        fi
    done
    echo "en"
}
INST_LANG="$(detect_lang)"

# === COLORS ===
RED='\033[38;2;204;0;0m'
ORANGE='\033[38;2;255;102;0m'
GREEN='\033[38;2;0;255;65m'
BONE='\033[38;2;245;240;220m'
GOLD='\033[38;2;255;215;0m'
DIM='\033[38;2;74;74;74m'
RESET='\033[0m'

# === PATHS ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.local/bin"
CLAUDE_DIR="${HOME}/.claude"
HOOKS_DIR="${CLAUDE_DIR}/hooks"
CLAUDE_MD="${CLAUDE_DIR}/CLAUDE.md"
CONFIG_FILE="${HOME}/.mechcode_config.json"
STATE_FILE="${HOME}/.mechcode_state.json"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"

# === FUNCTIONS ===

log_info()    { echo -e "${BONE}  [FORGE//] $1${RESET}"; }
log_success() { echo -e "${GREEN}  [RITE//]  $1${RESET}"; }

detect_shell() {
    local s; s="$(basename "${SHELL:-bash}")"
    case "$s" in zsh) echo "zsh" ;; fish) echo "fish" ;; *) echo "bash" ;; esac
}

get_rc_file() {
    case "$1" in
        zsh)  echo "${HOME}/.zshrc" ;;
        fish) echo "${HOME}/.config/fish/config.fish" ;;
        bash) [[ -f "${HOME}/.bashrc" ]] && echo "${HOME}/.bashrc" || echo "${HOME}/.bash_profile" ;;
    esac
}

kill_tmux_session() {
    if command -v tmux &>/dev/null; then
        tmux kill-session -t mechanicus 2>/dev/null && log_info "tmux session killed" || true
    fi
}

remove_mechcode() {
    for f in mechcode mechcode.py servoskull.py servoskull_monitor.py mechcode_hook.py; do
        local fp="${INSTALL_DIR}/${f}"
        if [[ -f "$fp" ]]; then
            rm -f "$fp"
            log_info "Removed: ${fp}"
        fi
    done
}

remove_hooks() {
    # Remove hook runner script
    if [[ -f "${HOOKS_DIR}/mechcode_hook.sh" ]]; then
        rm -f "${HOOKS_DIR}/mechcode_hook.sh"
        log_info "Removed hook script"
    fi

    # Remove hook entries from settings.json
    if [[ -f "$SETTINGS_FILE" ]]; then
        local py_cmd="python3"
        command -v python3 &>/dev/null || py_cmd="python"

        $py_cmd -c "
import json
with open('${SETTINGS_FILE}', 'r') as f:
    s = json.load(f)
hooks = s.get('hooks', {})
for event in list(hooks.keys()):
    hooks[event] = [
        entry for entry in hooks[event]
        if not any('mechcode_hook' in h.get('command','') for h in entry.get('hooks',[]))
    ]
    if not hooks[event]:
        del hooks[event]
if not hooks:
    s.pop('hooks', None)
with open('${SETTINGS_FILE}', 'w') as f:
    json.dump(s, f, indent=2, ensure_ascii=False)
" 2>/dev/null && log_info "Removed hooks from settings.json" || true
    fi

    # Clean up empty hooks dir
    if [[ -d "$HOOKS_DIR" ]] && [[ -z "$(ls -A "$HOOKS_DIR" 2>/dev/null)" ]]; then
        rmdir "$HOOKS_DIR" 2>/dev/null || true
    fi
}

restore_claude_md() {
    local latest_backup=""
    latest_backup="$(ls -t "${CLAUDE_MD}".backup.* 2>/dev/null | head -1 || true)"

    if [[ -n "$latest_backup" && -f "$latest_backup" ]]; then
        cp "$latest_backup" "$CLAUDE_MD"
        log_info "CLAUDE.md restored from: ${latest_backup}"
        rm -f "${CLAUDE_MD}".backup.*
    elif [[ -f "$CLAUDE_MD" ]]; then
        rm -f "$CLAUDE_MD"
        log_info "CLAUDE.md removed (no backup)"
    fi
}

remove_config() {
    for f in "$CONFIG_FILE" "$STATE_FILE"; do
        if [[ -f "$f" ]]; then
            rm -f "$f"
            log_info "Removed: ${f}"
        fi
    done
}

remove_shell_config() {
    local rc_file
    rc_file="$(get_rc_file "$(detect_shell)")"
    [[ ! -f "$rc_file" ]] && return

    local tmp_file
    tmp_file="$(mktemp)"

    local in_block=false
    while IFS= read -r line; do
        if [[ "$line" == *"Mechanicus Terminal"* ]]; then
            in_block=true
            continue
        fi
        if $in_block; then
            case "$line" in
                "alias mech="*|"# "*|"complete "*mech*|"compdef "*mech*|"_mech_completions"*|*"COMP"*|*"commands"*|*"themes"*|*"CURRENT"*|*"_describe"*|*"words["*|"}"*|"set -gx PATH"*"/.local/bin"*|"export PATH="*"/.local/bin"*|"")
                    continue ;;
                *)
                    in_block=false
                    echo "$line" ;;
            esac
        else
            echo "$line"
        fi
    done < "$rc_file" > "$tmp_file"

    mv "$tmp_file" "$rc_file"
    log_info "Shell config cleaned: ${rc_file}"
}

# === MAIN ===

main() {
    echo ""
    echo -e "${RED}=================================================================${RESET}"
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${RED}  MECHANICUS TERMINAL — RITO DE DESVINCULACION${RESET}"
    else
        echo -e "${RED}  MECHANICUS TERMINAL — RITE OF UNBINDING${RESET}"
    fi
    echo -e "${RED}=================================================================${RESET}"
    echo ""

    if [[ "$INST_LANG" == "es" ]]; then
        echo -e -n "${ORANGE}  Continuar? [y/N]: ${RESET}"
    else
        echo -e -n "${ORANGE}  Proceed? [y/N]: ${RESET}"
    fi
    read -r confirm
    confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')
    if [[ "$confirm" != "y" && "$confirm" != "yes" && "$confirm" != "si" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_info "Cancelado."
        else
            log_info "Cancelled."
        fi
        exit 0
    fi
    echo ""

    kill_tmux_session
    remove_mechcode
    remove_hooks
    restore_claude_md
    remove_config
    remove_shell_config

    echo ""
    echo -e "${RED}=================================================================${RESET}"
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${RED}  Rito de Desvinculacion completado. La Forja se apaga.${RESET}"
        echo -e "${DIM}  Reinicia tu terminal.${RESET}"
    else
        echo -e "${RED}  Rite of Unbinding complete. The Forge goes dark.${RESET}"
        echo -e "${DIM}  Restart your terminal.${RESET}"
    fi
    echo -e "${RED}=================================================================${RESET}"
    echo ""
}

main "$@"
