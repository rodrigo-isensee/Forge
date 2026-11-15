---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-fabrica
commit: f30ac8d2f3edb92ef9b6b0bd81299c1b6b746ce0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: mp1311-pre-envio-fabrica

## Gatilhos
Toca `bin/forge-check` (geração de brief) e `bin/forge-testes`, controles do Forge (`R-SEGURANCA`). Sem segredo, sem rede nova, sem workflow.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Verificado no head f30ac8d2:
- `pqs_de_pre_envio` e `linha_do_ci_do_parecer` (`bin/forge-check` por volta de 8280-8313) só montam texto de brief; nada é executado pelo gerador. O número do PR vem de `pr_da_branch` com `int()` (8174), então não há injeção na linha `gh pr check`. A branch segue como argumento de lista, sem shell (8164).
- `forge-testes --texto` roda `unittest` com lista fixa em código (`TESTES_DE_TEXTO`), sem entrada do usuário nem shell; recusa combinação com outras opções.
- `CAMINHO_DE_CODIGO` é regex linear, sem risco de backtracking relevante.
- Sem `gh` ou sem rede, o brief degrada para texto sem afirmar CI verde (falha segura).
- Testes rodados localmente: `tests.test_pre_envio_brief` e `tests.test_testes_tocados`, 161 testes, OK (1 skip). Suíte inteira fica para o CI do PR (ainda sem PR da branch).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas externas não usadas (mudança só de texto e orquestração local).
