#!/usr/bin/env bash
# Forge: instala os comandos `jarvis`, `jarvis-forge` e `forge` em ~/.local/bin e garante esse diretório no PATH do bash.
# O `forge` do terminal (ADR 0015, item 2) é um atalho que acha o bin/forge do plugin instalado (a versão mais nova do
# cache do Claude Code) e, sem plugin no cache, o desta cópia do Forge.
set -euo pipefail
raiz="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$HOME/.local/bin"
for atalho in jarvis jarvis-forge; do
  install -m 0755 "$raiz/scripts/$atalho" "$HOME/.local/bin/$atalho"
  echo "$atalho instalado em $HOME/.local/bin/$atalho"
done
temporario="$(mktemp)"
trap 'rm -f "$temporario"' EXIT
# shellcheck disable=SC2016 # o atalho expande $HOME e $alvo quando roda, não agora
{
  echo '#!/usr/bin/env bash'
  echo '# Forge: atalho `forge` do terminal (instalado por scripts/instalar-atalho.sh); executa o bin/forge do plugin.'
  echo 'set -euo pipefail'
  echo 'alvo="$(find "$HOME"/.claude/plugins/cache/*/forge/*/bin/forge -maxdepth 0 -type f 2>/dev/null | sort -V | tail -n 1 || true)"'
  printf '[ -n "$alvo" ] || alvo=%q\n' "$raiz/bin/forge"
  echo '[ -x "$alvo" ] || { echo "forge: não achei o plugin do Forge; instale com: claude plugin install forge@forge" >&2; exit 1; }'
  echo 'exec "$alvo" "$@"'
} > "$temporario"
install -m 0755 "$temporario" "$HOME/.local/bin/forge"
echo "forge instalado em $HOME/.local/bin/forge"
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  # shellcheck disable=SC2016 # $HOME e $PATH devem ir literais para o .bashrc
  printf '\n# atalhos pessoais (jarvis e forge)\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
fi
