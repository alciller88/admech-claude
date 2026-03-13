#!/usr/bin/env bash
# ═══⚙═══ RITO DE INICIACIÓN — MECHANICUS TERMINAL ═══⚙═══
# Designación: INSTALL-SCRIPT-Ω1
# 01001001 01001110 01010011 01010100 01000001 01001100 01001100
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
CLAUDE_MD_SRC="${SCRIPT_DIR}/config/CLAUDE.md"
CLAUDE_MD_DST="${CLAUDE_DIR}/CLAUDE.md"

# ═══⚙═══ FUNCTIONS ═══⚙═══

print_banner() {
    echo -e "${GOLD}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  ⚙ MECHANICUS TERMINAL — RITO DE INICIACIÓN ⚙"
    echo "  Rite of Initiation — Adeptus Mechanicus Wrapper for Claude Code"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${DIM}  01001001 01001110 01001001 01010100 01001001 01000001 01010100 01000101${RESET}"
    echo ""
}

print_disclaimer() {
    echo -e "${DIM}──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──${RESET}"
    echo -e "${BONE}This is an unofficial fan project created for personal and educational use."
    echo "Warhammer 40,000, Adeptus Mechanicus, and all related names, terms, characters,"
    echo "and lore are trademarks and/or copyright of Games Workshop Limited and are used"
    echo "here without permission. This project is not affiliated with, endorsed by, or"
    echo "connected to Games Workshop in any way. No commercial use is intended or permitted."
    echo -e "For the Omnissiah.${RESET}"
    echo -e "${DIM}──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──†──${RESET}"
    echo ""
}

log_info() {
    echo -e "${BONE}  [FORJA//] ⚙ $1${RESET}"
}

log_success() {
    echo -e "${GREEN}  [RITO//] ‡ $1${RESET}"
}

log_warning() {
    echo -e "${ORANGE}  [AUGUR//] † $1${RESET}"
}

log_error() {
    echo -e "${RED}  [HEREJÍA//] ☠ $1${RESET}"
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

check_claude() {
    if command -v claude &>/dev/null; then
        return 0
    fi
    log_error "HEREJÍA CRÍTICA — Claude Code no encontrado en PATH"
    log_error "CRITICAL HERESY — Claude Code not found in PATH"
    echo ""
    echo -e "${BONE}  El Espíritu de Máquina no puede ser invocado sin el binario sagrado.${RESET}"
    echo -e "${BONE}  The Machine Spirit cannot be awakened without the sacred binary.${RESET}"
    echo ""
    echo -e "${GOLD}  Instalar / Install:${RESET}"
    echo -e "${BONE}    npm install -g @anthropic-ai/claude-code${RESET}"
    echo ""
    echo -e "${DIM}  Tras la instalación, ejecute este rito nuevamente.${RESET}"
    echo -e "${DIM}  After installation, execute this rite again.${RESET}"
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
        log_error "Python 3.8+ no encontrado — Python 3.8+ not found"
        echo -e "${BONE}  El Omnissiah requiere Python 3.8+ para la Forja.${RESET}"
        exit 1
    fi

    # Check version >= 3.8
    local version
    version=$($py_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
    local major minor
    major=$(echo "$version" | cut -d. -f1)
    minor=$(echo "$version" | cut -d. -f2)

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 8 ]]; }; then
        log_error "Python ${version} detectado — se requiere 3.8+"
        log_error "Python ${version} detected — 3.8+ required"
        exit 1
    fi

    log_info "Python ${version} detectado — conforme al STC / STC-compliant"
}

backup_claude_md() {
    if [[ -f "$CLAUDE_MD_DST" ]]; then
        local timestamp
        timestamp="$(date +%Y%m%d_%H%M%S)"
        local backup_path="${CLAUDE_MD_DST}.backup.${timestamp}"

        log_warning "Fichero existente detectado — Existing file detected: ${CLAUDE_MD_DST}"
        echo ""
        echo -e "${BONE}  Se creará un backup automático en / Automatic backup will be created at:${RESET}"
        echo -e "${GOLD}    ${backup_path}${RESET}"
        echo ""
        echo -e -n "${ORANGE}  ¿Continuar? / Continue? [y/N]: ${RESET}"
        read -r confirm
        confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')
        if [[ "$confirm" != "y" && "$confirm" != "yes" && "$confirm" != "si" && "$confirm" != "sí" ]]; then
            log_info "Rito abortado por el Magos — Rite aborted by Magos"
            exit 0
        fi

        cp "$CLAUDE_MD_DST" "$backup_path"
        log_success "Backup creado — Backup created: ${backup_path}"
    fi
}

install_mechcode() {
    log_info "Creando directorio de instalación / Creating install directory: ${INSTALL_DIR}"
    mkdir -p "$INSTALL_DIR"

    log_info "Instalando mechcode.py / Installing mechcode.py"
    cp "${SCRIPT_DIR}/mechcode.py" "$MECHCODE_BIN"
    chmod +x "$MECHCODE_BIN"

    # Copy servoskull.py alongside mechcode
    if [[ -f "${SCRIPT_DIR}/servoskull.py" ]]; then
        cp "${SCRIPT_DIR}/servoskull.py" "${INSTALL_DIR}/servoskull.py"
        log_info "Servo-cráneo instalado / Servo-skull installed"
    fi

    log_success "mechcode instalado en / installed at: ${MECHCODE_BIN}"
}

install_claude_md() {
    log_info "Creando directorio Claude / Creating Claude directory: ${CLAUDE_DIR}"
    mkdir -p "$CLAUDE_DIR"

    if [[ ! -f "$CLAUDE_MD_SRC" ]]; then
        log_error "Grimorio no encontrado — Grimoire not found: ${CLAUDE_MD_SRC}"
        log_error "Asegúrese de ejecutar desde el directorio del repositorio."
        exit 1
    fi

    cp "$CLAUDE_MD_SRC" "$CLAUDE_MD_DST"
    log_success "Grimorio del Omnissiah instalado / Grimoire installed: ${CLAUDE_MD_DST}"
}

install_shell_config() {
    local shell_type
    shell_type="$(detect_shell)"
    local rc_file
    rc_file="$(get_rc_file "$shell_type")"

    log_info "Shell detectado / Shell detected: ${shell_type} (${rc_file})"

    # Check if alias already exists
    if grep -q "alias mech=" "$rc_file" 2>/dev/null; then
        log_info "Alias 'mech' ya existe en ${rc_file} — ya configurado"
        log_info "Alias 'mech' already exists in ${rc_file} — already configured"
        return
    fi

    local alias_block=""
    case "$shell_type" in
        fish)
            alias_block='
# ═══⚙═══ Mechanicus Terminal — Adeptus Mechanicus Wrapper ═══⚙═══
alias mech="mechcode"
# Completions
complete -c mech -f -a "on enable off disable ascii quiet full stealth status theme lore esp eng help" -d "Mechanicus command"
'
            ;;
        zsh)
            alias_block='
# ═══⚙═══ Mechanicus Terminal — Adeptus Mechanicus Wrapper ═══⚙═══
alias mech="mechcode"
# Zsh completions
_mech_completions() {
    local commands=(on enable off disable ascii quiet full stealth status theme lore esp eng --help)
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
# ═══⚙═══ Mechanicus Terminal — Adeptus Mechanicus Wrapper ═══⚙═══
alias mech="mechcode"
# Bash completions
_mech_completions() {
    local commands="on enable off disable ascii quiet full stealth status theme lore esp eng --help"
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
    log_success "Alias y autocompletado añadidos a / Alias and completions added to: ${rc_file}"

    # Ensure ~/.local/bin is in PATH
    if ! echo "$PATH" | tr ':' '\n' | grep -q "${INSTALL_DIR}"; then
        local path_line=""
        case "$shell_type" in
            fish)
                path_line="set -gx PATH ${INSTALL_DIR} \$PATH"
                ;;
            *)
                path_line="export PATH=\"${INSTALL_DIR}:\$PATH\""
                ;;
        esac
        echo "$path_line" >> "$rc_file"
        log_info "PATH actualizado en ${rc_file} / PATH updated"
    fi
}

show_success() {
    echo ""

    # Try to show servo-skull SUCCESS frame
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
print(get_frame('SUCCESS'))
" 2>/dev/null || true
    fi

    echo ""
    echo -e "${GOLD}═══════════════════════════════════════════════════════════════${RESET}"
    echo -e "${GOLD}  ⚙ El Rito de Iniciación ha concluido. La Forja está activa. ⚙${RESET}"
    echo -e "${GOLD}  The Rite of Initiation is concluded. The Forge is active.${RESET}"
    echo -e "${GREEN}  Que el Omnissiah guíe tus algoritmos, Magos. ‡${RESET}"
    echo -e "${GREEN}  May the Omnissiah guide your algorithms, Magos. ‡${RESET}"
    echo -e "${GOLD}═══════════════════════════════════════════════════════════════${RESET}"
    echo ""
    echo -e "${BONE}  Uso / Usage:${RESET}"
    echo -e "${BONE}    mech --help        ${DIM}→${BONE} Ver todos los comandos / See all commands${RESET}"
    echo -e "${BONE}    mech on            ${DIM}→${BONE} Activar la Forja / Activate the Forge${RESET}"
    echo -e "${BONE}    mech status        ${DIM}→${BONE} Estado actual / Current status${RESET}"
    echo -e "${BONE}    mech lore          ${DIM}→${BONE} Litanía del Omnissiah / Litany${RESET}"
    echo ""
    echo -e "${DIM}  Reinicie su terminal o ejecute / Restart your terminal or run:${RESET}"
    echo -e "${BONE}    source $(get_rc_file "$(detect_shell)")${RESET}"
    echo ""
    echo -e "${DIM}  01001100 01000001 01010101 01010011 — LAUS OMNISSIAH — M41${RESET}"
    echo ""
}

# ═══⚙═══ MAIN RITE ═══⚙═══

main() {
    print_banner
    print_disclaimer

    log_info "Iniciando verificaciones del sistema / Starting system checks..."
    echo ""

    # Pre-flight checks
    check_claude
    check_python
    echo ""

    # Backup existing CLAUDE.md if present
    backup_claude_md
    echo ""

    # Install components
    log_info "═══⚙═══ INSTALANDO COMPONENTES / INSTALLING COMPONENTS ═══⚙═══"
    echo ""
    install_mechcode
    install_claude_md
    install_shell_config
    echo ""

    # Victory
    show_success
}

main "$@"
