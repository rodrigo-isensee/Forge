---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 154a36f1283ebb81be649cf08e1235f4636ba6a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 S1a, `forge-check status` (PR #910, E20.7, revalidação)

Escopo: só o delta `0b412b4a..154a36f1`, lido por `forge-check parecer delta` (domínio do review: `bin/forge_estado.py`, `docs/indice-forge.md`, `tests/mutantes/v0481-s1-status-5.json`, `tests/test_forge_status_estado.py`). Os pareceres de QA e segurança do delta ficam com os seus papéis.

## Delta lido
- A1 da 1.ª rodada resolvido: `docs/indice-forge.md:44` ganhou a linha do `forge_estado.py`; `test_indice_forge` verde no CI (partes 3/5 em 3.12 e 3.14).
- A2 resolvido: `bin/forge_estado.py:100` passa a usar `instante()`, que converte o `ValueError` em `NaoVerificavel("data ilegível: ...")`. O `executar` já tratava esse caso e devolvia `não verificável (...)` com rc 0. É uma linha só, e não traz guarda nova fora da M33.
- Testes do ramo: `Itens.test_decisoes_com_data_fora_do_calendario_nao_verificavel` (02-30 e 13-45) e, pelo forge-check real com `-I`, ambiente limpo e HOME temporário, a sonda S1 deste review e a S1 da segurança (seis linhas, rc 0, sem traceback). A limpeza `ctx["seguro"]` é testada com uma limpeza falsa e também com a `sem_controle` real (gh falso com ESC e U+2028).
- Mutantes M33 (`instante` → `fromisoformat`) e M34 (sem `ctx["seguro"]`): os dois morreram, e cada um tem dois testes de comportamento, nenhum que leia a fonte.

## Como foi verificado
- `python3 -m unittest tests.test_forge_status_estado` no head: 24 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-s1-status-5.json`: M33 morreu (`bin/forge_estado.py:100`) e M34 morreu (`bin/forge_estado.py:134`).
- `bin/forge-mutante --cobertura --base 0b412b4a`: nenhuma guarda do delta sem mutante.
- CI do head lido em `gh pr checks 910`: as 10 partes da suíte (3.12 e 3.14), `teto de pulados`, `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)` e `árvore já provada na develop` estão verdes. Ficaram vermelhos só `bateria (pareceres)`, `bateria` e `catraca`, que esperam este parecer e o rótulo.

## Achados
- A3 (recomendado) bin/forge_estado.py:100 · continua aberto desde a 1.ª rodada: a hora da pergunta, sem fuso, herda o fuso de `agora`, e sem `--agora` a idade depende do fuso do container. Vira cartão depois do merge.

## Parecer
Aprovado. Os dois bloqueantes da 1.ª rodada foram corrigidos e cada correção tem teste do ramo de falha e mutante morto. O delta não traz bloqueante novo.

- ci: 154a36f1283ebb81be649cf08e1235f4636ba6a6 verde
