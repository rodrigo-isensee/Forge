---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a1-adr
commit: 2675e3ca9b12b61edd58b96251e23c05390185bc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.17, PR-VERDE A1, revalidação depois da volta única)

Revalidação (H3, `R-REVIEW`): li só `forge-check parecer delta docs/reviews/v0479-pv-a1-adr.md`, intervalo `ac1069d3..2675e3ca`, 3 arquivos no domínio (`changelog.d/v0479-pv-a1-adr.md`, ADR 0008 seção 3 linha 56, ADR 0018 linhas 93, 106, 114, 116, 117 e modelo de ameaças). 0 linha de código (H1 dentro do teto). Sem suíte local (brief); sem PR nesta etapa, logo sem CI a citar.

Delta lido contra os achados anteriores (deste parecer no ac1069d3 e da segurança, E57.11):
- A1 anterior (como o arquivo entra no índice) e A1 da segurança (bloqueante, `git` que escreve o índice): resolvidos em E3 (`:114`): o `declarar`/`retirar` põem o arquivo no índice com `-c core.attributesFile=/dev/null`, modo 100644, e conferem `git ls-files -s` contra o blob do `D-<Id>`; o hook barra todo `git` que escreve índice ou árvore com o caminho, listado na classe `escrita-por-agente` (`:93`) e na linha "Escrita por Write, Edit ou Bash" do modelo de ameaças. A confirmação é da segurança.
- A2 anterior (data do fim da transição): resolvido em E6 (`:117`), constante vazia no PV-A4 e data gravada pelo `tech-lead` em item seguinte, lida do `git log`.
- A3 anterior (retirada sem envio) e A2 da segurança (conferência só no `forge-fechar`): resolvidos em E5 (`:116`), conferência do blob e do `R-<Id>` também no pre-push e no `gh pr create` do hook.
- A4 anterior (desenho ausente na `develop`): resolvido como ordem de merge declarada (`:106`, E54.10): o desenho entra antes desta emenda.
- A3 da segurança (cabeçalho fora do `Sha256`): escrito na linha "Origem no CI" do modelo de ameaças.

ADR 0008 (`:56`) e o fragmento de changelog acompanham E3, E5 e E6 sem contradição.

## Achados
- A1 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:117 · E6: com a constante vazia a catraca aceita rótulo ou arquivo sem prazo, e o item que grava a data não tem prazo. Dar prazo ao item (ex.: aberto no dia do merge do PV-A4) ou checagem que acuse a constante vazia após 14 dias do merge.

## Parecer
Aprovado no head 2675e3ca. A volta única trata os quatro achados recomendados do review e os três da segurança no texto da emenda, sem afrouxar o que já estava (E4, `R-CUSTO` e N-CAT1 intactos; "Afrouxa?" inalterado e ainda correto). O achado novo é recomendado e vira cartão depois do merge.
