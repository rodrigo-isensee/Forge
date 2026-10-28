---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: bfd9e70ad2325fd5a04a2104fe041d4346384042
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: o hook parecer resolve a pasta do git como o git e o bash (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 2, revalidação por delta do parecer `7d6c866` (que revisou `212203a`). Delta lido: `212203a39fd4419c45dd797ea0737b7d05001d19..bfd9e70ad2325fd5a04a2104fe041d4346384042` (`96c642f` fix, `f1dc6d0` test, `bfd9e70` test), pela saída de `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md`: `hooks/parecer.py` +61 -17 (linhas 60, 188-222, 233, 239-240, 248-255, 257, 269, 271, 531-533, 535, 561, 564-565, 572-574, 583), as fixtures novas `tests/hooks/parecer/pasta-*`, `tests/mutantes/hk3-parecer-pasta-{1,2,3}.json` (texto novo) e `-{5..8}.json` (novas). Já lido na rodada 1 e fora do delta: o resto de `hooks/parecer.py`, `bin/forge-testes`, `tests/test_hooks_parecer_pasta.py`, `tests/test_testes_tocados.py`, `changelog.d/hk3-parecer-pasta.md` e a spec 4. Os pareceres de segurança e QA no delta não são deste review.

Veredito: **reprovado**. A1 a A3 da rodada 1 estão corrigidos e provados. O conserto do A1 do QA (`juntar_crases`) abriu uma regressão provada (A5, bloqueante, classe nova): uma crase sozinha entre apóstrofos ou aspas numa palavra antes do subcomando esconde o merge e o pull que o hook barrava na base.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_testes_tocados`: `Ran 82 tests in 16.757s` / `OK`; 77 fixtures `pasta-*` (mínimo 50).
- Mutantes: 8 specs `tests/mutantes/hk3-parecer-pasta-{1..8}.json`; não reexecutados aqui (o QA roda o `forge-mutante`).
- `tests/config.json`: fora do diff.
- Teto M14 (`git diff --numstat --no-renames ff3936a...bfd9e70`): 257 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 217, `tests/test_hooks_parecer_pasta.py` 33, `tests/test_testes_tocados.py` 2); corpus, mutantes, `changelog.d/` e `.md` fora; uma classe em `hooks/` (a pasta do git), com corpus próprio. Ok.
- Achados recorrentes (PA-7): lista vazia; A5 é a primeira ocorrência da classe; sem linha `AR-<n>`.

## Revalidação dos achados da rodada 1
Sondas da rodada 1 e novas, no formato do corpus, rodadas pela máquina do `tests/test_hooks.py` contra o `hooks/parecer.py` de `bfd9e70` (`$TMPDIR/tech-lead-hk3-parecer-pasta/sonda2/parecer/`; montagem: `{raiz}` = `proj` em `develop`, worktree `home/proj` em `melhoria/x`, `HOME={tmp}/home`).

| Achado | Sondas | Resultado em `bfd9e70` |
|---|---|---|
| A1 CDPATH por export ou prefixo | s5, s6, `declare -x CDPATH=...` (c6) | rc=2, corrigido (`hooks/parecer.py:240`, `:269`) |
| A2 GIT_DIR por printf -v, read, mapfile | s7, `mapfile -t GIT_DIR` + `export GIT_DIR` (c8), `export GIT_WORK_TREE=` (c5) | rc=2, corrigido (`hooks/parecer.py:240`, `SENSIVEIS` em `:60`) |
| A3 HOME reescrito na linha | s1, s2, s3, `read HOME` + `cd` (c7) | rc=2, corrigido (`hooks/parecer.py:193`, `:583`) |
| A4 gh com pasta desconhecida (recomendado) | sem mudança | segue recomendado (decisão técnica de 2026-10-28 11:49: os recomendados ficam como estão) |
| Controles do lado que passa | `cd proj` relativo sem CDPATH (c9), `cd <wt> && git pull --rebase ... && git push` (c11), `cd ~/proj && git pull --rebase` (c12) | rc=0, sem regressão |

Falsos positivos do lado seguro (aceitos pela decisão técnica de 2026-10-28 11:49): HOME, CDPATH ou desvio do git fixados por atribuição literal solta também ficam desconhecidos (`hooks/parecer.py:233`), então `HOME=/x; cd ~ && git pull` recusa mesmo com o valor conhecido; `entre_apostrofos(comando)` olha a linha inteira (`:535`), então `$W` entre apóstrofos em qualquer comando da linha (numa mensagem de commit, por exemplo) torna `W` desconhecido também no `cd $W` de outro comando; crase, `$( )`, `<( )` e `>( )` em qualquer pasta recusam (`:249`). Todos erram para a recusa; nenhum abre passagem.

## Sonda da regressão (A5)
- c2 ``git -c 'x.y=`' merge melhoria/x`` (cwd `{raiz}`, HEAD `develop`): `bfd9e70` rc=0; base `ff3936a` rc=2; `212203a` rc=2.
- c1 ``cd {raiz} && git -c 'x.y=`' merge melhoria/x`` (cwd na worktree): `bfd9e70` rc=0; base rc=2.
- c4 ``git -c "x.y=\`" merge melhoria/x``: `bfd9e70` rc=0; base rc=2.
- c13 ``git -c 'x.y=`' pull origin melhoria/x`` (HEAD `develop`): `bfd9e70` rc=0; base rc=2; o controle sem crase (c14) rc=2.
- c15 ``X='`' git merge melhoria/x``: `bfd9e70` rc=0; base rc=2.
- Git de verdade (`$TMPDIR/tech-lead-hk3-parecer-pasta/real.sh`): ``git -c 'x.y=`' merge -q melhoria/x`` na `develop` sai rc=0 e o commit de `melhoria/x` entra na `develop`. O gatilho é real.

## Achados
- A4 (recomendado) hooks/parecer.py:577 · gh pr create, ready e merge com pasta desconhecida (pushd, cd $UNK) são julgados pela pasta da sessão; fora da regra do modelo (só merge e pull), mas o docstring diz que o desconhecido nunca vale pela sessão
- A5 (bloqueante) hooks/parecer.py:221 · regressão (defeito provado), classe crase sozinha protegida por aspas: juntar_crases conta a crase depois do shlex, sem saber se estava entre apóstrofos ou aspas; git -c 'x.y=`' merge (ou pull) cola o subcomando numa palavra e passa (rc=0, na base rc=2)

## Parecer
Reprovado por A5. O resto do delta está bom: `SENSIVEIS` concentra num lugar só os nomes que o bash e o git leem sozinhos; o `None` em `variaveis` separa "mexida na linha" de "não fixada" sem o conjunto à parte que sugeri; `com_til` e o `cd` sozinho passam a usar o HOME da linha; e as fixtures novas cobrem cada sonda dos três pareceres.

- A5 · `hooks/parecer.py:213-222` (o `aberta ^=` em `:221`; chamado em `:531-533`) · `juntar_crases` recebe as palavras já sem aspas e trata toda contagem ímpar de crases como crase aberta. Uma crase literal entre apóstrofos, entre aspas com barra (`"\`"`) ou num valor de prefixo (``X='`'``) liga `aberta` e cola todas as palavras seguintes do comando numa só, e `analisar` deixa de ver o `merge` ou o `pull`. Sugestão: decidir a junção no texto cru, onde as aspas ainda existem (como `entre_apostrofos` faz); ou, do lado seguro, analisar as duas leituras (palavras cruas e juntadas) e recusar se qualquer uma barrar; ou tratar o comando com crase ímpar como pasta desconhecida. Fixtures: c1, c2, c4, c13 e c15 acima, no corpus `pasta-barra-*`, e um mutante que solte a guarda nova. Severidade: bloqueia.
- A4 · sem mudança desde a rodada 1. Severidade: recomendado.

Achado de segurança (A5 é contorno do portão R-REVIEW por regressão): vai como cartão ao `security-engineer`, que dá o parecer próprio em paralelo (E2.1); este review não o refaz.
