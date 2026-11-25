---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 2259b235acc1128432428bfa3723bd48a1610c55
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.48, code review por delta do #892)

Revalidação por delta, de `6d71827e` (parecer anterior, aprovado, E14.24) a `2259b235` (2ª volta E14.43, autorizada pelo dono em 25/11, G1.1). `forge-check parecer delta docs/reviews/v0481-docs-ok.md`: `revalida: sim` (`tests/mutantes/v0481-docs-ok.json` mudou depois do parecer). Delta lido: `git diff 6d71827e..2259b235`, com código só em `tests/test_forge_copia.py` (um teste) e `tests/mutantes/v0481-docs-ok.json` (M5); o resto são os pareceres de QA e de segurança, fora do meu domínio. `bin/forge-check` não mudou no delta e segue o parecer anterior.

## Parecer
**Aprovado.**

- **`tests/test_forge_copia.py:796`:** `test_brief_de_parecer_sem_a_linha_com_caminho_fora_da_forma` repete o caso do HOME com espaço nas três etapas de `ETAPAS_DE_PARECER` (review, seguranca, qa) e afirma que o brief não traz `CLONE-NOME-UNICO` nem `--revisao`. O controle positivo já existe (`test_brief_de_parecer_cria_o_clone_de_revisao` exige o `--revisao` com HOME limpo), então a ausência não passa por vazio. Teste de comportamento (gera o brief), não lê a fonte. Fecha o A1 (recomendado) da segurança.
- **`tests/mutantes/v0481-docs-ok.json` M5:** `de` igual à linha `bin/forge-check:9731`, `para` sem `valor_de_shell_seguro`, teste declarado o novo. Um mutante por guarda.
- **Rodado no head `2259b235`:** `python3 -m unittest tests.test_forge_copia.BriefSugereACopia`: 13 testes, OK. `forge-mutante --processos 1 tests/mutantes/v0481-docs-ok.json`: M1 e M2 morreram (`:11239`), M3 e M5 (`:9731`), M4 (`:9735`). `--cobertura --base 220ba3fa`: `:9731` coberta por M3 e M5, `:11239` por M1 e M2.
- **Ferramentas (citadas, não refeitas):** CI do head `2259b235` (run 45598108933): suíte 3.12 e 3.14 partes 1 a 5, `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, teto de pulados e árvore provada verdes; vermelhas só `bateria (pareceres)`, `bateria` e `catraca` (pareceres e o rótulo `afrouxa-regra` do dono, por `bin/forge-check` ser controle, R-CONFORMIDADE). O head remoto `3fd616cd` só acrescenta o parecer de QA.
- ci: 2259b235acc1128432428bfa3723bd48a1610c55 verde
