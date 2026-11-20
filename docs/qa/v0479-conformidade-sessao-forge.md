---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 29cbd24dc696ec318b4a53eb9322f46f149ae713
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-conformidade-sessao-forge (E51.13, revalidação)

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

## Achados
- A3 (recomendado) bin/forge-testes:1 · `--vermelho` do `test_hooks` leva 2200 s por cópia e não aceita `-k` nem classe; `test_vigia_registra` fica sem veredito por erro da base. Cartão: veredito por classe.
