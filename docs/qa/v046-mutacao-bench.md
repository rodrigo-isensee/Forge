---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 60bba369d14f778d47f085e4f68c59707c44388f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 E7.4 (mutação dirigida e medidas por versão)

Diff 8b5a44d5..60bba369: `bin/forge-mutante` (`--base SHA` com SPEC, M-1), `bin/forge-changelog release` (aviso M-5 e BENCH-POR-RELEASE), 2 specs de mutantes, testes, doc e fragmento.

## Critério -> teste -> resultado
| Obrigação (decisão do dono 12/11 11:06) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| M-1 roda só os mutantes do arquivo mudado; o resto sai `fora do diff` | `MutacaoDirigida.test_so_o_mutante_do_arquivo_mudado_roda` | mb..rev vs arquivo fora do diff | passa; cai na base |
| M-1: nenhum mutante no diff, saída 2, sem rodar | `test_nenhum_mutante_no_diff_sai_2_sem_rodar` | diff vazio para a spec | passa; cai na base |
| M-1: base inválida ou sem ancestral, saída 2 sem Traceback | `test_base_que_nao_e_commit_ou_sem_ancestral_sai_2` | base ilegível, histórico órfão | passa; cai na base |
| M-5/BENCH: aviso com a tag anterior, só no clone do Forge, sem mudar o código de saída | `ReleaseAvisaMedidasDaVersao` (4 testes) | com tag, sem tag, fora do Forge | passa; 2 caem na base |
| Nada no CI nem em `.githooks/` roda o placar | `test_nem_o_ci_nem_o_envio_rodam_o_placar` (mínimo de 3 fontes) | pasta vazia | passa; diff sem arquivo em `.github`/`.githooks` |

## Provas
- `python3 -m unittest tests.test_changelog`: Ran 73 tests, OK (9,5 s).
- `python3 -m unittest tests.test_forge_mutante`: Ran 105 tests, OK (98 s).
- Vermelho: base 8b5a44d5 (`git archive`) com os testes do head, classes novas: `Ran 7 tests, FAILED (failures=6)` (os 3 de MutacaoDirigida com 4 subcasos, e 2 de medidas). Os 2 restantes (fora do Forge, sem CI) afirmam ausência e passam na base por desenho. `forge-testes --vermelho 8b5a44d5` estourou o prazo de 590 s (rc 124, sem veredito); vale o vermelho manual acima mais a mutação.
- Mutantes: `forge-mutante` das 2 specs (M1..M10, 10 mutantes), `--processos 4`, rc 0, todos `morreu` (M1 :827, M2 :865, M3 :792, M4 :805, M5 :807, M6 :808, M7 :798, M8 :867, M9 changelog:217, M10 changelog:221).
- Cobertura: `forge-mutante --cobertura --base 8b5a44d5`: 9 condições `coberta` (M7 em :798 não aparece na lista, é linha de retorno, não condição); nenhuma linha de guarda sem mutante achada.
- Medida pedida pelo dono: o diff não toca `.github/` nem `.githooks/`; o CI do PR não ganha passo. Custo no teste: as 2 classes novas somam 2,1 s (7 testes), dentro dos 73 e 105 de cada módulo. O M-1 só roda a pedido (`--base`), o placar e o bench só imprimem aviso na release.
- O que só o CI do PR prova: a bateria completa no sha (check-run `bateria`) e o tempo de relógio do job antes e depois; localmente não há como comparar o job.

## Achados
- A1 (recomendado) bin/forge-mutante:827 · a precedência `cobertura or base and not spec` funciona, mas é frágil; parênteses explícitos deixariam a intenção óbvia (sem defeito observado).
