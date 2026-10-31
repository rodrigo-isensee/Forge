---
tipo: revisao-devops
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c2
commit: 60986081fb7ac6e64b18c66d5e6f6d569814bd5b
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-31
---
# Review de devops: impl-n-ci (c2)

## Parecer
Aprovado. Esta branch entrega a parte "medida no resumo" do E2 (item 55 d): duração por unidade (dez mais lentas), soma, maior unidade, desequilíbrio, módulos sem peso (lista limitada a 20) e os módulos no título de cada `::group::` do CI, em `scripts/suite-paralela.py`. O resumo só leva nomes de módulo (filtrados pelo conjunto de `partes`) e números; o teste `test_resumo_so_leva_nomes_e_numeros` prova que `::`, caminho e padrão de segredo da saída dos testes não chegam ao arquivo. Sem `GITHUB_STEP_SUMMARY` nada é escrito. A medida só informa: não muda divisão, veredito nem carimbo (a divisão é testada independente da execução anterior).

M14 (`agents/tech-lead.md:19`): cumpre. 117 linhas de código e teste (`suite-paralela.py` 44, `test_suite_paralela.py` 73; teto 400, e dentro do teto de 150 do plano do pedido); sem `hooks/`, sem `.github/`, sem arquivo de `PROTEGIDOS`. Uma classe de comportamento (a medida), commits separados de teste, código e teste de ausência.

Pipeline: nenhum workflow mudou; o script já roda no CI e o passo lê a variável `GITHUB_STEP_SUMMARY` que o runner já fornece. Sem minuto novo nem recurso pago. Ferramentas: `actionlint` e `shellcheck` fora do PATH, sem workflow nem shell no diff; lacuna registrada. Li o diff inteiro de `234dbe0` a `6098608`.

Ressalva de ordem: aqui `publicar_no_ci` ainda roda antes do veredito (`scripts/suite-paralela.py:515`) e só captura `OSError`; um erro de outro tipo ao montar o resumo derrubaria a execução. Isso é o que a branch c3 corrige (C-6). Por isso c2 não deve chegar à `develop` sem c3.

## Achados
- A1 (recomendado) scripts/suite-paralela.py:515 · o resumo é publicado antes do veredito e só trata OSError; sozinha, c2 deixa um erro do resumo mudar o resultado da suíte. Mesclar c3 junto ou logo depois (o `tech-lead` ordena); não devolve c2.
- A2 (recomendado) scripts/suite-paralela.py:445 · c2 e c3 saem da mesma base `234dbe0` e editam as mesmas funções; `git merge-tree` dá conflito em `scripts/suite-paralela.py` e `tests/test_suite_paralela.py`. A segunda a entrar precisa de rebase sobre a primeira.

## Custo e rollback
Sem minuto novo de CI nem recurso pago (`R-CUSTO`). Volta: reverter os commits da branch; o resumo antigo (total e linhas por processo) volta.
