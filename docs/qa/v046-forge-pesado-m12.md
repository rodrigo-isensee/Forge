---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/forge-pesado-m12
commit: cdfafd25f1f6dcbeb7d22caabdb58b68f53f6773
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E14.2, M12 `bin/forge-pesado`)

Head cdfafd25 lido na worktree limpa, sem escrita nela. Sem custo (`R-CUSTO`). Suíte inteira só no check-run `bateria` do PR (a branch ainda não tem PR); local rodei o módulo novo, o vermelho e os mutantes.

## Achados
- A1 (recomendado) bin/forge-pesado:1 · a mensagem do hook `pesado` e a skill `esperar-estado` (regra 5) ainda mandam ler ou apagar `pesado.json` à mão; falta apontar para `forge-pesado status` (já registrado pelo autor como etapa curta). Não bloqueia.

## Critério → teste → resultado
Sem `CA-n` de UX: a obrigação é a ordem do dono em E14.2 (mostrar quem tem a vez e esperar com teto, só leitura, sem mudar `hooks/`, teste em módulo novo) e `R-TETO`.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| status livre | `test_status_livre_sem_trava` | sem arquivo | passou |
| status ocupada (agente, comando, desde, pid vivo) | `test_status_ocupada_diz_quem_desde_quando_e_o_pid_vivo` | n/a | passou |
| pid só se mostra, não decide | `test_pid_morto_aparece_mas_nao_solta_a_trava` | pid inexistente | passou |
| trava vence em desde + teto | `test_trava_vencida_fica_livre` | 601 s (logo fora) | passou |
| `desde` não numérico ou JSON que não é objeto | `test_trava_sem_desde_numerico_ou_que_nao_e_objeto_fica_livre` | tipo inválido | passou |
| texto gravado não mexe no terminal | `test_comando_com_caractere_de_controle_sai_escapado` | ESC | passou |
| fila: só flock preso, sem apagar, sem seguir link | `test_fila_conta_so_a_senha_presa_sem_apagar_a_morta_nem_seguir_link` | link simbólico, senha morta | passou |
| estado ilegível, fora de projeto saem 2 | `test_json_ilegivel_sai_2`, `test_fora_de_projeto_sai_2` | JSON truncado, sem projeto | passou |
| esperar: livre sai 0; teto sai 1 com progresso; fila viva bloqueia; pega a vez | `test_esperar_livre_*`, `_ocupada_*`, `_com_fila_viva_*`, `_pega_a_vez_*` | teto, passo, fila | passou |
| teto fora da faixa (0, 541, nan, passo 0) sai 2; 540 vale | `test_teto_e_passo_fora_da_faixa_saem_2`, `test_teto_no_limite_vale` | 0, 540, 541, nan | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_pesado`: 15 testes, OK (5,6 s). Worktree continua limpa.
- Vermelho antes do verde, `bin/forge-testes --vermelho 2b896503...` (base 2b89650303b0, head cdfafd25f1f6): revertidos `bin/forge-pesado` e o fragmento; os 15 testes novos `H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=637; prova (asserção)=15`; rc 0.
- Mutantes, `bin/forge-mutante` nas duas specs (16): M1 a M16 `morreu`, nenhum sobrevivente nem equivalente; rc 0.
- Cobertura: `forge-mutante --cobertura --base 2b896503...` lista todas as condições mudadas (linhas 38, 53, 54, 60, 63, 75, 79, 93, 96, 103) com mutante; só a linha 112 (`__main__`) isenta, com motivo aceito.
- Só leitura: o teste da senha morta confirma que o arquivo fica; nenhum teste ou leitura do código encontrou escrita em `pesado.json` ou na fila. `hooks/` intocado (diff: 5 arquivos, `bin/`, `tests/`, changelog).
- Limite: o fluxo contra o hook real em duas sessões não foi exercitado; os testes usam estado montado à mão no formato que `hooks/pesado.py` grava.
