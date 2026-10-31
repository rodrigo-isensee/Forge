---
tipo: review
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c2
commit: 60986081fb7ac6e64b18c66d5e6f6d569814bd5b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-n-ci (c2)

## Achados
- A1 (recomendado) scripts/suite-paralela.py:445 · c2 e c3 reescrevem `montar_resumo` e `publicar_no_ci` a partir da mesma base: `git merge-tree 6098608 4c978e7` conflita nos 2 arquivos. Mesclar a c2 primeiro; a c3 volta reconstruída sobre ela (achado bloqueante da c3).
- A2 (recomendado) tests/test_suite_paralela.py:383 · `assertNotIn("resumo indisponível", erro)` não prova nada nesta branch: a mensagem só nasce na c3. Ganha sentido depois da c3; sem mudança aqui.

## Parecer
Aprovado. Li o diff inteiro de `234dbe0` a `6098608` (4 commits).

O que entrega: a primeira metade do E2 do pedido (item 55 d), a medida no resumo do CI, pela divisão da DECISÃO TÉCNICA do Jarvis de 2026-10-30 15:39: as 10 unidades mais lentas, a soma, a soma por processo, a maior unidade, o desequilíbrio, os módulos sem peso (até 20, com "e mais N") e os módulos no título de cada `::group::` (desenho §3.2; C-9, C-11, C-12). O resumo leva só nomes de módulo de `partes` e números (durações filtradas por nome conhecido e por número não negativo), nada da saída dos testes. A divisão continua decidida pelos pesos, não pela execução anterior (`test_divisao_nao_depende_da_execucao_anterior`). Sem `GITHUB_STEP_SUMMARY`, nada é escrito.

Testes: os do desenho §3.2, mais o limite das listas (AB-6), o resumo sem saída dos testes (AB-4) e a divisão estável (AB-7). Rodei `python3 -m unittest tests.test_suite_paralela` na worktree: `Ran 31 tests`, `OK`.

A proteção do veredito (C-6 a C-8: resumo depois do veredito, erro no resumo sem mudar o código de saída, execução reprovada fora do orçamento) é da c3. Nesta branch o resumo ainda sai antes do veredito e só `OSError` é capturado; não achei entrada que faça `montar_resumo` levantar outra exceção (há ao menos um processo, `duracoes` tem um valor por processo, relatório ausente é pulado), então não é defeito provado. Mas a c2 sozinha não fecha o E2: ele só fica inteiro com a c3 reconstruída sobre esta (A1).

M14 (agents/tech-lead.md, Teto por PR): cumpre. Contam 117 linhas (`scripts/suite-paralela.py` 44, `tests/test_suite_paralela.py` 73); o fragmento de `changelog.d/` fica fora. Sem `hooks/` nem `PROTEGIDOS`; um comportamento (a medida no resumo).

Ferramentas: sem `docs/engineering/praticas.md` com regras por ferramenta no Forge; a suíte roda no pre-push e no CI do PR. Pipeline: parecer de devops aprovado em `docs/devops/impl-n-ci.md`. Segurança (E1.3) é parecer à parte. `R-CUSTO`: sem minuto novo de CI.
