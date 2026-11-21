---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 2acfe2102f93ac66e2c86d572df67347e0963dca
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E80.11 (revalidação da CONFORMIDADE-TIL-EM-SUBSTITUICAO e da CONFORMIDADE-LINK-POR-COPIA)

Base `adc52def`, head `2acfe210`. Delta lido (`forge-check parecer delta`): `9451e78c..2acfe210`, com `hooks/conformidade.py`, `docs/hooks.md`, o fragmento, o índice das fixtures, 11 fixtures e as specs `-3`, `-4` e `-5`. Código do item em `hooks/conformidade.py`: 103 linhas a mais e 9 a menos desde a base (H1 dentro do teto).

## Achados
- A1 (bloqueante) hooks/conformidade.py:3904 · O `-m tarfile` com o `-e` colado ao arquivo (`-el.tar`, que o argparse aceita e extrai no diretório corrente) escapa pelo `(?![\w-])`: `cd ~/.claude && python3 -m tarfile -el.tar` dá 0 (S1, S2). Aceite o `-e` com o valor colado e ponha fixture.
- A2 (recomendado) hooks/conformidade.py:3909 · O `.git` no fim de uma URL também conta como arquivo em vigor: `git clone https://h/x/y.git && tar -xf a.tar -C src` recusa (S3). É falso positivo que só fecha, mas mostra a mensagem errada. Avalie `\.git(?![\w-])(?!$|\s)` ou declare o limite em docs/hooks.md.

## Sondas
- S1 · tech-lead, `cd ~/.claude && python3 -m tarfile -el.tar` · espera: 2 (A5: `-m tarfile -e` numa linha que cita arquivo em vigor) · obtido: 0
- S2 · tech-lead, `cd ~/.forge-contrib/wt/q/docs/pedidos && python3 -m tarfile -el.tar` (base `linkcopia-python-m-tarfile-bloqueia`) · espera: 2 · obtido: 0; com `-e l.tar` e com `--extract=l.tar` dá 2
- S3 · tech-lead, `git clone https://h/x/y.git && tar -xf a.tar -C src` · espera: 0 (nenhum arquivo em vigor) · obtido: 2

## Parecer
Reprovado pelo A1. A regra nova do A5 da segurança cobre `-e l.tar` e `--extract`, mas deixa passar a forma com o argumento colado, que o `tarfile` aceita. Prova: `python3 -I -m tarfile -el.tar` num diretório vazio extraiu `a.txt` com rc 0. No `zipfile` a forma colada não funciona, porque o `-e` exige 2 argumentos.

Realinhamentos conferidos, sem enfraquecer nada. O F6 continua desligando só o `.claude` (`claudeQ|forge|git`), e o V1 e o V2 cobrem `.forge` e `.git`, um mutante por alternativa. O S4 continua no `if False` da linha nova. O F5 só acompanha a linha da regex, que passou a começar por `(?![\w-])|php`, e continua mirando o `php`. O V3 restaura a condição antiga, ou seja, o mutante é a regressão exata. O V4 e o V5 desligam o ramo `-m tarfile|zipfile` e o `--extract`. As outras sondas deram o esperado: `cd .git && python3 -m zipfile -e l.zip .` dá 2, `d=~/.claude; python3 -m tarfile -e l.tar "$d"` dá 2 e `cd ~/.claude && tar -xf l.tar` dá 2.

Testes rodados no head, em segundo plano, com log, `rc=` e TMPDIR próprio: `test_fixtures_do_til_em_substituicao` (`tilsubst-*`), `test_fixtures_do_link_por_copia` (`linkcopia-*`), `tests.test_conformidade_verde` e `tests.test_hooks_volta_corpus`. Foram 79 testes em 335 s. Na primeira rodada, com o TMPDIR dentro de `~/.forge-contrib`, 4 falharam: 3 do `test_conformidade_verde` e o `test_corpus_nos_dois_hooks`. Na segunda, com o TMPDIR do `mktemp -d` fora da pasta de controle, os 4 passaram (36 testes, OK, `rc=0`). As falhas vinham do ambiente, não do head. A suíte inteira fica para o CI do PR (`R-REVIEW`).
