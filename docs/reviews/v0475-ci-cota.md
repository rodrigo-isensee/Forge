---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: e0ac850854ef8d5efc64507f04379864c893f803
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.58, branch melhoria/v0475-ci-cota)

Diff `2fa505d7...e0ac8508`: `bin/forge-cota-ci` (novo, 95 linhas), `tests/test_cota_ci.py` (88), `tests/mutantes/v0475-ci-cota.json` (11 mutantes), skills `ci-cd` e `esperar-estado`, fragmento `changelog.d/v0475-ci-cota.md`. Classe C pelo `forge-check pr` (sensível da catraca: `bin/forge-cota-ci`).

## Achados
- A1 (bloqueante) bin/forge-cota-ci:37 · R-QA: a catraca do CI barra o head; 11 guardas sem mutante (:22, :32, :37, :62, :63, :64, :76, :78, :81, :85, :94). Declare um mutante por guarda (passou de 8, `v0475-ci-cota-2.json`) ou isente com motivo; ramos :22, :37 e :78 sem teste de falha.
- A2 (recomendado) bin/forge-cota-ci:84 · o motivo do último endpoint apaga o do primeiro: usuário com 403 (escopo) e org com 404 imprime só o 404, e o dono perde a pista do escopo. Junte os motivos dos dois endpoints.
- A3 (recomendado) bin/forge-cota-ci:77 · FORGE_COTA_CI_ENDPOINT não é usado por teste nenhum (o teste o apaga) e, sem dono, imprime `gh api /users//settings/...`. Use-o num teste ou retire-o.
- A4 (recomendado) bin/forge-cota-ci:81 · o endpoint legado `settings/billing/actions` some nas contas da cobrança nova do GitHub (o novo é `settings/billing/usage`; não conferi contra a API, sem rede aqui). Nelas o aviso vira sempre `não verificável`. Confira e registre no PR.

## Sondas
- S1 · `regra_guardas_dos_hooks('.', '2fa505d7', 'e0ac8508')` de tests/catraca.py · espera: lista vazia · obtido: `R-QA: guarda de bin/forge-cota-ci mudada sem mutante declarado: sem mutante · :22 ... e mais 6`

## Parecer
Reprovado por A1. A catraca (`tests/catraca.py`, regra MUTANTES-SPEC-HOOKS) é check do CI e reprova este head. Rodei a mesma regra localmente (S1) e o `bin/forge-mutante --cobertura --base 2fa505d7` lista as 11 guardas que faltam. O autor devia ter rodado a cobertura antes do envio (V2). Os 11 mutantes declarados morrem todos (`bin/forge-mutante tests/mutantes/v0475-ci-cota.json`: M1 a M11 `morreu`), e o `tests.test_cota_ci` passa (11 testes OK). Faltam teste e mutante nos ramos de falha `resposta inesperada` (:37), `dono desconhecido` (:78) e origin fora do GitHub (:22).

O resto está correto. A ferramenta faz só leitura por `gh api` GET, sem token nem escopo novo (`R-CUSTO`). O limite é estrito (80% exato não avisa). Booleano não conta como número, e franquia zero não divide. Sem permissão, a saída é `não verificável` com o comando para o dono. O texto das skills é curto e cita o ID da regra. A segurança aprovou em 9ee6e990; cito o parecer sem refazê-lo.

Para o PR (sem achado de código):
- `git diff --numstat` dá 183 linhas de código e teste (95 + 88), acima da orientação de 150. O corpo do PR precisa da linha `teto: excedido, 183 linhas, <motivo>` (M14).
- O commit f5f96f56 tem o `Co-Authored-By` na mesma linha do assunto, sem linha em branco. O squash do merge resolve isso se o título do PR vier limpo.
- Os commits citam E3.42, a etapa do autor; está coerente.

Na volta, revalido pelo delta (`forge-check parecer delta`).
