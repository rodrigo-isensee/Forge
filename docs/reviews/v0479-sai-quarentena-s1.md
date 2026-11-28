---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sai-quarentena-s1
commit: 0e1e73639b761a4a4400dc1fd41a9281e57e61be
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.52, saída da quarentena da sonda S1)

## Achados
- A1 (recomendado) tests/provas/v0479-sai-quarentena-s1.md:3 · o motivo da quarentena pedia 10 rodadas verdes sob carga no CI; a prova é local (12 laços de CPU, load 29,96). Vale como proxy sem gastar 10 runs (R-CUSTO); o CI do PR é a única rodada no CI: cite-o no PR antes do merge.

## Sondas

## Parecer
Aprovado. O diff faz só o que a E37.41 pede: tira o `@unittest.skip` de `Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` (3 linhas, corpo intacto), devolve `teto_pulados` a 1 (`tests/config.json:930`, igual a `TETO_PULADOS_ORIGINAL` em `tests/quarentenas.py:13`, como o comentário dali exige no mesmo PR), traz a prova de 10/10 sob carga e o fragmento de changelog. Nenhuma guarda de código mudou (só teste e configuração); a mudança aperta, não afrouxa: a catraca T3 (`regra_teto_pulados`) aceita o teto que cai.

Conferido nesta revisão (teste novo, sem a suíte, que fica no CI):
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k sonda_s1 -k SondaS1ComRelogioFalso`: `Ran 3 tests in 9.388s`, `OK` (a S1 real roda, não pula).
- `python3 -I -m unittest discover -s tests -p test_catraca.py -k TetoDaQuarentena -k teto_pulados`: `Ran 15 tests in 3.394s`, `OK`; inclui `test_o_forge_nao_passa_do_teto_da_quarentena`, que lê o `tests/config.json` real com zero quarentenas abertas.
- Commit único, Conventional Commits em português, cita a etapa. Teto H1: 0 linhas de código.
