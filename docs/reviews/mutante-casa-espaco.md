---
tipo: review
contrato: 1
pedido: mutante-casa-espaco
branch: melhoria/mutante-casa-espaco
commit: 16beca149f3b033fc6c8149d1717d727c2e45af4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: mutante-casa-espaco

Pedido MUTANTE-CASA-ESPACO (FM1, PR 1), etapa E1.1 do MUTANTE-CASA-ESPACO-REV. Diff `042e5d8...16beca1` (c512d28, c17afb2, 16beca1).

## Achados
- A1 (bloqueante) tests/mutantes/mutante-casa-espaco.json:63 · C4 declarado equivalente, mas o próprio teste novo o mata: com `len(para)` fora, `test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam` dá erro (SyntaxError em vez de False). Trocar `equivalente` por `testes` com esse teste.
- A2 (recomendado) bin/forge-mutante:415 · "basta uma posição dentro do nó" pode ser lido como um byte só; o código exige o trecho inteiro dentro do nó em algum alinhamento possível. Sugestão: "basta um alinhamento com o trecho inteiro dentro do nó".

## O que foi conferido
- **Função `casa` (bin/forge-mutante:411-430).** Com `de = A+X+B` e `para = A+Y+B`, o máximo de bytes comuns é `comum = min(p+s, len(de), len(para))`; os alinhamentos válidos são `k` (tamanho de `A`) em `[comum-s, p]`, e o trecho mudado ocupa `[inicio+k, inicio+k+len(de)-comum)`. `primeira`/`ultima` intersectam esse intervalo de `k` com o do nó; a conta está certa. Sem sobreposição (`p+s <= min`), `comum-s = p` e a condição se reduz exatamente à antiga (`ini <= inicio+p` e `inicio+len(de)-s <= fim`), e o sufixo medido no `de` inteiro é igual ao medido depois do prefixo; logo o mutante comum que já casava não muda (o teste `test_casamento_pelo_intervalo_do_no_e_as_travas_do_de` segue verde).
- **Portão não afrouxa (DECISÃO TÉCNICA 2026-10-30 03:10).** Cada `k` aceito é uma decomposição real da troca, com o trecho inteiro dentro do nó; a mudança só alarga a escolha do alinhamento, não o tamanho do trecho. O que desliza para fora (`else yyyy` → `else yyyyy`) e o que remove mais que o nó (`aa e` → `e`) seguem `False` no teste novo; as travas de `de` único, 8+ não brancos e arquivo seguem antes do `ast`. O desvio do mecanismo em relação ao E1 do pedido é aceito: o objetivo do E1 é cumprido.
- **C4 (A1).** Rodei o C4 aplicado à mão numa worktree descartável: `FAILED (errors=1)`, `SyntaxError` de `k = q if else aa`. A própria justificativa admite a diferença (SyntaxError no lugar de False); no `--cobertura` isso vira rc 2 em vez da saída normal. Não é equivalente; é um mutante que o teste já mata e que a spec deixa de provar. Classe: equivalente declarado que o teste mata (requisito do E2: guardas novas com o vermelho antes do verde). Sem linha AR nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV); a classe fica registrada aqui.
- **Teste novo.** Cobre o ternário (inserção no fim do nó `f()`), o fim do nó numa compreensão (caso M6/M15), o deslize para fora e a remoção maior que o nó. Determinístico, sem I/O.
- **Teto M14.** `git diff --numstat --no-renames 042e5d8...16beca1`: `bin/forge-mutante` 8+3, `tests/test_forge_mutante.py` 8+0 = 19 de 150; spec, fragmento e `.md` ficam fora. Um comportamento só.
- **Changelog.** Fragmento `changelog.d/mutante-casa-espaco.md` presente; versão não mexida.
- **Neutralidade, custo, regras.** Nada de projeto, nada pago, `hooks/`, `tests/config.json` e `PROTEGIDOS` intocados.

## Saída das ferramentas (citada)
- `python3 -m unittest tests.test_forge_mutante`: 68 testes, OK.
- `bin/forge-mutante tests/mutantes/mutante-casa-espaco.json` (rev 16beca149f3b): C1, C2, C3, C5 e C6 morreram; C4 saiu como equivalente declarado; rc 0.
- `bin/forge-mutante --cobertura --base 042e5d8f73fc659615a4313c7213a661dfc32ce0`: a condição de bin/forge-mutante:425 coberta por C5; rc 0.
- shellcheck: sem shell no diff.

## Parecer
Reprovado por A1 só: a lógica do `casa` está correta e o portão não afrouxa. A volta é trocar, na spec, o campo `equivalente` do C4 por `testes` com `tests.test_forge_mutante.Cobertura.test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam` e rodar o `forge-mutante` de novo (o C4 deve sair `morreu`). A2 não devolve.
