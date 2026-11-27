---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: 1567d509452159c268e52384f694a7bf3881bdda
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.28, F6 corte do envio, PR #932, 1.ª rodada)

## Achados
- A1 (bloqueante) scripts/arvore-testada.py:186 · liga run e PR por `pull_requests`, que a API só preenche com PR aberto; no push da develop o PR já foi mesclado e a lista vem vazia: `prova_do_pr` nunca prova (S1, S2) e a suíte roda sempre. Ligue sem esse campo (head_sha e head_branch do PR), mantendo o A1 do #929.
- A2 (bloqueante) tests/test_arvore_testada.py:230 · o falso da API põe `pull_requests` preenchido no run de um PR já mesclado, mais frouxo que a API real (item 12 do checklist): a suíte fica verde com o A1 presente. O caso positivo precisa do formato real (lista vazia após o merge) e provar mesmo assim.
- A3 (recomendado) docs/protecao-de-branch.md:31 · "erro ou falha do job, a suíte roda inteira": com o job `arvore-envio` em falha (checkout, setup), as partes ficam puladas pelo `needs` e o agregador sai vermelho; a suíte não roda. Corrija o texto (vermelho, não suíte inteira) ou o `if` das partes.

## Sondas
- S1 · prova_do_pr na API real, SHA=11fc1867 (merge do #931, árvore 13aadd8 igual à do head d2c4831, bateria success no run 45959949382) · espera: (True, ...) · obtido: (False, 'nenhum PR mesclado em 11fc186 tem head de mesma árvore, ...'); mesmo resultado em 2bdf1a2 (#929)
- S2 · gh api repos/<repo>/actions/runs/45959949382 --jq '.pull_requests|length' e os ci.yml dos 12 últimos PRs mesclados na develop (#917 a #931) · espera: PR ligado ao run · obtido: 0 em todos; o run aberto do #932 traz 932:develop:11fc186

## Parecer
Reprovado. A estrutura está certa: job `arvore-envio` só com leitura, token só no passo da prova, falha fechada no script (exceção vira rc 1 sem detalhe), agregador que exige `arvore-envio` em success e as pernas puladas só com `provada=true`, e a cadeia do A1 do #929 (mesmo repositório, base develop, árvore do head igual à do commit, develop anterior e base do run ancestrais do head, job `bateria` único na tentativa mais recente). Tamanho pela ferramenta: 144 linhas de código, dentro do H1.

O defeito (A1) é de requisito: o objetivo do item é o envio pular a suíte com a árvore provada no PR, e a prova depende de um campo que a API do GitHub esvazia quando o PR fecha. Provado na API real (S1, S2): no merge do #931, cada passo passa (PR #931 mesclado em 11fc186, árvore igual, bateria success na tentativa 1) e só a ligação run→PR falha. É falha fechada, sem risco de segurança, mas o mecanismo nunca dispara. O falso dos testes (A2) é o que deixou isso verde. Sugestão: ligar pelo `head_branch` do run igual a `head.ref` do PR e `head_sha` igual ao head, e tirar a base do PR (`base.sha` da API do PR ou o compare com a develop anterior já feito), com caso de teste no formato real e mutante da guarda nova.

Suíte: testes afetados rodados à mão no head (`tests.test_arvore_testada`, `test_suite_partes`, `test_catraca`, `test_ci_local`): 583 testes, OK. CI do head 1567d509: partes, passos, instalação e árvore verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres e do rótulo. Mutantes declarados (14 em três specs) não rodados nesta rodada: a correção do A1 muda as guardas que eles cobrem.
