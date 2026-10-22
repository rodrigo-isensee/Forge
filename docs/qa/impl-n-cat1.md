---
tipo: qa
contrato: 1
pedido: impl-n-cat1
branch: melhoria/impl-n-cat1-2
commit: c6413c69240e0bd17768b9db7679619918a727de
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-22
---
# QA: impl-n-cat1

Escopo: a entrega `a3dbe22..c6413c6` (itens 1, 3, 4, 5 e 6 do desenho de N-CAT1; o item 2 ficou fora pela P-CAT1-1 = B). Depois dela só entraram os pareceres de review (2cee051) e de segurança (f07fc7d), que não são código. Tudo rodou em cópia própria em `$TMPDIR`, sem rede e sem `gh` real (`R-CUSTO`); a worktree compartilhada não mudou de HEAD. Sem plano antecipado: pedido de endurecimento sem especificação de UX, as obrigações são os itens do desenho e o modelo de ameaças.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Item 1: leitura do git que decide falha fechado, sem depender da ordem das regras | `FalhaFechadaDoGit` (`tests/test_catraca.py`); sonda: `--base deadbeef` com rótulo válido do dono | git que falha no `ls-tree` da base ou do head; estouro de prazo do git | passou: uma linha `R-CONFORMIDADE`, rc 1, o rótulo não libera |
| Item 3: resposta cortada e paginação acima do teto valem como sem rótulo | testes de `IncompleteRead` e de `api()` com teto+1 páginas | 3 páginas de 100, resposta cortada | passou: sem rastro de pilha, aviso `vale como sem rótulo` |
| Item 4: prazo total de 240 s, `min(30, restante)`, exceção `OSError`, `timeout-minutes` | testes com relógio dublê e o teste estrutural do `timeout-minutes` do job `catraca` | prazo esgotado na 3ª chamada; prazo maior que a metade do job | passou: a chamada nem sai, rc 1 |
| Item 5: parecer que não aprova barra em qualquer PR; QA reprovado também na `develop` (P-CAT1-2 = A) | testes (a), (b), (c) e de não regressão; sonda: PR só de `docs/` com QA reprovado e `--base-ref develop` | sem arquivo sensível; tipo não exigido; base `develop`; promoção fora | passou: `R-QA: parecer que não aprova`, rc 1; a promoção segue rc 0 |
| Item 6: forma compilada (`__pycache__/`, `.pyc`, `.pyo`, `.pyd`, `.so`) pede o rótulo do dono | subtestes por caminho, rótulo do dono, negativo de âncora e a árvore real via `git ls-files` | âncora `(^|/)__pycache__/`, sufixo no fim do caminho, mínimo de itens na árvore | passou |
| P3 = B: cada commit se reverte sozinho no HEAD | `git revert` de cada um dos 5 commits sobre c6413c6 numa cópia | cada item isolado | passou: sem conflito, suíte verde (214, 217, 216, 209 e 216 testes) |
| Recomendações do review e da segurança conferidas | rerodar os testes com as variáveis da API no ambiente | `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, `PR_NUMBER`, `HEAD_SHA` definidas | ver R1 abaixo (confirmada, não bloqueia) |

## Cenários e resultado real
- **Suíte do arquivo:** `python3 -m unittest tests.test_catraca` sobre c6413c6, com as quatro variáveis da API fora do ambiente: 222 testes, OK (base a3dbe22: 184, +38). A suíte completa roda no pre-push do envio.
- **Vermelho antes do verde:** os 222 testes novos contra o `tests/catraca.py` de a3dbe22 (`git show a3dbe226:tests/catraca.py` sobre a cópia): 25 falhas e 18 erros, ou seja, os testes dos itens quebram sem a mudança. O review (2cee051) mediu o mesmo por item, revertendo só o código de cada um.
- **Mutação:** não reexecutei; o review e a segurança já mataram os mutantes do desenho (a guarda voltando a `SEM_LISTA`, `listar` voltando a `[]`, `.so` fora da lista, `min` trocado por 30, QA filtrado na `develop`). Conferi no código que os testes citados existem. Sobrevive só o mutante que tira `PRAZO.reiniciar()` (cada execução da catraca é um processo novo).
- **Sondas pela linha de comando** (cópia em `$TMPDIR`, rótulo do dono válido e depois do último push):
  - base inexistente, modo `regras`: uma linha `R-CONFORMIDADE`, rc 1, rótulo não libera;
  - base inexistente, modo `pareceres`: idem;
  - PR só de `docs/` com QA reprovado, base `develop`: `R-QA: parecer que não aprova`, rc 1;
  - promoção (`--base-ref homolog`): rc 0, como a ADR 0008 manda.
- **Acessibilidade e E2E de interface:** não se aplicam, a entrega não tem interface.

### Recomendações (não bloqueiam)
- **R1 (confirmada; testes sem rede).** Com as quatro variáveis da API definidas no ambiente, `test_estouro_de_prazo_do_git_vira_uma_linha_e_rc_1` falha (1 falha em 222; as chamadas saem pelo `roda` de `tests/test_catraca.py`). Com elas fora, passa. O CI não as define para o passo dos testes (em `ci.yml` e `catraca.yml` elas são de outro passo), então o risco é só de ambiente local. Correção mínima, para o tech-lead: limpar as quatro variáveis no `setUp` da classe `Base`.
- **R2.** Os avisos `catraca: ...; vale como sem rótulo.` aparecem soltos na saída de testes antigos (`ExecucoesDoPr` e afins): ruído, não erro.
- As recomendações R2 a R7 da segurança e as do review (captura de `TimeoutExpired` fora das regras em `main`, prazo do `git fetch`) ficam para lote seguinte, como eles registraram; nenhuma afrouxa o que existia.
- Para o integrador: depois do merge, branch em voo com parecer reprovado já commitado fica vermelha no job `pareceres`, o que é intencional.

## Bugs
Nenhum aberto.
