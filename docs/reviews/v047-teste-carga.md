---
tipo: review
contrato: 1
pedido: v047-teste-carga
branch: melhoria/v047-teste-carga
commit: 3da64e122b71a831b97c1f33987950f353a0e5e7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047-teste-carga

Code review da E5.2 (classe C, 51 linhas de teste, abaixo do teto de 150) no head 3da64e12, por instância que não fez a entrega.

## Achados
- A1 (recomendado) tests/test_hooks.py:628 · `tests/mutantes/v047-teste-carga.json` ainda não existe no head; o QA declara os mutantes da fórmula (min, max, divisão, `OSError`) e a catraca os confere.

## Sondas

## Parecer
Aprovado. O fator `min(2, max(1, carga1min/núcleos))` multiplica o limite de CPU do corpus e o prazo do gh pendurado.

- Teto de 2x pega regressão real: o prazo do gh vai de 9 s a 18 s e o `sleep 30` do fixture segue além; o corpus tem teste que afirma 1,5x e 2x e o limite nunca passa do dobro.
- Leitura da carga falha para 1: `OSError` de `os.getloadavg` devolve 1.0, coberto por teste com mock. Núcleos ausentes recuam para 1.
- O corpus lê a carga antes do lote, e o lote não infla a própria medida.
- Rodei `test_medida_cpu` (8 testes, OK) e `test_hooks -k gh_pendurado` (OK), com carga de 13 em 12 CPUs. A suíte inteira fica no CI.
