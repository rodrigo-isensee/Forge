---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d4960f8e7e8e428d5eea5726f380740be9f51081
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 E90.20 (SIEG-G1 G1.2a, `forge-check autorizacao gravar`, merge da develop E90.19)

Revalidação por delta do parecer aprovado e2c9b109 (head 3e653044). Li o `forge-check parecer delta`: intervalo `3e653044..d4960f8e`, sem o que veio da base; no domínio, `bin/forge-check`, `bin/forge-testes`, `docs/indice-forge.md` e `tests/pesos-d4.json`.

## Conferido
- **Resolução do conflito:** contra a develop (`fc488261`), `bin/forge-testes` ganha só a palavra `"test_autorizacao_gravar",` na tupla `FORGE_CHECK` (`:160`, `git diff --word-diff`), ao lado de `test_autorizacao`; as entradas novas da develop (`test_trilha_forge_check`, `test_prepush_lote_pp1`) ficaram. `tests/pesos-d4.json` é a versão da develop mais `"test_autorizacao_gravar": 3.7`, o mesmo peso da branch em e2c9b109; JSON válido, 289 chaves em ordem.
- **Sem mudança de lógica:** o diff `fc488261..d4960f8e` em `bin/forge-check` e `docs/indice-forge.md` é idêntico, linha a linha, ao da branch desde o merge-base `15936278` até e2c9b109; a junção não alterou nada do item.
- **Seleção:** `bin/forge-testes --listar bin/forge_autorizacao.py` aponta `test_autorizacao` e `test_autorizacao_gravar`.
- **Testes dos arquivos tocados:** `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao tests.test_pesos_teto tests.test_pesos_do_ci`: 67 testes, OK. A suíte inteira roda no CI.
- **Decisão 3a do dono (23/11 16:53):** `bin/forge_autorizacao.py` fora deste delta; segue o que o parecer e2c9b109 conferiu.
- **A1 anterior (recomendado, travessão e aspas curvas):** fora do delta; segue como cartão depois do merge.

## Parecer
Aprovado (`R-REVIEW`). A resolução é a versão da develop mais a entrada do item, sem mudança de lógica.
