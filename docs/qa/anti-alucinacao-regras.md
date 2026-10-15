---
tipo: qa
contrato: 1
pedido: anti-alucinacao-regras
branch: melhoria/anti-alucinacao-regras
commit: b377f35
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-14
---
# QA - fatia 2 do anti-alucinacao (R-PROVA, R-BRIEF, conferente, correções do hook)

Links: desenho `~/.forge-contrib/propostas/anti-alucinacao.md` (§11, linha 2), `docs/adr/0011-analisador-de-comandos-gramatica-positiva.md`, `agents/conferente.md`. Sem UX nem API. Offline além de `gh` de leitura (`R-CUSTO`). Não altera código; cartões C1 a C8, S7, S8, `gh --jq env`, `test -e -v` e `shlex` ilegível ficam de fora.

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | suíte e `validar-plugin.sh` verdes | `python3 -m unittest discover -s tests -v`; `scripts/validar-plugin.sh` | n/a | Passou: "Ran 562 tests in 280.939s / OK"; "Validation passed" (uptime 3.74 ao iniciar) |
| PQ-2 | sem "máx. 3" no passo 1 do jarvis | `grep -n "máx. 3" agents/jarvis.md` | passo 1 | Passou: 1 ocorrência, linha 38 (passo 6, QA); passo 1 sem ela |
| PQ-3 | brief e entrega reais conferidos | roteiro do `conferente.md` à mão (abaixo) | brief sem PQ-n; branch apagada | Passou com ressalvas (AA2-02 e achados) |
| PQ-4 | corte sem marca reprovado | `grep -n "Retira do escopo original"` em brief de teste sem e com a marca | marca ausente x presente | Passou: sem marca, grep rc 1 e `corte: sem marca`; com marca, rc 0 |
| UL | uso legítimo pelo hook | seção 2 | papel de cada agente | 29/29 rc 0 |
| FB | falsos bloqueios da ADR | seção 3 | gramática positiva | 38/38 no rc anunciado |
| RG | fluxo comum dos agentes | seção 4 | `main` | 26/26 no rc esperado |

## PQ-3, brief real (este pedido), modo `brief`
O pedido não está em `docs/pedidos/` (não existe nesta árvore): fidelidade e corte não verificáveis por disco.
```
conferencia-brief: anti-alucinacao-regras -> forge:qa-engineer
grep -n "Retira do escopo original" brief-real.txt -> (vazio, rc 1)
grep -n "PQ-" brief-real.txt -> (vazio, rc 1); grep -n "NÃO tocar" -> (vazio, rc 1)
fidelidade: não verificável | decisões: não verificável | corte: não verificável | forma: PQ-n sem prova verificável | etapa: ok (o brief não manda abrir PR nem mesclar)
veredito-brief: reprovado
```
Achado de forma: o "Pronto quando" do brief traz "Prova:" por item, mas sem rótulo `PQ-n`, e não tem "NÃO tocar" nem "Fora do escopo". Pelas regras do próprio agente reprova; é da montagem do brief pelo Jarvis, não da fatia.

## PQ-3, entrega real (PR #122, `melhoria/anti-alucinacao-medicao-fix`, base develop), modo `entrega`
Entregar reconstruído do corpo do PR (o brief original não está em disco).
```
conferencia: anti-alucinacao-medicao-fix forge:tech-lead modo=entrega
PQ-1 cumpriu | gh pr view melhoria/anti-alucinacao-medicao-fix --json number,state,mergedAt -> 122, MERGED, 2026-10-14T20:07:35Z
PQ-2 cumpriu | git ls-remote origin refs/pull/122/head -> 2251ad5116dea5e4c7447fbbb8ea056de37adbf9 (git ls-remote origin <b> vazio: branch apagada, AA2-02)
PQ-3 cumpriu | git merge-base --is-ancestor 2251ad5 f2dbe3a && echo contém -> contém
PQ-4 cumpriu | test -f docs/qa/anti-alucinacao-medicao-fix.md, test -f docs/reviews/...md -> rc 0, rc 0
escopo: ok | git diff --name-only f2dbe3a^1...f2dbe3a -> 10 arquivos (bin/forge-check, tests/test_forge.py, docs/melhoria-continua.md, 4 bugs, 2 pareceres, CHANGELOG.md anexo)
corte: ok | todos os itens do corpo do PR têm commit
etapa: fora de ordem | gh pr checks 122 -> 11 checks `fail` em 2s (run 38629082240 conclusion failure); gh pr view 122 --json labels -> [] (bin/forge-check é protegido, exige afrouxa-regra)
veredito: não cumpriu
```
`forge-check pr anti-alucinacao-medicao-fix --ref 2251ad5 --base f2dbe3a^1` -> sem violação (review ac3d698 e QA dab099a aprovados, parecer 15:33 e 16:10 antes do PR 20:05). Sem `--ref` a mesma chamada na branch desta fatia acusa "desatualizado", ruído de ramo; o conferente precisa passar `--ref`/`--base` (já previsto na CLI, não escrito em `conferente.md`).

## PQ-4, corte sem marca (brief de teste)
Pedido com itens A, B, C; brief entrega A e B e põe C em "Fora do escopo" sem a marca. `grep -n "Retira do escopo original" brief-sem-marca.txt` -> vazio, rc 1: `corte: sem marca "item C"`, `veredito-brief: reprovado`. Controle com a marca: linha 2 encontrada, rc 0.

## Seção 2, uso legítimo pelo hook (29/29 rc 0)
Projeto descartável em `$TMPDIR`, hook `hooks/conformidade.py` desta árvore, entrada PreToolUse com `agent_type`. Conferente, rc 0: `git log -1 --format='%h %s'`, `git log -1 --format=%h develop`, `test -f src/app.js`, `test -e docs/pedidos/p1.md`, `git log -1 'HEAD@{1}'`, `grep -n 'v1$' src/app.js`, `git merge-base --is-ancestor HEAD develop && echo contém || echo não contém`, `git ls-remote origin melhoria/x`, `git diff --name-only develop...melhoria/x`, `gh pr view|diff|checks 122`, `gh run list --json conclusion`, `forge-check pr|docs`, `git --no-pager -C . log -1`, `grep -n "Retira do escopo original" ...`, `git rev-parse HEAD && git status`, `git cat-file -p HEAD | head -3`, `git show HEAD^ | wc -l`, `ls docs && pwd && cd src`, `git log -1 --format=%cI -- docs/reviews/x.md`, `gh pr view melhoria/x --json createdAt,mergedAt`, `gh pr view 122 --json labels`. tech-lead: `diff <(git log -1) <(git log -2)` e `for f in $(ls src); do echo $f; done`, rc 0. dev: `echo $(git rev-parse HEAD)`, `git log -1 # nota`, `x=$(git rev-parse HEAD) && echo $x`, rc 0.

## Seção 3, falsos bloqueios da ADR (rc 2 anunciado, obtido 2)
Conferente: `echo $?`; `echo $(git log -1)`; `git log -1 2>/dev/null`; `git log -1 HEAD@{1}`; `ls *`; `grep "a\|b"`; dois comandos em linhas; `test -x`, `test -n`; `grep '$(x)'`; `git log --grep='%G'`; `--show-signature`; `echo a #b`+linha; crase; `$X`; `cat <<E`; `\--output`; `git -c`; `> out`; `git commit`; `gh pr merge`; `git push`. Demais papéis: `git push origin $BRANCH`; laço com push; `cp $TMPDIR/x docs/reviews/y.md` (tech-lead); `{ git push origin melhoria/x; }`; heredoc sem aspas com push; `echo a #nota`+push (e `a#b`); crase; `{main,x}`; `$'main'`. Cada mensagem nomeia a construção e dá a forma literal que passa; o limite de 200 caracteres corta parte dela (AA2-01).

## Seção 4, regressão de fluxo comum
dev, tech-lead e qa, rc 0: `git add src/app.js`, `git commit -m "x"`, `git push origin melhoria/x`, `python3 -m unittest`, `git commit -m "$(cat <<'FIM' ... FIM )"`. `git push origin main` como dev, tech-lead e qa: rc 2 (R-MAIN). Extras: `git push origin develop` rc 2, `--force` rc 2 (R-VERIFY), `--no-verify` rc 2, `cat <<'FIM'` com "git push origin main" no corpo rc 0.

## Bugs (todos corrigidos)
| ID | Severidade | Resumo |
|---|---|---|
| AA2-01 | baixa (corrigido 276b7f8) | recusa corta a forma que passa (200 caracteres) e mostra `$T` por `$TMPDIR` |
| AA2-02 | baixa (corrigido 5df7ba4) | `conferente.md` sem forma de provar push de branch apagada após o merge |
Zero críticos, altos, médios e baixos abertos. AA2-01 corrigido em 276b7f8 e AA2-02 em 5df7ba4, reconferidos em b377f35 (hook real e `refs/pull/122/head`). `aceite_usuario`: não se aplica (0 bugs abertos); o campo estava como `sim` por engano, pois o dono não aceitou bug algum, e foi removido.

## Fora deste parecer
Segurança (`R-SEGURANCA`) e review já aprovaram; este parecer não declara "seguro". O conferente simulado pelo Jarvis (agente haiku) não foi rodado por mim: executei o roteiro à mão.
