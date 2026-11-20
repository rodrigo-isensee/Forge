---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: a554e34536490ff7af78000f76b67a1652f6e840
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

## Achados
- A3 (recomendado) bin/forge-testes:1 · `--vermelho` do `test_hooks` leva 2200 s por cópia e não aceita `-k` nem classe; `test_vigia_registra` fica sem veredito por erro da base. Cartão: veredito por classe.
