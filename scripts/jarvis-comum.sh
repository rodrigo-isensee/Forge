#!/usr/bin/env bash
# shellcheck shell=bash disable=SC2154
# Forge: trecho comum dos atalhos `jarvis` e `jarvis-forge` (BP3 S1): resolve o Claude Code mais novo e supervisiona a sessão.
# Não roda sozinho: os atalhos o carregam com `source` (arquivo ao lado do script) e definem antes `prefixo` e `rotulo`.
# CLAUDE-ATUAL-INICIO (BP3 S1, D1 do dono): o atalho abre sempre o Claude Code mais novo entre o do instalador oficial
# ($HOME/.local/bin/claude, que a atualização automática mantém) e o primeiro do PATH, nunca o do PATH só por ser o primeiro:
# um binário velho num diretório do sistema (por exemplo /usr/local/bin) vem antes e abriria uma versão atrasada.
# Só caminho absoluto de arquivo executável (nunca o diretório atual); iguais pelo caminho real contam uma vez; com um só
# candidato não roda nada; com dois, `--version` de cada um (10 s) e vence o maior número, o empate fica com o do instalador.
# Sem versão legível em nenhum, ou se o primeiro do PATH não responde `--version`, fica o `command -v claude` de sempre (nada
# que não se possa comparar o troca). Roda a cada abertura e a cada reabertura.
# Resultado em claude_bin (e claude_versao, quando conhecida); sem nenhum claude, claude_bin fica vazio.
resolver_claude() {
  local c real dir v vistos="
" maior="" primeiro primeiro_real v_primeiro=""
  local -a candidatos=() unicos=()
  claude_bin=""; claude_versao=""
  primeiro="$(command -v claude 2>/dev/null || true)"
  primeiro_real="$(readlink -f "$primeiro" 2>/dev/null || true)"
  [ -x "$HOME/.local/bin/claude" ] && [ -f "$HOME/.local/bin/claude" ] && candidatos+=("$HOME/.local/bin/claude")
  case "$primeiro" in /*) [ -x "$primeiro" ] && [ -f "$primeiro" ] && candidatos+=("$primeiro") ;; esac
  for c in ${candidatos[@]+"${candidatos[@]}"}; do
    real="$(readlink -f "$c" 2>/dev/null || printf '%s' "$c")"
    case "$vistos" in *"
$real
"*) continue ;; esac
    vistos="$vistos$real
"
    unicos+=("$c")
  done
  if [ "${#unicos[@]}" -eq 1 ]; then claude_bin="${unicos[0]}"; return 0; fi
  for c in ${unicos[@]+"${unicos[@]}"}; do
    if command -v timeout >/dev/null 2>&1; then
      v="$(timeout 10 "$c" --version </dev/null 2>/dev/null | grep -oE '^[0-9]+(\.[0-9]+)+' | head -n 1 || true)"
    else
      v="$("$c" --version </dev/null 2>/dev/null | grep -oE '^[0-9]+(\.[0-9]+)+' | head -n 1 || true)"
    fi
    [ -n "$v" ] || continue
    if [ -n "$primeiro_real" ] && [ "$(readlink -f "$c" 2>/dev/null || true)" = "$primeiro_real" ]; then v_primeiro="$v"; fi
    if [ -z "$maior" ] || [ "$(printf '%s\n%s\n' "$maior" "$v" | sort -V | tail -n 1)" != "$maior" ]; then
      maior="$v"; claude_bin="$c"; claude_versao="$v"
    fi
  done
  if [ -z "$claude_bin" ] || [ -z "$v_primeiro" ]; then claude_bin="$primeiro"; claude_versao=""; fi
  if [ -n "$claude_versao" ] && [ "$claude_bin" != "$primeiro" ]; then
    echo "$prefixo: usando o Claude Code $claude_versao ($claude_bin); o primeiro do PATH é outro e mais antigo." >&2
  fi
  return 0
}
# CLAUDE-ATUAL-FIM
# SUPERVISOR-INICIO (BP3 S1, D1 do dono): dentro do tmux o atalho não entrega o processo ao claude: roda-o e olha como saiu.
# Reabre (`--continue`, sempre com o Claude Code atual, resolvido de novo) só em saída anormal: código 128 ou mais, fora 129
# (terminal fechado), 130 (Ctrl+C) e 143 (kill de propósito: a parada de emergência tem de parar); 0 (/exit) e qualquer código abaixo de 128 (erro de uso) encerram como antes. Espera
# FORGE_QUEDA_ESPERA s (padrão 10) e conta as reaberturas na janela de FORGE_QUEDA_JANELA s (padrão 1800, 30 min): a 4.ª queda
# na janela, depois de 3 reaberturas, não reabre mais, avisa e deixa a janela esperando um Enter. O modo de permissão não muda
# (`--permission-mode auto`): a ação destrutiva segue perguntando. Cada queda vira uma linha em quedas.log, só com data,
# projeto, código de saída e número da tentativa (nunca texto do claude).
quedas_teto=3
registrar_queda() {
  local base dir
  case "${XDG_STATE_HOME:-}" in /*) base="$XDG_STATE_HOME" ;; *) base="$HOME/.local/state" ;; esac
  dir="$base/forge"
  mkdir -p "$dir" 2>/dev/null || return 0
  printf '%s projeto=%s saida=%s tentativa=%s acao=%s\n' "$(date +%Y-%m-%dT%H:%M:%S%z)" "$rotulo" "$1" "$2" "$3" >> "$dir/quedas.log" 2>/dev/null || true
}
supervisionar() {
  local rc espera janela agora t
  local -a recentes=() mantidas=()
  espera="${FORGE_QUEDA_ESPERA:-10}"; janela="${FORGE_QUEDA_JANELA:-1800}"
  case "$espera" in ''|*[!0-9]*) espera=10 ;; esac
  case "$janela" in ''|*[!0-9]*) janela=1800 ;; esac
  case "$janela" in *[1-9]*) ;; *) janela=1800 ;; esac  # 0 tiraria o teto de reaberturas
  while :; do
    resolver_claude
    if [ -z "$claude_bin" ]; then echo "$prefixo: claude não encontrado no PATH." >&2; return 127; fi
    rc=0
    "$claude_bin" "$@" || rc=$?
    if [ "$rc" -lt 128 ] || [ "$rc" = 129 ] || [ "$rc" = 130 ] || [ "$rc" = 143 ]; then return "$rc"; fi
    agora="$(date +%s)"
    mantidas=()
    for t in ${recentes[@]+"${recentes[@]}"}; do
      if [ $((agora - t)) -lt "$janela" ]; then mantidas+=("$t"); fi
    done
    recentes=(${mantidas[@]+"${mantidas[@]}"})
    if [ "${#recentes[@]}" -ge "$quedas_teto" ]; then
      registrar_queda "$rc" "$quedas_teto" desiste
      echo "$prefixo: o Jarvis caiu de novo (saída $rc) depois de $quedas_teto reaberturas em $((janela / 60)) min; não reabro mais. Veja o registro em ${XDG_STATE_HOME:-~/.local/state}/forge/quedas.log." >&2
      if [ -t 0 ]; then read -r -p "Enter para fechar esta janela " _ || true; fi
      return "$rc"
    fi
    recentes+=("$agora")
    registrar_queda "$rc" "${#recentes[@]}" reabre
    echo "$prefixo: o Jarvis caiu (saída $rc); reabrindo em ${espera}s (reabertura ${#recentes[@]} de $quedas_teto em $((janela / 60)) min)." >&2
    sleep "$espera"
    if [ "${1:-}" != --continue ]; then set -- --continue "$@"; fi
  done
}
# SUPERVISOR-FIM
