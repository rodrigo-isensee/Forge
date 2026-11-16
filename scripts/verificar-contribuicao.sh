#!/usr/bin/env bash
# Varre o diff da ponta ($2, padrão HEAD) contra origin/develop (ou a base dada em $1) atrás de segredos
# e caminhos pessoais. Falha (código 1) se achar algo; imprime arquivo e linha, nunca o valor.
# Linhas com a marca "forge:exemplo" são exemplos e ficam de fora.
# Uso: scripts/verificar-contribuicao.sh [base] [ponta]
# forge:ponta (marca lida pelo .githooks/pre-push: este script aceita a ponta)
set -euo pipefail

base="${1:-origin/develop}"
ponta="${2:-HEAD}"
if ! git rev-parse --verify --quiet "$base" >/dev/null; then
  echo "Base '$base' não encontrada. Rode 'git fetch origin' antes." >&2
  exit 2
fi

segredos=(
  'sk-[A-Za-z0-9_-]{20,}'
  'gh[pousr]_[A-Za-z0-9]{20,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'AKIA[0-9A-Z]{16}'
  '-{5}BEGIN [A-Z ]*PRIVATE KEY'
  '(password|senha)[[:space:]]*[=:][[:space:]]*["'\'']?[^[:space:]"'\''$<{]{3,}'
)
# Caminho pessoal: /home/<nome>/ e /Users/<nome>/ (também sob /mnt/<letra>/), nome com maiúscula, ponto ou hífen;
# nome que começa com ponto ({tmp}/home/.config) ou com '<' (marcador de modelo) passa, e o home do usuário runner do CI.
pessoal='/(home|Users)/[[:alnum:]_][[:alnum:]_.-]*/'

achados=0
relatar() { echo "  $1: $2"; achados=$((achados + 1)); }

# Arquivos .env adicionados (exceto modelos .env.example).
while IFS= read -r arq; do
  case "$(basename "$arq")" in
    .env.example | .env.sample | .env.template) ;;
    .env | .env.*) relatar "$arq" "arquivo .env não pode ser versionado" ;;
  esac
done < <(git -c core.quotepath=false diff --no-color --no-ext-diff --no-textconv --name-only --diff-filter=AM "$base"..."$ponta")

# Linhas adicionadas: "arquivo<TAB>linha<TAB>texto"; nome só do cabeçalho (antes do @@), sem citar acento nem o TAB final.
linhas=$(git -c core.quotepath=false diff --no-color --no-ext-diff --no-textconv --text -U0 "$base"..."$ponta" | awk '
  /^diff --git / { arq = ""; cab = 1; next }
  cab && /^\+\+\+ b\// { arq = substr($0, 7); sub(/\t$/, "", arq); next }
  cab && /^\+\+\+ "b\// { arq = substr($0, 8, length($0) - 8); next }
  /^@@/ { cab = 0; match($0, /\+[0-9]+/); n = substr($0, RSTART + 1, RLENGTH - 1) - 1; next }
  cab { next }
  /^\+/ { n++; print (arq == "" ? "<linha não atribuída>" : arq) "\t" n "\t" substr($0, 2) }
')

while IFS=$'\t' read -r arq n texto; do
  [ -n "$arq" ] || continue
  case "$texto" in *forge:exemplo*) continue ;; esac
  for p in "${segredos[@]}"; do
    if grep -Eq -- "$p" <<<"$texto"; then relatar "$arq:$n" "possível segredo"; break; fi
  done
  if grep -Eq -- "$pessoal" <<<"${texto//\/home\/runner\//@/}"; then relatar "$arq:$n" "caminho pessoal"; fi
done <<<"$linhas"

if [ "$achados" -gt 0 ]; then
  echo "Contribuição barrada: $achados achado(s) no diff contra $base." >&2
  exit 1
fi
echo "ok: nenhum segredo nem caminho pessoal no diff contra $base."
