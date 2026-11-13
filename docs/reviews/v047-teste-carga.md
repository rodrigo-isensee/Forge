---
tipo: review
contrato: 1
pedido: v047-teste-carga
branch: melhoria/v047-teste-carga
commit: 171232b97fb8f5a84b426b2fabc5f2a5f1ef5170
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047-teste-carga

Code review da E5.2 (classe C, 51 linhas de teste, abaixo do teto de 150) no head 3da64e12, por instância que não fez a entrega.

## Achados
- A1 (recomendado) tests/test_hooks.py:628 · resolvido no delta: `tests/mutantes/v047-teste-carga.json` existe com 14 mutantes, todos mortos.

## Sondas

## Parecer
Aprovado. O fator `min(2, max(1, carga1min/núcleos))` multiplica o limite de CPU do corpus e o prazo do gh pendurado.

- Teto de 2x pega regressão real: o prazo do gh vai de 9 s a 18 s e o `sleep 30` do fixture segue além; o corpus tem teste que afirma 1,5x e 2x e o limite nunca passa do dobro.
- Leitura da carga falha para 1: `OSError` de `os.getloadavg` devolve 1.0, coberto por teste com mock. Núcleos ausentes recuam para 1.
- O corpus lê a carga antes do lote, e o lote não infla a própria medida.
- Rodei `test_medida_cpu` (8 testes, OK) e `test_hooks -k gh_pendurado` (OK), com carga de 13 em 12 CPUs. A suíte inteira fica no CI.

## Revalidação (delta até 171232b9, volta E5.11)
Li `forge-check parecer delta` (3da64e12..171232b9; domínio: `tests/apoio_volta_unica.py`, `tests/test_hooks.py`, `tests/test_medida_cpu.py`, `tests/mutantes/v047-teste-carga.json`).

- A fórmula (`nucleos_do_processo`, `fator_de_carga`, teto 2) saiu de `test_hooks.py` para `tests/apoio_volta_unica.py`, definida antes do import de `test_hooks`, que a reimporta no fim do módulo; o `forge-mutante` só muta arquivo que não é de teste. Conferi as duas ordens de import (`import test_hooks` e `import apoio_volta_unica`): sem ciclo quebrado. Fórmula idêntica à aprovada.
- Testes novos em `test_medida_cpu.py`: carga de 1 min (não a de 15), carga dada vence a lida, núcleos do processo e recuo para 1. Rodei `test_medida_cpu` (12 testes, OK) e `test_hooks.PoolDosFixtures` (3, OK).
- Rodei `bin/forge-mutante tests/mutantes/v047-teste-carga.json`: M1 a M14 mortos. M10 morre por erro (o `OSError` do mock escapa sob `ValueError`), o que é morte válida. Uma guarda por mutante: `except OSError`, `min`/`max`, `is None`, `or`, `hasattr`.
- Tamanho: 95 linhas de código e teste contáveis, abaixo do teto de 150, um comportamento só.
- A suíte inteira fica no CI (sem PR aberto ainda).
