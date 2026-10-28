---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 77b539d3fb3e9ebde40af8cf36942298c54d7e10
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: o hook parecer resolve a pasta do git só quando ela é literal (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 3, revalidação por delta do parecer `85537c6` (que revisou `bfd9e70`). Delta lido: `bfd9e70ad2325fd5a04a2104fe041d4346384042..77b539d3fb3e9ebde40af8cf36942298c54d7e10`, pela saída de `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md`. Os commits de código são `f50a45e` (fix), `a65a98b` (corpus), `c808a9c`, `40eaf8c`, `07fc854` e `77b539d` (mutantes) e `c6cf772` (refactor). Os arquivos lidos são `hooks/parecer.py` +102 -128 (linhas 8-11, 54-68, 131-152, 183-184, 199-275, 509-513, 539-580), `changelog.d/hk3-parecer-pasta.md`, `tests/test_hooks_parecer_pasta.py` (docstring), as fixtures `pasta-*` novas ou renomeadas e `tests/mutantes/hk3-parecer-pasta-{1..13}.json`. Já lido nas rodadas 1 e 2 e fora do delta: o resto de `hooks/parecer.py`, `bin/forge-testes` e `tests/test_testes_tocados.py`. Os pareceres de segurança e QA e a linha AR-1 que entraram no intervalo não são deste review.

Veredito: **aprovado**. O A5 foi corrigido pela raiz: `juntar_crases` e `entre_apostrofos` saíram, e a palavra com expansão antes do subcomando deixa as pastas incertas (`globais`, `hooks/parecer.py:135`). A regra da DECISÃO TÉCNICA de 12:56 está cumprida: pasta só literal (`resolver`, `:238`), `cd` só no nível de cima (`soltos`, `:198`; `COMECA`, `:57`) e `~` só com HOME não mexido. Nenhuma sonda mostrou regressão contra a base.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_testes_tocados`: `Ran 82 tests in 16.266s` / `OK`. São 118 fixtures `pasta-*` (o mínimo é 50), 15 delas do lado que passa.
- `bin/forge-testes --listar hooks/parecer.py`: 14 módulos dirigidos. O pre-push do autor rodou 2179 testes, todos OK (histórico do pedido, 14:05), e o CI do PR roda a suíte inteira.
- Mutantes: 13 specs em `tests/mutantes/hk3-parecer-pasta-*.json`. Saíram o M15 e o M39, de trecho que não existe mais. O autor relata rc 0 nas 13. Não reexecutei aqui, porque o QA roda o `forge-mutante`.
- `tests/config.json`: fora do diff.
- Teto M14 (`git diff --numstat --no-renames ff3936a...77b539d`): 246 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 205, `tests/test_hooks_parecer_pasta.py` 34, `tests/test_testes_tocados.py` 2). Corpus, mutantes, `changelog.d/` e `.md` ficam fora. Há uma classe só em `hooks/` (a pasta do git), com corpus próprio. Ok.
- O fragmento `changelog.d/hk3-parecer-pasta.md` (+1 -1) descreve o comportamento novo. Está conforme a DECISÃO TÉCNICA de 14:09.
- Achados recorrentes (PA-7): AR-1 (`pasta-do-git-diferente-do-bash`) já está na lista. A6 repete a classe do A8 da segurança, invólucro que esconde o `cd`, então grava a linha AR-2 neste commit.

## Revalidação
As sondas estão no formato do corpus, em `$TMPDIR/tech-lead-hk3-parecer-pasta/sonda3/parecer/`, com 40 casos: os das rodadas 1 e 2 mais 17 novos (`d01` a `d17`). Rodaram pela máquina do `tests/test_hooks.py` contra a árvore de `77b539d` e contra a base `ff3936a`. Montagem: `{tmp}/proj` em `develop` e a worktree `{tmp}/home/proj` em `melhoria/x`.

| Alvo | Sondas | `77b539d` | Base `ff3936a` |
|---|---|---|---|
| A5 crase entre apóstrofos ou aspas antes do subcomando | c1, c2, c4, c13, c15, d10 (`git -c "x.y=\`" pull`) | rc=2 em todas | rc=2 |
| A5 crase fora da pasta (mensagem de commit e depois merge) | c10, d16 | rc=2 | rc=2 |
| A1 a A3 da rodada 1 (CDPATH, GIT_DIR, HOME) | s1 a s7, c3, c5 a c8 | rc=2 em todas | várias rc=0 (contornos que a base deixava passar) |
| `cd` fora do nível de cima | d03 (`cd W && cd R; git merge`), d13 (`(cd W); git merge` com cwd R) | rc=2 | d03 rc=2, d13 rc=0 |
| Pasta com glob ou chaves | d08 (`cd {tmp}/pro?`), d09 (`cd {tmp}/{proj,}`) | rc=2 | rc=0 |
| `-C` vazio, `-C` para a raiz, `~/..` | d07, d14, d17 | rc=2 | rc=2 |
| Lado que passa | c9, c11, c12, d05 (`cd W && git merge`), d06 (`git -C W merge`), d12 (`cd W && git pull --rebase origin melhoria/x && git push ...`) | rc=0 | rc=0 |
| Invólucro do `cd` | d01 (`! cd R; git merge`), d02 (`time cd R; ...`), d15 (`builtin cd R; ...`) | rc=0 | rc=0 (igual, sem regressão: A6) |

A d11 (`cd R && git pull --rebase origin develop`) sai com rc=0 nas duas árvores. É atualização a partir da própria integração, que o hook libera de propósito. A sonda é que esperava errado.

## Achados
- A4 (recomendado) hooks/parecer.py:551 · gh pr create, ready e merge com pasta desconhecida (pushd, cd fora do nível de cima) são julgados pela pasta da sessão; o merge e o pull recusam, o gh não; sem mudança desde a rodada 1
- A6 (recomendado) hooks/parecer.py:160 · `! cd`, `time cd`, `builtin cd` e `command cd` mudam a pasta do shell sem o hook ver o `cd` (rc=0, igual na base); mesma classe do A8 da segurança; a correção é tratar o comando com `cd` depois de um invólucro como pasta desconhecida

## Parecer
Aprovado. O delta simplifica o hook (-26 linhas líquidas em `hooks/parecer.py`): saíram o dicionário de variáveis, `entre_apostrofos`, `juntar_crases` e `efeito_nas_variaveis`, e entraram `mexidas_na_linha`, que devolve só os nomes sensíveis, e `globais`, que é a fonte única das opções globais do git e serve tanto a `analisar` quanto a `pastas_do_git`. Nenhuma referência ao código antigo sobrou. O `resolver` passou a conferir se a pasta existe e segue o link só no `-C` (`fisico`), como o git faz. Os docstrings, a mensagem de recusa e o fragmento de changelog dizem a regra nova.

O A4 e o A6 são recomendações, não bloqueiam e ficam para cartão próprio (decisão técnica de 2026-10-28 11:49: os recomendados ficam como estão). O A6 vai também como nota ao `security-engineer`, que já o registrou como A8.
