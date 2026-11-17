---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-heredoc-palavra
commit: 730261a5406e2269c9bb40cb747bc2e989e18f5d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047-hook-heredoc-palavra

Code review da E2.6 (HOOK-HEREDOC-PALAVRA-FP, classe C) no head 730261a5, base 5b1aacd5. Dois commits: f53efb93 (hook, fixtures, changelog, índice) e 730261a5 (mutantes).

## Achados
- A1 (bloqueante) hooks/parecer.py:274 · alvo de redireção sem valor literal (crase: cat > `echo bin/ls`) vira nome "" e escapa da guarda do programa gravado; o bash grava bin/ls e o ls da chamada o roda (S1). Sugestão: alvo sem valor literal faz corpos_de_dado devolver False, com fixture.
- A2 (bloqueante) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:44 · afrouxa a opção D da ADR 0011 (corpo marcava, agora é dado; 4 fixtures de recusa viram libera) sem emenda: falta a linha v047 com motivo, limites, rótulo afrouxa-regra e critério de reversão, como na linha 44 (ADR 0011:90, R-DECISAO).
- A3 (recomendado) changelog.d/v047-hook-heredoc-palavra.md:2 · o texto diz "arquivo com o nome de um desses programas" (a lista); o código compara com os programas da chamada: cat > bin/ls seguido só de grep passa. Alinhe o texto ao código.

## Sondas
- S1 · cat > `echo bin/ls` <<'FIM' (corpo #!/bin/sh e git merge melhoria/x) FIM e ls, como fixture heredoc-dado-*-bloqueia · espera: rc 2 R-REVIEW (como heredoc-dado-grava-programa-da-chamada-bloqueia) · obtido: rc 0, hook libera
- S2 · no bash, cat > `echo bin/ls` <<'FIM' sobre bin/ls executável e PATH com bin/ na frente, depois ls · espera: o ls roda o corpo gravado · obtido: imprimiu a sentinela do corpo (o modo do arquivo se mantém, sem chmod)

## Parecer
Reprovado por A1 e A2.

O que está certo: `corpos_de_dado` é pequena e legível, reaproveita `heredocs_simples`, `chamada_muda_o_corpo` e `programas_e_atribuicoes`; o novo tipo `dado` entra nos dois pontos certos (`marcas_da_chamada` e a lista `internos` de `conferir_linha`). As sondas de contorno que tentei seguem recusadas: alvo com aspas (`bin/'l's`), barra (`bin/l\s`), `>|`, `&>`, `$HOME/bin/ls`, `$X`, `$(echo bin/ls)`, `"`echo bin`/ls"`, `. ./f`, `./f`, `cat | sh`. `bin/{ls,x}` passa, mas o bash recusa a redireção ambígua: não é defeito.

A1: a guarda declarada pelo próprio autor (fixture `heredoc-dado-grava-programa-da-chamada-bloqueia`, mutante M7) é a do arquivo gravado com nome de programa da chamada; com a crase no alvo, `getattr(r.alvo, "valor", "")` dá `""` e a guarda não vê nada. Correção de lógica, volta ao autor: alvo sem `valor` literal tira a chamada do caminho de dado (falha fechado), fixture `-bloqueia` com crase e mutante na nova linha de guarda.

A2, a pergunta do brief: sim, é afrouxa-regra. As quatro fixtures (`texto-barra-heredoc-lido-e-ls` de HK3-PARECER e `heredoc-parecer-cat-e-wc`, `-echo-com-redirecao`, `-echo-em-segundo-plano` da 0.43.2) recusavam e passam a liberar, e o caminho de `cat` com `ls`, `wc`, `head`, `tail`, `grep`, `stat` sai da gramática positiva da opção D. O precedente do mesmo pedido (linha 44, HOOK-CONTRIB-HEREDOC-FP) registrou emenda; a linha 90 exige o rótulo. Precisa da nota na ADR 0011 com critério de reversão (sugestão: uma sonda em que o corpo dado como dado roda um comando de PR na mesma chamada) e do rótulo `afrouxa-regra` e destaque no título do PR.

Verificações: `tests/test_hooks_parecer_pasta.py` no head, numa cópia por `git archive` (5 testes, OK, 47 s); 15 sondas como fixtures temporárias no mesmo teste (só S1 é defeito). Mutantes: 9 declarados em 2 specs, um por guarda (M1 a M9), cobrindo as linhas de guarda mudadas; não rerrodei a mutação, cito a do autor. Sem PR aberto, então sem CI para citar. Tamanho: 34+8 linhas em `hooks/parecer.py` e 11 em `tests/*.py`, abaixo de 150, um comportamento só, corpus próprio `heredoc-dado-*` (10, os dois lados, mínimo afirmado). Falso de git ou gh: não há no diff.
