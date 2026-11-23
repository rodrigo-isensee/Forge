---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-promover-sem-auto
commit: a438dcc37ffd41ea37bd580521824fd217fd300b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: PROMOVER-SEM-AUTO-MERGE (E118.4)

Escopo: `scripts/promover-homolog.py` (passos 5 a 7), `docs/promocao-integrador.md`, testes `tests/test_promover_homolog.py` e specs de mutantes. Decisão do dono: merge automático proibido em qualquer PR. Sem suíte local; a suíte inteira é do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pendente sai com 4, sem comando de merge | `Execucao.test_check_pendente_nao_imprime_merge_e_sai_com_4` | pendente | passou |
| Sem check do PR, ou só do push, sai com 4 | `test_sem_checks_ainda_nao_imprime_merge`, `test_so_checks_do_push_nao_sao_verdes_e_nao_ha_merge` | vazio | passou |
| Obrigatório sem execução sai com 4 | `test_obrigatorio_sem_execucao_do_pr_nao_imprime_merge` | falta de 1 de 3 | passou |
| Obrigatório pulado sai com 1 | `test_obrigatorio_pulado_para` | skipping | passou |
| Nunca sai `--auto` (verde, pendente, vazio, push, vermelho, rótulo, dry-run) | `test_nunca_imprime_merge_automatico` | todos os caminhos | passou |
| Verde imprime merge direto preso ao head | `test_abre_o_pr_para_a_homolog_...` | head sha | passou |
| Lista obrigatória lida do `bin/forge-fechar` (ausente ou vazia para) | `ChecksObrigatorios.*` | lista vazia | passou |

## Provas
- Testes do módulo: `python3 -I -m unittest discover -s tests -p test_promover_homolog.py` → `Ran 47 tests ... OK`.
- Sondas: pendente rc 4 sem merge, obrigatório pulado rc 1, nenhum `--auto` em nenhuma saída (testes acima, no `gh` falso).
- Vermelho: `forge-testes --vermelho 38c37de9e --modulos tests.test_promover_homolog`: `vermelho: base=38c37de9e852 head=a438dcc37ffd`; `contagem: não prova (passa na base)=37; prova (API ausente)=2; prova (asserção)=8`; nenhum teste cai no HEAD.
- Mutantes: `forge-mutante tests/mutantes/v0480-promover-sem-auto.json tests/mutantes/v0480-promover-sem-auto-2.json` → M1 a M10 todos `morreu`; `forge-mutante tests/mutantes/promover-auto.json` → M1, M3, M4, M5, M6 `morreu`.
- Cobertura: `forge-mutante --cobertura --base 38c37de9e` → linhas 313, 314, 323, 324, 326, 362 cobertas; só aviso `spec editada · promover-auto.json` (M2 removido; a guarda do `--auto` agora é o teste novo).
- O remoto andou (pareceres de segurança e de review): rebase sobre ele, sem force.

## Cenários e resultado real
Sem bug aberto. Fora do alcance: o merge real no GitHub (o script só imprime) e a bateria completa (check-run `bateria` do CI).
