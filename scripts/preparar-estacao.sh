#!/usr/bin/env bash
# Forge: prepara do zero uma estação WSL (Ubuntu 24.04) para trabalhar com o Forge. Idempotente:
# só faz o que falta. Uso: preparar-estacao.sh [--simular] [--container]   (--simular só imprime o que faria)
#   --container  refaz, depois de o container ser recriado, o que vive fora de /workspaces e ~/.claude (gh, tmux,
#                ~/Forge, a área ~/.forge-contrib, o login do gh, a cópia vigente e o dev-marketplace); o
#                .devcontainer/devcontainer.json o roda a cada início. Saída: linhas "fez:", "falta:" e "conflito:".
set -euo pipefail

simular=0
container=0
for arg in "$@"; do
  case "$arg" in
    --simular) simular=1 ;;
    --container) container=1 ;;
    *) echo "uso: $0 [--simular] [--container]" >&2; exit 2 ;;
  esac
done

REPO="rodrigo-isensee/Forge"
DESTINO="$HOME/Forge"
NVM_VERSAO="v0.40.3"
NODE_LTS="24"

passo() { printf '\n==> %s\n' "$*"; }
# executa, ou só imprime com --simular
fazer() {
  if [ "$simular" = 1 ]; then printf '[simular] %s\n' "$*"; else "$@"; fi
}
tem() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------------------------------------------------------
# Modo --container (P9 da 0.43.1). Só /workspaces, ~/.claude e ~/.vscode-server sobrevivem à recriação; o resto do
# home some. Por isso a área de trabalho fica em $FORGE_PERSISTENTE/.forge-contrib (diretório real) com o link
# ~/.forge-contrib, e a configuração do gh em ~/.claude/gh com o link ~/.config/gh. Nunca apaga dados: um diretório
# real no home é movido para o lugar persistente; se os dois existirem, não mexe em nenhum e sai com 1.
# Variáveis (os testes as usam): FORGE_PERSISTENTE (padrão /workspaces), FORGE_ORIGEM (padrão
# $FORGE_PERSISTENTE/Forge), FORGE_CONTRIB_REPO (padrão rodrigo-isensee/forge-contrib) e XDG_DATA_HOME.
feitos=()
faltas=()
conflitos=()
fez() { feitos+=("$*"); }
falta() { faltas+=("$*"); }
conflito() { conflitos+=("$*"); }
como_root() {
  if [ "$(id -u)" = 0 ]; then fazer "$@"; else fazer sudo "$@"; fi
}

# GH-VERSAO-MINIMA: o gh do apt do Ubuntu (2.45) não tem `gh pr checks --json`, que o forge-fechar usa; a estação exige >= 2.47.
GH_MINIMO="2.47"
# gh_versao_ok: rc 0 se o gh existe e a versão é >= GH_MINIMO (maior.menor); versão ilegível conta como antiga.
gh_versao_ok() {
  local v maior menor
  tem gh || return 1
  v="$(gh --version 2>/dev/null | sed -n '1s/^gh version \([0-9][0-9]*\.[0-9][0-9]*\).*/\1/p')"
  [[ "$v" =~ ^[0-9]+\.[0-9]+$ ]] || return 1
  maior="${v%%.*}"; menor="${v#*.}"
  [ "$maior" -gt "${GH_MINIMO%%.*}" ] || { [ "$maior" -eq "${GH_MINIMO%%.*}" ] && [ "$menor" -ge "${GH_MINIMO#*.}" ]; }
}

# garantir_gh: gh >= GH_MINIMO, instalado ou atualizado pelo apt oficial do GitHub CLI (o do Ubuntu é antigo). Registra com fez/falta.
garantir_gh() {
  local chave lista tmp
  if gh_versao_ok; then fez "gh $(gh --version | sed -n '1s/^gh version \([^ ]*\).*/\1/p') (>= $GH_MINIMO)"; return 0; fi
  if ! tem curl || ! tem apt-get; then falta "instalar o gh >= $GH_MINIMO (sem curl ou apt-get aqui)"; return 0; fi
  chave=/etc/apt/keyrings/githubcli-archive-keyring.gpg
  lista=/etc/apt/sources.list.d/github-cli.list
  if [ ! -s "$lista" ]; then
    tmp="$(mktemp -d)"
    if fazer curl -fsSL -o "$tmp/chave.gpg" https://cli.github.com/packages/githubcli-archive-keyring.gpg; then
      printf 'deb [arch=%s signed-by=%s] https://cli.github.com/packages stable main\n' \
        "$(dpkg --print-architecture)" "$chave" > "$tmp/github-cli.list"
      como_root install -D -m 644 "$tmp/chave.gpg" "$chave"
      como_root install -D -m 644 "$tmp/github-cli.list" "$lista"
    fi
    rm -rf "$tmp"
  fi
  if como_root apt-get update -qq && como_root apt-get install -y -qq gh; then
    hash -r
    if [ "$simular" = 1 ] || gh_versao_ok; then fez "instalou o gh >= $GH_MINIMO (repositório oficial)"
    else falta "o gh instalado segue abaixo do $GH_MINIMO; confira o repositório $lista"; fi
  else
    falta "instalar o gh >= $GH_MINIMO (o apt falhou; rode de novo com rede)"
  fi
}

# Instala tmux e shellcheck se faltarem; o gh vem do apt oficial do GitHub CLI (garantir_gh).
container_pacotes() {
  local faltam=() p
  garantir_gh
  for p in tmux shellcheck; do tem "$p" || faltam+=("$p"); done
  if [ ${#faltam[@]} -eq 0 ]; then fez "tmux e shellcheck já instalados"; return 0; fi
  if ! tem apt-get; then falta "instalar ${faltam[*]} (sem apt-get aqui)"; return 0; fi
  if como_root apt-get update -qq && como_root apt-get install -y -qq "${faltam[@]}"; then
    fez "instalou ${faltam[*]}"
  else
    falta "instalar ${faltam[*]} (o apt falhou; rode de novo com rede)"
  fi
}

# Garante que $1 (no home) seja link para $2 (persistente). $3 = nome; $4 = 1 cria $2 vazio (0700) se faltar.
# Diretório real em $1 é movido para $2 (o mv entre discos copia e só remove a origem se a cópia der certo).
persistir() {
  local link="$1" real="$2" nome="$3" criar="${4:-0}"
  if [ -L "$link" ]; then
    if [ -e "$real" ] && [ "$(readlink -f "$link")" = "$(readlink -f "$real")" ]; then
      fez "$nome: $link já aponta para $real"; return 0
    fi
    if [ "$(readlink "$link")" = "$real" ]; then  # link certo, destino ainda por criar (ou clonar)
      if [ "$criar" = 1 ]; then fazer mkdir -p -m 700 "$real"; fez "$nome: criou $real"; fi
      return 0
    fi
    conflito "$nome: $link é link para $(readlink "$link"), não para $real; não mexi"; return 1
  fi
  if [ -e "$link" ] && [ ! -d "$link" ]; then
    conflito "$nome: $link existe e não é diretório; não mexi"; return 1
  fi
  if [ -d "$link" ]; then
    if [ -e "$real" ] || [ -L "$real" ]; then
      if [ "$simular" = 0 ] && rmdir "$link" 2>/dev/null; then
        :  # o do home estava vazio: nada se perde
      else
        conflito "$nome: existem $link e $real; não mexi em nenhum dos dois (junte à mão e rode de novo)"; return 1
      fi
    else
      fazer mkdir -p "$(dirname "$real")"
      fazer mv "$link" "$real"
      fez "$nome: moveu $link para $real"
    fi
  fi
  if [ ! -e "$real" ]; then
    [ "$criar" = 1 ] || return 0
    fazer mkdir -p -m 700 "$real"
  fi
  fazer mkdir -p "$(dirname "$link")"
  fazer ln -s "$real" "$link"
  fez "$nome: $link -> $real"
}

container_forge() {
  local link="$HOME/Forge"
  if [ -L "$link" ] && [ "$(readlink -f "$link")" = "$(readlink -f "$origem")" ]; then
    fez "$link já aponta para $origem"
  elif [ -e "$link" ] || [ -L "$link" ]; then
    fez "$link já existe e não é link para $origem; mantido"
  elif [ -d "$origem" ]; then
    fazer ln -s "$origem" "$link"
    fez "$link -> $origem"
  else
    falta "o repositório $origem não existe"
  fi
}

logado=0
# S-17/WORKFLOW-SCOPE: além do login, o token precisa dos escopos repo e workflow (sem workflow, o push que muda
# .github/ é recusado no fim). Sem a linha "Token scopes" (token de escopo fino), não adivinha.
container_escopos() {
  local saida linha e faltam=()
  saida="$(gh auth status 2>&1)" || return 0
  linha="$(printf '%s\n' "$saida" | command grep -m1 'Token scopes:')" || return 0
  for e in repo workflow; do
    [[ "$linha" == *"'$e'"* ]] || faltam+=("$e")
  done
  if [ ${#faltam[@]} -gt 0 ]; then
    falta "escopo do gh sem ${faltam[*]}: rode gh auth refresh -h github.com -s repo,workflow e depois este script de novo"
  fi
}

container_login() {
  if tem gh && gh auth status >/dev/null 2>&1; then
    logado=1
    fazer gh auth setup-git >/dev/null 2>&1 || true
    fez "gh com login (credencial em $HOME/.claude/gh)"
    container_escopos
  else
    falta "login do gh: rode gh auth login -s repo,workflow --web e depois este script de novo"
  fi
}

container_area() {
  local real="$persistente/.forge-contrib" link="$HOME/.forge-contrib"
  persistir "$link" "$real" "área de trabalho" 0 || return 0
  [ -e "$real" ] && return 0
  if [ "$logado" = 1 ] && fazer gh repo clone "$FORGE_CONTRIB_REPO" "$real" >/dev/null 2>&1; then
    fez "clonou $FORGE_CONTRIB_REPO em $real"
    persistir "$link" "$real" "área de trabalho" 0 || true
  elif [ "$logado" = 1 ]; then
    falta "clonar $FORGE_CONTRIB_REPO em $real (o gh repo clone falhou)"
  else
    falta "área de trabalho: clonar $FORGE_CONTRIB_REPO depois do login do gh"
  fi
}

container_vigente() {
  local saida
  if saida="$(fazer bash "$origem/scripts/jarvis-forge" --atualizar-vigente 2>&1)"; then
    fez "cópia vigente em dia ($dados/forge/vigente)"
  else
    falta "cópia vigente: $(printf '%s\n' "$saida" | tail -n 1)"
  fi
}

# Os links de $1 cujo alvo resolvido sai de $1, separados por espaço (vazio: nenhum).
links_fora() {
  local raiz alvo l saida=""
  raiz="$(realpath "$1")"
  while IFS= read -r -d '' l; do
    alvo="$(realpath -m "$l")"
    case "$alvo" in "$raiz"/*) ;; *) saida="$saida${saida:+ }${l#"$1"/}" ;; esac
  done < <(find "$1" -type l -print0)
  printf '%s' "$saida"
}

# O forge-dev no marketplace é CÓPIA de vigente/dev: link é recusado pelo Claude ("Path escapes plugin directory").
container_marketplace() {
  local mk="$dados/forge/dev-marketplace" dev="$dados/forge/vigente/dev" json
  if [ ! -d "$dev" ] && [ "$simular" = 0 ]; then falta "dev-marketplace: falta a cópia vigente"; return 0; fi
  json='{
  "name": "forge-dev-local",
  "owner": { "name": "Forge" },
  "plugins": [
    { "name": "forge-dev", "source": "./forge-dev", "description": "Forge, desenvolvimento da fábrica: agentes que só a sessão do Forge carrega (AQ)." }
  ]
}'
  if [ "$simular" = 1 ]; then
    printf '[simular] gravar %s e copiar %s para %s\n' "$mk/.claude-plugin/marketplace.json" "$dev" "$mk/forge-dev"
  else
    mkdir -p "$mk/.claude-plugin"
    printf '%s\n' "$json" > "$mk/.claude-plugin/marketplace.json"
    # forge-dev é derivado da cópia vigente (refeito a cada vez): trocar não perde dado.
    # L3 (review de segurança da 0.43.1): nada de seguir link; link em dev/ que sai da pasta recusa a cópia inteira.
    local fora
    fora="$(links_fora "$dev")"
    if [ -n "$fora" ]; then falta "dev-marketplace: link que sai de vigente/dev ($fora); nada copiado"; return 0; fi
    rm -rf "$mk/forge-dev.novo"
    cp -rP "$dev" "$mk/forge-dev.novo"
    if [ -L "$mk/forge-dev" ]; then rm -f "$mk/forge-dev"; else rm -rf "$mk/forge-dev"; fi
    mv "$mk/forge-dev.novo" "$mk/forge-dev"
  fi
  fez "dev-marketplace forge-dev-local com cópia de vigente/dev"
  if ! tem claude; then falta "rodar claude plugin marketplace update forge-dev-local (claude não instalado)"; return 0; fi
  if fazer claude plugin marketplace update forge-dev-local >/dev/null 2>&1; then
    fez "claude plugin marketplace update forge-dev-local"
  else
    falta "registrar o marketplace: claude plugin marketplace add $mk"
  fi
}

preparar_container() {
  persistente="${FORGE_PERSISTENTE:-/workspaces}"
  origem="${FORGE_ORIGEM:-$persistente/Forge}"
  FORGE_CONTRIB_REPO="${FORGE_CONTRIB_REPO:-rodrigo-isensee/forge-contrib}"
  dados="${XDG_DATA_HOME:-$HOME/.local/share}"
  container_pacotes
  persistir "$HOME/.config/gh" "$HOME/.claude/gh" "configuração do gh" 1 || true
  container_forge
  container_login
  container_area
  container_vigente
  container_marketplace
  local l
  for l in "${feitos[@]}"; do printf 'fez: %s\n' "$l"; done
  for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
  for l in "${conflitos[@]}"; do printf 'conflito: %s\n' "$l" >&2; done
  [ "$simular" = 1 ] && echo "(simulação: nada foi alterado)"
  [ ${#conflitos[@]} -eq 0 ]
}

if [ "$container" = 1 ]; then
  preparar_container
  exit $?
fi

passo "Sistema"
if [ -r /etc/os-release ] && command grep -q '^ID=ubuntu' /etc/os-release && command grep -qi microsoft /proc/version 2>/dev/null; then
  echo "Ubuntu em WSL: ok."
else
  echo "aviso: não parece Ubuntu em WSL; seguindo mesmo assim (o apt é necessário)." >&2
fi

passo "Pacotes do sistema (apt)"
faltam=()
for pacote in git tmux curl ca-certificates unzip python3 shellcheck jq bubblewrap socat; do
  if ! dpkg-query -W -f='${Status}' "$pacote" 2>/dev/null | command grep -q '^install ok installed'; then
    faltam+=("$pacote")
  fi
done
if [ ${#faltam[@]} -gt 0 ]; then
  echo "faltam: ${faltam[*]}"
  fazer sudo apt-get update
  fazer sudo apt-get install -y "${faltam[@]}"
else
  echo "todos já instalados."
fi

passo "GitHub CLI (gh >= $GH_MINIMO, repositório oficial)"
garantir_gh
for l in "${feitos[@]}"; do printf 'fez: %s\n' "$l"; done
for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
feitos=(); faltas=()

passo "Node $NODE_LTS (nvm) e pnpm"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  if [ "$simular" = 1 ]; then
    echo "[simular] curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSAO/install.sh | bash"
  else
    curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSAO/install.sh" | bash
  fi
fi
if [ -s "$NVM_DIR/nvm.sh" ]; then
  set +u
  # shellcheck disable=SC1091 # o nvm.sh só existe na máquina de destino
  . "$NVM_DIR/nvm.sh"
  set -u
  if nvm ls "$NODE_LTS" >/dev/null 2>&1; then
    echo "Node $NODE_LTS já instalado."
  else
    fazer nvm install "$NODE_LTS"
  fi
  fazer nvm alias default "$NODE_LTS"
  fazer nvm use "$NODE_LTS"
elif [ "$simular" = 1 ]; then
  echo "[simular] nvm install $NODE_LTS; nvm alias default $NODE_LTS"
else
  echo "erro: o nvm não foi instalado." >&2; exit 1
fi
if [ "$simular" = 1 ]; then
  echo "[simular] corepack enable && corepack prepare pnpm@latest --activate"
elif tem corepack; then
  corepack enable
  corepack prepare pnpm@latest --activate
else
  echo "aviso: corepack indisponível; instale o pnpm manualmente." >&2
fi

passo "Claude Code"
if tem claude; then
  echo "claude já instalado."
elif [ "$simular" = 1 ]; then
  echo "[simular] curl -fsSL https://claude.ai/install.sh | bash"
else
  curl -fsSL https://claude.ai/install.sh | bash
fi
export PATH="$HOME/.local/bin:$PATH"

passo "Repositório Forge em $DESTINO"
if [ -d "$DESTINO/.git" ]; then
  echo "já clonado."
elif [ "$simular" = 1 ]; then
  echo "[simular] gh auth status (exige login)"
  echo "[simular] gh repo clone $REPO $DESTINO"
else
  if ! gh auth status >/dev/null 2>&1; then
    echo "erro: o gh não está autenticado. Rode 'gh auth login' e execute este script de novo." >&2
    exit 1
  fi
  gh repo clone "$REPO" "$DESTINO"
fi
if [ -d "$DESTINO/.git" ]; then
  fazer git -C "$DESTINO" config core.hooksPath .githooks
elif [ "$simular" = 1 ]; then
  echo "[simular] git -C $DESTINO config core.hooksPath .githooks"
else
  echo "erro: $DESTINO não é um clone do Forge." >&2; exit 1
fi

passo "Identidade do git"
nome="$(git config --global user.name || true)"
email="$(git config --global user.email || true)"
if [ -n "$nome" ] && [ -n "$email" ]; then
  echo "git: $nome <$email>"
elif [ "$simular" = 1 ]; then
  echo "[simular] pedir user.name e user.email e gravar com git config --global"
elif [ -t 0 ]; then
  [ -n "$nome" ] || { read -r -p "Seu nome para os commits: " nome; git config --global user.name "$nome"; }
  [ -n "$email" ] || { read -r -p "Seu e-mail para os commits: " email; git config --global user.email "$email"; }
else
  echo "erro: defina a identidade e rode de novo: git config --global user.name 'Nome'; git config --global user.email 'e-mail'" >&2
  exit 1
fi

passo "Plugin do Forge no Claude Code"
if tem claude; then
  if claude plugin list 2>/dev/null | command grep -q 'forge@forge'; then
    echo "plugin forge@forge já instalado."
  else
    fazer claude plugin marketplace add "$REPO" || echo "aviso: marketplace já registrado ou indisponível; seguindo." >&2
    fazer claude plugin install forge@forge --scope user || echo "aviso: não foi possível instalar o plugin agora." >&2
  fi
elif [ "$simular" = 1 ]; then
  echo "[simular] claude plugin marketplace add $REPO"
  echo "[simular] claude plugin install forge@forge --scope user"
else
  echo "erro: o claude não foi instalado; rode o script de novo." >&2; exit 1
fi

passo "Atalhos (jarvis e jarvis-forge)"
if [ -x "$DESTINO/scripts/instalar-atalho.sh" ]; then
  fazer bash "$DESTINO/scripts/instalar-atalho.sh"
elif [ "$simular" = 1 ]; then
  echo "[simular] bash $DESTINO/scripts/instalar-atalho.sh"
else
  echo "erro: $DESTINO/scripts/instalar-atalho.sh não encontrado." >&2; exit 1
fi

passo "Docker"
if tem docker; then
  echo "docker encontrado."
else
  echo "docker não instalado (o script não o instala). Se o projeto precisar, ative a integração do Docker Desktop com este WSL."
fi

passo "O que falta fazer à mão"
cat <<'FIM'
1. Abra um terminal novo (para carregar PATH e nvm), rode `claude --permission-mode auto` e faça `/login`.
2. Para abrir o Jarvis: `jarvis-forge` (no Forge) ou `jarvis <projeto>`; roda no tmux, em `--permission-mode auto`, e aparece em claude.ai/code. Quem abrir o `claude` à mão usa `--permission-mode auto`.
3. Opcional, plugin do Telegram: lembre que o bot só aceita UMA sessão por vez, em todas as máquinas.
4. Credenciais (gh, claude, Telegram) não são copiadas entre máquinas: cada estação faz o próprio login.
FIM
[ "$simular" = 1 ] && echo "(simulação: nada foi alterado)"
exit 0
