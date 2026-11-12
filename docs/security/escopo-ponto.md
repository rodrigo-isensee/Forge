---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 0a0a7c808607535ddfe5e2eaf715a9340d7f8b8b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: escopo-ponto (E23.54, volta por delta)

Revalidação por delta `73e4848c..0a0a7c80` (E23.52) do parecer da E23.50. A7 e A8 estão corrigidos sem afrouxar nada: `veredito_trocado` roda `rev-list --full-history` e busca na pasta do portão do `tipo` com as subpastas; S6 e S7 refeitas no head dão rc 1, e as variantes pedidas (merge octopus nas duas ordens, ramo lateral com renomeação, link simbólico, parecer fora da pasta com o `tipo:` de um portão) também. Sobra uma variante da mesma família que nenhuma volta cobriu, a janela da busca: ela começa no Desde, e o reprovado commitado e apagado antes da última entrega conferida não é visto (A10, S8). Regride em relação à develop e bloqueia esta branch.

## Gatilhos
`R-SEGURANCA`: controle do Forge (a conferência de entrega decide o que é escopo da entrega e o que é anexo de portão).

## Achados
- A10 (bloqueante) bin/forge-check:2562 · a busca do veredito trocado começa no Desde (de), não no Base-sha: x.md reprovado commitado e apagado antes da última conferida some da janela; y.md aprovado com o mesmo commit: sai anexo do portão, rc 0 (S8)
- A6 (recomendado) bin/forge-check:2240 · cartão para a versão seguinte, furo anterior a esta branch: os filtros L08 e G2 (:2470) confiam na origin/develop local na etapa codigo; reescrita por git update-ref, escondem do escopo o arquivo fora do declarado (S4, S5)
- A9 (recomendado) bin/forge-check:1610 · cartão: o pr escolhe o parecer por (data, nome) e confia que a entrega recusou o forjado; defesa em profundidade: recusar o parecer cujo commit: tem outro veredito noutro arquivo da pasta na história da branch

## Sondas
- S8 · tests: x.md reprovado (commit R) sobre o revisado C; conferida C; volta 2 apaga x.md e cria docs/notas/b.md, conferida D; volta 3 cria y.md aprovado com commit: C; entrega --etapa codigo · espera: rc 1, y.md fora do declarado · obtido: rc 0, ok (anexo do portão) "docs/reviews/y.md"

## Detalhe dos achados
**Corrigidos nesta volta (refeitos no head, numa worktree destacada própria).**
- A7: `bin/forge-check:2345` usa `rev-list --full-history`. S6 (merge `--no-ff` do ramo lateral que apaga o x.md): rc 1, `fora do declarado no brief "docs/reviews/y.md"`. Variantes, todas rc 1 com y.md fora: merge octopus com o commit do revisor como primeiro pai e como último pai; ramo lateral cujo merge faz `git mv x.md y.md` e troca o veredito; ramo lateral com renomeação cruzada (o forjado nasce em `docs/notas/y.md` e o merge o move para `docs/reviews/y.md`, levando o x.md para `docs/notas/`). Testes `test_merge_de_ramo_lateral_que_apaga_o_reprovado_segue_fora` e `test_merge_com_o_ramo_lateral_como_primeiro_pai_segue_fora`; mutante M34.
- A8: `bin/forge-check:2344` toma `PASTA_E_REGRA[tipo][0]` e `ls-tree -r` (`:2349`). S7 (`docs/reviews/sub/y.md` com o x.md apagado antes): rc 1, sub/y.md fora. O `tipo` vem do prefixo do caminho (`:2541`), nunca do frontmatter, então a busca não depende de texto do autor. Teste `test_parecer_em_subpasta_do_portao_com_o_reprovado_apagado_segue_fora`; mutante M35.
- Link simbólico: `docs/reviews/sub` como link para `../notas` (com `docs/notas/y.md` aprovado, no escopo declarado) dá `fora do declarado no brief "docs/reviews/sub"`; `docs/reviews/y.md` como link para `../notas/y.md` dá y.md fora. O `git show` lê o alvo do link, sem frontmatter, e a função falha fechada. rc 1 nos dois.
- Parecer fora da pasta do portão com `tipo: review` e o `commit:` revisado: `docs/notas/y.md` passa como declarado no brief (não é parecer para o `pr`, que só lê a pasta do portão; sem ganho); `docs/reviewsX/y.md` e `docs/Reviews/y.md` saem fora do declarado (o prefixo exige a barra e casa a caixa). rc 1.

**A10, média (bloqueante: defeito provado no controle desta branch, com gatilho; regressão, a develop não tem o anexo do portão).** Evidência: `parecer_de_portao_da_branch` recebe `de` (`bin/forge-check:2562`), que é `valido or base_sha` (`:2466`), o Desde calculado da última `entrega conferida` da branch. `veredito_trocado` (`:2338`) só lê o `ls-tree` de `de` e os commits de `de..head` (`:2345`). Caminho de ataque: o revisor commita `docs/reviews/x.md` reprovado (`commit: C`, o Revisar-sha selado). Na volta seguinte o autor (tech-lead, que escreve em `docs/reviews/`) apaga o x.md junto com uma mudança declarada; a conferência dessa volta usa Desde C, e o x.md não existe nem em C nem no head, então nem aparece no escopo: rc 0, e o Jarvis grava `entrega conferida D` (S8, primeira parte). Na volta depois dessa, o autor commita `docs/reviews/y.md` com `branch:` e `pedido:` iguais, `commit: C` e `parecer: aprovado`; o Desde é D, o `ls-tree` de D não tem o x.md e o commit do revisor está antes de D: rc 0, `ok (anexo do portão)` (S8). No `forge-check pr` o y.md é o único parecer da pasta e é escolhido (`:1610`), como no A7. Correção mínima: a janela de `veredito_trocado` é a branch inteira, não a volta: passar `base_sha` em vez de `de` na chamada de `:2562` (o `rev-list --full-history base_sha..head` e o `ls-tree` do Base-sha). Provado numa cópia do head com só essa troca: S8 dá rc 1 (`fora do declarado no brief "docs/reviews/y.md"`), S6 e S7 seguem rc 1, e `tests.test_selo_e_entrega` com `tests.test_conf_escopo` seguem verdes (89 OK). Teste: S8 (duas conferidas, a do meio apagando o x.md). Mutante: voltar `base_sha` para `de` nessa chamada. Esforço P. Dono: tech-lead.

Nota de método: A5, A7, A8 e A10 são a mesma família (a busca do veredito trocado não vê a versão do revisor). As dimensões que a matriz da E23.42 devia ter trazido, para fechar a família de uma vez: posição do commit do revisor (dentro da volta, antes do Desde), topologia (linear, merge de dois pais nas duas ordens, octopus), caminho (mesmo arquivo, outro arquivo, subpasta, renomeação, link simbólico) e o campo do frontmatter (branch, commit, tipo). Com o A10 corrigido, as combinações sondadas nesta volta falham fechado; antes do Base-sha não há commit da branch.

**A6 (sem mudança, cartão).** O texto da E23.42 vale. Cartão: "L08/G2 confiam na origin/develop local na etapa codigo". Dono: tech-lead.

**A9 (cartão).** O A10 é o segundo furo da entrega que o `pr` herdaria; a defesa em profundidade da E23.50 vale (o `pr` recusa o parecer vigente quando outro arquivo da pasta, em qualquer commit da branch, tem o mesmo `commit:` e `branch:` com outro `parecer:`). Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lido: `forge-check parecer delta` (só `bin/forge-check` no domínio) e o diff de `tests/test_selo_e_entrega.py` e dos mutantes M34 e M35. Rodado no head, numa worktree destacada própria: `tests.test_selo_e_entrega` e `tests.test_conf_escopo` (89 testes, OK) e as sondas S6, S7, S8 e as variantes acima, numa subclasse de `ParecerDoPortao` fora da árvore. Os mutantes M1 a M35 e a cobertura são do QA. Varreduras de segredos e de workflow não se aplicam (sem segredo nem workflow no diff).
