---
tipo: qa
contrato: 1
pedido: hook-comentario-shlex
branch: melhoria/hook-comentario-shlex
commit: 136ad09ee16661bd2d10975ec1c5549890ff78e9
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---

# QA - HOOK-COMENTARIO-SHLEX (leitura do comentário nos hooks, volta 6)

Testado o código 136ad09 (HEAD c04de62 na worktree, só pareceres depois do código), comparado com a base 10c838f. Sondas em cópias por `git archive` dos dois commits em `$TMPDIR`, sem rede: os hooks reais (`conformidade`, `parecer`, `pesado`) rodam com o ambiente de uma fixture existente (repositório, papel, branch, pareceres), só com a linha trocada, como um agente que tenta passar pelo hook. Fontes: pedido `hook-comentario-shlex`, ADR 0013, pareceres de review (3df5ae5) e de segurança (c04de62), ambos aprovados.

## Resultado da suíte
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na raiz da worktree: `Ran 1201 tests in 293.508s`, `OK`.
- `scripts/validar-plugin.sh`: `✔ Validation passed`.

## Matriz (escopo → teste → resultado)
| Obrigação | Teste | Resultado (136ad09 / base) | Fronteira protegida |
|---|---|---|---|
| E1: `#` colado a palavra não esconde o resto (riscos do pedido) | `cat a#&&git push origin main`; `echo a#; git push --force origin main`; `grep x f#; forge sugerir --fila` | 2 / 0, 2 / 0, 2 / 2 | `#` no meio da palavra |
| E1: contextos em que o bash não abre comentário (A1, A2 das voltas 1 e 2) | `((#x))`, `((1 #x))`, `(( 1 #x ))` com `--no-verify`, `for ((…#x…))`, `[[ a =~ (#b) ]]`, `( #b)`, `(a\|#b)`, `@(a\|#b)`, `$(echo a)#b; … ${B:-main}`, `a\ #b; …` | todas 2 / todas 0 | `#` depois de espaço, `(` e `\|` |
| E1: linha ilegível recusada fora do papel só de leitura (A3, A4) | `git push --force origin main; (true)#'`, `… # it's ((` | 2 / 2 | aspa sem par no comentário |
| A7 (volta 4): `#` dentro de `${…}`, crase e `$[` | `echo ${x:- #b}; gh repo delete …`, `` echo `echo a #b`; … ``, `x=abc; echo ${x/ #y/z}; …`, `echo $[1 #x]; …` | 2 / 0 (as quatro) | expansão aberta |
| A8 (volta 5) e A6 do review | `` x=`#'`; gh repo delete dono/proj --yes # ' ``, a de aspa dupla, `` x=`#'`; gh pr merge … --merge # ' ``, `` echo `# it's`; gh pr merge … --merge; echo `# it's` `` e a de `true # it's` (parecer reprovado) | 2 / 0 (as cinco) | comentário dentro de crase com aspa |
| E2 / ADR 0013 T1: fixtures de recusa com `PARES_QUE_O_BASH_IGNORA` (prefixo e sufixo juntos) | amostra de 78 das 544 recusas de Bash de linha única (uma a cada 7) × 4 pares = 312 | 309 saem 2 (97 que a base soltava); 3 saem 0, todas `pesado/lancador-conta` (0 também na base) | prefixo + sufixo |
| E2: sufixo `; (true)#'` na mesma amostra | 78 linhas | 76 saem 2; 2 saem 0, ambas fixtures cuja linha já tem aspa aberta (`echo 'abre`, `grep -n 'v1 …`): o sufixo fecha a aspa e a linha vira legítima também no bash (artefato da sonda) | n/a |
| E2: comentário real continua comentário; nada legítimo muda | 27 linhas do dia a dia no `conformidade` e 5 `gh pr create` no `parecer` (abaixo) | 25 / 25 e 4 / 4 iguais à base; 3 recusas a mais | n/a |
| Vermelho antes do verde | toda linha de risco e de achado acima sai 0 na base 10c838f (comando: `scripts/sonda.py base casos.json`) | falha observada na base | n/a |
| Mutação no diff (manual, sem ferramenta na stack) | M1: crase fora de `ANTES_DE_CANDIDATO` (hooks/_comum.py:314); M2: regra da última linha física com crase e aspa desligada (:334); rodados T1, T2, T3 e `test_leituras_piso_da_develop_e_linha_ambigua` | M1 morto (9 falhas), M2 morto (12 falhas) | n/a |

## Comandos legítimos (o que passou a ser recusado a mais)
Liberam como na base: `git commit -m "fix: corrige o loop do #12"`, `"feat: x (#12)"`, `'docs: item #3 e #4'`, `'fix: #12 trata `` `fichas` ``'` (aspas simples), `"fix: trata `` `fichas` `` (#12)"` (crase antes do `#`), `git commit -F <arquivo>`, `git commit -m "$(printf 'fix: #12…')"`, `` echo `date` ``, `` echo "hoje: `date +%F`" ``, `` ls `pwd` ``, `ls # nota`, `git log --oneline -3 # ver`, `grep -n '#' …`, `python3 -c "print('#')"`, `echo a#b`, `x=1 # it's`, `git status -sb && git log --oneline -1 # it's ok`, `git push origin feature/x # PR #12`, `` test -f a && echo `cat a` # x ``; no `parecer`, `gh pr create … --body-file <arquivo>`, `--body-file - <<< 'x'`, `--title "feat: #12"` e `--body 'fecha #12; usa `` `fichas` ``'`.

Recusados a mais (2 no 136ad09, 0 na base), todos com `#` seguido de crase dentro de aspas duplas: `` git commit -m "fix(hooks): trata `#` na linha" ``, `` git commit -m "fix: #12 trata `fichas`" `` e `` gh pr create … --body "fecha #12 e o `x`" ``. Não conto como bug: entre aspas duplas a crase é substituição de comando, o bash executaria `fichas`/`x` e a mensagem sairia errada; o contorno é aspas simples, `-F` ou `--body-file` (o mesmo risco que o review da volta 6 registrou como recomendação).

## Fora do escopo (registrados, não reprovam)
- R1 da segurança (aspa sem par dentro de crase, cartão CRASE-ASPA-HOOK): aparece. `` x=`'`; gh repo delete dono/proj --yes; y=`'` `` sai 0 no 136ad09 e na base.
- `pesado` com crase em par (`FORA_DO_T2`, ADR 0013 item 5): aparece na amostra (`pesado/lancador-conta` com os pares 0, 1 e 2 sai 0, igual à base).
- HEREDOC-FURO-HOOK: não sondado nesta rodada; cartão à parte.

## Bugs
Nenhum aberto.

## Achados

## Parecer
Aprovado. O escopo E1 e E2 está coberto, e os riscos do pedido e os achados A1 a A8 das voltas 0 a 6 saem com código 2 nos hooks reais. Nenhum comando legítimo da amostra mudou, fora as 3 recusas a mais descritas acima (com contorno). A suíte e a validação do plugin passaram no HEAD. Sondas: `$TMPDIR/qa-shlex/scripts/sonda.py` e `casos.py`.
