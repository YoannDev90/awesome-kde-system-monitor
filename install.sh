#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/YoannDev90/awesome-kde-system-monitor"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/plasma-systemmonitor"
TOOL_NAME="generate-pages"

info()  { printf "\033[1;34m→\033[0m %s\n" "$*"; }
warn()  { printf "\033[1;33m!\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m✗\033[0m %s\n" "$*" >&2; exit 1; }

check_pygobject() {
    python3 -c "import gi" 2>/dev/null && return 0
    warn "PyGObject not found. Install it first:"
    echo ""
    echo "  Arch:       sudo pacman -S python-gobject glib2"
    echo "  Debian/Ubuntu: sudo apt install python3-gi gir1.2-glib"
    echo "  Fedora:     sudo dnf install python3-gobject glib2"
    echo "  openSUSE:   sudo zypper install python3-gobject"
    echo ""
    read -rp "Continue anyway? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || exit 1
}

install_tool() {
    if command -v uv &>/dev/null; then
        info "Installing $TOOL_NAME via uv..."
        uv tool install "$REPO"
        info "Installed: run 'generate-pages --help'"
        return
    fi

    if command -v pipx &>/dev/null; then
        info "Installing $TOOL_NAME via pipx..."
        pipx install "git+$REPO"
        info "Installed: run 'generate-pages --help'"
        return
    fi

    warn "Neither uv nor pipx found."
    info "Falling back to direct copy..."

    local tmp
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT

    info "Cloning repo..."
    git clone --depth 1 "$REPO" "$tmp"

    mkdir -p "$DEST"
    cp "$tmp"/*.page "$DEST/" 2>/dev/null || true
    info "Pages copied to $DEST"

    echo ""
    info "To install the CLI tool, install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  uv tool install $REPO"
}

install_pages_only() {
    local tmp
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT

    info "Cloning repo..."
    git clone --depth 1 "$REPO" "$tmp"

    mkdir -p "$DEST"
    cp "$tmp"/*.page "$DEST/" 2>/dev/null || true
    info "Pages copied to $DEST"
    info "Restart Plasma System Monitor or log out/in"
}

usage() {
    cat <<EOF
Usage: $0 [OPTION]

Install awesome-kde-system-monitor pages and/or CLI tool.

Options:
  --pages-only    Copy .page files only (no CLI tool)
  -h, --help      Show this help
  (no args)       Install CLI tool + pages

Examples:
  curl -sSL https://raw.githubusercontent.com/YoannDev90/awesome-kde-system-monitor/master/install.sh | bash
  curl -sSL .../install.sh | bash -s -- --pages-only
EOF
}

main() {
    local mode="all"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --pages-only) mode="pages"; shift ;;
            -h|--help)    usage; exit 0 ;;
            *)            error "Unknown option: $1" ;;
        esac
    done

    echo ""
    info "awesome-kde-system-monitor installer"
    echo ""

    check_pygobject

    if [[ "$mode" == "pages" ]]; then
        install_pages_only
    else
        install_tool
    fi
}

main "$@"
