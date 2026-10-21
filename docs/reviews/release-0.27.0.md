---
tipo: review
contrato: 1
pedido: release-0.27.0
branch: melhoria/release-0.27.0
commit: 23ecec1054c2b946d22eaa934c05c93996a92945
parecer: aprovado
revisor: forge:tech-lead (outra instância, E2.1)
data: 2026-10-21
---
# Review: release 0.27.0

Escopo: fechamento da versão `10c838f..23ecec1` (base 10c838fa35c96229d04ca96b0897cec19cbaa631) e a leva `0f480c8..10c838f` (#249 a #253). O revisor não é o autor do fechamento (D-ETAPAS-INST). Conferência feita só com git, sem trocar o HEAD da worktree.

Veredito sobre `23ecec1`: **APROVADO**, sem achados que bloqueiem.

## Achados

## O que foi conferido
1. **Versão.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.26.0 para 0.27.0; minor, conforme o SemVer do `CLAUDE.md` (nenhuma entrega da leva quebra os projetos).
2. **Arquivos do fechamento.** `git diff --stat 10c838f 23ecec1`: 8 arquivos, os dois `plugin.json`, o `CHANGELOG.md` e a remoção dos cinco fragmentos (`textos-a1`, `s-16-promocao-develop`, `forge-check-lote`, `ci-postinstall-cli`, `conf-so-leitura-fix`). Nenhum outro arquivo mudou; `changelog.d/` fica vazia.
3. **Seção [0.27.0].** `## [0.27.0] - 2026-10-21` logo abaixo de `## [Não publicado]` (vazia), com três itens em `### Alterado` (FORGE-CHECK-LOTE, S-16-PROMOCAO-DEVELOP, TEXTOS-A1) e dois em `### Corrigido` (CI-POSTINSTALL-CLI, CONF-SO-LEITURA-FIX). Cada linha é a do fragmento apagado, byte a byte (o diff mostra as mesmas linhas removidas e acrescentadas). ADR 0006 cumprida.
4. **Pareceres de review da leva.** Os cinco em `docs/reviews/` estão com `parecer: aprovado` e `## Achados` vazio. QA e segurança dos cinco presentes e aprovados; devops do #251 presente (é do papel, E2.2, não refeito aqui).
5. **O código mesclado é o código revisado.** Para cada PR, comparei o commit citado no parecer com o squash na develop, só nos arquivos do PR fora das pastas de parecer:
   - #249 (`b9a8d75` × `2960f1a`), #250 (`f804072` × `6ec81e1`), #251 (`d346475` × `f911dfa`): sem diferença.
   - #253 (`f3d68cb` × `10c838f`): o arquivo `tests/test_forge.py` difere por trazer o #252 da develop; o patch da branch (`0f480c8..f3d68cb`) e o do squash (`10c838f^..10c838f`) são iguais linha a linha.
   - #252: ver o item 6.
6. **Review em dia do código que governa os agentes (FORGE-CHECK-LOTE).** O parecer de review do lote na develop aponta `9c09ae0`; o código mesclado no squash `4c0ba8a` é `b69dbe9` (`git diff --stat b69dbe9 4c0ba8a` nos arquivos do PR: sem diferença). Entre `9c09ae0` e `b69dbe9` o único código que muda é `tests/test_forge.py` (+3 −2: a sentinela `/home/pessoa` passa a ser montada em tempo de execução, mesmo teste e mesmas asserções). Essa volta 2 tem re-review aprovado em `b3b165c` (`docs/reviews/forge-check-lote.md`, `commit: b69dbe9`), que está só na branch remota `melhoria/forge-check-lote` (confirmado por `git ls-remote`), fora da develop. Conclusão: toda a leva tem review aprovado do código que entrou, incluindo `bin/forge-check`, `agents/conferente.md`, `hooks/conformidade.json` e `tests/catraca.py`; o parecer de outro pedido não foi reescrito. Ver R1.
7. **Regras.** R-NEUTRO, R-CUSTO e R-VERIFY: o fechamento só toca versão e changelog, sem custo nem termo de projeto. R-FLUXO: a branch parte da develop no Base-sha do brief.

## Detalhe dos achados
- R1 (recomendado, não bloqueia) · A prova do re-review da volta 2 do FORGE-CHECK-LOTE (`b3b165c`) só existe na branch remota `melhoria/forge-check-lote`. Se a limpeza depois do merge (R-FLUXO) apagar essa branch, o commit deixa de ser alcançável e a develop fica com um parecer que aponta `9c09ae0` em vez do código mesclado. Sugestão para o integrador (E3.1) ou para o dono do pedido do lote: levar o parecer de `b3b165c` à develop por PR próprio, ou registrar o sha e o texto no pedido do lote, antes de apagar a branch; e, nas próximas levas, o parecer da última volta entra na branch antes do squash.
- R2 (recomendado, não bloqueia) · Duas linhas da seção [0.27.0] (S-16-PROMOCAO-DEVELOP e CI-POSTINSTALL-CLI) não terminam em ponto final, herdado dos fragmentos. Cosmético; não vale mexer no fechamento por isso.
