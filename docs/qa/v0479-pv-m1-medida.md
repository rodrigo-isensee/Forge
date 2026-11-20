---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: 580fea97a00363ac78560eae7a875e80cad7159b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: PR-VERDE M1 (`forge-placar ci-primeira`)

Obrigações: a definição D7 (aceita pelo dono em 20/11) como está no docstring de `bin/forge-placar`; sem especificação de UX nem contrato de API (ferramenta de linha de comando). Sem suíte local (E57.8): rodei só `tests/evals/test_placar.py`, as specs de mutantes e o vermelho do teste novo.

## Achados
- A1 (recomendado) tests/evals/test_placar.py:748 · a classe CiPrimeira (12 testes) ficou depois do `unittest.main()`: rodar o arquivo direto executa 52 de 64 testes. Pelo discover (CI) roda tudo; mover o bloco para antes do `if __name__`.
- A2 (recomendado) bin/forge-testes:785 · `--vermelho` só enxerga tests/test_*.py e recusa `--modulos evals.test_placar`; teste novo em tests/evals não tem vermelho pela ferramenta (feito à mão abaixo). Ampliar o glob.

## Critério → teste → resultado
| Critério (D7) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| verde só com a 1.ª execução de CI e Catraca em success | test_verde_nos_dois_exigidos | taxa 1.0 | passou |
| vermelho separado por workflow e por job, dia e semana ISO | test_catraca_vermelha_separada_por_workflow_e_job | job skipped fora da lista | passou |
| cancelada fora da taxa; vermelho ganha de cancelada e pendente | test_cancelada_..., test_vermelho_ganha_... | taxa None (0/0) | passou |
| 1.º head = do 1.º run depois de aberto (PR reaberto, branch reescrita) | test_primeiro_head_e_o_do_primeiro_run_depois_de_aberto | run anterior à abertura | passou |
| run de push ou de outra branch não é do PR | test_run_de_push_e_de_outra_branch_nao_e_do_pr | evento e branch | passou |
| rerun (attempt > 1) não é verde | test_rerun_verde_nao_conta_como_verde | attempt = 2 | passou |
| workflow fora da lista ignorado; exigido sem run = lacuna | test_workflow_fora_da_lista_nao_conta, test_exigido_sem_execucao_no_primeiro_head_e_lacuna | lista vazia de runs | passou |
| dependabot e fora da janela ficam fora | test_dependabot_e_pr_fora_da_janela_ficam_fora | limite exclusivo `--ate` (dia 21), PR de 11-01 | passou |
| fonte ausente ou ilegível: lacuna, rc 2, nunca verde | test_resposta_ilegivel_sai_lacuna_nunca_verde | não JSON, não lista, campo faltando, data inválida, item não objeto, aninhado fundo, arquivo ausente, `--json` | passou |
| `--exigidos` vazio é uso errado | test_exigidos_vazio_e_uso_errado | lista só com vírgula | passou |

Bordas que provei à parte: ver Provas (mutantes cobrem 28 condições do diff).

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests/evals -p test_placar.py`: Ran 64 tests, OK (12 do CiPrimeira, 14 s). Direto (`python3 -I tests/evals/test_placar.py`): Ran 52, OK (A1).
- Vermelho antes do verde (à mão, porque A2): cópia do HEAD com `bin/forge-placar` da base 5ccac0bf: os 12 testes do CiPrimeira falham (`FAILED (failures=18)`, subtestes incluídos); os 52 antigos passam.
- `bin/forge-mutante --cobertura --base 5ccac0bf...`: nenhuma linha "sem mutante"; 4 linhas `isenta` com motivo (ordem de impressão, traço, equivalência author/ramo, apoio do teste).
- `bin/forge-mutante --processos 2` nas 4 specs (`-`, `-2`, `-3`, `-4`): M1 a M29 (sem M12, que não existe nas specs), 28 mutantes, todos `morreu`; rc=0; nenhum sobrevivente. M2, M26 e M27 morreram por erro do teste declarado (controle verde).
- Segurança de entrada: o teste roda com `-I` e ambiente limpo (AR-4, AR-5); a ferramenta só lê arquivos JSON, sem rede (R-CUSTO).
- CI do mesmo sha (`bateria`): não citado; a suíte inteira é do CI do PR.
