---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: dc6bc47efb98f0f017510992325e629f64e29214
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E6.28, #878, G2.1 `forge-check parecer publicar`), volta por delta

Revalidação por delta da rodada reprovada em 841c14dc (E6.24; texto no git). Delta lido: `forge-check parecer delta` deste arquivo até dc6bc47e e `git diff 841c14dc..dc6bc47e`. O que é da branch (fora o que veio da develop pelos 3 merges, conferido pela comparação do diff próprio `merge-base..841c14dc` com `6cc4cd5a..dc6bc47e`): o `break` no `--` em `ultima_raiz`, 1 fixture nova, o mínimo de fixtures do lote de 8 para 9, o mutante M37 (e o ajuste dele em dc6bc47e), o ambiente do git em `tests/test_forge_pareceres.py`, a linha do índice e a união de `FORGE_CHECK` em `bin/forge-testes` na resolução do conflito (entra `test_forge_pronto` da develop e fica `test_forge_pareceres`). O resto do diff do intervalo veio da develop e já passou pelos portões dela.

Gatilhos: controles-do-forge, autorizacao, ci-cd.

O que aperta, o que é neutro, o que afrouxa:
- Aperta: `hooks/conformidade.py:1388` (`--` encerra a leitura da `--raiz`; a S1 da rodada anterior volta a barrar) e `tests/test_hooks.py:3126` (o mínimo do lote sobe de 8 para 9).
- Neutro: `tests/test_forge_pareceres.py:78` e `:336` (o git do teste com `sem_manutencao`, só junta chaves de manutenção; AR-4), `docs/indice-forge.md`, o M37 de dc6bc47e (só mantém o comentário na troca; AR-12) e a união em `bin/forge-testes`.
- Afrouxa: nada. Nenhuma fixture saiu, nenhuma asserção sumiu e nenhum mutante foi retirado.

## Achados

## Sondas

## Achados anteriores
- A1 da E6.24 (`ultima_raiz` lia depois do `--`): fechado em `hooks/conformidade.py:1388`. A S1 virou a fixture `tests/hooks/conformidade/contrib-publicar-raiz-depois-do-separador-no-forge-bloqueia.json` (código 2, `R-CONTRIB`), que passa no head. A correção é a mínima proposta, sem enfraquecer teste.
- M37: morto aqui numa cópia por `git archive` com a troca de dc6bc47e (`if False:` mantendo o comentário). `test_fixtures_do_publicar` falha só na fixture do separador.
- Caso vizinho do `break` conferido: um `--` usado como valor de outra opção antes de uma `--raiz=` (`--x -- --raiz=y`) não engana o hook, porque o argparse do Python 3.12 recusa a linha (rc 2, "expected one argument" ou "unrecognized arguments"). O hook para no `--` e a linha nem roda. Falha fechada.
- A1 do review E6.18 e A1/A2 da E6.16: seguem fechados (o delta próprio não toca `bin/forge-check` nem `bin/forge_pareceres.py`).

## Suíte e CI
Rodei aqui os módulos tocados: `tests.test_hooks.Hooks.test_fixtures_do_publicar` e `tests.test_forge_pareceres` (36 testes, OK). A bateria inteira fica com o CI. Run 45695317127 (CI) no head dc6bc47e: `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, as 10 partes da suíte (3.12 e 3.14), os dois `teto de pulados`, `instalação (python 3.14)` e `árvore já provada na develop` deram `success`. Falham só os jobs que esperam parecer. `bateria (pareceres)` falha porque os pareceres de review, QA e segurança da branch não aprovam no head (R-REVIEW, R-QA, R-SEGURANCA no log), e `bateria` é o agregador que cai por causa dela. A catraca (run 45695317364) falha com R-CONFORMIDADE porque a branch muda `bin/forge-check` e `hooks/conformidade.py`, que são controles, e isso só passa com o rótulo `afrouxa-regra` do dono, aplicado depois do último push. Não é falha de teste. O PR está `MERGEABLE`.
- ci: dc6bc47efb98f0f017510992325e629f64e29214 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. A lacuna fica registrada e nada foi instalado (`R-CUSTO`). A revisão foi estática, sem nenhuma chamada de escrita à API.
