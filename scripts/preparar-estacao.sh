#!/usr/bin/env bash
# Forge: prepara do zero uma estação WSL (Ubuntu 24.04) para trabalhar com o Forge. Idempotente:
# só faz o que falta. Uso: preparar-estacao.sh [--simular]   (--simular só imprime o que faria)
set -euo pipefail

simular=0
case "${1:-}" in
  "") ;;
  --simular) simular=1 ;;
  *) echo "uso: $0 [--simular]" >&2; exit 2 ;;
esac

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

passo "Sistema"
if [ -r /etc/os-release ] && grep -q '^ID=ubuntu' /etc/os-release && grep -qi microsoft /proc/version 2>/dev/null; then
  echo "Ubuntu em WSL: ok."
else
  echo "aviso: não parece Ubuntu em WSL; seguindo mesmo assim (o apt é necessário)." >&2
fi

passo "Pacotes do sistema (apt)"
faltam=()
for pacote in git tmux curl ca-certificates unzip python3 shellcheck jq gh; do
  if ! dpkg-query -W -f='${Status}' "$pacote" 2>/dev/null | grep -q '^install ok installed'; then
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
  if claude plugin list 2>/dev/null | grep -q 'forge@forge'; then
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
1. Abra um terminal novo (para carregar PATH e nvm), rode `claude` e faça `/login`.
2. Para abrir o Jarvis: `jarvis-forge` (no Forge) ou `jarvis <projeto>`; roda no tmux e aparece em claude.ai/code.
3. Opcional, plugin do Telegram: lembre que o bot só aceita UMA sessão por vez, em todas as máquinas.
4. Credenciais (gh, claude, Telegram) não são copiadas entre máquinas: cada estação faz o próprio login.
FIM
[ "$simular" = 1 ] && echo "(simulação: nada foi alterado)"
exit 0
