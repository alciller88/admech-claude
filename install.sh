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
    if [[ "$INST_LANG" == "es" ]]; then
        echo "  MECHANICUS TERMINAL — RITO DE INICIACION"
        echo "  Wrapper Adeptus Mechanicus para Claude Code"
    else
        echo "  MECHANICUS TERMINAL — RITE OF INITIATION"
        echo "  Adeptus Mechanicus Wrapper for Claude Code"
    fi
    echo "================================================================="
    echo -e "${DIM}  01001001 01001110 01001001 01010100${RESET}"
    echo ""
}

print_disclaimer() {
    echo -e "${DIM}--+--+--+--+--+--+--+--+--+--+--+--+--+--${RESET}"
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${BONE}Proyecto fan no oficial para uso personal/educativo."
        echo "Warhammer 40,000 y Adeptus Mechanicus son marcas de"
        echo "Games Workshop Limited. No afiliado ni respaldado por GW."
        echo -e "Por el Omnissiah.${RESET}"
    else
        echo -e "${BONE}This is an unofficial fan project for personal/educational use."
        echo "Warhammer 40,000 and Adeptus Mechanicus are trademarks of"
        echo "Games Workshop Limited. Not affiliated or endorsed by GW."
        echo -e "For the Omnissiah.${RESET}"
    fi
    echo -e "${DIM}--+--+--+--+--+--+--+--+--+--+--+--+--+--${RESET}"
    echo ""
}

log_info()    { echo -e "${BONE}  [FORGE//] $1${RESET}"; }
log_success() { echo -e "${GREEN}  [RITE//]  $1${RESET}"; }
log_warning() { echo -e "${ORANGE}  [AUGUR//] $1${RESET}"; }
log_error()   { echo -e "${RED}  [HERESY/] $1${RESET}"; }

# === OS DETECTION ===
detect_os() {
    # Returns: debian, fedora, arch, macos, wsl-debian, wsl-fedora, wsl-arch, wsl, or unknown
    if [[ "$(uname -s)" == "Darwin" ]]; then
        echo "macos"
        return
    fi

    local is_wsl="no"
    if [[ -f /proc/version ]] && grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
        is_wsl="yes"
    fi

    local distro="unknown"
    if [[ -f /etc/os-release ]]; then
        local id=""
        id=$(. /etc/os-release 2>/dev/null && echo "${ID:-}")
        local id_like=""
        id_like=$(. /etc/os-release 2>/dev/null && echo "${ID_LIKE:-}")
        case "$id" in
            ubuntu|debian|linuxmint|pop) distro="debian" ;;
            fedora|rhel|centos|rocky)    distro="fedora" ;;
            arch|manjaro|endeavouros)    distro="arch"   ;;
            *)
                # Fallback: check ID_LIKE
                case "$id_like" in
                    *debian*|*ubuntu*) distro="debian" ;;
                    *fedora*|*rhel*)   distro="fedora" ;;
                    *arch*)            distro="arch"   ;;
                esac
                ;;
        esac
    fi

    if [[ "$is_wsl" == "yes" ]]; then
        if [[ "$distro" != "unknown" ]]; then
            echo "wsl-${distro}"
        else
            echo "wsl"
        fi
    else
        echo "$distro"
    fi
}

# Resolve the package manager family from OS (strips wsl- prefix)
os_pkg_family() {
    local os="$1"
    case "$os" in
        wsl-debian) echo "debian" ;;
        wsl-fedora) echo "fedora" ;;
        wsl-arch)   echo "arch"   ;;
        wsl)        echo "debian" ;;  # assume debian-based WSL by default
        *)          echo "$os"    ;;
    esac
}

# Show the OS-specific install command for a given package
suggest_install_cmd() {
    local pkg="$1"
    local pkg_family
    pkg_family="$(os_pkg_family "$DETECTED_OS")"
    case "$pkg_family" in
        debian) echo -e "${BONE}    sudo apt install ${pkg}${RESET}" ;;
        fedora) echo -e "${BONE}    sudo dnf install ${pkg}${RESET}" ;;
        arch)   echo -e "${BONE}    sudo pacman -S ${pkg}${RESET}" ;;
        macos)  echo -e "${BONE}    brew install ${pkg}${RESET}" ;;
        *)
            # Unknown OS — show all options
            echo -e "${BONE}    Ubuntu/Debian: sudo apt install ${pkg}${RESET}"
            echo -e "${BONE}    Fedora:        sudo dnf install ${pkg}${RESET}"
            echo -e "${BONE}    Arch:          sudo pacman -S ${pkg}${RESET}"
            echo -e "${BONE}    macOS:         brew install ${pkg}${RESET}"
            ;;
    esac
}

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
        local claude_ver=""
        claude_ver=$(claude --version 2>/dev/null || echo "unknown")
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Claude Code encontrado (${claude_ver})"
        else
            log_success "Claude Code found (${claude_ver})"
        fi
        return 0
    fi
    if [[ "$INST_LANG" == "es" ]]; then
        log_error "Claude Code no encontrado en PATH"
        echo ""
        echo -e "${BONE}  Instalar con:${RESET}"
    else
        log_error "Claude Code not found in PATH"
        echo ""
        echo -e "${BONE}  Install with:${RESET}"
    fi
    echo -e "${BONE}    npm install -g @anthropic-ai/claude-code${RESET}"
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
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Python 3.8+ no encontrado"
            echo ""
            echo -e "${BONE}  Instalar con:${RESET}"
        else
            log_error "Python 3.8+ not found"
            echo ""
            echo -e "${BONE}  Install with:${RESET}"
        fi
        suggest_install_cmd "python3"
        echo ""
        exit 1
    fi

    local version
    version=$($py_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    local major minor
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 8 ]]; }; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Python ${version} detectado — se requiere 3.8+ (detected < required)"
        else
            log_error "Python ${version} detected — 3.8+ required"
        fi
        echo -e "${BONE}    detected: ${version}  |  required: >= 3.8${RESET}"
        exit 1
    fi

    if [[ "$INST_LANG" == "es" ]]; then
        log_success "Python ${version} (>= 3.8 requerido) — STC-compliant"
    else
        log_success "Python ${version} (>= 3.8 required) — STC-compliant"
    fi
}

check_tmux() {
    if command -v tmux &>/dev/null; then
        local ver
        ver=$(tmux -V 2>/dev/null || echo "unknown")
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "tmux encontrado: ${ver}"
        else
            log_success "tmux found: ${ver}"
        fi
        return 0
    fi
    if [[ "$INST_LANG" == "es" ]]; then
        log_warning "tmux no encontrado — el monitor sidebar requiere tmux"
        echo ""
        echo -e "${BONE}  Instalar tmux:${RESET}"
    else
        log_warning "tmux not found — sidebar monitor requires tmux"
        echo ""
        echo -e "${BONE}  Install tmux:${RESET}"
    fi
    suggest_install_cmd "tmux"
    echo ""
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${ORANGE}  Continuando sin tmux — mechcode funcionara en modo basico.${RESET}"
    else
        echo -e "${ORANGE}  Continuing without tmux — mechcode will work in basic mode.${RESET}"
    fi
    echo ""
}

backup_claude_md() {
    if [[ -f "$CLAUDE_MD_DST" ]]; then
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local backup_path="${CLAUDE_MD_DST}.backup.${timestamp}"

        if [[ "$INST_LANG" == "es" ]]; then
            log_warning "CLAUDE.md existente detectado"
            echo ""
            echo -e "${BONE}  Se creara backup en: ${backup_path}${RESET}"
            echo ""
            echo -e -n "${ORANGE}  Continuar? [y/N]: ${RESET}"
        else
            log_warning "Existing CLAUDE.md detected"
            echo ""
            echo -e "${BONE}  Backup will be created at: ${backup_path}${RESET}"
            echo ""
            echo -e -n "${ORANGE}  Continue? [y/N]: ${RESET}"
        fi
        read -r confirm
        confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')
        if [[ "$confirm" != "y" && "$confirm" != "yes" && "$confirm" != "si" ]]; then
            if [[ "$INST_LANG" == "es" ]]; then
                log_info "Abortado por el usuario"
            else
                log_info "Aborted by user"
            fi
            exit 0
        fi

        cp "$CLAUDE_MD_DST" "$backup_path"
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Backup creado: ${backup_path}"
        else
            log_success "Backup created: ${backup_path}"
        fi
    fi
}

install_mechcode() {
    mkdir -p "$INSTALL_DIR"

    # Copy all Python files
    for pyfile in mechcode.py servoskull.py servoskull_monitor.py mechcode_hook.py shared_config.py; do
        if [[ -f "${SCRIPT_DIR}/${pyfile}" ]]; then
            cp "${SCRIPT_DIR}/${pyfile}" "${INSTALL_DIR}/${pyfile}"
            if [[ "$INST_LANG" == "es" ]]; then
                log_info "Instalado ${pyfile}"
            else
                log_info "Installed ${pyfile}"
            fi
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

    if [[ "$INST_LANG" == "es" ]]; then
        log_success "mechcode instalado en: ${MECHCODE_BIN}"
    else
        log_success "mechcode installed at: ${MECHCODE_BIN}"
    fi
}

install_claude_md() {
    mkdir -p "$CLAUDE_DIR"

    if [[ ! -f "$CLAUDE_MD_SRC" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Grimorio no encontrado: ${CLAUDE_MD_SRC}"
        else
            log_error "Grimoire not found: ${CLAUDE_MD_SRC}"
        fi
        exit 1
    fi

    cp "$CLAUDE_MD_SRC" "$CLAUDE_MD_DST"
    if [[ "$INST_LANG" == "es" ]]; then
        log_success "Grimorio instalado: ${CLAUDE_MD_DST}"
    else
        log_success "Grimoire installed: ${CLAUDE_MD_DST}"
    fi
}

install_hooks() {
    mkdir -p "$HOOKS_DIR"

    # Make hook script available
    local hook_script="${INSTALL_DIR}/mechcode_hook.py"

    if [[ ! -f "$hook_script" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_warning "Script de hook no encontrado, omitiendo configuracion"
        else
            log_warning "Hook script not found, skipping hooks setup"
        fi
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
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Hooks de Claude Code instalados"
        else
            log_success "Claude Code hooks installed"
        fi
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_warning "No se pudieron configurar los hooks automaticamente"
        else
            log_warning "Could not configure hooks automatically"
        fi
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
        if [[ "$INST_LANG" == "es" ]]; then
            log_info "Alias 'mech' ya existe — omitiendo"
        else
            log_info "Alias 'mech' already exists — skipping"
        fi
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
    if [[ "$INST_LANG" == "es" ]]; then
        log_success "Alias + completions agregados a: ${rc_file}"
    else
        log_success "Alias + completions added to: ${rc_file}"
    fi

    # Ensure ~/.local/bin is in PATH
    if ! echo "$PATH" | tr ':' '\n' | grep -q "${INSTALL_DIR}"; then
        case "$shell_type" in
            fish) echo "set -gx PATH ${INSTALL_DIR} \$PATH" >> "$rc_file" ;;
            *)    echo "export PATH=\"${INSTALL_DIR}:\$PATH\"" >> "$rc_file" ;;
        esac
        if [[ "$INST_LANG" == "es" ]]; then
            log_info "PATH actualizado en ${rc_file}"
        else
            log_info "PATH updated in ${rc_file}"
        fi
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
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${GOLD}  Rito de Iniciacion completado. La Forja esta activa.${RESET}"
        echo -e "${GREEN}  Que el Omnissiah guie tus algoritmos, Magos.${RESET}"
    else
        echo -e "${GOLD}  Rite of Initiation complete. The Forge is active.${RESET}"
        echo -e "${GREEN}  May the Omnissiah guide your algorithms, Magos.${RESET}"
    fi
    echo -e "${GOLD}=================================================================${RESET}"
    echo ""
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${BONE}  Uso:${RESET}"
        echo -e "${BONE}    mech --help        ${DIM}->${BONE} Todos los comandos${RESET}"
        echo -e "${BONE}    mech <claude args> ${DIM}->${BONE} Lanzar con sidebar servo-skull${RESET}"
        echo -e "${BONE}    mech status        ${DIM}->${BONE} Config y estadisticas${RESET}"
        echo -e "${BONE}    mech kill          ${DIM}->${BONE} Terminar sesion tmux${RESET}"
    else
        echo -e "${BONE}  Usage:${RESET}"
        echo -e "${BONE}    mech --help        ${DIM}->${BONE} All commands${RESET}"
        echo -e "${BONE}    mech <claude args> ${DIM}->${BONE} Launch with servo-skull sidebar${RESET}"
        echo -e "${BONE}    mech status        ${DIM}->${BONE} Current config + stats${RESET}"
        echo -e "${BONE}    mech kill          ${DIM}->${BONE} Kill tmux session${RESET}"
    fi
    echo ""
    if [[ "$INST_LANG" == "es" ]]; then
        echo -e "${DIM}  Reinicia tu terminal o ejecuta: source $(get_rc_file "$(detect_shell)")${RESET}"
    else
        echo -e "${DIM}  Restart terminal or run: source $(get_rc_file "$(detect_shell)")${RESET}"
    fi
    echo -e "${DIM}  01001100 01000001 01010101 01010011 — LAUS OMNISSIAH${RESET}"
    echo ""
}

# === POST-INSTALL VALIDATION ===
post_install_validate() {
    echo ""
    echo -e "${DIM}──†──†──†──†──†──†──†──†──†──†──†──†──†──${RESET}"
    if [[ "$INST_LANG" == "es" ]]; then
        log_info "=== VERIFICACION POST-INSTALACION ==="
    else
        log_info "=== POST-INSTALL VALIDATION ==="
    fi
    echo ""

    local checks_passed=0
    local checks_total=5

    # 1. Check that all files were copied to ~/.local/bin
    local missing_files=""
    local files_ok="yes"
    for pyfile in mechcode.py servoskull.py servoskull_monitor.py mechcode_hook.py shared_config.py mechcode; do
        if [[ ! -f "${INSTALL_DIR}/${pyfile}" ]]; then
            files_ok="no"
            if [[ -z "$missing_files" ]]; then
                missing_files="${pyfile}"
            else
                missing_files="${missing_files}, ${pyfile}"
            fi
        fi
    done
    if [[ "$files_ok" == "yes" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Archivos instalados en ${INSTALL_DIR}"
        else
            log_success "Files installed in ${INSTALL_DIR}"
        fi
        checks_passed=$((checks_passed + 1))
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Archivos faltantes en ${INSTALL_DIR}: ${missing_files}"
            echo -e "${BONE}    Remediar: volver a ejecutar install.sh${RESET}"
        else
            log_error "Missing files in ${INSTALL_DIR}: ${missing_files}"
            echo -e "${BONE}    Remediate: re-run install.sh${RESET}"
        fi
    fi

    # 2. Check hooks registered in settings.json (parse with Python)
    local py_cmd="python3"
    command -v python3 &>/dev/null || py_cmd="python"

    local hooks_ok="no"
    if [[ -f "$SETTINGS_FILE" ]]; then
        hooks_ok=$($py_cmd -c "
import json, sys
try:
    with open('${SETTINGS_FILE}') as f:
        settings = json.load(f)
    hooks = settings.get('hooks', {})
    required = ['PreToolUse', 'PostToolUse', 'SessionStart', 'Stop']
    missing = [e for e in required if e not in hooks or len(hooks[e]) == 0]
    if not missing:
        print('yes')
    else:
        print('missing:' + ','.join(missing))
except Exception as ex:
    print('error:' + str(ex))
" 2>/dev/null || echo "error:python-failed")
    else
        hooks_ok="error:file-not-found"
    fi

    if [[ "$hooks_ok" == "yes" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Hooks registrados en settings.json"
        else
            log_success "Hooks registered in settings.json"
        fi
        checks_passed=$((checks_passed + 1))
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Hooks no configurados correctamente (${hooks_ok})"
            echo -e "${BONE}    Remediar: claude /hooks  o volver a ejecutar install.sh${RESET}"
        else
            log_error "Hooks not properly configured (${hooks_ok})"
            echo -e "${BONE}    Remediate: claude /hooks  or re-run install.sh${RESET}"
        fi
    fi

    # 3. Check CLAUDE.md installed
    if [[ -f "$CLAUDE_MD_DST" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "CLAUDE.md instalado en ${CLAUDE_MD_DST}"
        else
            log_success "CLAUDE.md installed at ${CLAUDE_MD_DST}"
        fi
        checks_passed=$((checks_passed + 1))
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "CLAUDE.md no encontrado en ${CLAUDE_MD_DST}"
            echo -e "${BONE}    Remediar: cp ${CLAUDE_MD_SRC} ${CLAUDE_MD_DST}${RESET}"
        else
            log_error "CLAUDE.md not found at ${CLAUDE_MD_DST}"
            echo -e "${BONE}    Remediate: cp ${CLAUDE_MD_SRC} ${CLAUDE_MD_DST}${RESET}"
        fi
    fi

    # 4. Check mech command is accessible
    if command -v mech &>/dev/null; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Comando 'mech' accesible en PATH"
        else
            log_success "'mech' command accessible in PATH"
        fi
        checks_passed=$((checks_passed + 1))
    elif command -v mechcode &>/dev/null; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Comando 'mechcode' accesible (alias 'mech' requiere reiniciar terminal)"
        else
            log_success "'mechcode' accessible (alias 'mech' requires terminal restart)"
        fi
        checks_passed=$((checks_passed + 1))
    elif [[ -x "$MECHCODE_BIN" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_warning "'mech' no esta en PATH aun — reiniciar terminal o ejecutar:"
        else
            log_warning "'mech' not in PATH yet — restart terminal or run:"
        fi
        echo -e "${BONE}    source $(get_rc_file "$(detect_shell)")${RESET}"
        # Count as pass since the file exists and is executable
        checks_passed=$((checks_passed + 1))
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "'mech' no encontrado — verificar instalacion"
            echo -e "${BONE}    Remediar: volver a ejecutar install.sh${RESET}"
        else
            log_error "'mech' not found — verify installation"
            echo -e "${BONE}    Remediate: re-run install.sh${RESET}"
        fi
    fi

    # 5. Check hook runner script exists and is executable
    if [[ -x "${HOOKS_DIR}/mechcode_hook.sh" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "Hook runner ejecutable en ${HOOKS_DIR}"
        else
            log_success "Hook runner executable in ${HOOKS_DIR}"
        fi
        checks_passed=$((checks_passed + 1))
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_error "Hook runner no encontrado o no ejecutable"
            echo -e "${BONE}    Remediar: volver a ejecutar install.sh${RESET}"
        else
            log_error "Hook runner not found or not executable"
            echo -e "${BONE}    Remediate: re-run install.sh${RESET}"
        fi
    fi

    # Summary
    echo ""
    if [[ "$checks_passed" -eq "$checks_total" ]]; then
        if [[ "$INST_LANG" == "es" ]]; then
            log_success "${checks_passed}/${checks_total} verificaciones exitosas — Forja operativa"
        else
            log_success "${checks_passed}/${checks_total} checks passed — Forge operational"
        fi
    else
        if [[ "$INST_LANG" == "es" ]]; then
            log_warning "${checks_passed}/${checks_total} verificaciones exitosas — revisar items marcados"
        else
            log_warning "${checks_passed}/${checks_total} checks passed — review flagged items above"
        fi
    fi
    echo -e "${DIM}──†──†──†──†──†──†──†──†──†──†──†──†──†──${RESET}"
}

# === MAIN ===

main() {
    # Detect OS early so check functions can use it
    DETECTED_OS="$(detect_os)"

    print_banner
    print_disclaimer

    if [[ "$INST_LANG" == "es" ]]; then
        log_info "Verificando sistema... (OS: ${DETECTED_OS})"
    else
        log_info "Running system checks... (OS: ${DETECTED_OS})"
    fi
    echo ""

    check_claude
    check_python
    check_tmux
    echo ""

    backup_claude_md
    echo ""

    if [[ "$INST_LANG" == "es" ]]; then
        log_info "=== INSTALANDO COMPONENTES ==="
    else
        log_info "=== INSTALLING COMPONENTS ==="
    fi
    echo ""
    install_mechcode
    install_claude_md
    install_hooks
    install_shell_config
    echo ""

    show_success

    post_install_validate
}

main "$@"
