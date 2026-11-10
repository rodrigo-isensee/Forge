#!/usr/bin/env bash
# Forge: publica as releases do GitHub que faltam entre 0.43.1 e 0.44.2 (versões que foram direto para a main).
# Uso: scripts/publicar-releases-faltantes.sh [--publicar] [--de X.Y.Z] [--ate X.Y.Z] [--ref origin/main]
# Para cada versão do CHANGELOG.md na faixa sem release (`gh release view vX.Y.Z` falha), mostra o comando
#   gh release create vX.Y.Z --target <sha do commit "release: X.Y.Z" na ref> --notes-file <seção do CHANGELOG>
# (com --title "Forge vX.Y.Z" e --latest=false: a release mais nova continua marcada como Latest), da mais velha à mais nova.
# Por padrão só imprime (simulação); com --publicar, executa. Versão sem commit "release: X.Y.Z" na ref é pulada com aviso.
# Saída: 0 tudo certo; 1 algum passo falhou (commit ausente, gh que falhou); 2 uso.
set -euo pipefail

de="0.43.1"
ate="0.44.2"
ref="origin/main"
publicar=0
while [ $# -gt 0 ]; do
  case "$1" in
    --publicar) publicar=1 ;;
    --de) de="${2:?--de pede a versão}"; shift ;;
    --ate) ate="${2:?--ate pede a versão}"; shift ;;
    --ref) ref="${2:?--ref pede a ref}"; shift ;;
    -h|--help) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "publicar-releases-faltantes: opção desconhecida: $1" >&2; exit 2 ;;
  esac
  shift
done

raiz="$(git rev-parse --show-toplevel)"
changelog="$raiz/CHANGELOG.md"
notas="$(mktemp -d "${TMPDIR:-/tmp}/forge-releases-XXXXXX")"

# versão dentro de [de, ate], pela ordem de versão
na_faixa() {
  [ "$(printf '%s\n%s\n' "$de" "$1" | sort -V | head -n1)" = "$de" ] &&
    [ "$(printf '%s\n%s\n' "$1" "$ate" | sort -V | head -n1)" = "$1" ]
}

# corpo da seção "## [X.Y.Z]" do CHANGELOG, sem o título
secao() {
  awk -v v="$1" '
    /^## \[/ { dentro = (index($0, "## [" v "]") == 1); next }
    dentro { print }
  ' "$changelog"
}

# sha do commit mais recente da ref cujo assunto é exatamente "release: X.Y.Z"
sha_da_release() {
  git -C "$raiz" log "$ref" --format='%H %s' | awk -v s="release: $1" '{ sha = $1; $1 = ""; sub(/^ /, "") } $0 == s { print sha; exit }'
}

modo="simulação"
[ "$publicar" -eq 1 ] && modo="publicação"
echo "publicar-releases-faltantes ($modo): versões de $de a $ate, commits em $ref"

# sem acesso ao GitHub, toda versão pareceria sem release: para antes
if ! gh release list --limit 1 >/dev/null 2>&1; then
  echo "publicar-releases-faltantes: não consegui ler as releases (gh sem acesso ou sem login)" >&2
  exit 1
fi

rc=0
faltam=0
while read -r versao; do
  na_faixa "$versao" || continue
  if gh release view "v$versao" >/dev/null 2>&1; then
    echo "v$versao: já publicada"
    continue
  fi
  sha="$(sha_da_release "$versao")"
  if [ -z "$sha" ]; then
    echo "v$versao: sem commit \"release: $versao\" em $ref; pulada" >&2
    rc=1
    continue
  fi
  arquivo="$notas/v$versao.md"
  secao "$versao" > "$arquivo"
  faltam=$((faltam + 1))
  echo "gh release create v$versao --target $sha --notes-file $arquivo --title \"Forge v$versao\" --latest=false"
  if [ "$publicar" -eq 1 ]; then
    gh release create "v$versao" --target "$sha" --notes-file "$arquivo" --title "Forge v$versao" --latest=false || rc=1
  fi
done < <(sed -n 's/^## \[\([0-9][0-9.]*\)\].*/\1/p' "$changelog" | sort -V)

if [ "$publicar" -eq 0 ]; then
  echo "simulação: $faltam release(s) a publicar; nada foi criado (rode com --publicar para executar)"
fi
exit "$rc"
