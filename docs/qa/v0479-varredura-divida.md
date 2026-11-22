---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-varredura-divida
commit: 5b1ad8ca2cd4c9ecc07c980cf02a16b066884c3f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: varredura semanal de dívida (E95.4)

Escopo: `scripts/varredura-divida.py`, `tests/test_varredura_divida.py`, specs `tests/mutantes/varredura-divida*.json`. Sem suíte local; o CI do PR roda a bateria.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só lê, não grava | Varredura.test_so_le | n/a | passou |
| Ordem estável, uma linha por achado | test_lista_cada_achado_em_ordem_estavel | ordem | passou |
| Base dada / sem develop usa main | test_base_dada_nao_se_lista, test_sem_develop_a_base_e_a_main | base ausente | passou |
| Pesos e spec ilegíveis | test_pesos_ilegiveis_nao_geram_achado, test_spec_no_lugar_nao_gera_achado, test_spec_recusada_vira_um_achado_e_sem_spec_nenhum | arquivo ilegível | passou |
| Raiz inexistente, fora do git, subpasta | test_raiz_que_nao_existe_e_erro_de_uso, test_pasta_fora_do_git_varre_o_que_tem, test_subpasta_varre_o_repositorio_inteiro | raiz inválida | passou |
| Cópias abaixo do limite ou fora do Forge | test_copias_abaixo_do_limite_ou_fora_do_forge_nao_se_listam | limite de MB | passou |
| Projeto do forge-init: zero achados | ProjetoDoForgeInit.test_projeto_novo_roda_sem_achado | projeto novo | passou |

## Cenários e resultado real
- Vermelho antes do verde (`bin/forge-testes --vermelho 9d5dcb6e7f5436c2fea8d7ed84a66fc3e6063f14 --modulos tests.test_varredura_divida`): `vermelho: base=9d5dcb6e7f54 head=7bfd64e7d4e2 módulos=test_varredura_divida`; `contagem: prova (asserção)=12`; os 12 testes H=ok, B=falha.
- Mutantes (`bin/forge-mutante` nas 3 specs, `--processos 2`): rc 0, M1 a M22 todos `morreu`, nenhum sobrevivente.
- `python3 -I -m unittest discover -s tests -p test_varredura_divida.py`: 12 testes OK.
- Sem `skip`, `skipIf` nem `expectedFailure` no módulo de teste (grep vazio).
- Saída no Forge (`--copias` inexistente): 46 linhas (11 branch-mesclada, 31 mutante-velho, 3 teste-lento, fecho `varredura: 45 achado(s)`), idêntica em duas rodadas, rc 0.
- Projeto criado com `bin/forge-init` e versionado: `varredura: 0 achado(s)`, rc 0.

## Revalidação (delta 7bfd64e7..5b1ad8ca)
- Vermelho do teste novo (`bin/forge-testes --vermelho dfc70dc5 --modulos tests.test_varredura_divida`): `vermelho: base=dfc70dc50cbc head=5b1ad8ca2cd4`; `test_filho_nao_grava_cache_de_bytecode_no_forge · H=ok · B=falha · prova (asserção)`; revertido à base: `scripts/varredura-divida.py`.
- Mutantes (`bin/forge-mutante` nas 3 specs, `--processos 2`): rc 0, M1 a M23 todos `morreu` (M23 em `scripts/varredura-divida.py:73`), nenhum sobrevivente.
- `skip`, `skipIf`, `expectedFailure` em `tests/test_varredura_divida.py`: grep vazio.
