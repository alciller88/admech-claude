#!/usr/bin/env bash
# ═══⚙═══ RITO DE DESVINCULACIÓN — MECHANICUS TERMINAL ═══⚙═══
# Designación: UNINSTALL-SCRIPT-Ω1
# 01010101 01001110 01001001 01001110 01010011 01010100 01000001 01001100 01001100
set -euo pipefail

# ═══⚙═══ COLORS ═══⚙═══
RED='\033[38;2;204;0;0m'
ORANGE='\033[38;2;255;102;0m'
GREEN='\033[38;2;0;255;65m'
BONE='\033[38;2;245;240;220m'
GOLD='\033[38;2;255;215;0m'
DIM='\033[38;2;74;74;74m'
RESET='\033[0m'

# ═══⚙═══ PATHS ═══⚙═══
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.local/bin"
CLAUDE_DIR="${HOME}/.claude"
MECHCODE_BIN="${INSTALL_DIR}/mechcode"
SERVOSKULL_BIN="${INSTALL_DIR}/servoskull.py"
CLAUDE_MD="${CLAUDE_DIR}/CLAUDE.md"
CONFIG_FILE="${HOME}/.mechcode_config.json"

# ═══⚙═══ FUNCTIONS ═══⚙═══

log_info() {
    echo -e "${BONE}  [FORJA//] ⚙ $1${RESET}"
}

log_success() {
    echo -e "${GREEN}  [RITO//] ‡ $1${RESET}"
}

log_warning() {
    echo -e "${ORANGE}  [AUGUR//] † $1${RESET}"
}

detect_shell() {
    local current_shell
    current_shell="$(basename "${SHELL:-bash}")"
    case "$current_shell" in
        zsh)  echo "zsh" ;;
        fish) echo "fish" ;;
        *)    echo "bash" ;;
    esac
}

get_rc_file() {
    local shell_type="$1"
    case "$shell_type" in
        zsh)  echo "${HOME}/.zshrc" ;;
        fish) echo "${HOME}/.config/fish/config.fish" ;;
        bash)
            if [[ -f "${HOME}/.bashrc" ]]; then
                echo "${HOME}/.bashrc"
            else
                echo "${HOME}/.bash_profile"
            fi
            ;;
    esac
}

remove_mechcode() {
    if [[ -f "$MECHCODE_BIN" ]]; then
        rm -f "$MECHCODE_BIN"
        log_info "mechcode eliminado / removed: ${MECHCODE_BIN}"
    else
        log_info "mechcode no encontrado — ya eliminado / already removed"
    fi

    if [[ -f "$SERVOSKULL_BIN" ]]; then
        rm -f "$SERVOSKULL_BIN"
        log_info "servoskull.py eliminado / removed: ${SERVOSKULL_BIN}"
    fi
}

restore_claude_md() {
    # Find the most recent backup
    local latest_backup=""
    latest_backup="$(ls -t "${CLAUDE_MD}".backup.* 2>/dev/null | head -1 || true)"

    if [[ -n "$latest_backup" && -f "$latest_backup" ]]; then
        cp "$latest_backup" "$CLAUDE_MD"
        log_info "CLAUDE.md restaurado desde backup / restored from backup: ${latest_backup}"
        # Clean up all backups
        rm -f "${CLAUDE_MD}".backup.*
        log_info "Backups eliminados / Backups cleaned up"
    elif [[ -f "$CLAUDE_MD" ]]; then
        rm -f "$CLAUDE_MD"
        log_info "CLAUDE.md eliminado (sin backup previo) / removed (no prior backup)"
    else
        log_info "CLAUDE.md no encontrado — nada que restaurar / nothing to restore"
    fi
}

remove_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        rm -f "$CONFIG_FILE"
        log_info "Config eliminado / removed: ${CONFIG_FILE}"
    else
        log_info "Config no encontrado — ya eliminado / already removed"
    fi
}

remove_shell_config() {
    local shell_type
    shell_type="$(detect_shell)"
    local rc_file
    rc_file="$(get_rc_file "$shell_type")"

    if [[ ! -f "$rc_file" ]]; then
        log_info "RC file no encontrado / not found: ${rc_file}"
        return
    fi

    # Remove the Mechanicus block (comment + alias + completions)
    local tmp_file
    tmp_file="$(mktemp)"

    local in_block=false
    while IFS= read -r line; do
        if [[ "$line" == *"═══⚙═══ Mechanicus Terminal"* ]]; then
            in_block=true
            continue
        fi
        if $in_block; then
            # End of block: next non-empty line that doesn't look like our config
            case "$line" in
                "alias mech="*|"complete "*mech*|"_mech_completions"*|"    "*COMP*|"    "*commands=*|"    "*themes=*|"}"*|"set -gx PATH"*"/.local/bin"*|"export PATH="*"/.local/bin"*|"")
                    continue
                    ;;
                *)
                    in_block=false
                    echo "$line"
                    ;;
            esac
        else
            echo "$line"
        fi
    done < "$rc_file" > "$tmp_file"

    mv "$tmp_file" "$rc_file"
    log_info "Alias y completions eliminados de / removed from: ${rc_file}"
}

show_farewell() {
    echo ""

    # Try to show servo-skull ERROR frame
    local py_cmd=""
    if command -v python3 &>/dev/null; then
        py_cmd="python3"
    elif command -v python &>/dev/null; then
        py_cmd="python"
    fi

    if [[ -n "$py_cmd" && -f "${SCRIPT_DIR}/servoskull.py" ]]; then
        $py_cmd -c "
import sys
sys.path.insert(0, '${SCRIPT_DIR}')
from servoskull import get_frame
print(get_frame('ERROR'))
" 2>/dev/null || true
    fi

    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${RESET}"
    echo -e "${RED}  ☠ El Rito de Desvinculación ha concluido. La Forja se apaga. ☠${RESET}"
    echo -e "${RED}  The Rite of Unbinding is concluded. The Forge goes dark.${RESET}"
    echo -e "${DIM}  The machine spirit returns to the Omnissiah. ☠${RESET}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${RESET}"
    echo ""
    echo -e "${DIM}  Reinicie su terminal / Restart your terminal.${RESET}"
    echo -e "${DIM}  01000101 01001110 01000100 — SIGNAL LOST — M41${RESET}"
    echo ""
}

# ═══⚙═══ MAIN RITE ═══⚙═══

main() {
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════════${RESET}"
    echo -e "${RED}  ☠ MECHANICUS TERMINAL — RITO DE DESVINCULACIÓN ☠${RESET}"
    echo -e "${RED}  Rite of Unbinding — Removing Adeptus Mechanicus Wrapper${RESET}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${RESET}"
    echo -e "${DIM}  01010101 01001110 01001001 01001110 01010011 01010100${RESET}"
    echo ""

    echo -e -n "${ORANGE}  ¿Proceder con la desvinculación? / Proceed with unbinding? [y/N]: ${RESET}"
    read -r confirm
    if [[ "${confirm,,}" != "y" && "${confirm,,}" != "yes" && "${confirm,,}" != "si" && "${confirm,,}" != "sí" ]]; then
        log_info "Rito cancelado. La Forja permanece activa. / Rite cancelled. Forge remains active."
        exit 0
    fi
    echo ""

    remove_mechcode
    restore_claude_md
    remove_config
    remove_shell_config

    show_farewell
}

main "$@"
