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

# validar <pasta>: roda o validador. Com a validação passando (código 0), o "✘ Found N problem" do perfil directory (README_MISSING em dev/ etc.)
# é só aviso de quem publica no diretório: sai como "aviso do perfil directory", para o ✘ não parecer falha. Com falha, a saída fica como veio.
validar() {
  local saida rc=0
  saida="$(claude plugin validate "$1" --strict 2>&1)" || rc=$?
  if [ "$rc" = 0 ]; then
    printf '%s\n' "$saida" | sed 's/^✘ Found /aviso do perfil directory (não reprova; a validação passou): /'
  else
    printf '%s\n' "$saida"
  fi
  return "$rc"
}
validar "$dir"
# O forge-dev (pasta dev/, só da sessão do Forge) tem manifesto próprio e também é validado.
validar "$dir/dev"
