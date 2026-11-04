---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/pr-parecer-por-branch
commit: 72be218e2198631c3716a68225b078a90020e0e3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: PARECER-POR-BRANCH (E11, forma mínima)

Diff `f54d9b7...72be218`: `bin/forge-check` (+14/-1), `tests/test_forge.py` (+27), fragmento de changelog. Total de código e teste: 42 linhas, abaixo do teto da M14; um comportamento só; sem `hooks/` nem `tests/catraca.py`.

## Contra o Entregar do brief 52
- Branch pela `--ref` (`origin/<b>`, `<b>`, `HEAD` em branch) ou, sem `--ref`, pela do HEAD: `branch_da_ref` cobre os quatro casos; só devolve nome que existe como branch local ou remota. Sha, tag e HEAD solto dão None. Atende.
- Vale o mais recente do tipo e pedido com `branch:` igual; sem nenhum, `da_branch or achados` mantém o comportamento antigo. Atende, e a reserva para o comportamento antigo está preservada.
- Reprovado da própria branch continua reprovando: a escolha só filtra, a leitura de `parecer:` segue igual. Atende (teste próprio).
- Testes: parecer de outra branch com caminho posterior na ordem (caso do #437), sha sem branch cai no mais recente, reprovado da branch, sem parecer da branch cai no de hoje. Rodei os 6 testes `pr_parecer`/`pr_sem_parecer_da_branch`, OK. Os falsos de `git` usam repositório real, sem imitação frouxa.
- Fragmento do changelog presente; `tests/catraca.py` e `hooks/` intactos.

## Parecer
Aprovado. Ver a recomendação em `## Achados`; não devolve.

## Achados
- A1 (recomendado) bin/forge-check:754 · `branch_da_ref` roda duas vezes por parecer e cada chamada abre subprocessos git; calcular uma vez antes do laço de tipos (fora do bloco de filtro) deixa a linha mais legível e mais barata.
