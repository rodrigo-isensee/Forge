# K339: tag movida, enxertos e tags de remoto no modelo de envio

Propósito: correção do `templates/projeto/.githooks/pre-push` pronta para o dono aplicar (a pasta `.githooks/` do modelo é travada para os agentes). Público: o dono, `tech-lead`, `security-engineer`, `qa-engineer`. Revisão: 2026-12-21.

Estado: proposta (v0478 E72.1, volta da segurança na E72.3; cartão K339-ENVIO-TAG-E-REPLACE, prioridade alta, segurança). Só aperta: nada que passa hoje e deve seguir passando muda (tag nova de outro nome, fast-forward real, apagar uma ref por envio).

## 1. Os buracos (laço de refs, linhas 6 a 52 do hook de hoje)
1. **Tag movida para um descendente passa.** A linha 18 só pergunta se o commit remoto é ancestral do local; para uma tag que já existe no remoto, mover para um filho responde que sim e o envio (com `--force` ou refspec `+`) segue. Tag publicada não se move: quem já a baixou fica com outro commit.
2. **Enxertos enganam a ancestralidade.** O `git merge-base --is-ancestor` da linha 18 lê os objetos de substituição locais (`git replace --graft <reescrito> <remoto>`) e o arquivo antigo de enxertos (`.git/info/grafts`, linha `<reescrito> <remoto>`): os dois fazem o histórico reescrito parecer descendente do remoto, e o envio forçado passa como fast-forward. O servidor não vê o enxerto; o histórico remoto é reescrito. O `--no-replace-objects` só desliga o primeiro (achado A1 da segurança na E72.1: com ele, o arquivo de enxertos ainda passava, `rc=0`).
3. **Tag com o nome de um remoto passa.** Na resolução de nomes do git, `refs/tags/<nome>` vem antes de `refs/remotes/<nome>`: com a tag `origin/develop` no clone, `origin/develop` passa a ler a tag; com a tag `origin`, `origin` (o `origin/HEAD`) também. Vale para qualquer remoto, não só `origin` (o hook recebe o nome do remoto do envio em `$1`). Quem baixa as tags do remoto herda a sombra (o próprio hook do modelo lê `origin/develop:<arquivo>` no "só texto").

## 2. A correção
- A checagem de ancestralidade do laço roda com `GIT_GRAFT_FILE=/dev/null git --no-replace-objects`, na mesma chamada: sem objetos de substituição e sem o arquivo de enxertos.
- Ref remota em `refs/tags/` que já existe no remoto (sha remoto não zerado) é recusada antes da ancestralidade, qualquer que seja o destino; tag nova segue livre. A mensagem de "mover a tag para outro commit" some, coberta pela recusa nova.
- Criar ou mover `refs/tags/origin`, `refs/tags/origin/*`, `refs/tags/<remoto do envio>` e `refs/tags/<remoto do envio>/*` é recusado (só o nome exato ou ele como pasta: `forkado` e `originais` passam); apagar (a limpeza, uma por envio, regra PREPUSH-DELETE) segue livre. Envio a uma URL sem remoto nomeado: o git passa a URL em `$1`, que não casa com nome de tag, e só valem as recusas fixas de `origin`.
- Dois testes vizinhos de `tests/test_prepush_so_docs.py` enviavam tag existente movida para conferir que a checagem do projeto roda; passam a enviar tag nova (o mesmo ramo "sem base clara, olha tudo").
- Fica como estava: o `git cat-file -e` da linha 14 (existência, não ancestralidade; um enxerto não cria objeto ausente) e as linhas `refs/tags/*` de `so_docs` e `arquivos_enviados`, que agora só veem tag nova e seguem como defesa.

## 3. Aplicar
O patch está em `docs/propostas/k339-pre-push.patch` (5 arquivos: hook, teste novo, 2 specs de mutantes, ajuste de 2 testes). `git apply --check` conferido sobre a `develop` em a6baf239 (2026-11-21, E72.3). Da raiz do Forge, numa branch a partir da `develop`:

```bash
git apply --check docs/propostas/k339-pre-push.patch && git apply docs/propostas/k339-pre-push.patch
python3 -m unittest tests.test_prepush_k339 tests.test_prepush_so_docs tests.test_prepush_refs
bin/forge-mutante tests/mutantes/k339-pre-push.json tests/mutantes/k339-pre-push-2.json
```

O diff do hook (o mesmo do patch):

```diff
@@ -8,18 +8,21 @@ while read -r _ local_sha remote_ref remote_sha; do
   # R-VERIFY: reescrever histórico de ref remota existente (não fast-forward) é decisão do usuário.
   # Recusar quando o objeto remoto não existe localmente é intencional: sem ele não há como provar que
   # é fast-forward; um `git fetch` resolve. Apagar ref (local_sha zerado) não passa por esta checagem.
+  # K339: o histórico é lido sem enxertos (--no-replace-objects contra o `git replace --graft`, GIT_GRAFT_FILE=/dev/null
+  # contra o antigo .git/info/grafts), e tag que já existe no remoto não se move, nem para um descendente (tag nova pode).
   case "$local_sha" in *[!0]*)
     case "$remote_sha" in *[!0]*)
       ref_nome="${remote_ref#refs/heads/}"; ref_nome="${ref_nome#refs/tags/}"
+      case "$remote_ref" in refs/tags/*)
+        echo "pre-push: R-VERIFY: a tag ${ref_nome} já existe no remoto e não se move (nem para um descendente); mover tag é decisão do usuário." >&2
+        exit 1 ;;
+      esac
       if ! git cat-file -e "$remote_sha" 2>/dev/null; then
         echo "pre-push: o commit atual de ${ref_nome} no remoto não existe aqui, então não dá para saber se o envio é fast-forward; rode 'git fetch' e tente de novo." >&2
         exit 1
       fi
-      if ! git merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null; then
-        case "$remote_ref" in
-          refs/tags/*) echo "pre-push: R-VERIFY: mover a tag ${ref_nome} para outro commit (histórico reescrito) bloqueado; reescrever histórico é decisão do usuário." >&2 ;;
-          *) echo "pre-push: R-VERIFY: envio não fast-forward para ${ref_nome} (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário." >&2 ;;
-        esac
+      if ! GIT_GRAFT_FILE=/dev/null git --no-replace-objects merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null; then
+        echo "pre-push: R-VERIFY: envio não fast-forward para ${ref_nome} (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário." >&2
         exit 1
       fi ;;
     esac ;;
@@ -30,6 +33,13 @@ while read -r _ local_sha remote_ref remote_sha; do
   fi
   # PREPUSH-REFS (v0457, D2 de docs/security/ameacas/v0457-hook-shell-pipe.md): a política vale para as refs reais do
   # envio, qualquer que seja a sintaxe (--branches, -c remote.*.mirror, refspec com curinga, --prune, pipe para o shell).
+  # K339: tag com o nome de um remoto (origin, ou o deste envio, que o git passa em $1), sozinho ou como pasta, sombreia a
+  # remota (`origin` e `origin/develop` passam a ler a tag); criar ou mover é bloqueado, apagar (limpeza) pode.
+  case "$local_sha:$remote_ref" in
+    *[!0]*:refs/tags/origin|*[!0]*:refs/tags/origin/*|*[!0]*:"refs/tags/${1:-origin}"|*[!0]*:"refs/tags/${1:-origin}"/*)
+       echo "pre-push: R-FLUXO: a tag '${remote_ref#refs/tags/}' imita um remoto (origin ou ${1:-origin}, sozinho ou com /...); envio bloqueado, escolha outro nome." >&2
+       exit 1 ;;
+  esac
   case "$remote_ref" in
     refs/heads/?*|refs/tags/?*) ;;
     *) echo "pre-push: R-FLUXO: a ref remota '${remote_ref}' não é branch (refs/heads/) nem tag (refs/tags/); envio bloqueado (o envio espelho leva refs/remotes/, refs/notes/ e afins)." >&2
```

## 4. Sondas (rodadas em 2026-11-21, git 2.43.0, contra o hook do modelo no `develop` a6baf239 e com o patch aplicado)
A sonda alimenta o hook com a linha que o git passaria no stdin (`<ref local> <sha local> <ref remota> <sha remoto>`) e o nome do remoto em `$1`, num repositório descartável com o hook copiado sozinho para uma pasta. Assim nenhum envio forçado de verdade é preciso. Uso: `bash sonda.sh <caminho absoluto do hook>`. Os shas mudam a cada rodada (commits novos).

```bash
set -u
HOOK="$1"
W=$(mktemp -d "${TMPDIR:-/tmp}/k339-sonda.XXXX")
cd "$W" && git init -q -b main r && cd r
git config user.email t@t; git config user.name t
git commit -q --allow-empty -m a; R=$(git rev-parse HEAD)
git commit -q --allow-empty -m b; C=$(git rev-parse HEAD)
git checkout -q --orphan outra; git commit -q --allow-empty -m x; L=$(git rev-parse HEAD)
Z=0000000000000000000000000000000000000000
p() { echo "--- S$1: $2"; printf '%s\n' "$4" | env -i PATH="$PATH" HOME="$W" bash "$HOOK" "$3" "$W/remoto.git" 2>&1 | grep -v '^pre-push: duracao' | grep -v '^pre-push.local:'; echo "rc=${PIPESTATUS[1]}"; }
p 1 "branch reescrita, sem graft (controle)" origin "refs/heads/x $L refs/heads/x $R"
git replace --graft "$L" "$R"
p 2 "branch reescrita, com git replace --graft L R" origin "refs/heads/x $L refs/heads/x $R"
git replace -d "$L" >/dev/null
echo "$L $R" > .git/info/grafts
p 9 "branch reescrita, com .git/info/grafts 'L R'" origin "refs/heads/x $L refs/heads/x $R"
rm .git/info/grafts
p 3 "tag existente movida para um descendente" origin "refs/tags/v1 $C refs/tags/v1 $R"
p 4 "tag existente movida para fora (controle)" origin "refs/tags/v1 $L refs/tags/v1 $R"
p 5 "tag nova refs/tags/origin/develop" origin "refs/tags/origin/develop $C refs/tags/origin/develop $Z"
p 10 "tag nova refs/tags/origin (sem barra)" origin "refs/tags/origin $C refs/tags/origin $Z"
p 11 "tag nova refs/tags/fork, envio ao remoto fork" fork "refs/tags/fork $C refs/tags/fork $Z"
p 12 "tag nova refs/tags/fork/develop, envio ao remoto fork" fork "refs/tags/fork/develop $C refs/tags/fork/develop $Z"
p 13 "tag nova refs/tags/forkado, envio ao remoto fork (precisa passar)" fork "refs/tags/forkado $C refs/tags/forkado $Z"
p 6 "tag nova comum (precisa passar)" origin "refs/tags/v2 $C refs/tags/v2 $Z"
p 7 "branch fast-forward real (precisa passar)" origin "refs/heads/x $C refs/heads/x $R"
p 8 "apagar tag refs/tags/origin/develop (limpeza, precisa passar)" origin "(delete) $Z refs/tags/origin/develop $C"
git tag origin "$R"; git update-ref refs/remotes/origin/HEAD "$C"
echo "--- efeito da tag origin: git rev-parse origin = $(git rev-parse origin 2>/dev/null) (a remota origin/HEAD de verdade é $C)"
rm -rf "$W"
```

Saída real, hook do modelo de hoje (os buracos são S2, S9, S3, S5, S10, S11 e S12, `rc=0`):

```text
--- S1: branch reescrita, sem graft (controle)
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S2: branch reescrita, com git replace --graft L R
rc=0
--- S9: branch reescrita, com .git/info/grafts 'L R'
rc=0
--- S3: tag existente movida para um descendente
rc=0
--- S4: tag existente movida para fora (controle)
pre-push: R-VERIFY: mover a tag v1 para outro commit (histórico reescrito) bloqueado; reescrever histórico é decisão do usuário.
rc=1
--- S5: tag nova refs/tags/origin/develop
rc=0
--- S10: tag nova refs/tags/origin (sem barra)
rc=0
--- S11: tag nova refs/tags/fork, envio ao remoto fork
rc=0
--- S12: tag nova refs/tags/fork/develop, envio ao remoto fork
rc=0
--- S13: tag nova refs/tags/forkado, envio ao remoto fork (precisa passar)
rc=0
--- S6: tag nova comum (precisa passar)
rc=0
--- S7: branch fast-forward real (precisa passar)
rc=0
--- S8: apagar tag refs/tags/origin/develop (limpeza, precisa passar)
rc=0
--- efeito da tag origin: git rev-parse origin = 1525119b4ea3f4f541baf6760014f57bc3cf5472 (a remota origin/HEAD de verdade é 645bea7a1966b96dbc89a16214ae91cdd7d227dc)
```

Saída real, hook com o patch aplicado (S2, S9, S3, S4, S5, S10, S11 e S12 recusam; S13, S6, S7 e S8 seguem):

```text
--- S1: branch reescrita, sem graft (controle)
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S2: branch reescrita, com git replace --graft L R
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S9: branch reescrita, com .git/info/grafts 'L R'
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S3: tag existente movida para um descendente
pre-push: R-VERIFY: a tag v1 já existe no remoto e não se move (nem para um descendente); mover tag é decisão do usuário.
rc=1
--- S4: tag existente movida para fora (controle)
pre-push: R-VERIFY: a tag v1 já existe no remoto e não se move (nem para um descendente); mover tag é decisão do usuário.
rc=1
--- S5: tag nova refs/tags/origin/develop
pre-push: R-FLUXO: a tag 'origin/develop' imita um remoto (origin ou origin, sozinho ou com /...); envio bloqueado, escolha outro nome.
rc=1
--- S10: tag nova refs/tags/origin (sem barra)
pre-push: R-FLUXO: a tag 'origin' imita um remoto (origin ou origin, sozinho ou com /...); envio bloqueado, escolha outro nome.
rc=1
--- S11: tag nova refs/tags/fork, envio ao remoto fork
pre-push: R-FLUXO: a tag 'fork' imita um remoto (origin ou fork, sozinho ou com /...); envio bloqueado, escolha outro nome.
rc=1
--- S12: tag nova refs/tags/fork/develop, envio ao remoto fork
pre-push: R-FLUXO: a tag 'fork/develop' imita um remoto (origin ou fork, sozinho ou com /...); envio bloqueado, escolha outro nome.
rc=1
--- S13: tag nova refs/tags/forkado, envio ao remoto fork (precisa passar)
rc=0
--- S6: tag nova comum (precisa passar)
rc=0
--- S7: branch fast-forward real (precisa passar)
rc=0
--- S8: apagar tag refs/tags/origin/develop (limpeza, precisa passar)
rc=0
--- efeito da tag origin: git rev-parse origin = 4a53301ea2c0bfc976957a1ca2c58e10ee684086 (a remota origin/HEAD de verdade é be55622bc624a668b528bd39982638f90b6402ee)
```

## 5. O `.githooks/pre-push` do próprio Forge tem o mesmo buraco
Sim, todos. O laço de refs dele (linhas 141 a 189) tem a mesma checagem (`git merge-base --is-ancestor` na linha 154, sem `--no-replace-objects`) e nenhuma recusa de tag existente nem de `refs/tags/origin/*`. Sonda: o laço extraído do hook (`sed -n '/^refs_branches=0; refs_remocoes=0/,/^done$/p' .githooks/pre-push`, com `modo_suite=0` antes e um `echo "laço de refs do Forge: passou" >&2` depois, porque o resto do hook roda a suíte), com a mesma sonda acima. Saída real:

```text
--- S1: branch reescrita, sem graft (controle)
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; rode 'git pull --rebase' e envie de novo, reescrever histórico é decisão do usuário.
rc=1
--- S2: branch reescrita, com git replace --graft L R
laço de refs do Forge: passou
rc=0
--- S3: tag existente movida para um descendente
laço de refs do Forge: passou
rc=0
--- S4: tag existente movida para fora (controle)
pre-push: R-VERIFY: mover a tag v1 para outro commit (histórico reescrito) bloqueado; reescrever histórico é decisão do usuário.
rc=1
--- S5: tag nova refs/tags/origin/develop
laço de refs do Forge: passou
rc=0
```

No Forge o efeito é menor (as tags de versão saem do `release.yml`, e `main`, `homolog` e `develop` são recusadas pelo nome antes de tudo), mas `melhoria/*` reescrita por enxerto e tag movida passam. Na volta E72.3, o mesmo laço extraído também deixou passar o arquivo antigo de enxertos (S9, `rc=0`) e as tags `origin` sem barra e `fork`/`fork/develop` com o remoto `fork` (S10 a S12, `rc=0`). Fora do alcance deste item (o cartão fala do modelo); as mesmas mudanças valem lá, com as classes `Forge` do teste. Há ainda um `git merge-base --is-ancestor` na linha 255 do hook do Forge (fora do laço) que lê os objetos de substituição e o arquivo de enxertos.

## 6. Testes e mutantes que entram com a aplicação (já no patch)
- `tests/test_prepush_k339.py`, classe `K339Modelo` (reusa a base de `tests/test_prepush_refs.py`; `roda_no_remoto` passa outro nome em `$1`): `test_graft_nao_forja_fast_forward`, `test_arquivo_de_grafts_nao_forja_fast_forward`, `test_fast_forward_real_passa`, `test_tag_existente_movida_para_descendente_recusa`, `test_tag_nova_passa`, `test_tag_origin_nova_recusa`, `test_tag_origin_sem_barra_recusa`, `test_tag_com_o_nome_do_remoto_recusa`, `test_tag_na_pasta_do_remoto_recusa`, `test_tag_com_prefixo_do_remoto_passa`, `test_apagar_tag_origin_passa`, `test_apagar_tag_do_remoto_passa`. Contra o hook de hoje: 8 falhas em 12 testes; contra o patch da E72.1 (1c6fdbe2): 6 falhas (grafts, `origin` sem barra, remoto `fork` e, pela mensagem nova, `origin/*`); com este patch, 12 de 12 passam.
- `tests/test_prepush_so_docs.py`: `PrePushSoDocs.test_tag_roda` e `ListaDosArquivos.test_sem_base_clara_olha_tudo` passam a enviar tag nova (sem isso, as duas falham com o patch, que recusa a tag existente antes da checagem).
- `tests/mutantes/k339-pre-push.json` (M1 a M8) e `tests/mutantes/k339-pre-push-2.json` (M9 a M11), um mutante por guarda mudada, 11 de 11 mortos com o patch aplicado (`bin/forge-mutante --processos 1`, rev da cópia de teste): M1 o `case` de tag existente (linha 16), M2 o `exit 1` dele (17), M3 o `--no-replace-objects` (24), M10 o `GIT_GRAFT_FILE=/dev/null` (24), M4 `origin/*`, M7 `origin` sem barra, M8 `$1` sozinho, M9 `$1/*` (os quatro na linha 39), M5 o `exit 1` da recusa de remoto (41), M6 e M11 o prefixo `*[!0]*:` que deixa apagar (`origin/*` e `$1`). A `--cobertura` aponta o shell como `não coberto`, por arquivo, como sempre.
- Também rodados com o patch: `tests.test_prepush_refs`, `tests.test_prepush_so_docs`, `tests.test_pre_push_afetados`, `tests.test_caminhos_extra_pre_push`, `tests.test_conf_escopo` (168 testes com o novo, verdes, 10 pulados pelo ambiente).

## Critério de reversão
Se um projeto precisar mover tag publicada (correção de versão) ou usar uma tag com o nome de um remoto, o dono faz à mão fora do hook (`R-VERIFY`: é decisão do usuário) ou reverte este patch; o hook não ganha variável nem opção que pule.
