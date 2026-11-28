---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 6aa5b7bec87035d37234363585f610a674fa0655
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-conformidade-sessao-forge (E51.17, revalidação)

Revalidação no head 29cbd24d (antes: d2358465), delta por `forge-check parecer delta`: `hooks/conformidade.py` (here-string e corpo de heredoc de shell lidos como trava, alias como trava, `gh pr edit` na lista dos que não chegam a uma trava), 14 fixtures `e51-*` e 1 `rverify-fp-*` novas, specs de mutantes `-3`, `-4` e `-5`, `tests/test_hooks.py`, `docs/hooks.md`, fragmento do changelog. Remoto sem avanço (`git fetch`: igual ao head local). Suíte inteira: só no CI do PR, não rodada aqui.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Travas valem para todo papel na sessão do Forge (R-MAIN, R-VERIFY, push para integração, tag v*) | `HookSessaoDoForge.test_travas_do_conformidade` | wt/* e clone, piso de fixtures | passou |
| O resto da linha segue livre (ADR 0009, seção 6) | mesmo teste (`-libera`: `gh pr edit $N`, `python3 - <<'EOF'`, crase escapada, `bash` com entrada de arquivo) | interpretador e leitura | passou |
| Here-string com push direto recusa (A1 anterior) | fixture `e51-wt-push-here-string-bloqueia` (`bash <<< 'git push origin develop'`) + M17 a M36 | `<<<` em wt/* | passou, A1 fechado |
| O que passava na base segue passando (A2 anterior) | 5 testes de `Hooks`, um a um | `$R`, crase, `${`, `$PWD`, R-VERIFY na crase | passou, A2 fechado |
| O `vigia` grava `violacoes.jsonl` | `HookSessaoDoForge.test_vigia_registra` | piso 2 | passou |

## Provas
Os 5 testes de `Hooks` do A2, forma `python3 -I -m unittest discover -s tests -p test_hooks.py -k <nome>`, cada um `Ran 1 test ... OK`: `test_fixtures_da_trilha_034` (23,8 s), `test_fixtures_do_lote_furo_hook_a` (15,8 s), `test_fixtures_do_rverify_falso_positivo` (6,1 s), `test_rotulo_so_dono_formas_alternativas` (21,9 s), `test_rotulo_so_dono_volta_2_crase_escapada_comentario_clone_e_remocao` (14,8 s). Classe `-k HookSessaoDoForge`: 2 testes, OK.

Mutantes do delta: `bin/forge-mutante --base d2358465fafc56c42b396ef7e1efe2c4d0e6e854 tests/mutantes/v0479-conformidade-sessao-forge-3.json -4.json -5.json`, saída 0, linha `base=d2358465... rev=29cbd24d...`, 20 de 20 `morreu` (M17 a M36, em `hooks/conformidade.py` 356, 2629 a 2753, 3803 a 3853). `--cobertura --base d2358465`: linhas 3823, 3832, 3842, 3844 e 3853 com mutante declarado (e morto acima); rc 0. O vermelho do parecer anterior (`forge-testes --vermelho`, 2200 s por cópia) segue valendo para as fixtures que já existiam; as novas morrem sob os mutantes.

## Revalidação E51.17 (head a554e345, delta 29cbd24d..a554e345)
Delta por `forge-check parecer delta`: `hooks/conformidade.py` (E51.14: shell ou eval aninhado no texto reavaliado, ou com here-string, é trava e fecha na dúvida), 8 fixtures `e51-wt-*` novas (4 bloqueiam, 4 liberam: `bash -c` de leitura, aninhado de leitura, here-string de leitura, `cat` com here-string de push), mutantes M37 e M38 na spec `-5`, `tests/test_hooks.py` (piso 40 para 48, igual às 48 fixtures), `docs/hooks.md`, fragmento do changelog. Remoto sem avanço da branch (`git fetch`: igual ao head local). Suíte inteira: só no CI do PR, não rodada aqui.

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Shell ou eval aninhado no texto reavaliado fecha na dúvida (E51.14) | `HookSessaoDoForge.test_travas_do_conformidade` (fixtures `e51-wt-push-bash-c-aninhado-variavel`, `-eval-here-string-aninhado`, `-force-bash-c-here-string`, `-here-string-aninhado`: bloqueiam) | um nível de aninhamento, here-string aninhado | passou |
| Leitura com `bash -c`, aninhado ou here-string segue livre | mesmo teste (4 fixtures `-libera`) | ADR 0009, seção 6 | passou |
| Piso de fixtures sobe com as novas | mesmo teste (`rodar("conformidade", 48, {0, 2})`) | pasta vazia ou renomeada | passou |

Provas: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: `Ran 2 tests in 12.786s`, `OK`. Mutantes do delta: `bin/forge-mutante --base 29cbd24dc696ec318b4a53eb9322f46f149ae713 tests/mutantes/v0479-conformidade-sessao-forge-5.json`, linha `base=29cbd24d... rev=a554e3453649`, M37 e M38 `morreu` em `hooks/conformidade.py:3842` (linha de guarda única do diff, dois mutantes), nenhum sobrevivente; M33 a M36 da mesma spec também `morreu`.

## Revalidação E51.21 (head bc385524, delta a554e345..bc385524)
Delta por `forge-check parecer delta`: `hooks/conformidade.py` (E51.18: `source` e ponto com here-string e shell que lê a entrada por pipe dentro do texto reavaliado são trava), 7 fixtures `e51-wt-*` novas (4 bloqueiam, 3 liberam: `find .` aninhado, `source` com here-string de leitura, `eval` aninhado), mutantes M39 a M41 (spec `-6`) e M32, M37, M38 reescritos, `tests/test_hooks.py` (piso 48 para 55, igual às 55 fixtures), `docs/hooks.md`, fragmento do changelog. Remoto sem avanço (`git fetch`: igual ao head local). Suíte inteira: só no CI do PR, não rodada aqui.

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `source`/ponto com here-string de push recusa na sessão do Forge (E51.18) | `HookSessaoDoForge.test_travas_do_conformidade` (`e51-wt-push-source-here-string`, `-ponto-here-string`, `-source-aninhado`) | `source /dev/stdin <<<`, um nível | passou |
| Shell que lê a entrada por pipe dentro do texto reavaliado fecha na dúvida | mesmo teste (`e51-wt-push-pipe-para-shell-aninhado`) | `bash -c 'echo … \| bash'` | passou |
| Leitura com `source <<<` e `find .` aninhado segue livre (ADR 0009, seção 6) | mesmo teste (`e51-wt-source-here-string-libera`, `-ponto-aninhado-libera`) | ponto como argumento, não como fonte | passou |
| Piso de fixtures sobe com as novas | mesmo teste (`rodar("conformidade", 55, {0, 2})`) | pasta vazia ou renomeada | passou |
| O que passava na base segue passando (A2 anterior) | 5 testes de `Hooks`, um a um | `$R`, crase, `${`, R-VERIFY | passou |

Provas: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: `Ran 2 tests ... OK`. Os 5 testes de `Hooks` (`test_fixtures_da_trilha_034`, `test_fixtures_do_lote_furo_hook_a`, `test_fixtures_do_rverify_falso_positivo`, `test_rotulo_so_dono_formas_alternativas`, `test_rotulo_so_dono_volta_2_crase_escapada_comentario_clone_e_remocao`), cada um `Ran 1 test ... OK`.

Vermelho: `forge-testes --vermelho` do `test_hooks` inteiro não termina em prazo útil (A3 anterior, 2200 s por cópia); feito por cópia em `$TMPDIR` com `hooks/conformidade.py` da base a554e345 e o resto do head: `-k test_travas_do_conformidade` dá `FAILED (failures=4)`, nas fixtures `e51-wt-push-pipe-para-shell-aninhado-bloqueia`, `-push-ponto-here-string-bloqueia`, `-push-source-aninhado-bloqueia` e `-push-source-here-string-bloqueia`; no head, passa. As 3 fixtures `-libera` e a de `eval` aninhado já passavam na base (regressão, não correção).

Mutantes do delta: `bin/forge-mutante --base a554e34536490ff7af78000f76b67a1652f6e840` nas specs `-4`, `-5` e `-6`, linha `base=a554e345... mb=a554e345... rev=bc385524277c69f47a6cb0f7ed5d37cee5706626`: 17 de 17 `morreu` (M25 a M41), nenhum sobrevivente; M39 `:3851`, M40 `:3856`, M41 `:3810`, M37 `:3849`, M38 `:3847`, M32 `:3857`. Linhas de guarda mudadas no diff (FONTES, `nivel and SHELLS`, `nivel and eval`, `nivel and FONTES and aqui`, `le_o_here_string`): todas com mutante.

## Revalidação E51.25 (head b22efaae, delta bc385524..b22efaae)
Delta por `forge-check parecer delta`: `hooks/conformidade.py` (E51.22: `source` ou ponto como programa, também depois de `builtin`/`command -p`, dentro do texto reavaliado é trava sem here-string; `find .` não é), 4 fixtures `e51-wt-*` novas (3 bloqueiam: `builtin .`, `command -p .`, `source /dev/stdin` por pipe; 1 libera: `find .` depois de pipe), mutantes M42 a M45 (spec `-7`) e M39 reescrito (spec `-6`), `docs/hooks.md`, fragmento do changelog. Remoto sem avanço (`git fetch`: igual ao head local).

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `source`/ponto como programa lendo o pipe, no texto reavaliado, recusa (A2 da segurança E51.20) | `HookSessaoDoForge.test_travas_do_conformidade` (`e51-wt-push-pipe-para-source-aninhado`, `-ponto-builtin-aninhado`, `-ponto-command-aninhado`: bloqueiam) | prefixo `builtin`, `command -p`, sem here-string | passou |
| Ponto como argumento segue livre (ADR 0009, seção 6) | mesmo teste (`e51-wt-ponto-argumento-pipe-aninhado-libera`) | `find .` depois de pipe | passou |
| Piso de fixtures | mesmo teste (`rodar("conformidade", 55, ...)`) | pasta vazia ou renomeada | passou, piso não subiu (A4) |

Provas: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: `Ran 2 tests in 10.166s`, `OK`.

Vermelho: por cópia em `$TMPDIR` com `hooks/conformidade.py` da base bc385524 e o resto do head, `-k test_travas_do_conformidade`: `FAILED (failures=3)`, nas fixtures `e51-wt-push-pipe-para-ponto-builtin-aninhado-bloqueia`, `-ponto-command-aninhado-bloqueia` e `-source-aninhado-bloqueia`; no head, `OK`. A fixture `-libera` passa nas duas (guarda de não regressão).

Mutantes do delta: `bin/forge-mutante --base bc385524277c69f47a6cb0f7ed5d37cee5706626 tests/mutantes/v0479-conformidade-sessao-forge-6.json tests/mutantes/v0479-conformidade-sessao-forge-7.json`, linha `base=bc385524... mb=bc385524... rev=b22efaae5769`: M39 a M45, 7 de 7 `morreu` (3810, 3811, 3817, 3858, 3863), nenhum sobrevivente. `--cobertura --base bc385524`: 3817 (M45) e 3858 (M39, M42) cobertas, rc 0.

## Achados
- A3 (recomendado) bin/forge-testes:1 · `--vermelho` do `test_hooks` leva 2200 s por cópia e não aceita `-k` nem classe; `test_vigia_registra` fica sem veredito por erro da base. Cartão: veredito por classe.
- A4 (recomendado) tests/test_hooks.py:3638 · piso de `e51-*` segue 55 e a pasta tem 59 fixtures (4 novas do E51.22); pasta que perca até 4 fixtures ainda passa. Subir o piso para 59.

## Revalidação E51.29 (head c792b567, antes b22efaae)

Delta por `forge-check parecer delta` (sem o que veio da `develop`): `docs/hooks-fixtures.md`, `docs/hooks.md`, `tests/apoio_volta_unica.py`, `tests/provas/v0479-corpus-custo.md`. Nenhum código de hook mudou no delta próprio; escopo funcional dos `CA` inalterado, aprovação anterior vale. Remoto sem avanço (`git fetch`: igual ao head local).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto do interpretador sobe só +2168 passos (DECISÃO DO DONO 20/11 19:55, só E51) | `tests.test_hooks_volta_corpus` (teto é a medida exata) | 5893967 para 5896135 = +2168; um passo a mais reprova | passou |
| Índice das fixtures igual ao gerado pelo script | `tests.test_indice_fixtures` | 3158 fixtures | passou |

Prova: `python3 -m unittest tests.test_hooks_volta_corpus tests.test_indice_fixtures` (sem `-I`): `Ran 40 tests in 170.991s · OK`. Registro em `tests/provas/v0479-corpus-custo.md` confere com o código e com a decisão. Suíte inteira: só no CI do PR, não rodada aqui. Teste novo de regra: nenhum no delta (só constante e índice gerado), sem vermelho antes do verde aplicável.

## Revalidação E51.32 (head 96c0215f, antes c792b567)

Delta por `forge-check parecer delta` (sem o que veio da `develop`): `docs/hooks-fixtures.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/apoio_volta_unica.py`, `tests/provas/v0479-corpus-custo.md`, `tests/test_hooks.py` e as fixtures `pp-*`. O hook e as fixtures vêm do E50 (#734, f96ede50), já aprovado no pedido próprio; o ganho próprio do E51 no delta é a constante da soma. Remoto sem avanço (`git fetch`: igual ao head local).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto da soma E50 + E51 = 5897219, +3252 sobre 5893967 (1084 + 2168; abaixo do aviso de +3300, DECISÃO DO DONO 20/11 19:09 e 19:55) | `tests.test_hooks_volta_corpus` (teto é a medida exata) | um passo a mais reprova; 5897219 igual à medida registrada | passou |
| Índice das fixtures igual ao gerado (3196 fixtures, com as `pp-*`) | `tests.test_indice_fixtures` | pasta de fixtures renomeada ou índice velho | passou |
| Barreira de papel nas pastas de parecer (E50, `test_fixtures_do_parecer_pelo_papel`, pisos 13 e 25) | check-run `bateria` do PR | papel x pasta x forma | herdado do parecer do E50 |

Prova: `python3 -m unittest tests.test_hooks_volta_corpus tests.test_indice_fixtures` (sem `-I`): `Ran 40 tests in 159.608s · OK`. A aritmética do registro em `tests/provas/v0479-corpus-custo.md` ("Soma do E50 e do E51") confere com a constante e com as duas decisões. Sem teste novo de regra do E51 no delta (vermelho antes do verde não se aplica). Suíte inteira: só no CI do PR, não rodada aqui.

## Revalidação E51.37 (head 6aa5b7be, delta 96c0215f..6aa5b7be)

Delta por `forge-check parecer delta`: só a fixture `tests/hooks/conformidade/e51-wt-ponto-argumento-pipe-aninhado-libera.json` (comando passa de `docs/reviews` para `docs/regras`, descrição explica: a ação crítica fica fora das pastas de parecer, para a barreira de papel do E50 não recusar por outro motivo, E51.34). Nenhum código de hook mudou. Remoto sem avanço (`git fetch`: igual ao head local). Suíte inteira: só no CI do PR, não rodada aqui.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `find .` depois de pipe, no texto reavaliado, segue livre; o motivo da liberação é a regra do E51, não a barreira de papel (E51.34) | `HookSessaoDoForge.test_travas_do_conformidade` (`e51-wt-ponto-argumento-pipe-aninhado-libera`) | ponto como argumento; pasta fora de parecer | passou |
| Teto da soma e índice das fixtures inalterados | `tests.test_hooks_volta_corpus`, `tests.test_indice_fixtures` | 5897219; 3196 fixtures | passou |

Provas: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: `Ran 2 tests in 5.020s`, `OK`. `python3 -m unittest tests.test_hooks_volta_corpus tests.test_indice_fixtures` (sem `-I`): `Ran 40 tests in 109.260s`, `OK`. `-k test_fixtures` (30 testes, 607 s): `FAILED (failures=2, skipped=4)`; as 2 falhas são o subteste `pesado/mesma-sessao-libera` (`test_fixtures` e `test_fixtures_do_v0442`, `PrazoEstourado: prazo de 120 s estourado`, `hooks/pesado.py`, usuário 5 s de CPU: espera, não cálculo). O delta não toca `hooks/pesado.py` nem fixtures `pesado/`; a mesma falha ocorre no head anterior aprovado 96c0215f (cópia `git archive` em `$TMPDIR`, `-k test_fixtures_do_v0442`: `Ran 1 test in 134.555s`, `FAILED (failures=1)`, mesmo subteste). Todas as fixtures `conformidade/` passaram. É ambiente do sandbox (mesma classe do L08 em `docs/qa/lote-l08.md`), não do delta; o CI (`bateria`) decide. Sem teste novo de regra no delta (só comando de fixture e descrição): vermelho antes do verde não se aplica.
