#!/usr/bin/env bash
# Forge: instala os comandos `jarvis` e `jarvis-forge` em ~/.local/bin e garante esse diretório no PATH do bash.
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$HOME/.local/bin"
for atalho in jarvis jarvis-forge; do
  install -m 0755 "$raiz/scripts/$atalho" "$HOME/.local/bin/$atalho"
  echo "$atalho instalado em $HOME/.local/bin/$atalho"
done
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  # shellcheck disable=SC2016 # $HOME e $PATH devem ir literais para o .bashrc
  printf '\n# atalhos pessoais (jarvis)\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
fi
