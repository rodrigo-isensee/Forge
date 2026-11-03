---
tipo: revisao-seguranca
contrato: 1
pedido: ci-suite-no-teto
branch: melhoria/ci-suite-no-teto
commit: 1effb9e26ca8dc9956f29a1426717ef9ebae115f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: ci-suite-no-teto

## Gatilhos
Controle do Forge: workflow em `.github/` (`R-SEGURANCA`). Custo: `R-CUSTO`.

## Achados

## Detalhe dos achados
Diff 1b6f418...1effb9e conferido: em `.github/workflows/ci.yml` mudam só três valores de `timeout-minutes` (linhas 26, 45 e 76: 10 para 20, 15 para 25, 15 para 25). Nenhum `if:`, `permissions:`, `continue-on-error`, passo, job, teste ou gate foi tocado; as ações seguem fixadas por SHA.
Janela de abuso: o teto maior vale para jobs que só rodam a suíte e as varreduras locais do repositório, sem espera por recurso externo nem segredo novo; o ganho de um autor malicioso de PR seria no máximo alguns minutos a mais de runner, sem acesso ampliado (o `permissions:` é o mesmo). Custo: em repositório que roda em runner hospedado, o teto só limita o pior caso e a execução normal não muda; nada pago é adicionado (`R-CUSTO`).
Teste: `tests/test_catraca.py:2696` afirma `["20","25","25"]` na ordem dos jobs, o que ancora os valores. `python3 -m unittest tests.test_catraca.Workflows`: 6 testes, OK.
Fragmento `changelog.d/ci-suite-no-teto.md`: sem dado sensível.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária para esta mudança (só valores numéricos); `actionlint`/`zizmor` rodam no CI.
