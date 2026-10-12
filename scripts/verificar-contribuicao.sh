#!/usr/bin/env bash
# Varre o diff da branch atual contra origin/develop (ou a base dada em $1) atrás de segredos
# e caminhos pessoais. Falha (código 1) se achar algo; imprime arquivo e linha, nunca o valor.
# Linhas com a marca "forge:exemplo" são exemplos e ficam de fora.
# Uso: scripts/verificar-contribuicao.sh [base]
set -euo pipefail

base="${1:-origin/develop}"
if ! git rev-parse --verify --quiet "$base" >/dev/null; then
  echo "Base '$base' não encontrada. Rode 'git fetch origin' antes." >&2
  exit 2
fi

segredos=(
  'sk-[A-Za-z0-9_-]{20,}'
  'ghp_[A-Za-z0-9]{20,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'AKIA[0-9A-Z]{16}'
  '-{5}BEGIN [A-Z ]*PRIVATE KEY'
  '(password|senha)[[:space:]]*[=:][[:space:]]*["'\'']?[^[:space:]"'\''$<{]{3,}'
)
pessoal='/home/[a-z_][a-z0-9_-]*/'

achados=0
relatar() { echo "  $1: $2"; achados=$((achados + 1)); }

# Arquivos .env adicionados (exceto modelos .env.example).
while IFS= read -r arq; do
  case "$(basename "$arq")" in
    .env.example | .env.sample | .env.template) ;;
    .env | .env.*) relatar "$arq" "arquivo .env não pode ser versionado" ;;
  esac
done < <(git diff --name-only --diff-filter=AM "$base"...HEAD)

# Linhas adicionadas: "arquivo<TAB>linha<TAB>texto".
linhas=$(git diff -U0 "$base"...HEAD | awk '
  /^\+\+\+ b\// { arq = substr($0, 7); next }
  /^@@/ { match($0, /\+[0-9]+/); n = substr($0, RSTART + 1, RLENGTH - 1) - 1; next }
  /^\+/ { n++; print arq "\t" n "\t" substr($0, 2) }
')

while IFS=$'\t' read -r arq n texto; do
  [ -n "$arq" ] || continue
  case "$texto" in *forge:exemplo*) continue ;; esac
  for p in "${segredos[@]}"; do
    if grep -Eq -- "$p" <<<"$texto"; then relatar "$arq:$n" "possível segredo"; break; fi
  done
  if grep -Eq -- "$pessoal" <<<"$texto"; then relatar "$arq:$n" "caminho pessoal"; fi
done <<<"$linhas"

if [ "$achados" -gt 0 ]; then
  echo "Contribuição barrada: $achados achado(s) no diff contra $base." >&2
  exit 1
fi
echo "ok: nenhum segredo nem caminho pessoal no diff contra $base."
