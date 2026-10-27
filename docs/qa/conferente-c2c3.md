---
tipo: qa
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: 5818e849140c76b535795feec6238af523d3f68b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: conferente-c2c3 (CONFERENTE-VELOCIDADE-REV, E3.1, revalidação 3 por delta cbb5227..5818e84)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 `--desde`: desfeito em commit linear depois da conferida (segurança A2, forma 1) | Entrega.test_desfeito_em_commit_linear_depois_da_conferida_fica_no_escopo | 4 etapas (codigo, pr, merge-integracao, pedido-de-merge-ao-dono) | passou; F1 morto |
| C1 desfeito pelo merge da base como último commit (forma 2) | Entrega.test_desfeito_pelo_merge_da_base_como_ultimo_commit_fica_no_escopo | 4 etapas, `git rm` dentro do merge | passou; F2 morto |
| C1 merge da base seguido de commit (forma 3) | Entrega.test_desfeito_pelo_merge_da_base_seguido_de_commit_fica_no_escopo | 4 etapas | passou; F3 morto |
| C1, C2, C3 da rodada anterior | conjuntos já aprovados em cbb5227 (c1, c2c3) | ver parecer anterior | passou; todos os mutantes mortos |

## Cenários e resultado real
- `python3 -m unittest`: tests.test_volta_por_delta 61 OK, tests.test_etapa_do_brief 52 OK, tests.test_conferencia_base_dono 21 OK.
- `bin/forge-mutante` uma spec por chamada, todas rc=0: conferente-c1-2 (F1, F2, F3 morreram), conferente-c1 (C1 a C8 morreram), conferente-c2c3 (C1 a C8 morreram).
- Lista contra o diff (5818e84 sobre cbb5227): a única linha de guarda mudada em `bin/forge-check` é a 950-951 (`n in desfeitos` no filtro dos dois pais, F2); as linhas 504-505 (commit linear e merge seguido de commit) têm F1 e F3; a 958 já tinha C7 do c1. Sem linha de guarda sem mutante.
- Mutação à mão (cópia em `$TMPDIR/qa-engineer-conferente-c2c3/m`) de `if valido else set()` na linha 950: sobrevive, e é equivalente: sem `valido`, `desfeitos_da_entrega` monta `base...None`, o git recusa e `nomes_do_intervalo` devolve `[]` (linha 729), o mesmo `set()`. Aceito como mutante equivalente.
- Vermelho antes do verde: o vermelho de cada teste novo é o mutante F1 a F3 (o teste cai sem a guarda); `forge-testes --vermelho` não rodado (sem suíte completa neste brief).
- A2 da segurança (4f7f81b) coberto nas três formas (linear, merge como último commit, merge seguido de commit), nas quatro etapas.
- Bugs abertos: nenhum.
