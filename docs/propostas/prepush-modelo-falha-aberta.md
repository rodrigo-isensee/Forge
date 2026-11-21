# PREPUSH-MODELO-FALHA-ABERTA: utilitário ausente no pre-push do modelo

Propósito: correção do `templates/projeto/.githooks/pre-push` pronta para o dono aplicar (a pasta `.githooks/` do modelo é travada para os agentes). Público: o dono, `tech-lead`, `security-engineer`, `qa-engineer`. Revisão: 2026-12-21.

Estado: proposta (v0478 E82.1; cartão PREPUSH-MODELO-FALHA-ABERTA, defeito de segurança, fila direta). Só aperta: com os utilitários no PATH, nada muda; o que falta barra o envio dizendo o que falta, nunca pula a checagem.

## 1. Os pontos levantados
A sonda (seção 4) tira do PATH, um por vez, cada utilitário que o hook chama. Três deixam o envio passar sem a conferência:

1. **`dirname` ausente pula a checagem do projeto** (linha 274). `local_hook="$(dirname "$0")/pre-push.local"` vira `/pre-push.local`, o `[ -x ]` falha e o envio segue com `rc=0`, sem aviso. O `pre-push.local` gerado também usa o `dirname` para achar a raiz (`cd "$(dirname "$0")/.."` vira `cd /..`, e a detecção pula o pronto rápido); a guarda no `pre-push` cobre os dois, porque ele roda antes e com o mesmo PATH.
2. **`tr` ausente desliga o limite de tempo e a barreira do órfão** (linha 94). O `lider_vivo` lê a saída de `jobs -rp` pelo `tr`; sem ele, a lista vem vazia, o laço de espera nem começa e o `wait` espera a checagem sem o `FORGE_PREPUSH_TIMEOUT` e sem conferir quem pediu o envio. Na sonda, a checagem de 4 s com limite de 1 s passa (`rc=0`).
3. **`python3` ausente pula a conferência de registros** (linha 326). Com a chave `registros` no `.forge/config.json`, o hook avisa e segue: o comando que reprovaria o envio não roda.

Os outros fecham ou só degradam, e ficam como estão:
- `mktemp`, `rm`, `mkdir`, `id`, `date`, `mv`, `nice`, `ionice`, `ps`, `sleep`, `timeout`: a checagem roda e o resultado vale (`sleep` ausente gira o laço sem pausa; `ps` ausente cai no PGID do próprio `$etapa`; `timeout` ausente roda os registros sem prazo; `mv` e `date` só tiram a ordem da fila).
- `flock`: a checagem roda sem esperar a vez, com aviso (como hoje; a trava é de carga, não de política).
- `find`: barra o envio com a mensagem de pasta recusada (fecha; a mensagem não diz que falta o `find`).
- `python3` em `caminhos_extra`: aviso, o PATH não muda e a checagem roda (a ferramenta que faltar reprova nela).
- `git`: o git põe a pasta dele no começo do PATH do hook, e a falha do `git` no laço de refs, no `so_docs` e na junção já barra ou faz a checagem olhar tudo.
- Fora da classe "utilitário": o `git rev-parse --show-toplevel` que falha em `comando_de_registros` (repositório sem árvore) e o `.forge/config.json` ilegível seguem com aviso, como o D3 deixou; o `pre-push.local` ausente ou sem permissão de execução é escolha do projeto.

## 2. A correção
- `local_hook`: o `dirname` ausente, que sai com erro ou que devolve vazio barra o envio com a mensagem "o dirname (coreutils) falta no PATH ou falhou".
- `lider_vivo`: só builtins (`for` sobre a saída de `jobs -rp`), sem o `tr`; o limite e a barreira do órfão não dependem mais de utilitário.
- `comando_de_registros`: sem `python3`, o config que cita `"registros"` barra o envio ("falta no PATH: python3"); sem a chave, aviso e segue (nada a conferir). O texto do config é lido pelo próprio bash, sem outro utilitário.

## 3. Aplicar
Da raiz do Forge, numa branch a partir da `develop` (o `git apply` lê o bloco `diff` deste arquivo e ignora o texto em volta). `git apply --check` conferido sobre a `develop` em 2097f9bf, e também depois do patch do K339 (`docs/propostas/k339-pre-push.patch`, os mesmos trechos com 10 linhas de deslocamento) e do K152 (o `pre-push.local`, outro arquivo):

```bash
git apply --check docs/propostas/prepush-modelo-falha-aberta.md && git apply docs/propostas/prepush-modelo-falha-aberta.md
python3 -m unittest tests.test_prepush_falha_fechada tests.test_prepush_so_docs tests.test_prepush_refs tests.test_caminhos_extra_pre_push
bin/forge-mutante tests/mutantes/v0479-prepush-falha-fechada.json
```

Projetos já criados recebem o hook novo pela atualização do modelo (o `.githooks/pre-push` é do Forge, não do projeto).

```diff
diff --git a/templates/projeto/.githooks/pre-push b/templates/projeto/.githooks/pre-push
index 788a6d5..20188a7 100755
--- a/templates/projeto/.githooks/pre-push
+++ b/templates/projeto/.githooks/pre-push
@@ -90,8 +90,9 @@ so_docs() {
 # A checagem roda num grupo próprio: Ctrl-C, TERM ou HUP no hook a encerram com os filhos e barram o envio. Sinal só
 # para o $etapa lançado e, quando o PGID dele é o próprio $etapa e não o do hook, para o grupo dele; senão, só o $etapa.
 encerrada=0
-lider_vivo() {
-  case " $(jobs -rp | tr '\n' ' ') " in *" $etapa "*) return 0 ;; esac
+lider_vivo() {  # PREPUSH-MODELO-FALHA-ABERTA: só builtins (sem o tr, a lista vinha vazia e o limite e o órfão desligavam)
+  local p
+  for p in $(jobs -rp); do [ "$p" = "$etapa" ] && return 0; done
   return 1
 }
 encerrar_etapa() {
@@ -271,7 +272,12 @@ print(":".join(boas))
 
 # Checagem própria do projeto: .githooks/pre-push.local executável; o forge-init (e a migração 0.47.1) o cria com o pronto
 # rápido da stack (lint, formatação e tipos, de stacks/<stack>/pronto.md), e o projeto o ajusta.
-local_hook="$(dirname "$0")/pre-push.local"
+# PREPUSH-MODELO-FALHA-ABERTA: sem o dirname, o caminho virava "/pre-push.local" e a checagem era pulada (o pre-push.local
+# gerado também o usa para achar a raiz); ausente, com erro ou com saída vazia, barra o envio, nunca pula a checagem.
+if ! pasta_hook="$(dirname -- "$0" 2>/dev/null)" || [ -z "$pasta_hook" ]; then
+  echo "pre-push: o dirname (coreutils) falta no PATH ou falhou; a checagem do projeto não acha o pre-push.local; envio barrado. Corrija o PATH e envie de novo." >&2; exit 1
+fi
+local_hook="$pasta_hook/pre-push.local"
 if [ -x "$local_hook" ]; then
   if so_docs; then
     echo "pre-push: só texto (docs/**, .md, changelog.d/**) ou junção com a develop, sem código novo; lint e typecheck pulados (o CI roda tudo)"
@@ -317,13 +323,17 @@ fi
 # PR-VERDE D3 (v0478 E57.75): a conferência de registros do projeto (índices, mapas e contagens derivados que o CI reprova), só
 # leitura e em segundos: o comando da chave opcional `registros` do .forge/config.json, rodado da raiz; vazia ou sem a chave, nada
 # roda. Vale em todo envio de branch, também o só de texto (o registro pode ser texto), com o prazo FORGE_REGISTROS_PRAZO (180 s,
-# só dígitos). Saída fora de 0 barra o envio (falha fechada), como a chave que não é comando de uma linha; sem python3 ou com o
-# config ilegível, aviso e segue (o CI confere). Sem variável nem opção que pule.
+# só dígitos). Saída fora de 0 barra o envio (falha fechada), como a chave que não é comando de uma linha e, sem python3,
+# o config que cita a chave; com o config ilegível, aviso e segue (o CI confere). Sem variável nem opção que pule.
 comando_de_registros() {
   local cfg_reg
   cfg_reg="$(git rev-parse --show-toplevel 2>/dev/null)/.forge/config.json"
   if [ ! -f "$cfg_reg" ] || [ -L "$cfg_reg" ]; then return 0; fi
-  command -v python3 >/dev/null 2>&1 || { echo "pre-push: aviso: sem python3; registros do .forge/config.json não lido (o CI confere)" >&2; return 0; }
+  # PREPUSH-MODELO-FALHA-ABERTA: sem python3, o config que cita "registros" barra o envio (antes, aviso e seguia sem conferir)
+  if ! command -v python3 >/dev/null 2>&1; then
+    case "$(<"$cfg_reg")" in *'"registros"'*) echo "pre-push: falta no PATH: python3; a chave registros do .forge/config.json não foi lida e o envio foi barrado. Instale o python3 ou corrija o PATH e envie de novo." >&2; return 1 ;; esac
+    echo "pre-push: aviso: sem python3; .forge/config.json sem a chave registros, nada a conferir" >&2; return 0
+  fi
   python3 -I -c '
 import json, sys
 try:
```

## 4. Sondas (2026-11-21, git 2.43.0, Forge na `develop` 2097f9bf)
A sonda cria um projeto pelo `bin/forge-init` da cópia do Forge dada (stack python, com código), um remoto nu e uma pasta de ferramentas só com links para os utilitários que o hook chama; troca o `pre-push.local` por um que anota que rodou e reprova, e envia uma branch nova por utilitário retirado, com `env -i` e o PATH só nessa pasta. Cenário A: a checagem do projeto reprova (`rc=0` é a checagem pulada). B: a checagem passa e a chave `registros` é `false` (`rc=0` é a conferência pulada). C: a checagem dura 4 s com `FORGE_PREPUSH_TIMEOUT=1` (`rc=0` é o limite desligado). Uso: `bash sonda.sh <raiz do Forge> <pasta vazia>`; o "depois" usa uma cópia do Forge (`bin/forge-init`, `templates`, `stacks`, `.claude-plugin`) com o patch aplicado.

```bash
set -u
FORGE="$1"; W="$2"
rm -rf "$W"; mkdir -p "$W/casa"; chmod 700 "$W/casa"
GIT=$(command -v git)
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
git init -q --bare "$W/remoto.git"
mkdir "$W/proj" && cd "$W/proj" && git init -q -b develop
"$FORGE/bin/forge-init" --stack python --sem-sandbox . >/dev/null 2>&1 || echo "forge-init rc=$?"
git config core.hooksPath .githooks
printf '[project]\nname="x"\n' > pyproject.toml; mkdir -p src; echo 'x = 1' > src/a.py
git add -A && git commit -q -m base && git remote add origin "$W/remoto.git" && git push -q origin develop 2>/dev/null
F="$W/ferramentas"; mkdir "$F"
UTIL="bash env dirname mktemp rm tr ps sleep find mkdir id date flock mv nice ionice python3 timeout"
for u in $UTIL; do ln -s "$(command -v "$u")" "$F/$u"; done
local_() { printf '#!/usr/bin/env bash\n%s\n' "$1" > .githooks/pre-push.local; chmod +x .githooks/pre-push.local; }
registros() { printf '{"caminhos_extra": [], "registros": "%s"}\n' "$1" > .forge/config.json; }
i=0
envio() {  # $1 cenário, $2 utilitário retirado (ou -), resto: env extra
  local cen="$1" tira="$2"; shift 2; i=$((i+1))
  git switch -q --no-track -c "feature/s$i" develop && echo "y$i = 2" >> src/a.py && git add -A && git commit -q -m "c$i"
  [ "$tira" = - ] || mv "$F/$tira" "$F/.fora"
  printf -- '--- %s, sem %s: ' "$cen" "$tira"
  env -i PATH="$F" HOME="$W/casa" "$@" "$GIT" push origin "feature/s$i" > "$W/saida" 2>&1; rc=$?
  [ "$tira" = - ] || mv "$F/.fora" "$F/$tira"
  echo "rc=$rc"; grep '^pre-push' "$W/saida" | grep -v duracao | sed 's/^/    /'
}
# A: a checagem do projeto sempre reprova (rc=0 = pulada)
local_ 'echo "pre-push.local: rodou e reprovou" >&2; exit 1'; registros ""; git add -A; git commit -q -m A; git push -q origin develop 2>/dev/null
for u in - $UTIL; do case $u in bash|env) continue;; esac; envio A "$u"; done
# B: a checagem passa e os registros reprovam (rc=0 = registros pulados)
git switch -q develop; local_ 'exit 0'; registros false; git add -A; git commit -q -m B; git push -q origin develop 2>/dev/null
for u in - python3 timeout dirname; do envio B "$u"; done
# C: a checagem demora 4 s e o limite é 1 s (rc=0 = limite desligado)
git switch -q develop; local_ "$(command -v sleep) 4; exit 0"; registros ""; git add -A; git commit -q -m C; git push -q origin develop 2>/dev/null
for u in - tr ps sleep; do envio C "$u" FORGE_PREPUSH_TIMEOUT=1; done
```

Saída real, modelo de hoje (os buracos são `A, sem dirname`, `B, sem python3` e `C, sem tr`, com `rc=0`):

```text
--- A, sem -: rc=1
    pre-push.local: rodou e reprovou
--- A, sem dirname: rc=0
--- A, sem mktemp: rc=1
    pre-push.local: rodou e reprovou
--- A, sem rm: rc=1
    pre-push.local: rodou e reprovou
--- A, sem tr: rc=1
    pre-push.local: rodou e reprovou
--- A, sem ps: rc=1
    pre-push.local: rodou e reprovou
--- A, sem sleep: rc=1
    pre-push.local: rodou e reprovou
--- A, sem find: rc=1
    pre-push: <pasta>/casa/.local/state/forge não é pasta do próprio usuário (ou é link, ou tem escrita de grupo ou de outros); recusada. Apague-a ou corrija com chmod 700 e tente de novo.
--- A, sem mkdir: rc=1
    pre-push.local: rodou e reprovou
--- A, sem id: rc=1
    pre-push.local: rodou e reprovou
--- A, sem date: rc=1
    pre-push.local: rodou e reprovou
--- A, sem flock: rc=1
    pre-push: sem flock; a checagem do projeto roda sem esperar a vez
    pre-push.local: rodou e reprovou
--- A, sem mv: rc=1
    pre-push: aviso: a senha da fila não foi criada; a espera segue só pela trava, sem a ordem de chegada.
    pre-push.local: rodou e reprovou
--- A, sem nice: rc=1
    pre-push.local: rodou e reprovou
--- A, sem ionice: rc=1
    pre-push.local: rodou e reprovou
--- A, sem python3: rc=1
    pre-push: aviso: sem python3; caminhos_extra do .forge/config.json não lido
    pre-push.local: rodou e reprovou
--- A, sem timeout: rc=1
    pre-push.local: rodou e reprovou
--- B, sem -: rc=1
    pre-push: registros: false
    pre-push: a conferência de registros saiu 1 (registro desatualizado, sem veredito ou prazo de 180 s); corrija e envie de novo. Nunca --no-verify.
--- B, sem python3: rc=0
    pre-push: aviso: sem python3; caminhos_extra do .forge/config.json não lido
    pre-push: aviso: sem python3; registros do .forge/config.json não lido (o CI confere)
--- B, sem timeout: rc=1
    pre-push: registros: false
    pre-push: a conferência de registros saiu 1 (registro desatualizado, sem veredito ou prazo de 180 s); corrija e envie de novo. Nunca --no-verify.
--- B, sem dirname: rc=1
    pre-push: registros: false
    pre-push: a conferência de registros saiu 1 (registro desatualizado, sem veredito ou prazo de 180 s); corrija e envie de novo. Nunca --no-verify.
--- C, sem -: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
--- C, sem tr: rc=0
--- C, sem ps: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
--- C, sem sleep: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
```

Saída real, com o patch aplicado (os três barram com a mensagem; o resto igual):

```text
--- A, sem -: rc=1
    pre-push.local: rodou e reprovou
--- A, sem dirname: rc=1
    pre-push: o dirname (coreutils) falta no PATH ou falhou; a checagem do projeto não acha o pre-push.local; envio barrado. Corrija o PATH e envie de novo.
--- A, sem mktemp: rc=1
    pre-push.local: rodou e reprovou
--- A, sem rm: rc=1
    pre-push.local: rodou e reprovou
--- A, sem tr: rc=1
    pre-push.local: rodou e reprovou
--- A, sem ps: rc=1
    pre-push.local: rodou e reprovou
--- A, sem sleep: rc=1
    pre-push.local: rodou e reprovou
--- A, sem find: rc=1
    pre-push: <pasta>/casa/.local/state/forge não é pasta do próprio usuário (ou é link, ou tem escrita de grupo ou de outros); recusada. Apague-a ou corrija com chmod 700 e tente de novo.
--- A, sem mkdir: rc=1
    pre-push.local: rodou e reprovou
--- A, sem id: rc=1
    pre-push.local: rodou e reprovou
--- A, sem date: rc=1
    pre-push.local: rodou e reprovou
--- A, sem flock: rc=1
    pre-push: sem flock; a checagem do projeto roda sem esperar a vez
    pre-push.local: rodou e reprovou
--- A, sem mv: rc=1
    pre-push: aviso: a senha da fila não foi criada; a espera segue só pela trava, sem a ordem de chegada.
    pre-push.local: rodou e reprovou
--- A, sem nice: rc=1
    pre-push.local: rodou e reprovou
--- A, sem ionice: rc=1
    pre-push.local: rodou e reprovou
--- A, sem python3: rc=1
    pre-push: aviso: sem python3; caminhos_extra do .forge/config.json não lido
    pre-push.local: rodou e reprovou
--- A, sem timeout: rc=1
    pre-push.local: rodou e reprovou
--- B, sem -: rc=1
    pre-push: registros: false
    pre-push: a conferência de registros saiu 1 (registro desatualizado, sem veredito ou prazo de 180 s); corrija e envie de novo. Nunca --no-verify.
--- B, sem python3: rc=1
    pre-push: aviso: sem python3; caminhos_extra do .forge/config.json não lido
    pre-push: falta no PATH: python3; a chave registros do .forge/config.json não foi lida e o envio foi barrado. Instale o python3 ou corrija o PATH e envie de novo.
--- B, sem timeout: rc=1
    pre-push: registros: false
    pre-push: a conferência de registros saiu 1 (registro desatualizado, sem veredito ou prazo de 180 s); corrija e envie de novo. Nunca --no-verify.
--- B, sem dirname: rc=1
    pre-push: o dirname (coreutils) falta no PATH ou falhou; a checagem do projeto não acha o pre-push.local; envio barrado. Corrija o PATH e envie de novo.
--- C, sem -: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
--- C, sem tr: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
--- C, sem ps: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
--- C, sem sleep: rc=1
    pre-push: a checagem do projeto passou de 1 s e foi encerrada com os filhos; o envio foi barrado. Suba FORGE_PREPUSH_TIMEOUT ou veja a carga da máquina.
```

## 5. O `.githooks/pre-push` do próprio Forge
O buraco do `dirname` não existe lá (o hook não o usa: vai à raiz por `git rev-parse --show-toplevel`, com `|| exit 1`), nem o do `tr` no limite (o envio leve não roda etapa com limite) nem o dos registros. A mesma classe aparece nas checagens baratas: sem `sort` (linha 293) ou sem `mktemp` (linha 281), a lista de arquivos do envio fica vazia, sem aviso, e a sintaxe, o shellcheck e a neutralidade não olham nada. Sonda: clone do Forge com a `develop` no remoto, branch `melhoria/s<n>` com um `.py` com erro de sintaxe em `bin/` e o fragmento do changelog, PATH com todos os programas do sistema menos um. Saída real:

```text
--- Forge, .py com erro de sintaxe, sem -: rc=1
    pre-push: erro de sintaxe Python em bin/forge_sonda_1.py.
    pre-push: checagens baratas reprovadas em 1s; a suíte nem entrou na fila. Nunca --no-verify.
--- Forge, .py com erro de sintaxe, sem sort: rc=0
    pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
--- Forge, .py com erro de sintaxe, sem mktemp: rc=0
    pre-push: envio leve: sem testes locais; a bateria completa roda no CI do PR (opt-in: FORGE_PREPUSH_SUITE=afetados ou 1).
```

O efeito é menor que no modelo (as checagens baratas adiantam o CI, que roda as mesmas no PR, e o hook do Forge já diz "ferramenta ausente: aviso e segue"), mas aqui nem o aviso sai. Fora do alcance deste item (o cartão fala do modelo, e o hook do Forge também é travado): o conserto lá seria `sem_caminhos=1` com aviso quando o `sort` ou o `mktemp` falham.

## 6. Testes e mutantes
- `tests/test_prepush_falha_fechada.py` aplica o bloco `diff` acima numa cópia temporária do hook do modelo (com o patch já aplicado no modelo, usa o hook como está) e o roda direto, com a linha de ref no stdin, num repositório descartável e com o PATH numa pasta de links. Classes: `DirnameAusente` (ausente, com erro, com saída vazia, e o controle com tudo no PATH), `LimiteSemTr` (a checagem longa encerrada pelo limite sem o `tr`) e `RegistrosSemPython` (com a chave barra, sem a chave segue).
- `tests/mutantes/v0479-prepush-falha-fechada.json`: um mutante por guarda mudada, nas linhas `+` deste arquivo (o teste lê o patch daqui, então mutar a linha do patch muta o hook aplicado).

## Critério de reversão
Se um projeto enviar de uma máquina sem `python3` e com a chave `registros` no config (o Forge já exige o Python), ele instala o `python3` ou tira a chave; se a guarda do `dirname` barrar um envio legítimo, o dono reverte o patch. O hook não ganha variável nem opção que pule.
