---
tipo: revisao-devops
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 4c978e7460e4cff62a1ab6d320d52bc3f4aae6c1
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-31
---
# Review de devops: impl-n-ci (c3)

## Parecer
Aprovado. Esta branch entrega a parte "veredito protegido" do E2 (item 55 d, C-6 a C-8): o veredito (`OK` ou `FAILED`) é impresso antes do resumo (`scripts/suite-paralela.py:516`), o código de saída é decidido antes e não muda; qualquer exceção ao montar ou gravar o resumo vira a linha `resumo indisponível` no stderr (captura ampla, comentada, justificada: o resumo é informativo). O que só vale depois do verde (pesos regravados, carimbo) foi extraído para `fechar_verde`, sem mudar a ordem: pesos e carimbo continuam só com execução verde, e a execução reprovada leva a linha "não vale para o orçamento". Módulo sem duração é listado (limite de 20). Verifiquei no diff que `FAILED` continua devolvendo 1 e `OK` devolvendo 0.

M14 (`agents/tech-lead.md:19`): cumpre. 149 linhas de código e teste (`suite-paralela.py` 48, `test_suite_paralela.py` 101; teto 400 e o limite de 150 do plano); sem `hooks/`, `.github/` nem `PROTEGIDOS`; uma classe de comportamento, teste antes do código nos commits.

Pipeline: nenhum workflow mudou; sem minuto novo nem recurso pago (`R-CUSTO`). A captura ampla de exceção não é `continue-on-error` nem check desligado: o veredito já saiu e o resumo nunca o esconde (`R-VERIFY`). Ferramentas: `actionlint` e `shellcheck` fora do PATH, sem workflow nem shell no diff; lacuna registrada. Li o diff inteiro de `234dbe0` a `4c978e7`.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:433 · c3 reescreve `montar_resumo` e `publicar_no_ci` de forma diferente da c2 (mesma base `234dbe0`); o merge das duas conflita em `scripts/suite-paralela.py` e `tests/test_suite_paralela.py`. Resolver no rebase da segunda a entrar, mantendo a ordem veredito e depois resumo.

## Custo e rollback
Sem minuto novo de CI nem recurso pago. Volta: reverter os commits da branch; o resumo volta a ser publicado antes do veredito.
