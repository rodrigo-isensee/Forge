---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: c072741112e9383735cb82019aa0523acb4fa6a6
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
