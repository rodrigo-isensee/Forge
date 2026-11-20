---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae8-ruleset
commit: c2f75cacdf29be4eea6ffb8bd96a263f89399021
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E58.10, AE8.1 no head c2f75cac, revalidação)

## Escopo lido
Revalidação (H3, `R-REVIEW`): só o delta de `forge-check parecer delta docs/reviews/v0479-ae8-ruleset.md`, intervalo `a298cdbc..c2f75cac`, domínio código e testes: `docs/protecao-de-branch.md`, `templates/projeto/docs/engineering/protecao-de-branch.md` e `changelog.d/v0479-ae8-ruleset.md` (+22 −9, só texto, 0 linha de código; sem guarda nova nem mutante a declarar). Suíte não rodada (brief: sem suíte local); `docs/engineering/praticas.md` sem regra "decidida por" que alcance o diff.

## Delta lido
- A1 anterior (datas): resolvido em `docs/protecao-de-branch.md:44`; o quadro de 15/11 fica separado dos sete merges (#680 a #715), posteriores.
- A2 anterior (nome do ruleset): resolvido; `checks-obrigatorios-develop-main` citado no passo 1, no passo 4 e na conferência; só o `main-do-dono` pode ter bypass, e só na `main` (D10).
- A3 anterior (alvo por curinga): resolvido nos dois arquivos; `~ALL`, `~DEFAULT_BRANCH` e curinga citados, e o `exclude` passa a ser conferido.
- Novo: a lista de rulesets vem de `rules/branches/<branch>` (GET, só leitura, `R-CONFORMIDADE`), que já aplica include e exclude; cada regra traz `ruleset_id`. Neutralidade (`R-NEUTRO`) mantida no modelo de projeto ("branch de integração"). Changelog só em fragmento.

## Achados
- A1 (recomendado) docs/protecao-de-branch.md:56 · `rules/branches/<b>` devolve só regras ativas: ruleset em Evaluate ou Disabled some da lista, e o "enforcement active" do passo 2 fica vazio de sentido. Dizer que o `portoes` e o `checks-obrigatorios-develop-main` têm de aparecer na lista; ausência é achado. Mesmo no modelo, linha 59.

## Parecer
Aprovado. Os três achados anteriores foram resolvidos no texto, sem afrouxar portão nem dar escrita a agente (`R-CONFORMIDADE`, `R-FLUXO`). O achado novo é de precisão, sem defeito provado: vira cartão depois do merge (`R-REVIEW`).
