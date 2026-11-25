---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 6d71827e0a25324caf731a6d17949b158ce7e348
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.24, code review por delta do #892)

Revalidação por delta, de `9fa5f832` (parecer anterior, aprovado, E14.19) a `6d71827e` (volta única E14.22). `forge-check parecer delta docs/reviews/v0481-docs-ok.md`: `revalida: sim` (`bin/forge-check` mudou depois do parecer). Delta lido: `git diff 9fa5f832..6d71827e`, com uma linha de código em `bin/forge-check`, o `de`/`para` do M6 em `tests/mutantes/v0478-clone-nome-unico.json` e os pareceres de QA e de segurança (docs, fora do meu domínio). O resto do diff da branch não mudou e segue o parecer anterior.

## Parecer
**Aprovado.**

- **`bin/forge-check:11241`:** `gravar =not` volta a `gravar = not`, só o espaço, sem mudar o comportamento; a linha sai do diff contra a base, o que fecha o A1 (recomendado) do parecer anterior e o A1 do QA. A spec `tests/mutantes/v046-pr-hook-prazo-2.json` M12 volta a achar o trecho uma vez.
- **`tests/mutantes/v0478-clone-nome-unico.json` M6:** `de` e `para` passam de `if` a `elif`, alinhados ao ramo `elif copia and valor_de_shell_seguro("raiz", copia):` de `bin/forge-check:9735`, que o diff da branch criou; a guarda e o teste declarado (`test_brief_sem_a_linha_com_caminho_fora_da_forma`) são os mesmos. Fecha o A2 do QA. O `if` da linha 9731 (com `etapa in ETAPAS_DE_PARECER`) segue coberto pelo M3 de `tests/mutantes/v0481-docs-ok.json`.
- **Mutantes, rodados no head `6d71827e`:** `forge-mutante --processos 1 --ids M6 tests/mutantes/v0478-clone-nome-unico.json`: `M6 · morreu · bin/forge-check:9735`. `--ids M12 tests/mutantes/v046-pr-hook-prazo-2.json`: `M12 · morreu · bin/forge-check:11241`. `--cobertura --base 220ba3fa`: `spec editada` (v0478-clone-nome-unico), `:9731` coberta por M3 e `:11239` por M1 e M2.
- **`--conferir --todas` igual à base:** a saída no head `6d71827e` e num checkout de `220ba3fa` tem as mesmas 26 linhas (`diff` vazio, rc 1 nos dois); nenhuma é do M6 nem do M12. O que resta são specs antigas com trecho repetido ou ausente, já presentes na base, fora deste pedido.
- **Ferramentas (citadas, não refeitas):** CI do #892 no head `6d71827e` em andamento na hora deste parecer; `suíte` partes 2/5 e 5/5, `bateria (passos)`, `bateria (verificações longas)` e `instalação` verdes; `bateria (pareceres)` e `catraca` vermelhas por faltarem os pareceres neste head e o rótulo do dono (`bin/forge-check` é controle, R-CONFORMIDADE). O merge depende do CI verde.
