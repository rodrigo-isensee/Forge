---
tipo: review
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido-p2
commit: 11a3bdbaac2c6f53b80dcad437bcd3e9fb2fab38
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-01
---
# Review: heredoc-rapido (passo 2)

Etapa E1.8 (instância revisora, não a autora). Diff lido: `299f01f..11a3bdb`, o que o passo 2 acrescenta à develop atual (o passo 1, #417, já está nela). Conferido contra o desenho `docs/propostas/heredoc-rapido.md` (b, último parágrafo) e os controles C-1 a C-8 de `docs/security/ameacas/heredoc-rapido-passo2.md`. O parecer anterior neste arquivo era do passo 1 (branch `melhoria/heredoc-rapido`) e foi substituído por este.

## O que a branch entrega
Item E1, passo 2: a linha marcada que o `tirar_heredocs` lê fica menor (marca `__fh<pos>__` no lugar de `__forge_heredoc_<pos>__`, com uma fonte única: `marca()` escreve e `MARCAS` procura, `hooks/_comum.py:847-853`), e a `aspa_escapada` passa a ser lida na linha sem marcas (`resto`), cuja leitura o chamador faz de qualquer jeito (`leituras(..., sem_marcas=)`, `:827` e `:1753`). Nenhum teto sobe: o teste do orçamento segue com 5,0 s e ganha as formas `x=$(` e `|` do C-7.

## M14
`git diff --numstat --no-renames origin/develop...11a3bdb`: `hooks/_comum.py` 23+10, `tests/test_hooks.py` 24+3, total 60 linhas que contam; ficam fora o fragmento `changelog.d/`, as seis fixtures de `tests/hooks/conformidade/` e a spec `tests/mutantes/heredoc-rapido-p2.json`. Abaixo de 150, sem linha de exceção (nem cabe: mexe em `hooks/`). Um comportamento, uma classe em `hooks/`: a leitura da linha marcada no `tirar_heredocs`, com corpus próprio (C-8 a a f). Cumpre.

## Controles do modelo de ameaças, lidos no diff
- C-1 (oráculo diferencial): rodei, no mesmo processo, o `tirar_heredocs(..., com_gravado=True)` de `299f01f` e o de `11a3bdb` sobre 597 linhas (todas as fixtures com `<<` e uma matriz de 13 posições × 5 mecanismos × 7 donos, com `$(`, `"$(`, `<(`, `eval`, composto, `#` com aspa, `\`⏎, `|`⏎, `$'a\'b'`, operador colado e marca escrita pela pessoa). Uma diferença só, na marca escrita pela pessoa (`echo __fh21__ && cat <<'E' | sh`): o dono passa de `sh cat sh` para `sh echo cat sh`, isto é, **maior**, o que o C-1 aceita (a palavra igual à marca só junta texto ao dono). Nenhuma diferença em `resto`, `gravado` nem nos corpos.
- C-2: a marca é `[A-Za-z0-9_]`, começa por `_`, sem `=`, fora de `COMPOSTOS`, cercada de espaço, única por posição; os quatro usos saem de `marca()`/`MARCAS` (grep: nenhum `__forge_heredoc_` sobra em `hooks/`, `bin/` ou `tests/*.py`). O teste `test_marca_do_heredoc_e_palavra_comum_entre_espacos` (`tests/test_hooks.py:1682`) prova isso na linha marcada real.
- C-3: o caminho `trechos=None` e o `opaco`/`ilegivel` não mudaram no diff.
- C-4 (T2) e C-6 (T4): fora do diff; não há recorte nem cache novo.
- C-5 (T3): só a `aspa_escapada` vem do `resto`; `comentario_ambiguo`, `corpos_se_leem` e `comandos` continuam sobre a marcada. A troca é segura: `marcada` é o `resto` com uma palavra `[A-Za-z0-9_]` inserida depois de um espaço, que não abre `$'…'` nem fica dentro de um (o `<<` dentro de aspas não é heredoc). O oráculo acima confirma. O mutante P4 está declarado equivalente na spec com essa justificativa, que aceito.
- C-7: o teste do orçamento cobre "um por linha", `&&`, `x=$(` (recusa pelo teto de palavras, com a mensagem fixada) e `|`. A forma com `#` (3000 heredocs, ~20 s) ficou de fora por decisão do dono (P-HEREDOC-COMENTARIO = B, pedido heredoc-comentario); não é deste PR.
- C-8: as fixtures (a) a (f) estão no corpus e recusam; (g) está na spec de mutantes (P1 marca sem espaços, P2 marca com `=`, P3 condição invertida). Mutantes "dono vazio" e "recorte por linha física" não se aplicam: o diff não toca nesses caminhos.
- Achado de segurança novo: nenhum. O review de segurança é a E1.9 (`docs/security/`), não refeito aqui.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks.Hooks.test_marca_do_heredoc_e_palavra_comum_entre_espacos tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`: `Ran 3 tests in 188.448s` `OK` (local, load 5,5 a 9,1).
- Mutação (`bin/forge-mutante tests/mutantes/heredoc-rapido-p2.json`): o autor relatou P1 a P3 mortos na E1.7 (entrega conferida 4384236); a medida no runner e a rodada de mutantes do QA são da E1.10.

## Achados
- A1 (recomendado) hooks/_comum.py:1753 · o P4 é equivalente só pelo argumento de que a marca não muda a aspa_escapada; um teste que compare palavras_do_texto(marcada) e (resto) na matriz do C-1 deixaria essa premissa provada na suíte, não só no parecer.
- A2 (recomendado) hooks/_comum.py:847 · a marca curta torna mais provável a palavra igual escrita pela pessoa; o efeito é só dono maior (fixture C-8 d e oráculo), sem bypass. Registrado para a E1.9 decidir se basta.

## Parecer
Aprovado. O passo 2 cumpre o desenho e a M14 (60 linhas, um comportamento, uma classe em `hooks/`), não sobe teto e o oráculo diferencial contra a base não acha dono menor. A1 e A2 são recomendações e não devolvem.
