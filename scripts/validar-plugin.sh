#!/usr/bin/env bash
# Valida o plugin (claude plugin validate --strict) numa cópia limpa em $TMPDIR.
# Motivo: com o sandbox do Bash o bubblewrap cria pontos de montagem vazios na raiz
# (.mcp.json etc.) e o validador falha neles. A cópia leva só o que o git rastreia,
# com o conteúdo atual do disco (inclui mudanças ainda não commitadas).
set -euo pipefail

raiz="$(git rev-parse --show-toplevel)"
dir="$(mktemp -d "${TMPDIR:-/tmp}/forge-validar.XXXXXX")"
trap 'rm -rf "$dir"' EXIT

cd "$raiz"
# Arquivos rastreados que sumiram do disco (apagados, ainda sem commit) ficam de fora.
git ls-files -z | while IFS= read -r -d '' f; do
  [ -e "$f" ] && printf '%s\0' "$f"
done | tar --null -T - -cf - | tar -xf - -C "$dir"

claude plugin validate "$dir" --strict
