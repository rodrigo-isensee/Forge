#!/usr/bin/env bash
# Forge: instala o comando `jarvis` em ~/.local/bin e garante esse diretório no PATH do bash.
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$HOME/.local/bin"
install -m 0755 "$raiz/scripts/jarvis" "$HOME/.local/bin/jarvis"
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  printf '\n# atalhos pessoais (jarvis)\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
fi
echo "jarvis instalado em $HOME/.local/bin/jarvis"
