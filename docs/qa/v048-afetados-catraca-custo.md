---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: ecc3b7429450779edbda367bb40ddf834e4417d4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (#960, AFETADOS-CATRACA-E-CUSTO, E9.1 e E9.2, classe C), delta da volta 1

Delta `f4ae675c..ecc3b742`, revisado em cópia própria (`.../v048-afetados-catraca-custo-qa-engineer-2`). Revisor, não autor. A rodada completa de f4ae675c fica no histórico git deste arquivo.

## Achados
- A2 (recomendado) bin/forge-testes:575 · `contar_testes` conta `def test*` por `ast` e erra para baixo (7325 contados contra 7439 reais); do 1º parecer, fora do delta: cartão depois do merge, documente como aproximação.

## Sondas
- S1 (A1 anterior, resolvido) · `modulos_listados(["bin/forge-mutante"])` no head ecc3b742, com a catraca no plano · espera: test_forge_mutante, test_hooks_volta_corpus, test_pre_push_patch · obtido: `test_forge, test_forge_mutante, test_hooks_volta_corpus, test_indice_forge, test_oraculo_sempre_atual, test_oraculo_v047, test_pre_push_patch` (recorte H5 de volta); a linha da catraca vai ao stderr e o stdout do plano tem 1 linha.

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Plano numa linha no stdout, catraca no stderr | `ContratoDoListar.test_modulos_listados_de_bin_forge_mutante_no_forge`, `PeloComando` (`len(stdout.splitlines()) == 1`) | diff em bin/ com catraca no plano | passou |
| Catraca apagada no diff ou trocada por symlink pede a catraca e reprova sem executar | `CustoECatraca.test_catraca_em_link_pede_a_catraca_e_nao_e_rodavel`, `test_catraca_apagada_no_diff_pede_a_catraca`, `test_catraca_comum_e_rodavel`, `PeloComando.test_catraca_em_link_reprova_sem_executar` | symlink, apagada no diff, projeto sem catraca (segue sem) | passou |
| scripts/ em PASTAS_DA_CATRACA | `test_hooks_bin_e_protegidos_levam_a_catraca_e_o_custo` (`scripts/outro.py`), `test_o_resto_fica_como_esta` (`lib/scripts/x.py`, `tests/scripts/x`) | prefixo, não substring | passou |

## Evidência
- Testes do delta, `python3 -m unittest tests.test_afetados_catraca_custo tests.test_forge_mutante.ContratoDoListar`: `Ran 23 tests ... OK`.
- Vermelho do contrato, `bin/forge-testes --vermelho c7df0398 --modulos test_forge_mutante`: `contagem: não prova (passa na base)=158; prova (asserção)=1` (o `ContratoDoListar`, como esperado; os 158 são a suíte antiga do módulo, que passa na base).
- Mutantes, `bin/forge-mutante tests/mutantes/v048-afetados-catraca-custo-5.json ...-2.json ...-3.json --processos 3`, saída 0: M32 a M39 e M9 a M23 todos `morreu` (M33 a M39 e M9, M12, M21 incluídos). `--cobertura --base f4ae675c` e `--base ed6e6dbf`: toda linha de guarda mudada coberta; a 1235 da base isenta com motivo; nenhuma sem mutante.
- A suíte inteira não foi rodada aqui (G3): vale o CI.

## CI
- ci: ecc3b7429450779edbda367bb40ddf834e4417d4 verde

No `gh pr checks` do #960, run do ecc3b742: suíte 1/5 a 5/5, instalação, bateria (passos), bateria (verificações longas), catraca (conferência) e árvore já provada verdes; só `bateria (pareceres)` falha (espera pareceres), fora da conta.

## Parecer
Aprovado no delta. A1 resolvido: contrato do `--listar` no teste do forge-mutante, vermelho visto, catraca apagada ou trocada por symlink reprova sem executar, M33 a M39 e M9, M12, M21 mortos pela asserção. A2 antigo segue cartão pós-merge.
