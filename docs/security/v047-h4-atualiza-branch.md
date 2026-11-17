---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-h4-atualiza-branch
commit: 07009e3e69f9f2276d2f6f303343f4c2ac2d6a25
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (H4, forge-fechar traz a develop por merge)

Revalidação por delta (E2.724). Rodada anterior: aprovado em ea5c12c8 (commit b0f9652d, no git). Delta lido: `forge-check parecer delta` de ea5c12c8..07009e3e; no domínio só `docs/fechamento-integrador.md` (passo 2b) e `docs/protecao-de-branch.md` (item 8); fora dele, os pareceres de review e QA. `bin/forge-fechar` e os testes não mudaram (`git diff --stat`).

## Achados
- A1 (recomendado) bin/forge-fechar:767 · aberto, sem mudança: o merge-tree que vira commit enviado lê os atributos locais (merge=union torna limpo um conflito); use a árvore vazia como fonte de atributos, como a juncao_limpa (bin/forge-check:2538)

## Sondas

## Gatilhos
Gatilhos: controle do Forge (forge-fechar: envio a branch remota, cadeia de pareceres, R-VERIFY, R-FLUXO), documentação normativa do fechamento e da proteção de branch.

## Verificado no delta (sem achado)
- Passo 2b (docs/fechamento-integrador.md:20) descreve o que o código faz e foi lido na rodada anterior: trazida só em `melhoria/*` e na primeira volta (`--trazida`), commit com a árvore do merge-tree e pais head conferido e base do servidor, branch local por compare-and-swap ou fast-forward da worktree limpa, `git push origin` sem force e sem pular o pre-push (R-VERIFY), recomeço da cadeia no head novo; falha de escrita ou envio para sem PR; fora de `melhoria/*` vale o E8. Nada no texto promete garantia que o código não dá nem afrouxa regra.
- Item 8 (docs/protecao-de-branch.md:21): mantém "Require branches to be up to date" desmarcado (decisão E8) e "Block force pushes"; só acrescenta que o fechamento traz a base em `melhoria/*`. A garantia continua nos checks exigidos `bateria` e `catraca` com a fonte fixada.
- Pareceres de review e QA: só arquivos em docs/reviews/ e docs/qa/, fora do domínio.

## Detalhe dos achados
A1. Estado: aberto, recomendado, sem mudança desde a rodada anterior (detalhe completo no commit b0f9652d). Severidade baixa; barreira: a catraca do CI refaz a junção no servidor sem os atributos locais. Correção mínima: `git --attr-source=<árvore vazia> merge-tree ...` em `conflito_com`. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta` e leitura do diff; código e testes sem mudança, então sem teste a rodar de novo; suíte inteira só no CI (sem PR nesta etapa, por pedido do brief).
