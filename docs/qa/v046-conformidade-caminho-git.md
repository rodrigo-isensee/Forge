---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: abfccb7e24fb7ef005e53080d81d60c3896234cc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 conformidade-caminho-git (E20.9)

Diff lido: 8b5a44d5..22187bae (hooks/conformidade.py `resto_no_git`, `nomes_do_git`, chamada em `alvos_da_escrita`; 20 fixtures `gitcomum-*`; `tests/test_hook_git_comum.py`; 7 mutantes). Regra: R-QA, R-CONFORMIDADE.

## Achados
- A4 (bloqueante) hooks/conformidade.py:1076 · origem de link de `git rev-parse` com curinga (`ln "$(git rev-parse --git-dir)"/c?nfig h`) sai 0 e liga o `.git/config`; escapa das regras específicas (E20.32, sonda minha; igual ao A11 de segurança)
- A1 (recomendado) hooks/conformidade.py:969 · falso positivo: `$TMPDIR/logs/a.log` e `"$(git rev-parse --show-toplevel)/hooks/novo.py"` (pasta hooks/ do próprio Forge) agora recusam (exit 2); antes passavam. Falha fechada, contorno com caminho literal; sem fixture que o fixe nem o documente.
- A2 (recomendado) tests/mutantes/v046-conformidade-caminho-git.json:30 · G3 morre por ValueError (`max([])` em hooks/conformidade.py:973), não pela regra; o ramo `not fins` sem erro não é provado separado. Equivalente na prática (a fixture literal-forge-bloqueia não o distingue).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Resto após `$(…)` em nome do git recusa | gitcomum-s1-subst-comum-forge, subst-config, subst-sem-aspas-hooks, crase-forge, worktree-subst-forge | `$(…)` opaca e entre aspas; crase; worktree | passou |
| Resto após variável recusa | gitcomum-s2-variavel-forge, variavel-hooks, variavel-tee-head, variavel-description | `$d`, `${d}`; nome só no disco (description) | passou |
| Literal segue barrado | gitcomum-literal-forge-bloqueia | sem substituição | passou |
| Escritas comuns seguem livres | mktemp, tmpdir, subst-pwd-src, subst-toplevel-docs, variavel-docs, variavel-sozinha (vazio), literal-docs, git-commit, git-fetch, git-worktree-add | resto fora dos nomes do git; resto vazio | passou |
| Os 7 mutantes morrem pelo motivo certo | forge-mutante | G1-G7 | passou (G3 por ValueError, A2) |

Falta de casos que liberam (sondas minhas, fixtures descartáveis na minha worktree, não commitadas): `$TMPDIR/config.json`, `$(pwd)/info.md`, `d=refs; cp x $d/a.md`, `$PWD/index.html` liberaram (as duas últimas por não haver substituição/ramo que as pegue ou resto de arquivo não pasta; as quatro saíram 0); `$TMPDIR/logs/a.log` e `.../hooks/novo.py` recusaram (A1).

## Provas
- PQ-1: `git log --format=%H -1 22187bae11aba23d2e8fe705b6302647d7a34134` -> 22187bae11aba23d2e8fe705b6302647d7a34134
- `python3 -m unittest tests.test_hook_git_comum`: Ran 1 test, OK (2.6 s), 20 fixtures.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git.json` (rc 0): G1 a G7 todos `morreu` (conformidade.py:959, 969, 971, 974, 982, 325, 981).
- Motivo por mutante (rodado à mão): G4 cai em mktemp, subst-toplevel-docs, tmpdir, variavel-docs; G7 em variavel-description-bloqueia; G3 em literal-docs e subst-pwd-src (ValueError).
- Um mutante por condição nova: nomes_do_git (G4, G5, G7), SO_VARIAVEL (G6), SUBSTITUICAO (G2), `not fins` (G3), alvo somado (G1).
- Vermelho antes do verde: fixtures e módulo novos; os 7 mutantes provam que cada ramo é exercido (a base não tem `resto_no_git`).
- Suíte inteira: não rodei (R-TETO); vale o check-run `bateria` do sha no CI do PR.

## Revalidação por delta 22187bae..c0727411 (E20.14)
Delta lido: `forge-check parecer delta` lista conformidade.py, 22 fixtures novas (42 `gitcomum-*`: 27 recusam, 15 liberam), `tests/test_hook_git_comum.py` (mínimo 42), 2 specs de mutantes (G1-G14), docs/hooks-fixtures.md e changelog. Veredito: aprovado.
- QA A1 (mensagem do falso positivo): resolvido; hooks/conformidade.py:956 manda usar o caminho literal; G11 morre se a mensagem some. `$TMPDIR/logs/a.log` segue recusando (falha fechada), agora explicada.
- QA A2 (G3): resolvido; com `max(fins, default=0)` (conformidade.py:982) G3 deixa de cair em ValueError e morre pela regra, na fixture `gitcomum-literal-config-libera` (exit 2 com a mensagem do falso positivo, esperado 0). Rodado à mão em worktree descartável.
- Segurança A1 e A3 (`$(…)`/crase com `rev-parse --git-dir|--git-common-dir|--absolute-git-dir|--git-path <x>`): cobertos por s1-gitpath-*, crase-gitpath, s3-crase-sem-aspas, s4-gitdir, s5-variavel-gitdir; G9, G10, G14 morrem. A2 (`${d%/}/config`): s2-operador-config; G6 morre. A5 (`--target-directory=`): a5-target-directory-igual, -variavel (recusam) e -docs-libera; G12 morre. A3 (crase em palavra com `--`): G13 morre.
- Casos que liberam: sondei 8 comandos em fixtures descartáveis (não commitadas), todos saíram 0 como devem: `$(git rev-parse --show-toplevel)/docs/n.md`, `git rev-parse --git-dir > docs/n.md`, `ls "$(git rev-parse --git-dir)/hooks"`, `cat "$(git rev-parse --git-dir)/config" > docs/o.md`, `cp x $TMPDIR/config.json`, `cp x "$(pwd)/info.md"`, `"$(git rev-parse --git-dir)/../docs/n.md"`, `d=docs; cp x $d/n.md`. As 15 fixtures que liberam cobrem a classe; sem lacuna bloqueante.
- A4, A6 e A7 ficam em cartão (fora do delta); sem achado novo.
- Achado novo A3 (recomendado) tests/hooks/conformidade: `$TMPDIR/config.json` (nome com sufixo, não é `config`) libera e nenhuma fixture o fixa; cartão baixo, não bloqueia.

## Provas (revalidação)
- PQ-1: `git log --format=%H -1 c072741112e9383735cb82019aa0523acb4fa6a6` -> c072741112e9383735cb82019aa0523acb4fa6a6
- `python3 tests/test_hook_git_comum.py`: Ran 1 test in 4.5s, OK (42 fixtures).
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git.json` (rev c072741112e9): G1 a G8 todos `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-2.json`: G9 a G14 todos `morreu` (conformidade.py:1401, 1013, 956, 1483, 1484, 1170).
- Um mutante por condição nova: DIR_DO_GIT na atribuição (G9), expansão (G10), mensagem (G11), `--target-directory=` (G12), crase em palavra (G13), crase em REV_PARSE (G14).
- Suíte inteira: não rodei (R-TETO); vale o check-run `bateria` do sha no CI do PR.

## Revalidação por delta c0727411..cddc8915 (E20.20)
Delta lido: `_REV_PARSE` saiu; `valor_do_rev_parse` e `trocar_rev_parse` (hooks/conformidade.py:368-382) leem o corpo por palavras (shlex); 16 fixtures `gitcomum-v2-*` (58 `gitcomum-*`), mínimo 58, spec `-3` (G17 a G19) e G15, G16 na `-2`. Veredito: aprovado, sem achado novo.
- G15 a G19 morrem pelo motivo certo (rodados à mão, um a um, em worktree descartável): G15 (opção do diretório) cai em s4-gitdir, v2-menos-c-gitdir, v2-quiet-gitdir; G16 (`--git-path`) em 12 fixtures de gitpath; G17 (`CAMINHO_SIMPLES`) só em v2-argumento-com-aspas; G18 (`valor is None`) em mktemp, toplevel-docs, v2-menos-c-toplevel-libera, toplevel-hooks-recusa-limite; G19 (`"rev-parse" in palavras`) em crase-generica/opcao-config e mktemp-libera.
- Casos que liberam seguem livres (sondas minhas, fixtures descartáveis, não commitadas, saída 0): `cp x $(git rev-parse --show-toplevel)/docs/n.md`, o mesmo seguido de `&& git rev-parse --git-dir`, `"$(git -C . rev-parse --show-toplevel)/docs/n.md"`, `echo $(git rev-parse --git-dir) > docs/o.md`, `$(git rev-parse --git-dir)/../docs/n.md`; as fixtures v2-menos-c-ler-libera e v2-menos-c-toplevel-libera os fixam.
- Casos de abuso fora das fixtures, todos recusam (exit 2, R-CONFORMIDADE): `"$(git rev-parse --git-dir)/config"`, `2>/dev/null` dentro, `-c a=b` com `--git-common-dir`, `\git -q`, `/usr/bin/git --git-path "hooks/pre-push"`, crase com `--git-dir=.git` e `--absolute-git-dir`, `--git-path $x`, `--git-path` sem argumento, `$(echo hi; git rev-parse --git-dir)`, `$(git rev-parse --git-dir | cat)`, `$(git rev-parse --git-dir; true)`.
- A3 do QA (`$TMPDIR/config.json` libera sem fixture) e A4, A5 do mv, A6, A7, A8 seguem em cartão, fora do delta.

## Provas (revalidação E20.20)
- PQ-1: `git log --format=%H -1 cddc8915fda2dd271907323e1a2c04beebd2bd28` -> cddc8915fda2dd271907323e1a2c04beebd2bd28
- `python3 tests/test_hook_git_comum.py`: Ran 1 test in 6.256s, OK (58 fixtures).
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git.json` (rc 0, rev cddc8915fda2): G1 a G8 `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-2.json` (rc 0): G9 a G16 `morreu` (conformidade.py:1428, 1040, 983, 1510, 1511, 380, 370, 372).
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-3.json` (rc 0): G17, G18, G19 `morreu` (conformidade.py:374, 381, 368).
- `bin/forge-mutante --cobertura --base 8b5a44d5ffd509c8c63d3e9f68dbef20071c7d3e`: rc 0, só linhas `coberta`.
- Suíte inteira: não rodei (R-TETO); vale o check-run `bateria` do sha no CI do PR.

## Revalidação por delta cddc8915..3b3d7a67 (E20.32)
Delta lido (`forge-check parecer delta`, sem o que veio da develop): hooks/conformidade.py (`origens_do_rev_parse`, `checar_link` e `no_git` em `segmento_lido`), 6 fixtures `gitcomum-v3-*` (64 `gitcomum-*`, mínimo 64), bin/forge-testes (test_hook_git_comum no mapa FORGE_CHECK), tests/test_testes_tocados.py (78 para 79), spec `-4` (G20 a G26). Veredito: reprovado por um achado novo, o A4 abaixo (confirmei por sonda o A11 do parecer de segurança 0857bbb9); A1 a A3 da E20.29 resolvidos.
- A4 (bloqueante) hooks/conformidade.py:1076 · a origem livre da regra `.git/` também escapa das específicas quando tem curinga: `ln "$(git rev-parse --git-dir)"/c?nfig h` sai 0 (era 2 no cddc8915) e o link físico grava no `.git/config`; mesma classe com `[c]onfig`, `hook[s]/…`. Nenhuma fixture o fixa; falta fixture que barre e o código que o recuse.
- A1 (origem de `git rev-parse` livre só da regra genérica `.git/`): fixtures origem-gitdir-libera e origem-variavel-libera (saem 0); destino, `.git/config`, `.git/hooks/`, `.git/forge/` e `-S`, `-t`, opção longa, `--` seguem 2. G20 a G24 e G26 morrem.
- A3 (variável do `.git` atrás de lançador segue na linha): fixture lancador-variavel-bloqueia (2); G25 morre.
- A2: test_hook_git_comum no mapa; o módulo roda quando bin/forge-check muda (test_testes_tocados, 79).
- Vermelho em 0fc55eac (árvore dele com os `tests/` do head sobrepostos, worktree minha descartável): test_hook_git_comum falha em 3 fixtures (`v3-lancador-variavel-bloqueia`, `v3-link-origem-gitdir-libera`, `v3-link-origem-variavel-libera`; as 3 `-bloqueia` restantes já passavam e fixam comportamento mantido); test_testes_tocados falha em 3 (`test_forge_check_roda_os_modulos_dele`, `test_mapa_lista_todo_modulo_que_usa_o_forge_check` e uma de `test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo`, por test_pre_push_leve, vinda do merge da develop). Passam no head.
- Sonda do A4 (fixture descartável, esperava 2): `ln "$(git rev-parse --git-dir)"/c?nfig h` -> `AssertionError: 0 != 2`. Vermelho que o autor deve fixar com fixture `gitcomum-v3-*` e corrigir em `origens_do_rev_parse` (recusar a origem com `?`, `*`, `[` ou `{`); responsável: dev da stack (autor).
- Sondas minhas (18 fixtures descartáveis, não commitadas, todas como esperado; nenhuma usava curinga, por isso o A4 passou por mim na primeira leitura). Recusam (2): `ln -s "$(git rev-parse --git-dir)/config" x`, destino `.../hooks/p`, origem livre com destino `.../hooks/p` na mesma linha, `-S`, `-t docs`, `--`, `--target-directory=docs`, só `ln <origem>` (a origem é o destino), `.git/HEAD` literal, `.../hooks/pre-push`, `.../forge/x`, `time d=$(git rev-parse --git-dir); cp x $d/config`, `&& ln x "$(…)/config"`, segundo link para `.git/hooks/q`. Liberam (0): `d=$(git rev-parse --git-dir); ln $d/HEAD h`, `ln -sf` e `ln -sn` com a origem, `ln <origem> docs/a docs/b`.
- CI do PR: não há PR aberto para a branch (`gh pr checks` sem resultado); a bateria completa fica para o check-run do PR. Não rodei a suíte inteira (R-TETO).

## Provas (revalidação E20.32)
- PQ-1: `git log --format=%H -1 3b3d7a67387c4c61bfd51692513a03bec916d492` -> 3b3d7a67387c4c61bfd51692513a03bec916d492
- tests.test_conformidade_verde: Ran 11 tests, OK (32.5 s). tests.test_testes_tocados: Ran 149, OK (skipped=1, sandbox: /proc de outro namespace de pid; skip do próprio teste, não meu).
- tests.test_hooks_volta_lancador: Ran 22 tests, OK (328.9 s; `skipped=25` são subtestes que o próprio módulo pula no sandbox). tests.test_hook_git_comum: Ran 1 test, OK (15 s, 64 fixtures).
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-4.json` (rc 0, rev 3b3d7a67387c, árvore limpa): G20 a G26 `morreu` (conformidade.py:1074, 1074, 1077, 1060, 1060, 1416, 1056).
- Um mutante por linha de guarda mudada: opção (G20, G21), origem de rev-parse (G22), regra genérica (G23, G24, G26), variável atrás do lançador (G25).

A volta 5 (E20.42) fecha os achados deste parecer: A4 (curinga na origem de rev-parse) e os demais que ele deixou bloqueantes.

## Revalidação por delta b283521c..abfccb7e (E20.42, volta 5)
Delta lido (3 commits: 15dfdc3a fix, f84306a6 mutantes, abfccb7e docs): hooks/conformidade.py (`COLCHETE_DE_DIGITO`, `sem_caixa`, `origem_so_generica`), 11 fixtures `gitcomum-v3-*` novas (mínimo atualizado), spec `-6` (G34 a G39), AR-13. Veredito: aprovado.
- A1 (mutante sobrevivente no ramo do diretório comum): fechou. Fixture `gitcomum-v3-worktree-comum-config-bloqueia`; G36 (`filter(None, (git,))`) morre em hooks/conformidade.py:1104.
- A2 (linha de guarda sem mutante): fechou. `forge-mutante --cobertura --base c340c322` sem nenhuma `sem mutante`, `não coberto` ou `só equivalente`; 1083 (G38), 1097 (G34, G39), 1104 (G37) cobertas.
- Delta sem achado novo. Sondei o colchete: `[[:digit:]]`, `[[=c=]]`, `[^x]`, `[0-9][a]` ficam com `[` depois de retirar o colchete de dígitos e recusam; `[0-9-]+` só admite dígito e hífen, sem letra, então o bash e o glob do Python leem igual. Desvio declarado (par `forge-suite-Xverde.[0-9]`) coberto por `gitcomum-v3-colchete-digito-libera` e G39.

## Provas (revalidação E20.42)
- PQ-1: `git log --format=%H -1 abfccb7e24fb7ef005e53080d81d60c3896234cc` -> abfccb7e24fb7ef005e53080d81d60c3896234cc
- Vermelho: worktree destacada na base do delta (b283521c) com as fixtures novas copiadas: `python3 -m unittest tests.test_hook_git_comum` FAILED (failures=6: classe-config, equivalencia-config, negacao-config, negacao-hooks, nocaseglob-config, ordenacao-config, todas recusa que a base libera). As outras 5 passam na base por desenho (guardas de regressão; mortas pelos mutantes G36 a G39).
- Head abfccb7e: `python3 -m unittest tests.test_hook_git_comum` Ran 1 test, OK.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-4.json` rc 0: G20 a G26 `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-5.json` rc 0: G27 a G33 `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-6.json` rc 0: G34, G39, G35, G36, G37, G38 `morreu` (conformidade.py:1097, 1097, 1103, 1104, 1104, 1083).
- `bin/forge-mutante --cobertura --base c340c322` rc 0, só linhas `coberta`.
- Suíte inteira: não rodei (R-TETO); vale o check-run `bateria` do sha no CI do PR.
