---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/v0457-refs-push
commit: b12f6d9be42f4b3b5f00bce51be535b567207483
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (3b, PREPUSH-REFS, PR #506)

Etapa E9.6, classe C. Instância que não fez a entrega. Diff lido: `git diff 8b5a44d5..b12f6d9b` (6 commits, 13 arquivos, numstat 415+/14-).

## Achados
- A1 (recomendado) tests/test_prepush_so_docs.py:154 · os nomes test_duas_refs_uma_docs_outra_codigo_roda e test_duas_refs_so_docs_pulam (:164) dizem roda/pula, mas agora afirmam a recusa de duas branches; renomear e, se valer, cobrir o plano só-docs com uma branch e uma tag.
- A2 (recomendado) docs/hooks.md:124 · a seção do pre-push não cita a PREPUSH-REFS (ref só em refs/heads e refs/tags, uma branch com código e uma remoção por envio); a regra vale para as pessoas nos projetos e merece uma linha na doc dos hooks.

## Sondas

## Parecer
**Aprovado.** Sem bloqueante.

**Patch do dono (decisão 4a, R-CONFORMIDADE).** O commit 3d4a884f toca só `.githooks/pre-push` e `templates/projeto/.githooks/pre-push` (22 linhas cada). `git show 3d4a884f`, sem as linhas `index`, é idêntico a `/root/.forge-contrib/patches/refs-push.patch` (sha256 800bf885…a6fb, o mesmo do histórico de 12:17), e `git apply --check -R` do patch passa no head. Os hooks não foram reescritos por agente.

**Política.** As três recusas ficam no laço `while read`, depois das recusas de R-VERIFY e das branches protegidas, e valem para cada ref real do envio: ref remota fora de `refs/heads/?*` e `refs/tags/?*` (`.githooks/pre-push:170-174`), mais de uma branch com código (`:179-182`; tag não conta) e mais de uma remoção (`:185-188`). Os contadores começam em 0 antes do laço (`:139`, modelo `:4`) e não vêm do ambiente; um teste prova isso. Os dois hooks têm o mesmo bloco. A limpeza do `bin/forge-fechar` apaga uma ref por envio (`:591`), então segue compatível com a regra de uma remoção. O dono aceitou que a regra de uma branch por envio vale para as pessoas nos projetos (ORDEM DO DONO de 13:50) e aplicou o rótulo `afrouxa-regra`.

**Testes.** `tests/test_prepush_refs.py` tem 20 casos (6 de política e 4 de envio real pelo git, para cada hook), com `--branches`, `--all`, `--mirror`, notas e `--prune` com curinga. Os testes de envio real também conferem que o remoto não muda. O ambiente é montado do zero (AR-4 conferido). Os 6 módulos ajustados trocam a segunda branch por tag, ou passam a esperar a recusa. A asserção do envio que só apaga voltou a ficar separada, e a catraca do PR está verde. Mutantes: 16 em duas specs (8 por hook), um por linha de guarda, com o ramo de falha (`exit 1`) coberto. Todo `de` aparece uma única vez no head (AR-12 conferido). `bin/forge-testes` mapeia o hook do modelo para `test_prepush_refs`.

**Tamanho (M14).** São 243 linhas que contam (tests/*.py 197, os dois hooks 44 e bin 2). O corpo do PR traz `teto: excedido, ~240 linhas`, com o motivo (44 linhas do patch do dono e 168 do módulo novo), e o PR trata um comportamento só.

**Rodado aqui** (worktree destacada no head, um módulo por vez):
- `tests.test_prepush_refs`: 20 OK.
- `tests.test_pre_push_trava`: 50 OK, 4 pulados.
- `tests.test_pre_push_afetados`, `tests.test_pre_push_ja_no_remoto`, `tests.test_pre_push_parecer` e `tests.test_pre_push_segredo`: OK.
- `tests.test_prepush_so_docs`: OK, 9 pulados. Todos os pulos são do sandbox (`/proc` e `chown`), fora do diff.
- `shellcheck` nos dois hooks: limpo.

**CI do PR #506** (`gh pr checks 506`, run 43288706245, head b12f6d9b): `catraca`, `instalação (python 3.14)` e `árvore já provada na develop` estão verdes. `bateria (passos)` falhou só no passo de R-REVIEW, por falta deste parecer ("PR toca bin/forge-testes … sem parecer aprovado de review"). Por isso as partes da suíte ficaram como `skipping`, e `bateria` e `bateria (python 3.14)` ficaram vermelhas em cascata. A bateria completa ainda não rodou. Ela é o portão do merge e roda de novo com os pareceres na branch. O merge espera a tag (decisão 5 do v0457).
