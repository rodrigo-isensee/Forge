---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: afc7083d568d98634c39a498fef1954cc4f3dc1f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (E110, placar: prometido ao lado do real)

Escopo: `bin/forge-placar propostas` com `prometido: <N>%` na Métrica (MEDIR-DE-NOVO-O-PROMETIDO). Sem suíte local; a suíte inteira é do check-run `bateria` do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Real medido ao lado do prometido | test_real_medido_ao_lado_do_prometido | n/a | passou |
| `--json` com `prometidos` | test_json_traz_o_prometido_e_o_real | n/a | passou |
| Janela de depois aberta: sem medida | test_janela_de_depois_aberta_sai_sem_medida | um dia antes de fechar | passou |
| Janela fecha no dia: mede | test_janela_que_fecha_no_dia_mede | dia exato do fechamento | passou |
| Sem fonte / base zero | test_sem_fonte_sai_sem_medida, test_base_zero_sai_sem_medida | vazio, divisão por zero | passou |
| Métrica fora do placar não quebra | test_metrica_fora_do_placar_nao_quebra_e_sai_sem_medida | métrica inválida | passou |
| Valor não numérico é falta | test_prometido_sem_numero_e_falta | entrada inválida | passou |
| Sem prometido, sem linha | test_proposta_sem_prometido_nao_ganha_a_linha | vazio | passou |
| Só uma janela sem medida | test_so_a_janela_de_antes_sem_medida_sai_sem_medida | janela parcial | passou |
| Sem ID vira `?` | test_proposta_sem_id_sai_com_interrogacao | ID vazio | passou |
| Decimal com vírgula e sinal | test_decimal_com_virgula_e_ganho_que_sobe | formato | passou |

## Execução (head afc7083d, TMPDIR próprio)
- `python3 -I -m unittest discover -s tests -p test_placar_prometido.py`: Ran 12 tests, OK.
- `python3 -m unittest tests.evals.test_placar`: Ran 68 tests, OK.
- Vermelho (manual, em cópia da base 900bfdfe com o teste novo): Ran 12 tests, FAILED (failures=9, errors=3), os 12 caem sem a implementação. `forge-testes --vermelho 900bfdfe` (suíte inteira, 233 módulos) terminou com rc=2: `test_placar_prometido` com 9 testes `prova (asserção)` (H=ok, B=falha) e 3 com B=erro (`test_json_traz_o_prometido_e_o_real`, `test_proposta_sem_id_sai_com_interrogacao`, `test_proposta_sem_prometido_nao_ganha_a_linha`: a base não tem a chave `prometidos`, erro e não asserção, `sem veredito`); nenhum cai no HEAD. O rc=2 vem de módulos alheios ao diff: `test_hooks` (prazo, sem veredito) e `test_oraculo_sempre_atual.Falha.test_prazo_estourado_mata_o_filho_e_segue` (H=erro, B=erro, falha da entrega, não toca o placar). Contagem: dívida pré-existente=39; falha da entrega=1; prova=9; sem veredito=4.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-placar-prometido.json tests/mutantes/v0478-placar-prometido-2.json`: M1 a M9 `morreu`, nenhum sobrevivente.
- `forge-mutante --cobertura --base 900bfdfe`: linhas 554, 580, 583, 586, 595, 625 cobertas; 593 e 594 saem "sem mutante" mas com `por quê` apontando M6/M7 (mortos); `tests/pesos-d4.json` é dado, não regra.
