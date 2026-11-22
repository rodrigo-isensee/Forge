---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 3a4fd5c0582c5b0700a67fa04eb6a8877093c058
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E103.18, CONTADOR-DA-VERSAO, revalidação da 3ª volta)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0480-contador-versao.md`, intervalo 1593c1a1..3a4fd5c0, sem o que veio da develop; no domínio: `skills/fluxo-do-pedido/SKILL.md`, `tests/mutantes/v0480-contador-versao-5.json`, `tests/test_forge_contador.py`, `tests/test_reval_delta.py`. Parecer anterior: reprovado no head 1593c1a1 por A1.

Ferramentas citadas, sem refazer: a suíte inteira fica com o CI do PR #787 no head 3a4fd5c0. Rodado aqui só o do item: `tests.test_forge_contador` e `tests.test_reval_delta`, 35 testes, OK; e o mutante M36 (S1).

## A1 resolvido
- O caso real voltou: `changelog.d/README.md` em `test_conta_fragmentos_sem_readme_e_sobe_o_patch` e em `test_teto_da_configuracao`, com as mesmas asserções de antes.
- Caso novo de caixa mista: `test_readme_com_caixa_mista_nao_conta` (`changelog.d/Readme.md`, espera `1 de 20`).
- M36 declarado em `tests/mutantes/v0480-contador-versao-5.json` (`.lower()` removido) e morto por 3 testes (S1).
- A citação ficou em `CITACOES_CONHECIDAS` com a contagem exata do arquivo (`tests/test_forge_contador.py`: 2, motivo `nome`; as duas ocorrências são as linhas 90 e 117). É registro de nome sintético, no mesmo molde das outras entradas do `_NOME`; a guarda não ficou mais frouxa. Mexe na lista da guarda: o parecer de segurança sobre ela é do `security-engineer`, não daqui.

## Nenhum teste afrouxado
O delta não remove nem enfraquece asserção: troca dois nomes de arquivo sintéticos de volta para `README.md`, soma um teste e um mutante, e soma uma entrada com contagem exata à lista de citações conhecidas.

## Corte do item
`skills/fluxo-do-pedido/SKILL.md` voltou ao texto da develop: `git diff bfed8033 3a4fd5c0 -- skills/fluxo-do-pedido/` sai vazio. A linha "Contador da versão" saiu junto com o resto. O item fica só com o `bin/forge-contador` e os testes dele.

## Sondas
- S1 · cópia do head 3a4fd5c0 com bin/forge-contador:54 sem `.lower()`; `tests.test_forge_contador` · espera: falha · obtido: 25 testes, 3 falhas (`test_conta_fragmentos_sem_readme_e_sobe_o_patch`, `test_readme_com_caixa_mista_nao_conta`, `test_teto_da_configuracao`)

## Parecer
Aprovado no head 3a4fd5c0. O A2 do parecer anterior (recomendado, fora do delta) segue como cartão.
