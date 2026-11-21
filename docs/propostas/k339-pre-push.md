# K339: tag movida e `git replace` no modelo de envio

Propósito: correção do `templates/projeto/.githooks/pre-push` pronta para o dono aplicar (a pasta `.githooks/` do modelo é travada para os agentes). Público: o dono, `tech-lead`, `security-engineer`, `qa-engineer`. Revisão: 2026-12-21.

Estado: proposta (v0478 E72.1, cartão K339-ENVIO-TAG-E-REPLACE, prioridade alta, segurança). Só aperta: nada que passa hoje e deve seguir passando muda (tag nova, fast-forward real, apagar uma ref por envio).

## 1. Os três buracos (laço de refs, linhas 6 a 52 do hook de hoje)
1. **Tag movida para um descendente passa.** A linha 18 só pergunta se o commit remoto é ancestral do local; para uma tag que já existe no remoto, mover para um filho responde que sim e o envio (com `--force` ou refspec `+`) segue. Tag publicada não se move: quem já a baixou fica com outro commit.
2. **`git replace --graft` engana a ancestralidade.** O `git merge-base --is-ancestor` da linha 18 lê os objetos de substituição locais: `git replace --graft <reescrito> <remoto>` faz o histórico reescrito parecer descendente do remoto, e o envio forçado passa como fast-forward. O servidor não vê o enxerto; o histórico remoto é reescrito.
3. **Tag `refs/tags/origin/*` passa.** Na resolução de nomes do git, `refs/tags/<nome>` vem antes de `refs/remotes/<nome>`: com a tag `origin/develop` no clone, `origin/develop` passa a ler a tag. Quem baixa as tags do remoto herda a sombra (o próprio hook do modelo lê `origin/develop:<arquivo>` no "só texto").

## 2. A correção
- Toda checagem de ancestralidade do laço roda com `git --no-replace-objects`.
- Ref remota em `refs/tags/` que já existe no remoto (sha remoto não zerado) é recusada antes da ancestralidade, qualquer que seja o destino; tag nova segue livre. A mensagem de "mover a tag para outro commit" some, coberta pela recusa nova.
- Criar ou mover `refs/tags/origin/*` é recusado; apagar (a limpeza, uma por envio, regra PREPUSH-DELETE) segue livre.
- Dois testes vizinhos de `tests/test_prepush_so_docs.py` enviavam tag existente movida para conferir que a checagem do projeto roda; passam a enviar tag nova (o mesmo ramo "sem base clara, olha tudo").
- Fica como estava: o `git cat-file -e` da linha 14 (existência, não ancestralidade; um `git replace` não cria objeto ausente) e as linhas `refs/tags/*` de `so_docs` e `arquivos_enviados`, que agora só veem tag nova e seguem como defesa.

## 3. Aplicar
O patch está em `docs/propostas/k339-pre-push.patch` (4 arquivos: hook, teste novo, spec de mutantes, ajuste de 2 testes). Da raiz do Forge, numa branch a partir da `develop`:

```bash
git apply --check docs/propostas/k339-pre-push.patch && git apply docs/propostas/k339-pre-push.patch
python3 -m unittest tests.test_prepush_k339 tests.test_prepush_so_docs tests.test_prepush_refs
bin/forge-mutante tests/mutantes/k339-pre-push.json
```

O diff do hook (o mesmo do patch):

```diff
@@ -8,18 +8,21 @@ while read -r _ local_sha remote_ref remote_sha; do
   # R-VERIFY: reescrever histórico de ref remota existente (não fast-forward) é decisão do usuário.
   # Recusar quando o objeto remoto não existe localmente é intencional: sem ele não há como provar que
   # é fast-forward; um `git fetch` resolve. Apagar ref (local_sha zerado) não passa por esta checagem.
+  # K339: o histórico é lido com --no-replace-objects (um `git replace --graft` local não forja a ancestralidade), e tag que
+  # já existe no remoto não se move, nem para um descendente (tag nova pode).
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
+      if ! git --no-replace-objects merge-base --is-ancestor "$remote_sha" "$local_sha" 2>/dev/null; then
+        echo "pre-push: R-VERIFY: envio não fast-forward para ${ref_nome} (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário." >&2
         exit 1
       fi ;;
     esac ;;
@@ -30,6 +33,12 @@ while read -r _ local_sha remote_ref remote_sha; do
   fi
   # PREPUSH-REFS (v0457, D2 de docs/security/ameacas/v0457-hook-shell-pipe.md): a política vale para as refs reais do
   # envio, qualquer que seja a sintaxe (--branches, -c remote.*.mirror, refspec com curinga, --prune, pipe para o shell).
+  # K339: tag refs/tags/origin/* sombreia a remota de mesmo nome (`origin/develop` passa a ler a tag); criar ou mover é
+  # bloqueado, apagar (limpeza) pode.
+  case "$local_sha:$remote_ref" in
+    *[!0]*:refs/tags/origin/*) echo "pre-push: R-FLUXO: a tag '${remote_ref#refs/tags/}' imita uma branch remota (origin/...); envio bloqueado, escolha outro nome." >&2
+       exit 1 ;;
+  esac
   case "$remote_ref" in
     refs/heads/?*|refs/tags/?*) ;;
     *) echo "pre-push: R-FLUXO: a ref remota '${remote_ref}' não é branch (refs/heads/) nem tag (refs/tags/); envio bloqueado (o envio espelho leva refs/remotes/, refs/notes/ e afins)." >&2
```

## 4. Sondas (rodadas em 2026-11-21, git 2.43.0, contra o hook do modelo no `develop` a6baf239)
A sonda alimenta o hook com a linha que o git passaria no stdin (`<ref local> <sha local> <ref remota> <sha remoto>`), num repositório descartável com o hook copiado sozinho para uma pasta (sem o `pre-push.local` ao lado). Assim nenhum envio forçado de verdade é preciso. Uso: `bash sonda.sh <caminho absoluto do hook>`.

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
p() { echo "--- S$1: $2"; printf '%s\n' "$3" | env -i PATH="$PATH" HOME="$W" bash "$HOOK" origin "$W/remoto.git" 2>&1 | grep -v '^pre-push: duracao'; echo "rc=${PIPESTATUS[1]}"; }
p 1 "branch reescrita, sem graft (controle)" "refs/heads/x $L refs/heads/x $R"
git replace --graft "$L" "$R"
p 2 "branch reescrita, com git replace --graft L R" "refs/heads/x $L refs/heads/x $R"
git replace -d "$L" >/dev/null
p 3 "tag existente movida para um descendente" "refs/tags/v1 $C refs/tags/v1 $R"
p 4 "tag existente movida para fora (controle)" "refs/tags/v1 $L refs/tags/v1 $R"
p 5 "tag nova refs/tags/origin/develop" "refs/tags/origin/develop $C refs/tags/origin/develop $Z"
p 6 "tag nova comum (precisa passar)" "refs/tags/v2 $C refs/tags/v2 $Z"
p 7 "branch fast-forward real (precisa passar)" "refs/heads/x $C refs/heads/x $R"
p 8 "apagar tag refs/tags/origin/develop (limpeza, precisa passar)" "(delete) $Z refs/tags/origin/develop $C"
git tag origin/main "$R"; git update-ref refs/remotes/origin/main "$C"
echo "--- efeito da tag origin/main: git rev-parse origin/main = $(git rev-parse origin/main 2>/dev/null) (a remota de verdade é $C)"
rm -rf "$W"
```

Saída real, hook do modelo de hoje (os buracos são S2, S3 e S5, `rc=0`):

```text
--- S1: branch reescrita, sem graft (controle)
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S2: branch reescrita, com git replace --graft L R
rc=0
--- S3: tag existente movida para um descendente
rc=0
--- S4: tag existente movida para fora (controle)
pre-push: R-VERIFY: mover a tag v1 para outro commit (histórico reescrito) bloqueado; reescrever histórico é decisão do usuário.
rc=1
--- S5: tag nova refs/tags/origin/develop
rc=0
--- S6: tag nova comum (precisa passar)
rc=0
--- S7: branch fast-forward real (precisa passar)
rc=0
--- S8: apagar tag refs/tags/origin/develop (limpeza, precisa passar)
rc=0
--- efeito da tag origin/main: git rev-parse origin/main = ccf49bb649a93e77f99356c13626800b6e3d1b0d (a remota de verdade é 0d24cba0767165b65c45e89972187373d5bfb680)
```

Saída real, hook com o patch aplicado (S2, S3, S4 e S5 recusam; S6, S7 e S8 seguem):

```text
--- S1: branch reescrita, sem graft (controle)
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S2: branch reescrita, com git replace --graft L R
pre-push: R-VERIFY: envio não fast-forward para x (histórico reescrito) bloqueado; faça rebase sobre a remota e envie normalmente, reescrever histórico é decisão do usuário.
rc=1
--- S3: tag existente movida para um descendente
pre-push: R-VERIFY: a tag v1 já existe no remoto e não se move (nem para um descendente); mover tag é decisão do usuário.
rc=1
--- S4: tag existente movida para fora (controle)
pre-push: R-VERIFY: a tag v1 já existe no remoto e não se move (nem para um descendente); mover tag é decisão do usuário.
rc=1
--- S5: tag nova refs/tags/origin/develop
pre-push: R-FLUXO: a tag 'origin/develop' imita uma branch remota (origin/...); envio bloqueado, escolha outro nome.
rc=1
--- S6: tag nova comum (precisa passar)
rc=0
--- S7: branch fast-forward real (precisa passar)
rc=0
--- S8: apagar tag refs/tags/origin/develop (limpeza, precisa passar)
rc=0
```

## 5. O `.githooks/pre-push` do próprio Forge tem o mesmo buraco
Sim, os três. O laço de refs dele (linhas 141 a 189) tem a mesma checagem (`git merge-base --is-ancestor` na linha 154, sem `--no-replace-objects`) e nenhuma recusa de tag existente nem de `refs/tags/origin/*`. Sonda: o laço extraído do hook (`sed -n '/^refs_branches=0; refs_remocoes=0/,/^done$/p' .githooks/pre-push`, com `modo_suite=0` antes e um `echo "laço de refs do Forge: passou" >&2` depois, porque o resto do hook roda a suíte), com a mesma sonda acima. Saída real:

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

No Forge o efeito é menor (as tags de versão saem do `release.yml`, e `main`, `homolog` e `develop` são recusadas pelo nome antes de tudo), mas `melhoria/*` reescrita por enxerto e tag movida passam. Fora do alcance deste item (o cartão fala do modelo); as mesmas três mudanças valem lá, com as classes `Forge` do teste. Há ainda um `git merge-base --is-ancestor` na linha 255 do hook do Forge (fora do laço) que lê os objetos de substituição.

## 6. Testes e mutantes que entram com a aplicação (já no patch)
- `tests/test_prepush_k339.py`, classe `K339Modelo` (reusa a base de `tests/test_prepush_refs.py`): `test_graft_nao_forja_fast_forward`, `test_fast_forward_real_passa`, `test_tag_existente_movida_para_descendente_recusa`, `test_tag_nova_passa`, `test_tag_origin_nova_recusa`, `test_apagar_tag_origin_passa`. Contra o hook de hoje: 4 de 6 falham; com o patch, 6 de 6 passam.
- `tests/test_prepush_so_docs.py`: `PrePushSoDocs.test_tag_roda` e `ListaDosArquivos.test_sem_base_clara_olha_tudo` passam a enviar tag nova (sem isso, as duas falham com o patch, que recusa a tag existente antes da checagem).
- `tests/mutantes/k339-pre-push.json`, um mutante por linha de guarda mudada, todos mortos com o patch aplicado (`bin/forge-mutante`): M1 o `case` de tag existente (linha 16), M2 o `exit 1` dele (17), M3 o `--no-replace-objects` (24), M4 o `case` de `refs/tags/origin/*` (39), M5 o `exit 1` dele, M6 o prefixo `*[!0]*:` que deixa apagar. `bin/forge-mutante --conferir` confere os trechos; a `--cobertura` aponta o shell como `não coberto`, por arquivo, como sempre.
- Também rodados com o patch: `tests.test_prepush_refs`, `tests.test_pre_push_afetados`, `tests.test_caminhos_extra_pre_push`, `tests.test_conf_escopo` (verdes).

## Critério de reversão
Se um projeto precisar mover tag publicada (correção de versão), o dono faz à mão fora do hook (`R-VERIFY`: é decisão do usuário) ou reverte este patch; o hook não ganha variável nem opção que pule.
