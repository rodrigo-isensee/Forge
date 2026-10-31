---
tipo: revisao-devops
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c1
commit: 655ae8c8a6f56ac44c78e241ee570dcebbd39222
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-31
---
# Review de devops: impl-n-ci (c1)

## Parecer
Aprovado. Esta branch entrega os itens E1 (pool de threads por subprocesso, numa fonte só) e E3 (pesos regravados em `tests/pesos-d4.json`, 79 módulos, JSON válido) do pedido. O limite de CPU do corpus fica separado do pool (`trabalhadores_do_limite_de_cpu`), então subir o pool não o afrouxa (C-3); o mutante M4 de `tests/mutantes/prop-tempo-cpu.json` foi atualizado para o novo nome e continua apontando para o mesmo trecho.

M14 (`agents/tech-lead.md:19`): cumpre. Linhas de código e teste contadas pela regra do Forge: 70 (`apoio_volta_unica.py` 15, `test_hooks.py` 47, `test_hooks_volta_corpus.py` 8; o mutante de `tests/mutantes/` fica fora); o teto é 400. Não toca `hooks/`, `.github/`, `.githooks/` nem `tests/catraca.py`, então não há classe de comportamento em `hooks/` a contar. `pesos-d4.json` e o fragmento de changelog ficam fora da conta. Um item de comportamento, um commit que se reverte sozinho (três commits: teste, código, pesos).

Pipeline: nenhum workflow mudou, nenhuma ação, permissão, cache ou gatilho. O dimensionamento do pool lê a afinidade do processo e ignora `FORGE_NPROC`, e o piso de 2 e o teto de 4 limitam as threads (que esperam subprocesso e não usam CPU). Ferramentas: `actionlint` e `shellcheck` não estão no PATH e não se aplicam (sem workflow nem script de shell no diff); lacuna registrada. Li o diff inteiro de `234dbe0` a `655ae8c`.

## Achados
- A1 (recomendado) tests/test_hooks.py:521 · `def nucleos_do_processo` fica colada ao bloco de constantes, sem as duas linhas em branco entre definições; só estilo, não devolve.

## Custo e rollback
Sem minuto novo de CI nem recurso pago (`R-CUSTO`); o pool passa a ter até 4 threads em máquina de 4 núcleos ou mais, mas cada thread só espera um subprocesso e o limite de CPU não muda. Volta: reverter os três commits (cada um se reverte sozinho); os pesos antigos voltam com o revert do commit de pesos.
