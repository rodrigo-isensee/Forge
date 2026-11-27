---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-gerador-unico
commit: aae451ccb8dd8a651cce82ccba20af2a955e2f51
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (gerador único, #946, E48.2)

Escopo: 1ª rodada completa do diff `319a968d..aae451cc` (5 commits): `scripts/gerar-derivados.py`, `tests/test_gerar_derivados.py`, as specs `tests/mutantes/v0481-gerador-unico*.json`, a linha nova e as 5 frases encurtadas de `skills/engineering-practices/SKILL.md`, a linha do índice do Forge e o fragmento do changelog.

- ci: aae451ccb8dd8a651cce82ccba20af2a955e2f51 verde
- checks lidos (run 46062141853 do Revisar-sha): suíte 1/5 a 5/5, passos, python 3.14, verificações longas, instalação (python 3.14), teto de pulados e árvore provada verdes; `bateria (pareceres)` e `bateria` esperam os pareceres; `catraca` verde
- teste do item: `python3 -m unittest tests/test_gerar_derivados.py`, 10 testes, OK no head.
- mutantes: 12 declarados (M1 a M8 e M9 a M12, uma guarda por linha), todos mortos (`bin/forge-mutante --processos 1` nas duas specs); `--cobertura --base 319a968d`: toda condição do diff coberta.
- tamanho (H1): 71 linhas de código em `scripts/gerar-derivados.py`, docstring incluída; um comportamento; dentro do teto de 150.
- skill: as 5 frases encurtadas guardam cada regra (prevalência do `praticas.md`, escape só com comentário, devolução antes do review sem rodada nem volta de `R-QA` e conferida pelo Jarvis por `PQ-n`, item 12 do checklist, linha `AR-<n>` escrita pelo `tech-lead`); nenhum trecho removido aparece em `tests/config.json` nem em teste.

## Achados
- A1 (recomendado) scripts/gerar-derivados.py:55 · no `--conferir`, rc 1 do gerador vale como "desatualizado"; uma exceção do Python também sai 1, e o traceback some (sonda S1). O rc do script fica certo; a mensagem engana. Sugestão: o gerador imprime "desatualizado" na saída; conferir isso, senão "gerador vermelho" com a saída.
- A2 (recomendado) skills/engineering-practices/SKILL.md:57 · com "a linha" cortado, "o `tech-lead` a escreve" ficou sem antecedente feminino; "o `tech-lead` a grava" sobre "a linha `AR-<n>`" ou "o escreve" resolve.

## Parecer
**Aprovado.** O script faz o que o pedido diz: lista fechada de geradores chamados pelo caminho literal com `sys.executable -I`, cwd na raiz do script, sem `GIT_*` no ambiente e sem stdin; gerador ausente é avisado e pulado; "mudou" ou "sem mudança" por comparação de bytes do derivado; rc 1 com gerador vermelho nos dois modos; `--conferir` repassa a flag aos geradores, que não gravam; uso errado sai 2 antes de rodar qualquer gerador. Os dois geradores reais aceitam `--conferir` com rc 0/1, como o script supõe. Os testes usam raiz de brinquedo, ambiente limpo e `python3 -I`, cobrem cada ramo, e o teste do Forge real afirma o mínimo de 5 linhas. A1 e A2 são de mensagem e texto, sem regra perdida; viram cartão depois do merge. Commits em Conventional Commits em português, cada um coerente. Critério de reversão no PR (falhas de `test_indice_*` nos 14 dias seguintes).

Sonda S1 (prova do A1, recomendado): gerador falso `raise RuntimeError("quebrou de verdade")` no lugar de `scripts/indice-forge.py`, depois `gerar-derivados.py --conferir`; esperado "gerador vermelho (rc=1): ... RuntimeError"; obtido "docs/indice-forge.md: desatualizado; rode scripts/gerar-derivados.py", rc=1.
