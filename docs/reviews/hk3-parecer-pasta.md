---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 79d0f6f24a8af8753776651c896441e522309570
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: o hook parecer resolve a pasta do git só quando ela é literal (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 5. É a revalidação por delta do parecer `4268d63`, que revisou `4ae417e`. O brief manda ler o delta `7f0ce80e96831bde3f75fc3eeb60acccde8166bf..79d0f6f24a8af8753776651c896441e522309570`. A saída de `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md` dá o intervalo `4ae417e..79d0f6f`, que é o mesmo código: os commits de portão `4268d63`, `0a4e752` e `7f0ce80` não mexem em código. Os commits de código são `374f834` (fix) e `79d0f6f` (mutante). Arquivos lidos:
- `hooks/parecer.py` +11 -5 (linhas 219-231, `sem_condicao`);
- as 10 fixtures `pasta-barra-cd-condicao-*` novas e a `pasta-passa-opcao-sem-time-nao-e-do-time.json`;
- `tests/mutantes/hk3-parecer-pasta-16.json` (M113 a M119).

A linha de `docs/engineering/achados-recorrentes.md` que o delta mostra é a AR-2, que eu mesmo atualizei em `4268d63`. Ficou como "já lido" e fora do delta: o resto de `hooks/parecer.py`, `bin/forge-testes`, `tests/test_hooks_parecer_pasta.py`, `tests/test_testes_tocados.py`, `changelog.d/hk3-parecer-pasta.md` e as fixtures das rodadas 1 a 4.

Veredito: **aprovado**. A volta 4 fecha o A7. `sem_condicao` agora tira, em qualquer ordem e repetidas, as palavras de `CONDICAO` e `CORPO`, as atribuições (`ATRIBUICAO`) e o `-p` e o `--`, estes só depois de um `time`. Com isso o `cd` ou o `pushd` que sobra deixa a pasta desconhecida, e o merge recusa. Não há regressão do que `4268d63` aprovou.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 1 test in 4.434s` / `OK`. São 140 fixtures `pasta-*` (o mínimo é 50), 17 delas do lado que passa.
- Pre-push do autor: relatado verde no histórico do pedido. O CI do PR roda a suíte inteira.
- Mutantes M113 a M119 (`hk3-parecer-pasta-16.json`): conferi que cada `de` aparece uma vez só em `hooks/parecer.py`. O M116 tem a fixture própria do lado que passa (`-p cd R; -- cd R` sem `time`). Não reexecutei o `forge-mutante`, que é do QA.
- `tests/config.json`: fora do diff.
- Teto M14 (`git diff --numstat --no-renames ff3936a...79d0f6f`): 263 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 222, `tests/test_hooks_parecer_pasta.py` 34, `tests/test_testes_tocados.py` 2), abaixo de 400. Corpus, mutantes, `changelog.d/` e `.md` ficam fora. Há uma classe só em `hooks/` (a pasta do git), com corpus próprio. Ok. A DECISÃO TÉCNICA de 16:24 fala em 224 linhas. A diferença é de contagem e não muda o resultado.
- Achados recorrentes (PA-7): conferi a AR-1 (`pasta-do-git-diferente-do-bash`) e a AR-2 (`cd-escondido-por-involucro`). Os casos da AR-2 que eram bloqueantes estão fechados. O que sobra da classe é o A6 (`builtin cd`, `command cd`), que é recomendado e igual à base. Nenhuma classe se repetiu neste delta, e a AR-2 fica como está, com `vezes: 3`.

## Revalidação
As sondas estão no formato do corpus, em `$TMPDIR/tech-lead-hk3-parecer-pasta/sonda5/parecer/`, com 74 casos: os 62 da rodada 4 mais 12 novos (`f01` a `f12`). Rodaram pela máquina do `tests/test_hooks.py` contra `79d0f6f`, `4ae417e` e a base `ff3936a`. Conferi as formas do A7 no bash real: `time -p cd`, `! X=1 cd` e `time -- cd` imprimem `/tmp`.

| Alvo | Sondas | `79d0f6f` | `4ae417e` |
|---|---|---|---|
| A7 (`time -p`, `time --`, `! time -p`, atribuição depois de `!`, `if`, `time`, `if !`) | e03 a e06, e20 a e22 | rc=2 em todas | rc=0 |
| Combinações novas (`time -p -- X=1 cd`, `if time -p cd`, `while ! X=1 time -p cd`, `X=1 time -p cd`, `! A+=1 cd`, `time -p pushd`, `if A=1 B=2 cd`, `time -p cd W`) | f02 a f05, f08 a f11 | rc=2 em todas | rc=0 |
| Lado que passa (`X=1 cd W && git pull --rebase origin melhoria/x`, `cd W; time -p git merge`, `cd W && time -- git pull --rebase`, merge solto em W) | f01, f06, f07, f12, mais c9, c11, c12, d05, d06, d12, e11, e13 | rc=0 | rc=0 |
| Tudo o que `4268d63` aprovou | as outras 51 | igual a `4ae417e` | — |

Entre `79d0f6f` e `4ae417e`, só mudaram os 15 casos das duas primeiras linhas, todos de rc=0 para rc=2. As únicas divergências que sobram em `79d0f6f` são a d11, que continua esperando errado como nas rodadas 3 e 4, e a d15 e a e16, que são o A6 e também passam na base.

A formulação `no_time` continua ligada depois de um `!` (`time ! -p cd` é lido como `cd`). No bash, nesse caso, o `-p` é o comando e o `cd` não roda. A recusa sai a mais, do lado seguro, e não vira achado.

## Achados
- A4 (recomendado) hooks/parecer.py:567 · gh pr create, ready e merge com pasta desconhecida (pushd, cd fora do nível de cima) são julgados pela pasta da sessão; o merge e o pull recusam, o gh não; sem mudança desde a rodada 1
- A6 (recomendado) hooks/parecer.py:161 · `builtin cd`, `command cd` e `if builtin cd` mudam a pasta do shell sem o hook ver o `cd` (rc=0, igual na base); mesma classe do A8 da segurança

## Parecer
Aprovado. O A7 está fechado. A correção segue a sugestão do parecer anterior: as atribuições e as opções do `time` saem na mesma volta das palavras de condição, e não num passo à parte. A função continua com um propósito só, e o docstring diz a regra nova. Cada guarda nova tem o seu mutante (M113 a M119), e a fixture do lado que passa (M116) impede que o `-p` solto vire recusa. As 74 sondas não mostram nenhuma regressão contra `4ae417e`. O A4 e o A6 continuam como recomendações e ficam como estão (decisão técnica de 2026-10-28 11:49).
