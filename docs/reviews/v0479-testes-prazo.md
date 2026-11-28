---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-testes-prazo
commit: 15d0b7fde78e496c9b6d1cfaa2dd29f46f691fb4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E43.2 (lote 1 da varredura de testes de prazo)

Diff revisado: `5ccac0bf..15d0b7fd` (2 commits; `tests/test_estado_da_branch.py`, `tests/test_doutor_relogio.py`, `tests/mutantes/v0479-testes-prazo.json`, `tests/provas/v0479-testes-prazo.md`, `changelog.d/v0479-testes-prazo.md`). Só teste e documentação; nenhum código de produção mudou (H1 não se aplica).

## Ferramenta (citada, sem refazer)
- `bin/forge-mutante tests/mutantes/v0479-testes-prazo.json --processos 1` (rev 15d0b7fde78e): M1 morreu (`bin/forge-check:8852`), M2 morreu (`bin/forge-check:8865`), M3 morreu (`bin/forge_versoes.py:225`).
- suíte: 15d0b7fde78e496c9b6d1cfaa2dd29f46f691fb4 rc=0 módulos=test_estado_da_branch,test_doutor_relogio
- Módulos tocados: `python3 -m unittest tests.test_estado_da_branch tests.test_doutor_relogio`: 33 testes, OK. Suíte inteira: fica com o CI do PR (`R-REVIEW`).

## Leitura
- `test_gh_lento_respeita_o_teto`: deixa de dormir 30 s; o `subprocess.run` falso só intercepta `gh` (o `git` segue real) e levanta `TimeoutExpired` com o teto recebido. Prova o teto passado (`{10}`), a linha `não verificável (gh passou de 10 s)` e `recusas == []` (não barra). O caminho pela CLI do `não verificável` continua coberto pelos casos `sem gh` e `sem rede` (linhas 130 e 132), então a troca para chamada em processo não perde o fio do `gerar`.
- `test_conexao_que_nunca_responde_estoura_no_prazo_total`: o fio fica preso num `Event` soltado só depois da volta; se a função esperasse o fio, a volta viria pelo teto do `wait` e `sozinha` acusaria. Determinístico, sem medir duração; `finally` solta o fio, sem thread pendurada no fim da suíte.
- Mutantes: um por guarda tocada pelos testes, cada um com teste de comportamento do ramo de falha, nenhum lendo texto da fonte.
- Prova: a varredura registra o critério, as medidas e o que sobra (oráculo protegido e `tests/test_hooks.py` fora por ordem do dono), sem editar oráculo.
- Commits em Conventional Commits em português; fragmento de changelog presente.

## Sondas

## Parecer
Aprovado. Os dois testes deixam de depender da velocidade da máquina e continuam provando o comportamento (teto do `gh` e prazo total do relógio); os três mutantes declarados morrem. Sem achados.
