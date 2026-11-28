---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-afetados-catraca-custo
commit: f4ae675c22dd8b656a5dc28a7db85f1e3e3d1e99
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (#960, AFETADOS-CATRACA-E-CUSTO, E9.1 e E9.2, classe C)

1ª rodada completa no head f4ae675c (E9.4), diff `ed6e6dbf..f4ae675c`. Revisor, não autor; cópia própria em `/workspaces/.forge-contrib/.forge/wt/v048-afetados-catraca-custo-qa-engineer`.

## Achados
- A1 (bloqueante) bin/forge-testes:1353 · a linha "catraca no diff" no stdout do plano quebra `modulos_listados` (bin/forge-mutante:1193, fullmatch no stdout): diff em bin/, hooks/ ou protegido perde o recorte H5. Reproduzido (S1); o review achou o mesmo (A1 dele).
- A2 (recomendado) bin/forge-testes:575 · `contar_testes` conta `def test*` por `ast` e erra para baixo em módulos com herança, `load_tests` ou geração: 7325 contados contra 7439 reais (9 de 263 módulos divergem). O corte de 1000 pode atrasar ~1,5%; documente como aproximação.

## Sondas
- S1 · `modulos_listados(["bin/forge-mutante"])` no head f4ae675c · espera: test_forge_mutante, test_hooks_volta_corpus, test_pre_push_patch · obtido: `set()`, pois o stdout do plano tem 2 linhas (a 2ª, "catraca no diff"); bug médio, só prazo

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E9.1: hooks/, bin/ e protegido levam catraca e custo | `CustoECatraca.test_hooks_bin_e_protegidos_levam_a_catraca_e_o_custo`, `ListaDaCatracaReal` | caminho protegido fora de hooks/ e bin/ (`scripts/conferir-release.py`) | passou |
| E9.1: o resto fica como está | `test_o_resto_fica_como_esta`, `PeloComando.test_listar_sem_hook_bin_nem_protegido_fica_como_esta` | `scripts/protegido.pyx`, `docs/hooks/x.md`, lista vazia | passou |
| E9.1: falha fechada | `test_protegidos_ilegiveis_contam_como_tocados`, `test_catraca_em_link_nao_conta`, `test_sem_a_catraca_nada_muda` | PROTEGIDOS vazia, não-texto, ausente, link | passou |
| E9.1: catraca roda no modo do diff e devolve a saída dela, também sem teste afetado | `PeloComando.test_afetados_roda_a_catraca_...`, `test_sem_teste_afetado_a_catraca_roda_mesmo_assim`, `test_custo_vermelho_reprova_...` | saída diferente de 0, plano vazio | passou |
| E9.2: 1000 mantém, 1001 corta | `PeloComando.test_no_limite_o_plano_fica_inteiro` (998+1+1), `test_acima_do_limite_...` (999+1+1) | os dois lados do limite | passou |
| E9.2: contagem sem importar | `LimiteLocal.test_conta_so_os_metodos_test_das_classes`; conferida à parte contra `unittest` real nos 263 módulos | módulo ilegível, ausente, função solta | passou, com A2 |
| E9.2: testes do arquivo mudado | `LimiteLocal.test_testes_do_arquivo_mudado` (MAPA, convenção, subcomando, sem test_forge) | `test_forge` excluído | passou |
| E9.2: corte só no `--afetados` | `PeloComando.test_o_limite_vale_so_para_os_afetados` | 1001 testes sem `--afetados` | passou |
| Estável de ponta a ponta: o consumidor `modulos_listados` | nenhum teste | stdout de duas linhas | sem teste: A1 |

## Evidência
- Testes do diff: `tests/test_afetados_catraca_custo.py` 19 OK (via `unittest discover -s tests`).
- Vermelho antes do verde, `bin/forge-testes --vermelho ed6e6dbf --modulos test_afetados_catraca_custo`: 7 provam por asserção e 10 por API ausente; 2 "não prova (passa na base)" (`test_listar_sem_hook_bin_nem_protegido_fica_como_esta`, `test_o_limite_vale_so_para_os_afetados`), guardas de regressão do comportamento antigo, aceitas. Contagem: `não prova=2; prova (API ausente)=10; prova (asserção)=7`.
- Mutantes: `bin/forge-mutante` nas 5 listas (`tests/mutantes/v048-afetados-catraca-custo{,-2,-3,-4,-5}.json`, `--processos 4`): M1 a M32 todos `morreu`, M32 pelo `test_conta_so_os_metodos_test_das_classes`. `--cobertura --base ed6e6dbf`: toda guarda mudada coberta, a 1235 da base isenta com motivo; nenhuma sem mutante.
- A suíte inteira não foi rodada aqui (G3): fica para o CI.

## CI
Sem linha `- ci:`. No PR #960, o run do f4ae675c foi substituído pelo dos pareceres (descendente 4f92db0b, diff só em docs/reviews e docs/security); neste instante a suíte 1/5 a 5/5 está pendente no descendente, a `bateria (pareceres)` e a `catraca` vermelhas (esperam parecer aprovado ou rótulo) e a `catraca (conferência)` pendente; no run anterior estava vermelha pelo texto do PR (A2 do review). Sem CI verde do head, o QA não aprova.

## Parecer
Reprovado, por A1 (bloqueante): o plano do forge-testes ganhou uma 2ª linha no stdout que desliga o recorte de módulos do forge-mutante justamente nos diffs de classe C; falta um teste de contrato que rode `modulos_listados` com a catraca no plano. Os critérios E9.1 e E9.2 e os dois lados do limite estão provados, M1 a M32 morrem pela asserção e o vermelho foi visto. A2 vira cartão depois do merge. Na volta, retesto só o delta de `forge-check parecer delta`.
