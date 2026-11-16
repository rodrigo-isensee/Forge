#!/usr/bin/env bash
# Forge: instala os comandos `jarvis`, `jarvis-forge` e `forge` em ~/.local/bin e garante esse diretório no PATH do bash.
# Cada um é um TRAMPOLIM (ADR 0017, âncora): um script curto que, a cada uso, lê o installPath ativo do escopo do usuário em
# ~/.claude/plugins/installed_plugins.json e executa dali o script do plugin (scripts/jarvis, scripts/jarvis-forge, bin/forge).
# Nunca a maior versão do cache (pode ser pasta órfã) nem o work tree: o atalho segue o plugin que o Claude Code ativou, e uma
# atualização do plugin vale na próxima abertura sem reinstalar nada. Sem plugin ativo, diz o comando de instalação e sai com 1.
set -euo pipefail
mkdir -p "$HOME/.local/bin"
temporario="$(mktemp)"
trap 'rm -f "$temporario"' EXIT
# Modelo do trampolim: aspas simples no heredoc, nada é expandido aqui; @NOME@ e @RELATIVO@ são trocados abaixo.
modelo="$(cat <<'MODELO'
#!/usr/bin/env bash
# Forge: trampolim `@NOME@` (instalado por scripts/instalar-atalho.sh); executa @RELATIVO@ do installPath ativo do plugin.
set -euo pipefail
alvo="$(python3 -I -c 'import json, os, sys
casa = os.path.realpath(os.path.expanduser("~"))
cache = os.path.join(casa, ".claude", "plugins", "cache")
try:
    with open(os.path.join(casa, ".claude", "plugins", "installed_plugins.json"), encoding="utf-8") as f:
        itens = json.load(f)["plugins"]["forge@forge"]
    ativos = [i["installPath"] for i in itens if i.get("scope") == "user" and isinstance(i.get("installPath"), str)]
    real = os.path.realpath(ativos[-1])
    if os.path.isabs(ativos[-1]) and real.startswith(cache + os.sep):
        print(os.path.join(real, sys.argv[1]))
except (OSError, ValueError, KeyError, TypeError, IndexError):
    pass' '@RELATIVO@' 2>/dev/null || true)"
if [ -z "$alvo" ] || [ ! -x "$alvo" ]; then
  echo "@NOME@: não achei o plugin do Forge ativo; instale com: claude plugin install forge@forge" >&2
  exit 1
fi
exec "$alvo" "$@"
MODELO
)"
for par in "jarvis:scripts/jarvis" "jarvis-forge:scripts/jarvis-forge" "forge:bin/forge"; do
  nome="${par%%:*}"
  relativo="${par#*:}"
  modelo_do_atalho="${modelo//@NOME@/$nome}"
  printf '%s\n' "${modelo_do_atalho//@RELATIVO@/$relativo}" > "$temporario"
  install -m 0755 "$temporario" "$HOME/.local/bin/$nome"
  echo "$nome instalado em $HOME/.local/bin/$nome (segue o plugin ativo)"
done
if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
  # shellcheck disable=SC2016 # $HOME e $PATH devem ir literais para o .bashrc
  printf '\n# atalhos pessoais (jarvis e forge)\nexport PATH="$HOME/.local/bin:$PATH"\n' >> "$HOME/.bashrc"
fi
