#!/usr/bin/env bash
# === RITO DE INICIACION — MECHANICUS TERMINAL ===
# Installs mechcode + servo-skull monitor + Claude Code hooks
set -euo pipefail

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
MECHCODE_BIN="${INSTALL_DIR}/mechcode"
CLAUDE_MD_SRC="${SCRIPT_DIR}/config/CLAUDE.md"
CLAUDE_MD_DST="${CLAUDE_DIR}/CLAUDE.md"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"

# === FUNCTIONS ===

print_banner() {
    echo -e "${GOLD}"
    echo "================================================================="
    echo "  MECHANICUS TERMINAL — RITO DE INICIACION"
    echo "  Rite of Initiation — Adeptus Mechanicus Wrapper for Claude Code"
    echo "================================================================="
    echo -e "${DIM}  01001001 01001110 01001001 01010100${RESET}"
    echo ""
}

print_disclaimer() {
    echo -e "${DIM}--+--+--+--+--+--+--+--+--+--+--+--+--+--${RESET}"
    echo -e "${BONE}This is an unofficial fan project for personal/educational use."
    echo "Warhammer 40,000 and Adeptus Mechanicus are trademarks of"
    echo "Games Workshop Limited. Not affiliated or endorsed by GW."
    echo -e "For the Omnissiah.${RESET}"
    echo -e "${DIM}--+--+--+--+--+--+--+--+--+--+--+--+--+--${RESET}"
    echo ""
}

log_info()    { echo -e "${BONE}  [FORGE//] $1${RESET}"; }
log_success() { echo -e "${GREEN}  [RITE//]  $1${RESET}"; }
log_warning() { echo -e "${ORANGE}  [AUGUR//] $1${RESET}"; }
log_error()   { echo -e "${RED}  [HERESY/] $1${RESET}"; }

detect_shell() {
    local s
    s="$(basename "${SHELL:-bash}")"
    case "$s" in
        zsh)  echo "zsh" ;;
        fish) echo "fish" ;;
        *)    echo "bash" ;;
    esac
}

get_rc_file() {
    case "$1" in
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

check_claude() {
    if command -v claude &>/dev/null; then
        log_success "Claude Code found"
        return 0
    fi
    log_error "Claude Code not found in PATH"
    echo ""
    echo -e "${BONE}  Install: npm install -g @anthropic-ai/claude-code${RESET}"
    echo ""
    exit 1
}

check_python() {
    local py_cmd=""
    if command -v python3 &>/dev/null; then
        py_cmd="python3"
    elif command -v python &>/dev/null; then
        py_cmd="python"
    fi

    if [[ -z "$py_cmd" ]]; then
        log_error "Python 3.8+ not found"
        exit 1
    fi

    local version
    version=$($py_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    local major minor
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 8 ]]; }; then
        log_error "Python ${version} detected — 3.8+ required"
        exit 1
    fi

    log_success "Python ${version} — STC-compliant"
}

check_tmux() {
    if command -v tmux &>/dev/null; then
        local ver
        ver=$(tmux -V 2>/dev/null || echo "unknown")
        log_success "tmux found: ${ver}"
        return 0
    fi
    log_warning "tmux not found — sidebar monitor requires tmux"
    echo ""
    echo -e "${BONE}  Install tmux:${RESET}"
    echo -e "${BONE}    Ubuntu/Debian: sudo apt install tmux${RESET}"
    echo -e "${BONE}    macOS:         brew install tmux${RESET}"
    echo -e "${BONE}    Arch:          sudo pacman -S tmux${RESET}"
    echo ""
    echo -e "${ORANGE}  Continuing without tmux — mechcode will work in basic mode.${RESET}"
    echo ""
}

backup_claude_md() {
    if [[ -f "$CLAUDE_MD_DST" ]]; then
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local backup_path="${CLAUDE_MD_DST}.backup.${timestamp}"

        log_warning "Existing CLAUDE.md detected"
        echo ""
        echo -e "${BONE}  Backup will be created at: ${backup_path}${RESET}"
        echo ""
        echo -e -n "${ORANGE}  Continue? [y/N]: ${RESET}"
        read -r confirm
        confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')
        if [[ "$confirm" != "y" && "$confirm" != "yes" && "$confirm" != "si" ]]; then
            log_info "Aborted by user"
            exit 0
        fi

        cp "$CLAUDE_MD_DST" "$backup_path"
        log_success "Backup created: ${backup_path}"
    fi
}

install_mechcode() {
    mkdir -p "$INSTALL_DIR"

    # Copy all Python files
    for pyfile in mechcode.py servoskull.py servoskull_monitor.py mechcode_hook.py; do
        if [[ -f "${SCRIPT_DIR}/${pyfile}" ]]; then
            cp "${SCRIPT_DIR}/${pyfile}" "${INSTALL_DIR}/${pyfile}"
            log_info "Installed ${pyfile}"
        fi
    done

    # Make mechcode executable
    chmod +x "${INSTALL_DIR}/mechcode.py"

    # Create wrapper script
    local py_cmd="python3"
    command -v python3 &>/dev/null || py_cmd="python"

    cat > "$MECHCODE_BIN" << WRAPPER
#!/usr/bin/env bash
exec ${py_cmd} "${INSTALL_DIR}/mechcode.py" "\$@"
WRAPPER
    chmod +x "$MECHCODE_BIN"

    log_success "mechcode installed at: ${MECHCODE_BIN}"
}

install_claude_md() {
    mkdir -p "$CLAUDE_DIR"

    if [[ ! -f "$CLAUDE_MD_SRC" ]]; then
        log_error "Grimoire not found: ${CLAUDE_MD_SRC}"
        exit 1
    fi

    cp "$CLAUDE_MD_SRC" "$CLAUDE_MD_DST"
    log_success "Grimoire installed: ${CLAUDE_MD_DST}"
}

install_hooks() {
    mkdir -p "$HOOKS_DIR"

    # Make hook script available
    local hook_script="${INSTALL_DIR}/mechcode_hook.py"

    if [[ ! -f "$hook_script" ]]; then
        log_warning "Hook script not found, skipping hooks setup"
        return
    fi

    chmod +x "$hook_script"

    local py_cmd="python3"
    command -v python3 &>/dev/null || py_cmd="python"

    # Create the hook runner script
    cat > "${HOOKS_DIR}/mechcode_hook.sh" << HOOKSCRIPT
#!/usr/bin/env bash
# Mechanicus Terminal hook — updates servo-skull monitor state
cat | ${py_cmd} "${hook_script}"
exit 0
HOOKSCRIPT
    chmod +x "${HOOKS_DIR}/mechcode_hook.sh"

    # Update settings.json to register hooks
    local hook_cmd="${HOOKS_DIR}/mechcode_hook.sh"

    if [[ -f "$SETTINGS_FILE" ]]; then
        # Backup existing settings
        cp "$SETTINGS_FILE" "${SETTINGS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi

    # Read existing settings or create new
    local existing="{}"
    if [[ -f "$SETTINGS_FILE" ]]; then
        existing=$(cat "$SETTINGS_FILE" 2>/dev/null || echo "{}")
    fi

    # Use Python to merge hooks into settings
    $py_cmd -c "
import json, sys

try:
    settings = json.loads('''${existing}''')
except:
    settings = {}

if 'hooks' not in settings:
    settings['hooks'] = {}

hook_cmd = '${hook_cmd}'

# Define hook events we want to listen to
events = [
    'PreToolUse', 'PostToolUse', 'PostToolUseFailure',
    'SubagentStart', 'SubagentStop', 'SessionStart', 'Stop'
]

for event in events:
    if event not in settings['hooks']:
        settings['hooks'][event] = []

    # Check if our hook is already registered
    existing_hooks = settings['hooks'][event]
    already = any(
        any(h.get('command', '') == hook_cmd for h in entry.get('hooks', []))
        for entry in existing_hooks
        if isinstance(entry, dict)
    )
    if not already:
        settings['hooks'][event].append({
            'matcher': '',
            'hooks': [{
                'type': 'command',
                'command': hook_cmd
            }]
        })

with open('${SETTINGS_FILE}', 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print('OK')
" 2>/dev/null

    if [[ $? -eq 0 ]]; then
        log_success "Claude Code hooks installed"
    else
        log_warning "Could not configure hooks automatically"
        log_info "Run 'claude /hooks' to verify hook configuration"
    fi
}

install_shell_config() {
    local shell_type
    shell_type="$(detect_shell)"
    local rc_file
    rc_file="$(get_rc_file "$shell_type")"

    log_info "Shell: ${shell_type} (${rc_file})"

    if grep -q "alias mech=" "$rc_file" 2>/dev/null; then
        log_info "Alias 'mech' already exists — skipping"
        return
    fi

    local alias_block=""
    case "$shell_type" in
        fish)
            alias_block='
# === Mechanicus Terminal ===
alias mech="mechcode"
complete -c mech -f -a "on enable off disable status theme lore esp eng sidebar kill help" -d "Mechanicus command"
'
            ;;
        zsh)
            alias_block='
# === Mechanicus Terminal ===
alias mech="mechcode"
_mech_completions() {
    local commands=(on enable off disable status theme lore esp eng sidebar kill --help)
    local themes=(rojo verde hueso golden)
    if (( CURRENT == 2 )); then
        _describe '\''command'\'' commands
    elif (( CURRENT == 3 )) && [[ "${words[2]}" == "theme" ]]; then
        _describe '\''theme'\'' themes
    fi
}
compdef _mech_completions mech
'
            ;;
        *)
            alias_block='
# === Mechanicus Terminal ===
alias mech="mechcode"
_mech_completions() {
    local commands="on enable off disable status theme lore esp eng sidebar kill --help"
    local themes="rojo verde hueso golden"
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "${COMP_WORDS[1]}"))
    elif [[ ${COMP_CWORD} -eq 2 && "${COMP_WORDS[1]}" == "theme" ]]; then
        COMPREPLY=($(compgen -W "$themes" -- "${COMP_WORDS[2]}"))
    fi
}
complete -F _mech_completions mech
'
            ;;
    esac

    echo "$alias_block" >> "$rc_file"
    log_success "Alias + completions added to: ${rc_file}"

    # Ensure ~/.local/bin is in PATH
    if ! echo "$PATH" | tr ':' '\n' | grep -q "${INSTALL_DIR}"; then
        case "$shell_type" in
            fish) echo "set -gx PATH ${INSTALL_DIR} \$PATH" >> "$rc_file" ;;
            *)    echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "$rc_file" ;;
        esac
        log_info "PATH updated in ${rc_file}"
    fi
}

show_success() {
    echo ""

    # Try to show servo-skull
    local py_cmd=""
    command -v python3 &>/dev/null && py_cmd="python3"
    [[ -z "$py_cmd" ]] && command -v python &>/dev/null && py_cmd="python"

    if [[ -n "$py_cmd" && -f "${SCRIPT_DIR}/servoskull.py" ]]; then
        $py_cmd -c "
import sys; sys.path.insert(0, '${SCRIPT_DIR}')
from servoskull import get_frame
print(get_frame('SUCCESS', compact=True))
" 2>/dev/null || true
    fi

    echo ""
    echo -e "${GOLD}=================================================================${RESET}"
    echo -e "${GOLD}  Rite of Initiation complete. The Forge is active.${RESET}"
    echo -e "${GREEN}  May the Omnissiah guide your algorithms, Magos.${RESET}"
    echo -e "${GOLD}=================================================================${RESET}"
    echo ""
    echo -e "${BONE}  Usage:${RESET}"
    echo -e "${BONE}    mech --help        ${DIM}->${BONE} All commands${RESET}"
    echo -e "${BONE}    mech <claude args> ${DIM}->${BONE} Launch with servo-skull sidebar${RESET}"
    echo -e "${BONE}    mech status        ${DIM}->${BONE} Current config + stats${RESET}"
    echo -e "${BONE}    mech kill          ${DIM}->${BONE} Kill tmux session${RESET}"
    echo ""
    echo -e "${DIM}  Restart terminal or run: source $(get_rc_file "$(detect_shell)")${RESET}"
    echo -e "${DIM}  01001100 01000001 01010101 01010011 — LAUS OMNISSIAH${RESET}"
    echo ""
}

# === MAIN ===

main() {
    print_banner
    print_disclaimer

    log_info "Running system checks..."
    echo ""

    check_claude
    check_python
    check_tmux
    echo ""

    backup_claude_md
    echo ""

    log_info "=== INSTALLING COMPONENTS ==="
    echo ""
    install_mechcode
    install_claude_md
    install_hooks
    install_shell_config
    echo ""

    show_success
}

main "$@"
