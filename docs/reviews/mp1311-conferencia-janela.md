---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-conferencia-janela
commit: 773e7e7aa9f87a8dfa14e308a0c1b167ecd0c06d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: melhorias-de-projeto-1311 (item 1, janela da conferência de entrega)

Head revisado 773e7e7a, classe C, `bin/forge-check`. Instância que não fez a entrega (E1.13).

## Achados
- A1 (recomendado) bin/forge-check:2543 · a docstring de `parecer_de_portao_da_branch` passou de 120 colunas nas linhas novas; quebrar no próximo toque.

## Sondas

## Parecer
Aprovado.

- Parecer disfarçado de código: o desconto em `etapa in ETAPAS_DE_CODIGO` mantém todas as condições do anexo do portão: pasta de parecer (`PASTA_E_REGRA`), fora de `com_controle`, frontmatter com `tipo`, `branch`, `pedido` e `parecer`, `commit:` igual ao `Revisar-sha:` de brief selado do portão certo (registro do Jarvis, não texto do autor) e sem veredito trocado. Código de produção fora de `docs/<portão>/` segue como escopo; o teste `test_parecer_de_outro_portao_na_etapa_qa_e_anexo_do_portao` e o mutante M1 fixam o alargamento só para as etapas de código.
- `--desde` só no commit do autor: exige estar em `revisados_do_autor` (brief selado de portão da mesma branch e pedido), ser ancestral do head, não ser ancestral do Base-sha e passar pela recusa de `pedido_na_entrega`. Os testes cobrem commit não revisado, fora da branch, na base e com pedido na entrega; M2 a M4 e M5 a M7 morrem.
- Evidência: `forge-mutante tests/mutantes/mp1311-conferencia-janela.json` M1..M7 todos mortos; `JanelaDaEntrega` e `ParecerDoPortao` (27 testes) OK. Tamanho: cerca de 124 linhas de código e teste, abaixo de 150. Suíte completa: CI do PR.
- Observação sem achado: o `--desde` revisado vale para qualquer portão da branch, não só o do papel que conferiu; coerente com o `Revisar-sha:` ser o commit que o portão leu.
