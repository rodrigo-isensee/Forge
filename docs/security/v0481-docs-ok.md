---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 6d71827e0a25324caf731a6d17949b158ce7e348
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.26, #892, classe C, volta por delta)

Gatilhos: controle do Forge (saída do `forge-check docs`, portão dos pareceres), texto do brief dos portões (cópia do revisor), specs de mutante das guardas.

## Delta lido
`forge-check parecer delta` de `9fa5f83..6d71827e` (E14.22): no domínio só `bin/forge-check`; fora, `tests/mutantes/v0478-clone-nome-unico.json` (lido mesmo assim, é a spec da guarda). Os commits de parecer do intervalo (review, QA, o meu anterior) não tocam código. Já lido na rodada anterior: o resto do diff `220ba3fa..9fa5f83` (ela fica no git). Achados anteriores: nenhum bloqueante; a observação de estilo `gravar =not` foi corrigida neste delta.

- **`bin/forge-check:11241` (neutro):** só o espaço em `gravar = not`; a expressão é a mesma. O M12 de `tests/mutantes/v046-pr-hook-prazo-2.json` volta a casar uma vez e morre (`forge-mutante ... --ids M12`: `M12 · morreu · bin/forge-check:11241`).
- **`tests/mutantes/v0478-clone-nome-unico.json` M6 (aperta):** o `de` passa ao ramo `elif copia and valor_de_shell_seguro("raiz", copia):` (`bin/forge-check:9735`), casa uma vez e morre (`M6 · morreu · bin/forge-check:9735`). Mutantes do pedido (`tests/mutantes/v0481-docs-ok.json`, M1 a M4): todos morrem no `6d71827e`.
- **`forge-mutante --conferir --todas`:** saída do `6d71827e` igual à da base `220ba3fa` (mesmas 26 linhas, rc 1 nas duas, todas de specs antigas fora deste pedido: v0457 M20 e z075 M1/M2 entre elas); nenhuma de v0478 nem de v046. Só aperta ou neutro.

## Achados
- A1 (recomendado) bin/forge-check:9731 · o ramo de revisão (COPIA-REVISAO) tem a guarda valor_de_shell_seguro do caminho, mas nenhum teste a mata: tirá-la sobrevive à classe BriefSugereACopia. Antes do split o M6 cobria todas as etapas; agora só o elif. Falta teste e mutante para etapa de parecer.

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:9731`; sonda local com uma spec em arquivo (troca `if copia and valor_de_shell_seguro("raiz", copia) and etapa in ETAPAS_DE_PARECER:` por `if copia and etapa in ETAPAS_DE_PARECER:`, testes `tests.test_forge_copia.BriefSugereACopia`): `S1 · sobreviveu · bin/forge-check:9731`. Caminho de ataque: hoje nenhum, a guarda está no código; o risco é a regressão silenciosa, quem editar esse ramo pode tirá-la sem teste falhar, e um caminho de cópia fora da forma de shell iria cru ao comando `forge-copia clone ... --revisao` que o revisor copia do brief. Severidade baixa. Correção mínima: o caso de `test_brief_sem_a_linha_com_caminho_fora_da_forma` repetido com etapa de parecer (review, seguranca ou qa), e um mutante M5 em `tests/mutantes/v0481-docs-ok.json` com o `de` da linha 9731 e o `para` acima. Esforço P. Dono: o autor do #892 (`bin/forge-check` e testes).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `forge-mutante` (M6, M12, a spec do pedido, `--conferir --todas` no head e numa cópia da base) e a sonda S1. A suíte inteira é do CI do #892 no `6d71827e`; o merge depende dele verde.
