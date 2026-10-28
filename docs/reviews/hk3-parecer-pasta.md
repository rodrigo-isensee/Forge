---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 4ae417ecff39652c5d439c294ad2e582cf81861f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: o hook parecer resolve a pasta do git só quando ela é literal (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 4, revalidação por delta do parecer `64113d3` (que revisou `77b539d`). O delta lido é `77b539d3fb3e9ebde40af8cf36942298c54d7e10..4ae417ecff39652c5d439c294ad2e582cf81861f`, pela saída de `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md`. Os commits de código são `8f70137` (fix), `8d1504f` e `4ae417e` (mutantes). Arquivos lidos:
- `hooks/parecer.py` +15 -4 (linhas 9-10, 60, 219-227 e 562-564);
- `changelog.d/hk3-parecer-pasta.md`;
- as 11 fixtures `pasta-*` novas;
- `tests/mutantes/hk3-parecer-pasta-{3,14,15}.json`.

Já lido nas rodadas 1 a 3 e fora do delta: o resto de `hooks/parecer.py`, `bin/forge-testes`, `tests/test_hooks_parecer_pasta.py` e `tests/test_testes_tocados.py`. Os pareceres de segurança e QA e a linha AR-2 entraram no intervalo, mas não são deste review: a AR-2 é minha, de `64113d3`, e foi atualizada aqui.

Veredito: **reprovado**. A volta 3 fecha as formas da DECISÃO TÉCNICA de 14:45 que estão no corpus: `if`, `elif`, `while`, `until`, `!`, `time`, `function`, `popd` e o bloco. Também não regride nada do que `64113d3` aprovou. Mas `sem_condicao` só tira a palavra que abre a parte. O `cd` que vem depois de `time -p`, `time --` ou de uma atribuição de prefixo (`! X=1 cd`, `if X=1 cd`, `time X=1 cd`) continua mudando a pasta do bash sem o hook ver, e o merge passa com rc=0 (A7).

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 1 test in 3.241s` / `OK`. São 129 fixtures `pasta-*` (o mínimo é 50), 16 delas do lado que passa.
- Pre-push do autor: 2179 testes OK (histórico do pedido, 15:26). O CI do PR roda a suíte inteira.
- Mutantes: M99 a M112 em `hk3-parecer-pasta-14.json` e `-15.json`, e o M23 reancorado em `-3.json`. Conferi que cada `de` aparece uma vez só em `hooks/parecer.py`. Não reexecutei o `forge-mutante`, que é do QA. O autor relata rc 0.
- `tests/config.json`: fora do diff.
- Teto M14 (`git diff --numstat --no-renames ff3936a...4ae417e`): 257 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 216, `tests/test_hooks_parecer_pasta.py` 34, `tests/test_testes_tocados.py` 2). Corpus, mutantes, `changelog.d/` e `.md` ficam fora. Há uma classe só em `hooks/` (a pasta do git), com corpus próprio. Ok.
- O fragmento `changelog.d/hk3-parecer-pasta.md` (+1 -1) descreve o comportamento novo. Está conforme a DECISÃO TÉCNICA de 15:31.
- Achados recorrentes (PA-7): o A7 é a terceira vez da classe `cd-escondido-por-involucro`, depois do A6 deste review e do A8/A10 da segurança. A linha AR-2 passa para `vezes: 3`, com a última ocorrência em `hooks/parecer.py:224`, neste commit.

## Revalidação
As sondas estão no formato do corpus, em `$TMPDIR/tech-lead-hk3-parecer-pasta/sonda4/parecer/`, com 62 casos: os 40 da rodada 3 mais 22 novos (`e01` a `e22`). Rodaram pela máquina do `tests/test_hooks.py` contra `4ae417e`, `77b539d` e a base `ff3936a`. Montagem: `{tmp}/proj` em `develop` e a worktree `{tmp}/home/proj` em `melhoria/x`. Cada forma de `cd` que vale como achado foi conferida no bash real (`bash -c "cd /; <forma> cd /tmp; echo $PWD"` imprime `/tmp`).

| Alvo | Sondas | `4ae417e` | `77b539d` e base |
|---|---|---|---|
| Fechado na volta 3 (`if`, `while`, `until`, `!`, `! !`, `time`, `function`, `f() {`, `\cd`, `'cd'`) | d01, d02, e01, e02, e07, e08, e09, e14, e15, e17, e18, e19 | rc=2 em todas | rc=0 (o contorno passava) |
| `popd` | e10 | rc=2 | rc=2 |
| Tudo o que `64113d3` aprovou (A1 a A5, crase, CDPATH, HOME, GIT_DIR, glob, `-C` vazio, subshell) | c0 a c15, s1 a s7, d03 a d17 | igual à rodada 3 | — |
| Lado que passa | c9, c11, c12, d05, d06, d12, e11 (`cd W && git pull --rebase origin melhoria/x`), e13 (`cd W; time git merge`) | rc=0 | rc=0 |
| **A7**: opção do `time` | e03 (`time -p cd R; git merge`), e20 (`time -- cd R`), e21 (`! time -p cd R`) | **rc=0** | rc=0 |
| **A7**: atribuição de prefixo depois da palavra que abre | e04 (`! X=1 cd R`), e05 (`if X=1 cd R; then :; fi`), e06 (`time X=1 cd R`), e22 (`if ! A=b cd R`) | **rc=0** | rc=0 |
| A6 (invólucro `builtin`, `command`) | d15, e16 (`if builtin cd R; ...`) | rc=0 | rc=0 (igual, sem regressão) |

A e12 (`if true; then :; fi; cd W && git merge melhoria/y`, rc=2) mostra que depois de um bloco o `cd` literal deixa de ser lido. É o lado seguro, igual em `77b539d`. A d11 continua esperando errado, como na rodada 3.

## Achados
- A4 (recomendado) hooks/parecer.py:561 · gh pr create, ready e merge com pasta desconhecida (pushd, cd fora do nível de cima) são julgados pela pasta da sessão; o merge e o pull recusam, o gh não; sem mudança desde a rodada 1
- A6 (recomendado) hooks/parecer.py:161 · `builtin cd`, `command cd` e `if builtin cd` mudam a pasta do shell sem o hook ver o `cd` (rc=0, igual na base); mesma classe do A8 da segurança
- A7 (bloqueante) hooks/parecer.py:224 · cd-escondido-por-involucro, requisito da decisão de 14:45: `time -p cd R`, `time -- cd R`, `! X=1 cd R`, `if X=1 cd R` e `time X=1 cd R` seguidos de merge passam (rc=0, sondas e03 a e06, e20 a e22); sem_condicao não tira opção do time nem atribuição

## Parecer
Reprovado só pelo A7. O delta é pequeno e legível. `sem_condicao` é uma função de um propósito, o conjunto `CONDICAO` fica ao lado de `CORPO`, e a condição `len(comando) < len(sem)` separa o `cd` solto do `cd` que vem depois da palavra que abre. O M101 e o M102 matam as duas direções dessa condição. O M23 foi reancorado no texto novo. O docstring do módulo, a mensagem de recusa e o fragmento de changelog dizem a regra nova. Não houve regressão contra `77b539d` nem contra a base em nenhuma das 62 sondas.

Correção sugerida para o A7: depois de cada palavra de `CONDICAO`, tirar também `-p` e `--` do `time` e as atribuições (`sem_atribuicoes`), ou tratar como pasta desconhecida a parte cujo comando, depois de condição e atribuições, seja `cd`; uma fixture por forma e um mutante para cada guarda nova. O bash real troca a pasta em todas as formas do A7.

O A7 é bloqueante porque é requisito da própria volta, não recomendação promovida: a decisão de 14:45 manda tratar o `cd` depois de `!`, `if` e `time`, e essas formas são `cd` depois dessas palavras. O A4 e o A6 continuam recomendações e ficam como estão (decisão técnica de 2026-10-28 11:49). O A7 vai como nota ao `security-engineer`, porque é a continuação do A10 dele.
