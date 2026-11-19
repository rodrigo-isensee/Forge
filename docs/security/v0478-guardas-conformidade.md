---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: 40dc5f4f1c305481e7b7657626aaadac513fd100
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (E1.19, revalidação no head 40dc5f4f e pergunta do dono "só aperta?")

Delta lido (`forge-check parecer delta`): `f36dad1a..40dc5f4f`; no domínio, `hooks/conformidade.py` (uma linha, `:2293`), `docs/hooks.md` (a frase do `busybox`) e `tests/test_conformidade_verde.py` (`AtualizacaoAtrasDoBusybox`, `:621`). Rodada anterior (E1.17, D1 a D3, P1 a P3, S19, S20) no git, em `1ed45d9d`.

Gatilhos: hook de conformidade (controle de escrita), estado do hook agentes (teto, R-TETO), falha fechada.

Estado dos achados anteriores: A6 fechado (`:2293` varre as palavras originais com `atualizacao`, sem `so_binarios`, a mesma chamada que a base fazia com o `busybox` em `ENVOLVEDORES`; o `toybox` ganha a varredura); A7 e A3 seguem recomendados, sem mudança.

## Só aperta?
**Não.** Duas coisas aceitam o que a `origin/develop` recusava:
- **P2, aceito pelo dono** (DECISÃO DO DONO 2026-11-19 09:44): com a sessão no clone, o limite de agentes vem só do `.forge/config.json` da raiz da sessão (protegido pela A3); o da worktree, mais estrito ou ilegível, deixa de recusar. Motivo a registrar no PR: o arquivo da cópia é gravável pelo agente e não é controle. Sem mudança desde `1ed45d9d`.
- **A8, novo nesta leitura e não aceito:** `busybox git switch -c feature/x` (ou `toybox`, ou `checkout -b`) seguido de `;`, `||` ou `&&` e de `git push`, `git commit`, `git merge`, `git rebase`, `git reset --hard`, `git cherry-pick` ou `git revert` na `main`: a base recusava (R-MAIN, R-REVIEW, R-VERIFY), o head libera (S21). Nem o `busybox` nem o `toybox` têm applet `git`: a troca não acontece e o comando seguinte roda na `main`. Corrige o que a E1.17 disse do P3 ("a cadeia para no primeiro comando"): vale só para `&&`. O efeito já era alcançável na base por outra grafia (`false && git switch -c x; git push`, S22), por isso é recomendado e não bloqueia; mas é aceitação nova, e o rótulo espera o OK do dono ou a correção abaixo.

Com a correção do A8, a resposta passa a ser: só aperta, fora o P2 aceito.

Método: o mesmo de `1ed45d9d` (executor de fixtures da suíte, `tests/test_hooks.py`, com os hooks da `origin/develop` `c720891e`, sem mudança em `hooks/` desde o merge-base `4182a6b9`, e os do head, por `git archive`); conta a transição do código de saída (2 recusa, `ask` pergunta, 0 libera).
- D1, corpus do head (2271 fixtures do `conformidade`): 2→2 1683, 0→0 565, ask→ask 19, 0→2 4; **2→0 e 2→ask: zero** (igual à E1.17).
- D2, prefixo `busybox `/`toybox ` em cada Bash do corpus e 83 comandos gerados × 8 papéis × projeto e clone (5494): 0→2 1892, 0→ask 34, **2→0 2** (eram 5): as três citações de `forge atualizar` do antigo P3 voltam a recusar como na base; ficam as duas do A8 (`dir36-branch-no-proprio-projeto-libera` com `busybox` e `toybox`).
- D3, 54 applets × 10 cargas × 3 prefixos × 2 papéis (3240): 2→2 2142, 0→2 270, **2→0 zero**; os **196 casos do A6** (os mesmos arquivos de `1ed45d9d`): 196 de 196 em 2→2, com "troca o plugin e mexe no projeto".
- Legítimos atrás do applet (41 comandos × 3 prefixos × 7 papéis, projeto): 861 de 861 rc 0 nos dois lados.

O resto do que só aperta segue como em `1ed45d9d` (nada no delta toca esses ramos).

Testes do delta: `AtualizacaoAtrasDoBusybox` 2 OK (118 s; 54 applets × 2 papéis recusados, 5 legítimos livres). Suíte inteira: só no CI (brief sem suíte local); CI do head não citável (sem PR).

## Achados
- A8 (recomendado) hooks/conformidade.py:2306 · Depois da troca pelo applet (`:2294`), `busybox|toybox git switch -c x` registra a troca de branch que não acontece (sem applet git): `; git push`, `; git commit`, `|| git merge` na main recusavam na base e passam (S21). Corrigir: não registrar `ramos` quando o programa original é busybox/toybox.
- A7 (recomendado) hooks/conformidade.py:2292 · Lacuna anterior, não regressão: applet do busybox que roda programa e não está em LANCADORES (`chroot`, `setarch`, `nsenter`, `su -c`, `ash -c`...) esconde `git push --no-verify`, `rm -rf .githooks`, `gh pr merge --admin`: rc 0 na base e no head.
- A3 (recomendado) hooks/conformidade.py:2374 · Lista negativa não fecha a família: sort -o, curl -o, wget -O, gzip, zip -m, patch -o, split, sqlite3, git -C init, dpkg-deb -x, ar x, pax -r, interpretador e destino vindo do arquivo (tar -P, 7z -spf, cpio -i absoluto, unzip -:) gravam no estado com rc 0. Saída: sandbox (dono).

## Detalhe dos achados
**A8.** Caminho: um subagente na `main` de um projeto com busybox ou toybox no PATH roda `busybox git switch -c feature/x; git push`; o hook acredita na troca, o `busybox` sai com "applet not found" e o `git push` envia a `main`. Restam o `pre-push` e a proteção da branch no remoto. Severidade baixa: ator interno, e a base já deixava o mesmo efeito com `false && git switch -c x; git push` (S22), lacuna de modelo (a troca é tida como feita, seja qual for o fluxo) a tratar em cartão à parte. Comandos que passam a liberar depois de `busybox|toybox git switch -c x;` na `main` (S21): `git push`, `git push origin HEAD`, `git commit`, `git commit --amend`, `git merge develop`, `git rebase develop`, `git reset --hard HEAD~1`, `git cherry-pick`, `git revert`; com `toybox git checkout -b x;` também. Correção mínima, em `leitura_do_segmento`: guardar que houve troca pelo applet (`por_applet = True` no ramo de `:2292`) e, em `:2306`, `if parte and parte[0] == "branch" and not por_applet:`. Teste: as entradas de S21 com rc 2 e as duas fixtures `dir36` com `busybox`/`toybox` de D2. Dono: tech-lead. Fechar o A8 torna o "só aperta?" um sim (com o P2 aceito); deixá-lo aberto pede o OK do dono para o rótulo.

**A7, A3.** Sem mudança desde `1ed45d9d`.

## Sondas
- S21 · `busybox git switch -c feature/x; git push`, `busybox git switch -c feature/x || git commit -m x`, `toybox git checkout -b feature/x; git commit -m x`, tech-lead e qa-engineer, projeto na `main` · espera: rc 2 (como na base) · obtido: rc 0 no head, rc 2 na base
- S22 · Bash `false && git switch -c feature/x; git push` e `git switch -c feature/x --bad-opt; git push origin HEAD`, forge:tech-lead, projeto na `main` · espera: rc 2 · obtido: rc 0 na base e no head (lacuna anterior)

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum gravado em `docs/security/aceites/`; o P2 tem a aceitação do dono no pedido (09:44), a registrar no PR. Ferramentas: executor de fixtures da suíte sobre os hooks da `origin/develop` e do head (11 005 entradas por lado), 861 legítimos e as sondas S21 e S22; teste do delta (2 OK). Lacunas: busybox e toybox fora do PATH (sondas só no analisador); suíte inteira não rodada localmente; CI do head não citável.
