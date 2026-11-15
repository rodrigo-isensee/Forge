#!/usr/bin/env bash
# Preparo do container do projeto (E2.54). Idempotente, nunca apaga dados. Uso: preparar-ambiente.sh [--verificar]
#   (sem opção)  faz o que falta: gh (apt oficial), login do gh pelo GH_TOKEN do ambiente, link ~/.forge-contrib para
#                /workspaces/.forge-contrib, core.hooksPath=.githooks. Linhas "fez:" e "falta:".
#   --verificar  só confere (nada é alterado); "ambiente: ok" ou uma linha "falta:" por item com o comando exato; sai 1 se faltar.
# Variáveis: FORGE_PROJETO (pasta do projeto; padrão a pasta acima deste script) e FORGE_PERSISTENTE (padrão /workspaces).
set -euo pipefail

verificar=0
case "${1:-}" in
  "") ;;
  --verificar) verificar=1 ;;
  *) echo "uso: $0 [--verificar]" >&2; exit 2 ;;
esac

projeto="${FORGE_PROJETO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
persistente="${FORGE_PERSISTENTE:-/workspaces}"
real="$persistente/.forge-contrib"
link="$HOME/.forge-contrib"
preparo="bash $projeto/.devcontainer/preparar-ambiente.sh"
tem() { command -v "$1" >/dev/null 2>&1; }
como_root() { if [ "$(id -u)" = 0 ]; then "$@"; else sudo "$@"; fi; }

feitos=(); faltas=()
link_ok() { [ -d "$real" ] && [ "$(readlink -f "$link")" = "$(readlink -f "$real")" ]; }
hooks_ok() { [ "$(git -C "$projeto" config --get core.hooksPath 2>/dev/null || true)" = ".githooks" ]; }

if [ "$verificar" = 1 ]; then
  tem gh || faltas+=("gh não instalado: rode $preparo")
  if tem gh && ! gh auth status >/dev/null 2>&1; then
    faltas+=("gh sem login (o GH_TOKEN não chegou ao ambiente): ponha o GH_TOKEN no ambiente do container e rode $preparo; sem token, gh auth login -s repo,workflow --web")
  fi
  link_ok || faltas+=("link $link -> $real ausente ou sem destino: rode $preparo")
  if [ -e "$projeto/.git" ]; then hooks_ok || faltas+=("core.hooksPath de $projeto não é .githooks: rode $preparo"); fi
  if [ ${#faltas[@]} -eq 0 ]; then echo "ambiente: ok"; exit 0; fi
  for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
  exit 1
fi

if tem gh; then
  feitos+=("gh já instalado")
elif tem curl && tem apt-get; then
  tmp="$(mktemp -d)"
  chave=/etc/apt/keyrings/githubcli-archive-keyring.gpg
  if curl -fsSL -o "$tmp/chave.gpg" https://cli.github.com/packages/githubcli-archive-keyring.gpg; then
    printf 'deb [arch=%s signed-by=%s] https://cli.github.com/packages stable main\n' "$(dpkg --print-architecture)" "$chave" > "$tmp/gh.list"
    como_root install -D -m 644 "$tmp/chave.gpg" "$chave"
    como_root install -D -m 644 "$tmp/gh.list" /etc/apt/sources.list.d/github-cli.list
  fi
  rm -rf "$tmp"
  if como_root apt-get update -qq && como_root apt-get install -y -qq gh; then feitos+=("instalou gh"); else faltas+=("instalar gh (o apt falhou; rode de novo com rede)"); fi
else
  faltas+=("instalar gh (sem curl ou apt-get aqui)")
fi

if tem gh && gh auth status >/dev/null 2>&1; then
  gh auth setup-git >/dev/null 2>&1 || true
  feitos+=("gh com login")
else
  faltas+=("login do gh: ponha o GH_TOKEN no ambiente do container e rode $preparo (ou gh auth login -s repo,workflow --web)")
fi

if link_ok; then
  feitos+=("$link já aponta para $real")
elif [ -L "$link" ]; then
  faltas+=("$link é link para $(readlink "$link"), não para $real; não mexi")
elif [ -e "$link" ]; then
  faltas+=("$link existe e não é link; não mexi (junte à mão em $real e rode de novo)")
else
  mkdir -p "$real"; chmod 700 "$real"
  ln -s "$real" "$link"
  feitos+=("$link -> $real")
fi

if [ -e "$projeto/.git" ]; then
  if hooks_ok; then
    feitos+=("core.hooksPath=.githooks")
  elif [ -z "$(git -C "$projeto" config --get core.hooksPath 2>/dev/null || true)" ]; then
    git -C "$projeto" config core.hooksPath .githooks
    feitos+=("core.hooksPath=.githooks")
  else
    faltas+=("core.hooksPath de $projeto é de outra ferramenta; mantido")
  fi
fi

for l in "${feitos[@]}"; do printf 'fez: %s\n' "$l"; done
for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
[ ${#faltas[@]} -eq 0 ]
