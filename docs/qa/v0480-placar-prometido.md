---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: d27d69cdee924cacfd4ad969e30ec426ecdf5f1b
parecer: aprovado
escopo: incremental
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
- Vermelho (manual, em cópia da base 900bfdfe com o teste novo): Ran 12 tests, FAILED (failures=9, errors=3), os 12 caem sem a implementação. `forge-testes --vermelho 900bfdfe` foi interrompido por demora (sem veredito); o vermelho vale pela rodada manual.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-placar-prometido.json tests/mutantes/v0478-placar-prometido-2.json`: M1 a M9 `morreu`, nenhum sobrevivente.
- `forge-mutante --cobertura --base 900bfdfe`: linhas 554, 580, 583, 586, 595, 625 cobertas; 593 e 594 saem "sem mutante" mas com `por quê` apontando M6/M7 (mortos); `tests/pesos-d4.json` é dado, não regra.

## Revalidação (head b57a9676, delta desde afc7083d)
Delta de código: `PROMETIDO` limitado a 6 dígitos inteiros (`bin/forge-placar:111`, o float nunca vira `inf`), mensagem de falta, mapa do `forge-testes` e mutantes M6, M7, M10. Sem achado.
- Provas: `python3 -I -m unittest discover -s tests -p test_placar_prometido.py`: Ran 14 tests, OK.
- Provas: `bin/forge-mutante --base afc7083d568d98634c39a498fef1954cc4f3dc1f --ids M6,M7,M10 <spec-1> <spec-2>`: `base=afc7083d… rev=b57a9676…`; M6 `morreu · bin/forge-placar:594`, M7 `morreu · bin/forge-placar:593`, M10 `morreu · bin/forge-placar:111`; rc 0, nenhum sobrevivente.
- Suíte inteira: check-run `bateria` do PR no mesmo sha (não rodada local).

## Revalidação (head d27d69cd, merge da develop)
Delta no domínio: `bin/forge-testes` (mapa do `test_ambiente_recriacao`), `tests/pesos-d4.json` e `tests/test_testes_tocados.py`, todos vindos da develop com o conflito resolvido em `test_testes_tocados.py`. Nada toca `bin/forge-placar`. Sem achado.
- Provas: `python3 -I -m unittest discover -s tests -p test_testes_tocados.py`: Ran 196 tests, OK (skipped=1, skip herdado da develop).
- Provas: `python3 -I -m unittest discover -s tests -p test_placar_prometido.py`: Ran 14 tests, OK.
- Suíte inteira: check-run `bateria` do PR no mesmo sha (não rodada local).
