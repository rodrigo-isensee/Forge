---
tipo: revisao-devops
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 44617ead4fee4eab8193b8e07cda121e45f5cf2b
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-31
---
# Review de devops: impl-n-ci (c3, sobre a develop com a c2)

## Parecer
Aprovado. Diff lido: `c162bcb` a `44617ea` (o que a c3 acrescenta à develop, que já tem a c2 pelo PR #408). A branch entrega a parte "veredito protegido" do item E2 (item 55 d, C-6 a C-8): o veredito (`OK` ou `FAILED`) é impresso (`scripts/suite-paralela.py:535`) antes de o resumo ser montado e gravado, e o código de saída é decidido antes (1 em `FAILED`, 0 em `OK`, sem mudança). Qualquer exceção em `montar_resumo` ou na escrita vira `resumo indisponível` no stderr (`:461`, captura ampla comentada: o resumo é informativo e o veredito já saiu). O que só vale depois do verde (pesos regravados, carimbo) foi para `fechar_verde` (`:540`), na mesma ordem; execução reprovada recebe "não vale para o orçamento" e não leva as linhas de medida da c2; módulo sem duração é listado (limite 20). O merge da c2 resolveu o conflito do A1 do parecer anterior: as linhas de medida da c2 ficaram sob a regra C-7.

M14 (`agents/tech-lead.md:19`): cumpre. Contagem sobre a develop: 41 linhas em `scripts/suite-paralela.py` (28 + 13) e 95 em `tests/test_suite_paralela.py` (80 + 15), total 136, dentro do teto de 150. Sem `hooks/`, `.github/` nem `PROTEGIDOS`; um comportamento só (veredito antes do resumo e resumo que não derruba o veredito); teste de cada comportamento no mesmo diff (veredito primeiro, processo morto, resumo que falha sem mudar o código, ambiente do teste que não escreve no resumo real do CI).

Pipeline: nenhum workflow mudou; sem minuto novo de CI nem recurso pago (`R-CUSTO`). A captura ampla não é `continue-on-error` nem check desligado: o veredito já foi impresso e o código de saída não depende do resumo (`R-VERIFY`). Nada escreve na `main` (`R-MAIN`). Ferramentas: `actionlint` e `shellcheck` fora do PATH, sem workflow nem shell no diff; lacuna registrada.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:461 · `except Exception` também engole erro de programação em `montar_resumo`; o aviso traz só o tipo. Se o resumo sumir do CI sem causa visível, incluir a mensagem curta no stderr. Não devolve.

## Custo e rollback
Sem minuto novo de CI nem recurso pago. Volta: reverter o merge da branch na develop; o resumo volta a ser publicado antes do veredito.
