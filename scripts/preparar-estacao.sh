#!/usr/bin/env bash
# Forge: prepara do zero uma estação WSL (Ubuntu 24.04) para trabalhar com o Forge. Idempotente:
# só faz o que falta. Uso: preparar-estacao.sh [--simular] [--container] [--verificar]   (--simular só imprime o que faria)
#   --container  refaz, depois de o container ser recriado, o que vive fora de /workspaces e ~/.claude (gh, tmux,
#                ~/Forge, a área ~/.forge-contrib, o login do gh, core.hooksPath, a cópia vigente e o dev-marketplace);
#                o .devcontainer/devcontainer.json o roda a cada início (E2.54), sem o dono, com FORGE_PREPARO_ESSENCIAL=1
#                (só gh, link, login, clone da área e hooksPath; sem a cópia vigente nem o dev-marketplace, que executam
#                código do work tree; o comando baixa a main pelo GitHub sem o gh, nunca a cópia de trabalho). Saída: linhas "fez:", "falta:" e "conflito:".
#   --ferramentas  só instala as ferramentas dos portões (PORTAO-DEVOPS-FERRAMENTAS, abaixo), pelo dono; o preparo completo
#                da estação também as instala, o --container não (o postStart não baixa binário sem o dono).
#   --verificar  só confere (nada é alterado) gh, login, link ~/.forge-contrib e core.hooksPath; imprime "ambiente: ok"
#                ou uma linha "falta:" por item, com o comando exato, e sai com 1 (o hook SessionStart `hooks/ambiente.py` a roda
#                ao abrir e põe as linhas no contexto, para o Jarvis dá-las na 1ª mensagem).
set -euo pipefail

simular=0
container=0
verificar=0
ferramentas=0
for arg in "$@"; do
  case "$arg" in
    --simular) simular=1 ;;
    --container) container=1 ;;
    --verificar) verificar=1 ;;
    --ferramentas) ferramentas=1 ;;
    *) echo "uso: $0 [--simular] [--container] [--verificar] [--ferramentas]" >&2; exit 2 ;;
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
# Impressão digital da chave do repositório apt do gh (chave ativa do keyring oficial, conferida em 2026-11-15). Chave
# trocada pelo GitHub: a conferência falha fechada e o preparo diz o que fazer (nada é instalado sem ela).
CHAVE_GH_FPR=7F38BBB59D064DBCB3D84D725612B36462313325
chave_confere() {
  local gnupg
  tem gpg || return 1
  gnupg="$(mktemp -d)"
  if GNUPGHOME="$gnupg" gpg --batch --show-keys --with-colons "$1" 2>/dev/null | command grep -q "^fpr:::::::::$CHAVE_GH_FPR:"; then
    rm -rf "$gnupg"; return 0
  fi
  rm -rf "$gnupg"; return 1
}

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

# PORTAO-DEVOPS-FERRAMENTAS (R-CUSTO): ferramentas dos portões de devops e de segurança (skill cyber-security), só gratuitas e
# sem credencial, em ~/.local/bin. Binário só entra se o sha256 bater com as somas da mesma release (integridade do download,
# não autenticidade) e com o sha256 fixado aqui ao lado da versão: release trocada depois vira "falta:". zizmor e semgrep vêm
# do PyPI por pipx, com versão fixada. Bump de versão, soma e pacote seguem juntos pelo mesmo review. A falha de uma não barra as outras: vira
# "falta:". O trivy roda no CI (a skill manda), não aqui.
ACTIONLINT_V="1.7.12"; GITLEAKS_V="8.30.1"; OSV_V="v2.7.1"; ZIZMOR_V="1.32.0"; SEMGREP_V="1.186.0"
ACTIONLINT_SHA="8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
GITLEAKS_SHA="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
OSV_SHA="fb7dab19a8bd9bbe5c3189f09d4b7ee1820c9553a23bac202648a56efd2f6ee8"
# instalar_binario nome url url-das-somas arquivo-nas-somas sha256-fixado [binario-dentro-do-tar.gz]
instalar_binario() {
  local nome="$1" url="$2" somas="$3" arq="$4" fixo="$5" tar="${6:-}" tmp esperado real ok bin="$HOME/.local/bin"
  if tem "$nome"; then fez "$nome já instalado"; return 0; fi
  if ! tem curl; then falta "instalar $nome (sem curl)"; return 0; fi
  if [ "$simular" = 1 ]; then printf '[simular] baixar %s e conferir o sha256 em %s\n' "$url" "$somas"; fez "instalaria $nome em $bin"; return 0; fi
  tmp="$(mktemp -d)"
  if curl -fsSL -o "$tmp/$arq" "$url" && curl -fsSL -o "$tmp/somas" "$somas"; then
    esperado="$(awk -v a="$arq" '$2 == a || $2 == "*" a {print $1; exit}' "$tmp/somas")"
    real="$(sha256sum "$tmp/$arq" | cut -d' ' -f1)"
    if [ -z "$esperado" ] || [ "$real" != "$esperado" ]; then
      falta "$nome: o sha256 do download não bate com as somas da release; não instalei"
    elif [ "$real" != "$fixo" ]; then
      falta "$nome: o sha256 do download não bate com a soma fixada no script; não instalei"
    else
      mkdir -p "$bin"
      if [ -n "$tar" ]; then
        if tar -xzf "$tmp/$arq" -C "$tmp" "$tar" && install -m 755 "$tmp/$tar" "$bin/$nome"; then ok=1; else ok=0; fi
      elif install -m 755 "$tmp/$arq" "$bin/$nome"; then ok=1; else ok=0; fi
      if [ "$ok" = 1 ]; then fez "instalou $nome em $bin"; else falta "instalar $nome (a extração ou a cópia falhou; o binário não foi instalado)"; fi
    fi
  else
    falta "instalar $nome (o download falhou; rode de novo com rede)"
  fi
  rm -rf "$tmp"
}
instalar_pipx() { # nome versão
  if tem "$1"; then fez "$1 já instalado"; return 0; fi
  if ! tem pipx; then
    if tem apt-get; then como_root apt-get install -y -qq pipx >/dev/null 2>&1 || true; fi
    tem pipx || { falta "instalar $1 (sem pipx; rode sudo apt-get install pipx e de novo)"; return 0; }
  fi
  if fazer pipx install "$1==$2" >/dev/null 2>&1; then fez "instalou $1 (pipx)"; else falta "instalar $1 (o pipx falhou; rode de novo com rede)"; fi
}
garantir_ferramentas() {
  local a="https://github.com/rhysd/actionlint/releases/download/v$ACTIONLINT_V" g="https://github.com/gitleaks/gitleaks/releases/download/v$GITLEAKS_V"
  local o="https://github.com/google/osv-scanner/releases/download/$OSV_V"
  case "$(uname -m)" in x86_64) ;; *) falta "ferramentas dos portões: só x86_64 é coberto aqui; instale à mão"; return 0 ;; esac
  instalar_binario actionlint "$a/actionlint_${ACTIONLINT_V}_linux_amd64.tar.gz" "$a/actionlint_${ACTIONLINT_V}_checksums.txt" "actionlint_${ACTIONLINT_V}_linux_amd64.tar.gz" "$ACTIONLINT_SHA" actionlint
  instalar_binario gitleaks "$g/gitleaks_${GITLEAKS_V}_linux_x64.tar.gz" "$g/gitleaks_${GITLEAKS_V}_checksums.txt" "gitleaks_${GITLEAKS_V}_linux_x64.tar.gz" "$GITLEAKS_SHA" gitleaks
  instalar_binario osv-scanner "$o/osv-scanner_linux_amd64" "$o/osv-scanner_SHA256SUMS" osv-scanner_linux_amd64 "$OSV_SHA"
  instalar_pipx zizmor "$ZIZMOR_V"
  instalar_pipx semgrep "$SEMGREP_V"
}
imprimir_resultado() {
  local l
  for l in "${feitos[@]}"; do printf 'fez: %s\n' "$l"; done
  for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
  feitos=(); faltas=()
}

# GH-VERSAO-MINIMA:o gh do apt do Ubuntu (2.45) não tem `gh pr checks --json`, que o forge-fechar usa; a estação exige >= 2.47.
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
  chave="${FORGE_APT_CHAVE:-/etc/apt/keyrings/githubcli-archive-keyring.gpg}"  # FORGE_APT_*: só os testes
  lista="${FORGE_APT_LISTA:-/etc/apt/sources.list.d/github-cli.list}"
  if [ ! -s "$lista" ]; then
    tmp="$(mktemp -d)"
    if fazer curl -fsSL -o "$tmp/chave.gpg" https://cli.github.com/packages/githubcli-archive-keyring.gpg; then
      if [ "$simular" = 1 ] || chave_confere "$tmp/chave.gpg"; then
        printf 'deb [arch=%s signed-by=%s] https://cli.github.com/packages stable main\n' \
          "$(dpkg --print-architecture)" "$chave" > "$tmp/github-cli.list"
        como_root install -D -m 644 "$tmp/chave.gpg" "$chave"
        como_root install -D -m 644 "$tmp/github-cli.list" "$lista"
      else
        falta "chave do apt do gh sem a impressão digital $CHAVE_GH_FPR (ou sem gpg); não instalei: confira em https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
        rm -rf "$tmp"; return 0
      fi
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

# E119.1 (AMBIENTE-SOBREVIVE-RECRIACAO): o Claude Code atual. O home some com o container e o binário claude do PATH da imagem pode ser
# antigo; o instalador oficial (nativo, de claude.ai, sem custo) põe o binário em ~/.local/bin/claude, que se atualiza sozinho.
# Só instala se esse binário faltar (rodar duas vezes não muda nada) e garante ~/.local/bin na frente do PATH do bash. Falha
# (sem rede) vira "falta:", nunca barra o container.
claude_ok() { [ -x "$HOME/.local/bin/claude" ]; }
garantir_path_local() {
  [ "$simular" = 0 ] || return 0
  command grep -qE '^[[:space:]]*export PATH=.*\.local/bin' "$HOME/.bashrc" 2>/dev/null && return 0
  # shellcheck disable=SC2016 # $HOME e $PATH devem ir literais para o .bashrc
  printf '\n# claude e atalhos pessoais\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
  fez "$HOME/.local/bin entrou na frente do PATH do bash"
}
container_claude() {
  local tmp
  if claude_ok; then
    fez "Claude Code já instalado em $HOME/.local/bin/claude"
  elif ! tem curl; then
    falta "instalar o Claude Code (sem curl aqui): baixe com curl -fsSL -o instalar-claude.sh https://claude.ai/install.sh e depois rode bash instalar-claude.sh"
  elif [ "$simular" = 1 ]; then
    printf '[simular] baixar https://claude.ai/install.sh e rodar com bash\n'
  else
    tmp="$(mktemp -d)"
    if curl -fsSL --proto '=https' --proto-redir '=https' --connect-timeout 20 --max-time 120 -o "$tmp/instalar.sh" https://claude.ai/install.sh \
       && { if tem timeout; then timeout 300 bash "$tmp/instalar.sh"; else bash "$tmp/instalar.sh"; fi; } </dev/null >/dev/null 2>&1 && claude_ok; then
      fez "instalou o Claude Code atual em $HOME/.local/bin/claude"
    else
      falta "instalar o Claude Code (o download ou a instalação falhou; rode de novo com rede): baixe com curl -fsSL -o instalar-claude.sh https://claude.ai/install.sh e depois rode bash instalar-claude.sh"
    fi
    rm -rf "$tmp"
  fi
  garantir_path_local
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
  container_hooks
}

# E2.54: o core.hooksPath mora no .git/config do clone, que sobrevive; só refaz se faltar, e nunca troca o de outra
# ferramenta (valor diferente de .githooks fica como está, com aviso).
container_hooks() {
  { [ -d "$origem/.git" ] || [ -f "$origem/.git" ]; } || return 0
  local atual
  atual="$(git -C "$origem" config --get core.hooksPath 2>/dev/null || true)"
  if [ -n "$atual" ] && [ "$atual" != ".githooks" ]; then
    falta "core.hooksPath de $origem é $atual (de outra ferramenta); mantido"
    return 0
  fi
  [ -n "$atual" ] || fazer git -C "$origem" config core.hooksPath .githooks
  fez "core.hooksPath=.githooks em $origem"
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

# FORGE-SEMPRE-ATUAL (ADR 0017, âncora): o installPath ativo do escopo do usuário, lido de installed_plugins.json e só se estiver
# dentro de ~/.claude/plugins/cache. Imprime o caminho; nada se não há plugin ativo. Nunca o work tree nem a maior pasta do cache.
plugin_ativo() {
  tem python3 || return 0
  python3 -I -c 'import json, os
casa = os.path.realpath(os.path.expanduser("~"))
cache = os.path.join(casa, ".claude", "plugins", "cache")
try:
    with open(os.path.join(casa, ".claude", "plugins", "installed_plugins.json"), encoding="utf-8") as f:
        itens = json.load(f)["plugins"]["forge@forge"]
    ativos = [i["installPath"] for i in itens if i.get("scope") == "user" and isinstance(i.get("installPath"), str)]
    real = os.path.realpath(ativos[-1])
    if os.path.isabs(ativos[-1]) and real.startswith(cache + os.sep):
        print(real)
except (OSError, ValueError, KeyError, TypeError, IndexError):
    pass' 2>/dev/null || true
}

# Refaz os atalhos jarvis, jarvis-forge e forge em ~/.local/bin (a recriação do container apaga o home), sempre como
# trampolins, e, no preparo essencial (o postStart), roda a atualização do plugin uma vez: sem pergunta, sem barrar; o
# resultado fica no registro.log da ferramenta. Tudo do installPath ativo; sem plugin ativo, só diz o que falta.
container_atalhos_e_plugin() {
  local ativo saida
  ativo="$(plugin_ativo)"
  if [ -z "$ativo" ] || [ ! -f "$ativo/scripts/instalar-atalho.sh" ]; then
    falta "atalhos jarvis e forge: o plugin do Forge não está ativo; rode claude plugin install forge@forge --scope user e depois este script de novo"
    return 0
  fi
  if saida="$(fazer bash "$ativo/scripts/instalar-atalho.sh")"; then
    [ "$simular" = 0 ] || printf '%s\n' "$saida"
    fez "atalhos jarvis, jarvis-forge e forge em $HOME/.local/bin (seguem o plugin ativo)"
  else
    falta "atalhos: o instalar-atalho.sh falhou; rode bash $ativo/scripts/instalar-atalho.sh"
  fi
  [ "${FORGE_PREPARO_ESSENCIAL:-0}" = 1 ] || return 0
  if [ -x "$ativo/bin/forge-sempre-atual" ]; then
    # o resultado (e o motivo de uma falha) fica no registro.log da ferramenta; o postStart nunca falha por ela
    if [ "$simular" = 1 ]; then
      fazer "$ativo/bin/forge-sempre-atual" --gatilho poststart
    elif command -v timeout >/dev/null 2>&1; then
      timeout 90 "$ativo/bin/forge-sempre-atual" --gatilho poststart </dev/null >/dev/null 2>&1 || true
    else
      "$ativo/bin/forge-sempre-atual" --gatilho poststart </dev/null >/dev/null 2>&1 || true
    fi
    fez "atualização do plugin tentada no postStart (resultado em registro.log, na pasta de dados do plugin)"
  else
    fez "plugin ativo sem a ferramenta de atualização (versão anterior à 0.47); o atalho cobre na próxima atualização"
  fi
}

preparar_container() {
  persistente="${FORGE_PERSISTENTE:-/workspaces}"
  origem="${FORGE_ORIGEM:-$persistente/Forge}"
  FORGE_CONTRIB_REPO="${FORGE_CONTRIB_REPO:-rodrigo-isensee/forge-contrib}"
  dados="${XDG_DATA_HOME:-$HOME/.local/share}"
  persistir "$HOME/.config/gh" "$HOME/.claude/gh" "configuração do gh" 1 || true  # primeiro: sem ela o sandbox do Bash não abre
  container_pacotes
  container_claude
  container_forge
  container_login
  container_area
  container_atalhos_e_plugin
  if [ "${FORGE_PREPARO_ESSENCIAL:-0}" = 1 ]; then
    fez "essencial: cópia vigente e dev-marketplace ficam para o comando manual"
  else
    container_vigente
    container_marketplace
  fi
  local l
  for l in "${feitos[@]}"; do printf 'fez: %s\n' "$l"; done
  for l in "${faltas[@]}"; do printf 'falta: %s\n' "$l"; done
  for l in "${conflitos[@]}"; do printf 'conflito: %s\n' "$l" >&2; done
  [ "$simular" = 1 ] && echo "(simulação: nada foi alterado)"
  [ "$simular" = 1 ] || container_essenciais
  [ ${#conflitos[@]} -eq 0 ] && [ ${#ausentes[@]} -eq 0 ]
}

# DEVCONTAINER-SEM-GH: o que o container recriado precisa para o time trabalhar (gh, tmux, ~/.config/gh e o link
# ~/.forge-contrib). Faltou, sai com rc 1 e uma linha "erro:" na saída de erro: o postStartCommand não engole mais a falha.
ausentes=()
container_essenciais() {
  local l real="$persistente/.forge-contrib"
  tem gh || ausentes+=("gh não instalado")
  tem tmux || ausentes+=("tmux não instalado")
  [ -d "$HOME/.config/gh" ] || ausentes+=("$HOME/.config/gh ausente (o sandbox do Bash não abre sem ele)")
  if [ -d "$real" ] && [ "$(readlink -f "$HOME/.forge-contrib")" != "$(readlink -f "$real")" ]; then
    ausentes+=("link $HOME/.forge-contrib -> $real ausente")
  fi
  for l in "${ausentes[@]}"; do printf 'erro: %s; rode bash %s/scripts/preparar-estacao.sh --container\n' "$l" "$origem" >&2; done
}

# E2.54: só confere; cada falta traz o comando exato. Sai com 1 se faltar algo.
verificar_container() {
  persistente="${FORGE_PERSISTENTE:-/workspaces}"
  origem="${FORGE_ORIGEM:-$persistente/Forge}"
  local preparo="bash $origem/scripts/preparar-estacao.sh --container" real="$persistente/.forge-contrib" atual l
  local f=()
  tem gh || f+=("gh não instalado: rode $preparo")
  if tem gh && ! gh auth status >/dev/null 2>&1; then
    f+=("gh sem login (o login mora em ~/.claude/gh e sobrevive à recriação; falta fazê-lo uma vez): gh auth login -s repo,workflow --web e depois $preparo")
  fi
  claude_ok || f+=("Claude Code atual ausente em $HOME/.local/bin/claude (o do PATH pode ser antigo): rode $preparo")
  if [ ! -d "$real" ] || [ "$(readlink -f "$HOME/.forge-contrib")" != "$(readlink -f "$real")" ]; then
    f+=("link $HOME/.forge-contrib -> $real ausente ou sem destino: rode $preparo")
  fi
  if [ -d "$origem/.git" ] || [ -f "$origem/.git" ]; then
    atual="$(git -C "$origem" config --get core.hooksPath 2>/dev/null || true)"
    [ "$atual" = ".githooks" ] || f+=("core.hooksPath de $origem não é .githooks: rode $preparo")
  fi
  if [ ${#f[@]} -eq 0 ]; then echo "ambiente: ok"; return 0; fi
  for l in "${f[@]}"; do printf 'falta: %s\n' "$l"; done
  return 1
}

if [ "$verificar" = 1 ]; then
  verificar_container
  exit $?
fi

if [ "$ferramentas" = 1 ]; then
  garantir_ferramentas
  imprimir_resultado
  [ "$simular" = 1 ] && echo "(simulação: nada foi alterado)"
  exit 0
fi

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

passo "Ferramentas dos portões (actionlint, zizmor, gitleaks, osv-scanner, semgrep)"
garantir_ferramentas
imprimir_resultado

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
