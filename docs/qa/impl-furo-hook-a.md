---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 336c43f199a90375d098cce24325fffa9fffca0d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS)

Etapa E1.4 (`R-QA`). Não sou o autor. Base `234dbe0`, head testado `336c43f`. Review e segurança aprovados em `bb78ecd`; depois deles só `tests/` mudou (fixtures e mutantes). Sem especificação de UX: as obrigações vêm do item E3 do pedido e do desenho §2.1 (flags do merge e `CONFIG_PROTEGIDA` no hook `conformidade`).

## Achados
- A1 (recomendado) hooks/conformidade.py:372 · `git merge -m --squash <b>` na develop recusa, embora `--squash` ali seja o texto da mensagem (valor de `-m`). Falso bloqueio raro e do lado seguro; sem correção exigida.
- A2 (recomendado) docs/hooks.md:104 · `--config-env` e `GIT_CONFIG_*` seguem fora do alcance (já declarado no texto, achado N1 do modelo de ameaças): cartão do dono, não defeito desta branch.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3-1: merge/pull na integração recusa `-s`/`--strategy`, `-X`/`--strategy-option`, `--squash`, `--no-commit` (todo papel) | fixtures `merge-flag-{squash,strategy-*,s-*,x-*,no-commit*,grupo-curto,pull-*,depois-de-no-squash}-bloqueia` via `test_fixtures` e `test_fixtures_do_lote_furo_hook_a` | forma curta colada e agrupada, abreviação longa, opção depois de `--no-squash` | passou |
| E3-2: sem flag e em `melhoria/*` o merge segue livre | `merge-flag-sem-flag-libera`, `merge-flag-na-melhoria-libera`, `merge-flag-mensagem-colada-libera` | `-m` com valor, outra branch | passou |
| E3-3: `git config` das chaves do merge (`mergeoptions`, `pull.twohead`, `pull.octopus`, `merge.*.driver`) recusa, inclusive `--worktree`, `-c`, `--`, `set`/`unset` e opções antes da chave | fixtures `merge-flag-config-*-bloqueia`, `merge-flag-por-c-mergeoptions-bloqueia` | chave com valor começado em `-`, `set --all`, `--comment`/`--value`, `--worktree` | passou |
| E3-4: leitura e chave sem valor seguem livres | `merge-flag-config-get-com-valor-libera`, `merge-flag-config-rastreio-libera` | só a chave, `--get` | passou |
| `R-REVIEW` e `R-CONFORMIDADE` citados nas recusas | `test_fixtures` (campo `regra`) | n/a | passou |

## Cenários e resultado real
- Suíte completa da worktree no head: `python3 -m unittest discover -s tests` · `Ran 2310 tests in 952.376s`, `OK (skipped=27)`, rc=0. Os 27 pulados são condicionais da própria suíte, nenhum marcado por mim.
- Vermelho antes do verde: `forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155` abre com `vermelho: base=234dbe0fb90b head=336c43f199a9`, reverte à base `hooks/conformidade.py`, `docs/hooks.md` e os pareceres, e mantém os testes. Provam: `tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)` e `tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a · H=ok · B=falha · prova (asserção)`. Nenhum teste cai no HEAD (`H=falha`: 0). rc=0.
- Mutação: `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a3.json tests/mutantes/impl-furo-hook-a-a3-2.json` · 20 mutantes (A3-m1 a A3-m20), todos `morreu`, rc=0.
- Cobertura contra o diff: `bin/forge-mutante --cobertura --base 234dbe0fb90b005450d7c2eb59e6241ea9779155` saiu rc=0, com as linhas de guarda mudadas (371, 372, 374, 376, 378, 1083, 1107, 1250, 1256, 1260, 1263, 1265, 1266, 1269, 1271) todas `coberta`. Conferi à mão o diff de `git_config`: `subcomando or` (A3-m18), `chaves and a not in CONFIG_ESCOPO` (A3-m15), o `--` e o `--worktree` com `do_merge` têm mutante; nenhuma linha de guarda sem mutante.
- Sondas próprias das funções `opcao_de_merge_que_muda_o_resultado` e `CONFIG_PROTEGIDA`: `--sq`, `--no-c`, `--no-commit=true`, `-xs`, `-Xours`, `--strategy-o=ours`, `--no-squash --squash` recusam; `--ff-only`, `--no-ff`, `--stat`, `-ms`, `-m msg-s` liberam; `branch.feat/x.mergeoptions=--squash` e `Merge.x.Driver` (caixa) casam. Só o falso bloqueio do A1.
- M14 (`agents/tech-lead.md:19`): `git diff --numstat --no-renames 234dbe0..336c43f` sobre `bin/ hooks/ scripts/ .github/ .githooks/ tests/*.py tests/config.json` dá 45+9 em `hooks/conformidade.py` e 5 em `tests/test_hooks.py`: 59 linhas, abaixo de 150; uma classe de comportamento em `hooks/` (merge na integração que muda o resultado revisado), com corpus próprio. **A branch cumpre a M14.**

Bugs abertos: nenhum.
