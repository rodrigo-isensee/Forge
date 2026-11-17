---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-heredoc-palavra
commit: 55418634d158dda4f8693915d16162d03ebfe256
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047-hook-heredoc-palavra

Code review da E2.6 (HOOK-HEREDOC-PALAVRA-FP, classe C) no head 730261a5, base 5b1aacd5. Dois commits: f53efb93 (hook, fixtures, changelog, índice) e 730261a5 (mutantes).

## Revalidação (E2.56, head 55418634)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-heredoc-palavra.md`, intervalo 228d0083..55418634, sem o que veio da develop: 2 arquivos no domínio, `tests/mutantes/v047-hook-heredoc-fp.json` e `-2.json`. Junção da develop (006907f9, #637, sem conflito) pelo forge-fechar; `hooks/parecer.py` sem mudança no intervalo.
- M2: `de` passa a `OPCAO_DO_PYTHON.fullmatch(a) for a in opcoes` (parecer.py:218), `para` `True for a in opcoes`: mesma guarda (o python com script ou -c não é leitor da entrada).
- M14: `de` passa a `if leitor not in ("python", "dado") and not corpo_so_lido(dono)]` (parecer.py:1059), `para` `if leitor != "dado" and ...`: tira só a isenção do python, mesma guarda de antes.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 testes, OK. `bin/forge-mutante` nas duas specs (rev 55418634): M1-M4, M6-M16 `morreu`, nenhum `(erro)`, saída 0; M2 em parecer.py:218 e M14 em parecer.py:1059. Sem achado novo; parecer mantido.

## Revalidação (E2.50, head 228d0083)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-heredoc-palavra.md`, intervalo 76b50dc7..228d0083, sem o que veio da develop: 1 arquivo no domínio, `docs/hooks-fixtures.md`. Junção da develop (ba968580) pelo integrador, conflito só nesse índice gerado, resolvido rodando o script.
- `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`; as linhas mudadas são contagens e prefixos do corpus da develop (`agentes`, `conformidade`), sem mudança no código da branch.
- Entre 76b50dc7 e o pai 56e18e0a só entraram pareceres (qa, review, security). Sem achado novo; parecer mantido.

## Revalidação (E2.37, head 76b50dc7)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-heredoc-palavra.md`, intervalo 7185b64c..76b50dc7, 7 arquivos no domínio (hooks/parecer.py, ADR 0011, índice de fixtures, 3 fixtures novas, spec -2 de mutantes). Correção do A3 da segurança (E2.15) pela E2.32, commit 76b50dc7.
- hooks/parecer.py:281 passa a recusar `{` no nome do alvo (`*?[{`): `bin/l{s..s}` não vira dado. A chave só no diretório (`bi{n..n}/ls`) cai na guarda do nome de programa; `{a,b}` com duas palavras o bash recusa como redireção ambígua. Falha fechado, só perde liberação.
- 3 fixtures `heredoc-dado-alvo-com-chave-*-bloqueia` (no fim, no início, com grep) entram no corpus `heredoc-dado-*`, que o teste percorre com mínimo afirmado.
- M9 realinhado ao texto novo da linha e M12 novo (a chave sai do filtro) na mesma linha 281.
- ADR 0011:45, emenda v047 cita a chave com o exemplo; docstring de `corpos_de_dado` alinhada.
Verificações: `bin/forge-mutante tests/mutantes/v047-hook-heredoc-palavra-2.json` no head, 1 processo: M9, M10, M11 e M12 morreram. `bin/forge-mutante --cobertura --base 7185b64c`: linha 281 coberta por M9 e M12, sem guarda descoberta. Tamanho do delta: 2+2 em hooks/parecer.py e 11+1 na spec. Sem PR aberto, sem CI para citar. Sem achado novo.

## Revalidação (E2.14, head 7185b64c)
Delta lido: `forge-check parecer delta docs/reviews/v047-hook-heredoc-palavra.md`, intervalo 730261a5..7185b64c, 11 arquivos no domínio (hooks/parecer.py, ADR 0011, changelog, índice de fixtures, 5 fixtures novas, 2 specs de mutantes). Commits 11a96c7a, 142513b2, 7185b64c.
- A1 resolvido: `corpos_de_dado` devolve False com crase fora dos corpos (hooks/parecer.py:273) e com alvo sem valor literal (:278); 5 fixtures `heredoc-dado-*-bloqueia` (crase no alvo inteiro, no meio, com cat, com head, e alvo '') cobrem S1. A crase literal entre aspas fora dos corpos também recusa: falha fechado, só perde liberação.
- A2 resolvido: emenda v047 na ADR 0011:45 com motivo, limites, rótulo afrouxa-regra e critério de reversão.
- A3 resolvido: changelog.d/v047-hook-heredoc-palavra.md:2 fala dos programas da própria chamada e cita a crase.
Verificações: `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_dado_libera_e_bloqueia` no head, OK (4,3 s). `bin/forge-mutante` nas 2 specs, 1 processo: M1 a M11 morreram. `bin/forge-mutante --cobertura --base 730261a5`: linhas 273 e 278 cobertas por M10 e M11, sem guarda descoberta. Tamanho do delta: 8+2 em hooks/parecer.py. Sem PR aberto, sem CI para citar.

## Achados
- A1 (bloqueante) hooks/parecer.py:274 · alvo de redireção sem valor literal (crase: cat > `echo bin/ls`) vira nome "" e escapa da guarda do programa gravado; o bash grava bin/ls e o ls da chamada o roda (S1). Sugestão: alvo sem valor literal faz corpos_de_dado devolver False, com fixture.
- A2 (bloqueante) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:44 · afrouxa a opção D da ADR 0011 (corpo marcava, agora é dado; 4 fixtures de recusa viram libera) sem emenda: falta a linha v047 com motivo, limites, rótulo afrouxa-regra e critério de reversão, como na linha 44 (ADR 0011:90, R-DECISAO).
- A3 (recomendado) changelog.d/v047-hook-heredoc-palavra.md:2 · o texto diz "arquivo com o nome de um desses programas" (a lista); o código compara com os programas da chamada: cat > bin/ls seguido só de grep passa. Alinhe o texto ao código.

## Sondas
- S1 · cat > `echo bin/ls` <<'FIM' (corpo #!/bin/sh e git merge melhoria/x) FIM e ls, como fixture heredoc-dado-*-bloqueia · espera: rc 2 R-REVIEW (como heredoc-dado-grava-programa-da-chamada-bloqueia) · obtido: rc 0, hook libera
- S2 · no bash, cat > `echo bin/ls` <<'FIM' sobre bin/ls executável e PATH com bin/ na frente, depois ls · espera: o ls roda o corpo gravado · obtido: imprimiu a sentinela do corpo (o modo do arquivo se mantém, sem chmod)

## Parecer
Aprovado no head 76b50dc7 (revalidação E2.37, delta do A3 da segurança sem achado). Antes: aprovado no head 7185b64c (revalidação E2.14), A1, A2 e A3 resolvidos. Rodada anterior, no head 730261a5: reprovado por A1 e A2.

O que está certo: `corpos_de_dado` é pequena e legível, reaproveita `heredocs_simples`, `chamada_muda_o_corpo` e `programas_e_atribuicoes`; o novo tipo `dado` entra nos dois pontos certos (`marcas_da_chamada` e a lista `internos` de `conferir_linha`). As sondas de contorno que tentei seguem recusadas: alvo com aspas (`bin/'l's`), barra (`bin/l\s`), `>|`, `&>`, `$HOME/bin/ls`, `$X`, `$(echo bin/ls)`, `"`echo bin`/ls"`, `. ./f`, `./f`, `cat | sh`. `bin/{ls,x}` passa, mas o bash recusa a redireção ambígua: não é defeito.

A1: a guarda declarada pelo próprio autor (fixture `heredoc-dado-grava-programa-da-chamada-bloqueia`, mutante M7) é a do arquivo gravado com nome de programa da chamada; com a crase no alvo, `getattr(r.alvo, "valor", "")` dá `""` e a guarda não vê nada. Correção de lógica, volta ao autor: alvo sem `valor` literal tira a chamada do caminho de dado (falha fechado), fixture `-bloqueia` com crase e mutante na nova linha de guarda.

A2, a pergunta do brief: sim, é afrouxa-regra. As quatro fixtures (`texto-barra-heredoc-lido-e-ls` de HK3-PARECER e `heredoc-parecer-cat-e-wc`, `-echo-com-redirecao`, `-echo-em-segundo-plano` da 0.43.2) recusavam e passam a liberar, e o caminho de `cat` com `ls`, `wc`, `head`, `tail`, `grep`, `stat` sai da gramática positiva da opção D. O precedente do mesmo pedido (linha 44, HOOK-CONTRIB-HEREDOC-FP) registrou emenda; a linha 90 exige o rótulo. Precisa da nota na ADR 0011 com critério de reversão (sugestão: uma sonda em que o corpo dado como dado roda um comando de PR na mesma chamada) e do rótulo `afrouxa-regra` e destaque no título do PR.

Verificações: `tests/test_hooks_parecer_pasta.py` no head, numa cópia por `git archive` (5 testes, OK, 47 s); 15 sondas como fixtures temporárias no mesmo teste (só S1 é defeito). Mutantes: 9 declarados em 2 specs, um por guarda (M1 a M9), cobrindo as linhas de guarda mudadas; não rerrodei a mutação, cito a do autor. Sem PR aberto, então sem CI para citar. Tamanho: 34+8 linhas em `hooks/parecer.py` e 11 em `tests/*.py`, abaixo de 150, um comportamento só, corpus próprio `heredoc-dado-*` (10, os dois lados, mínimo afirmado). Falso de git ou gh: não há no diff.
