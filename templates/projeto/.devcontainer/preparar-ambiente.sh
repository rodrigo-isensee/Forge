#!/usr/bin/env bash
# Preparo do container do projeto (E2.54). Idempotente, nunca apaga dados. Uso: preparar-ambiente.sh [--verificar]
#   (sem opção)  faz o que falta: gh (apt oficial), tmux (apt do sistema), Claude Code atual (instalador oficial, em ~/.local/bin), link ~/.forge-contrib para
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
# Impressão digital da chave do repositório apt do gh (chave ativa do keyring oficial, conferida em 2026-11-15); trocada
# pelo GitHub, a conferência falha fechada e nada é instalado.
CHAVE_GH_FPR=7F38BBB59D064DBCB3D84D725612B36462313325
chave_confere() {
  local gnupg
  tem gpg || return 1
  gnupg="$(mktemp -d)"
  if GNUPGHOME="$gnupg" gpg --batch --show-keys --with-colons "$1" 2>/dev/null | grep -q "^fpr:::::::::$CHAVE_GH_FPR:"; then
    rm -rf "$gnupg"; return 0
  fi
  rm -rf "$gnupg"; return 1
}
como_root() { if [ "$(id -u)" = 0 ]; then "$@"; else sudo "$@"; fi; }

# Claude Code atual: o home some com o container e o binário claude do PATH da imagem pode ser antigo. O instalador oficial (nativo, de
# claude.ai, sem custo) põe o binário em ~/.local/bin/claude, que se atualiza sozinho; só roda se esse binário faltar.
claude_ok() { [ -x "$HOME/.local/bin/claude" ]; }

feitos=(); faltas=()
link_ok() { [ -d "$real" ] && [ "$(readlink -f "$link")" = "$(readlink -f "$real")" ]; }
hooks_ok() { [ "$(git -C "$projeto" config --get core.hooksPath 2>/dev/null || true)" = ".githooks" ]; }

if [ "$verificar" = 1 ]; then
  tem gh || faltas+=("gh não instalado: rode $preparo")
  if tem gh && ! gh auth status >/dev/null 2>&1; then
    faltas+=("gh sem login (o login mora em ~/.claude/gh e sobrevive à recriação; falta fazê-lo uma vez): gh auth login -s repo,workflow --web e depois $preparo")
  fi
  tem tmux || faltas+=("tmux não instalado (a sessão do Jarvis não sobrevive a uma queda do terminal sem ele): rode $preparo")
  claude_ok || faltas+=("Claude Code atual ausente em $HOME/.local/bin/claude (o do PATH pode ser antigo): rode $preparo")
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
  chave="${FORGE_APT_CHAVE:-/etc/apt/keyrings/githubcli-archive-keyring.gpg}"  # FORGE_APT_*: só os testes
  lista="${FORGE_APT_LISTA:-/etc/apt/sources.list.d/github-cli.list}"
  if curl -fsSL -o "$tmp/chave.gpg" https://cli.github.com/packages/githubcli-archive-keyring.gpg && chave_confere "$tmp/chave.gpg"; then
    printf 'deb [arch=%s signed-by=%s] https://cli.github.com/packages stable main\n' "$(dpkg --print-architecture)" "$chave" > "$tmp/gh.list"
    como_root install -D -m 644 "$tmp/chave.gpg" "$chave"
    como_root install -D -m 644 "$tmp/gh.list" "$lista"
  fi
  [ -s "$lista" ] || faltas+=("chave do apt do gh não baixada ou sem a impressão digital $CHAVE_GH_FPR (ou sem gpg); não instalei o gh")
  rm -rf "$tmp"
  if [ ! -s "$lista" ]; then :
  elif como_root apt-get update -qq && como_root apt-get install -y -qq gh; then feitos+=("instalou gh")
  else faltas+=("instalar gh (o apt falhou; rode de novo com rede)"); fi
else
  faltas+=("instalar gh (sem curl ou apt-get aqui)")
fi

if tem gh && gh auth status >/dev/null 2>&1; then
  gh auth setup-git >/dev/null 2>&1 || true
  feitos+=("gh com login")
else
  faltas+=("login do gh: gh auth login -s repo,workflow --web e depois $preparo")
fi

if tem tmux; then
  feitos+=("tmux já instalado")
elif tem apt-get && como_root apt-get update -qq && como_root apt-get install -y -qq tmux; then
  feitos+=("instalou tmux")
else
  faltas+=("instalar tmux (o apt falhou ou não existe aqui; rode de novo com rede)")
fi

if claude_ok; then
  feitos+=("Claude Code já instalado em $HOME/.local/bin/claude")
elif tem curl; then
  tmp="$(mktemp -d)"
  if curl -fsSL --proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120 -o "$tmp/instalar.sh" https://claude.ai/install.sh \
     && { if tem timeout; then timeout 300 bash "$tmp/instalar.sh"; else bash "$tmp/instalar.sh"; fi; } </dev/null >/dev/null 2>&1 && claude_ok; then
    feitos+=("instalou o Claude Code atual em $HOME/.local/bin/claude")
  else
    faltas+=("instalar o Claude Code (o download ou a instalação falhou; rode de novo com rede): baixe com curl -fsSL -o instalar-claude.sh https://claude.ai/install.sh e depois rode bash instalar-claude.sh")
  fi
  rm -rf "$tmp"
else
  faltas+=("instalar o Claude Code (sem curl aqui): baixe com curl -fsSL -o instalar-claude.sh https://claude.ai/install.sh e depois rode bash instalar-claude.sh")
fi
if ! grep -qE '^[[:space:]]*export PATH=.*\.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  # shellcheck disable=SC2016 # $HOME e $PATH devem ir literais para o .bashrc
  printf '\n# claude e atalhos pessoais\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
  feitos+=("$HOME/.local/bin entrou na frente do PATH do bash")
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
