#!/usr/bin/env bash
# Grava (ou mescla) a chave "env" em .claude/settings.local.json, que o git ignora.
# Caminhos de cache vêm de ${TMPDIR:-/tmp} e do UID; credencial via gh, sem token no arquivo.
# Idempotente: preserva o que já existe no arquivo. Uso: configurar-ambiente-local.sh [raiz-do-repo]
set -euo pipefail

raiz="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
destino="$raiz/.claude/settings.local.json"
cache="${TMPDIR:-/tmp}/claude-$(id -u)/cache"

mkdir -p "$raiz/.claude"
CACHE="$cache" DESTINO="$destino" python3 -c '
import json, os
destino, cache = os.environ["DESTINO"], os.environ["CACHE"]
try:
    with open(destino) as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}
cfg.setdefault("env", {}).update({
    "npm_config_cache": cache + "/pacotes-js",
    "XDG_CACHE_HOME": cache + "/xdg",
    "PIP_CACHE_DIR": cache + "/pip",
    "PLAYWRIGHT_BROWSERS_PATH": cache + "/playwright",
    "GIT_CONFIG_COUNT": "3",
    "GIT_CONFIG_KEY_0": "url.https://github.com/.insteadOf",
    "GIT_CONFIG_VALUE_0": "git@github.com:",
    "GIT_CONFIG_KEY_1": "credential.https://github.com.helper",
    "GIT_CONFIG_VALUE_1": "",
    "GIT_CONFIG_KEY_2": "credential.https://github.com.helper",
    "GIT_CONFIG_VALUE_2": "!gh auth git-credential",
    "GIT_TERMINAL_PROMPT": "0",
})
with open(destino, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")
'

ignorado="/.claude/settings.local.json"
touch "$raiz/.gitignore"
grep -qxF "$ignorado" "$raiz/.gitignore" || printf '%s\n' "$ignorado" >> "$raiz/.gitignore"
echo "Ambiente local gravado em $destino (reinicie a sessão do Claude)."
