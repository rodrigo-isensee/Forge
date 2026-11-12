---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: 22187bae11aba23d2e8fe705b6302647d7a34134
parecer: aprovado
escopo: completo
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
