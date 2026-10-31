---
tipo: revisao-seguranca
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 2aac6769fc3d502e6cee0aceb0a7b6ee464a8303
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: impl-forge-check-a (branch a1)

Diff lido: `234dbe0..0ba0a57` (1844275 C1, d4eea24 C2, 0ba0a57 fragmento), contra o modelo de ameaças `docs/security/ameacas/forge-check-a.md` (controles C-1 a C-11, casos A1 a A9 e B1 a B6).

## Item entregue e M14
- Item: E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO-DUPLO), o caminho do Pedido pelo realpath do arquivo do pedido e o `caminho_do_pedido` sem caminho duplo.
- M14 (agents/tech-lead.md:19): `git diff --numstat --no-renames` dá `bin/forge-check` 37+7 e `tests/test_forge.py` 86+2, 132 linhas, abaixo de 150; o fragmento fica fora. Um comportamento (a leitura do caminho do Pedido, que o C1 compara com o arquivo que o C2 resolve). Cumpre.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-check` é o portão de escopo do conferente, e a união de briefs decide o que entra no escopo conferido.

## Revalidação (head 2aac676)
Parecer anterior sobre 0ba0a57 (reprovado, A1). `forge-check delta --parecer` listou `bin/forge-check:983-984` (+2) e `tests/test_forge.py:4846-4853` (+8); li só isso. O resto do código ficou como já lido; o 2aac676 em si só acrescenta o review do tech-lead (docs).
- A1 resolvido: `bin/forge-check:983-984` devolve falso para `Pedido:` ausente ou vazio antes do `removeprefix`, cumprindo o C-4; `uniao_de_briefs` segue com a reprovação de escopo e a linha de veredito (rc 1, sem pilha de erro). Teste novo `tests/test_forge.py:4846-4853` confere rc 1, sem `Traceback` e a linha `escopo:`. `EntregasParalelas` e `CaminhoDoPedido`: 16 testes, OK, na worktree.
- Nenhum achado novo no delta (2 linhas de guarda, sem shell, caminho nem entrada nova).
- M14 (agents/tech-lead.md:19): `bin/forge-check` 39+7 e `tests/test_forge.py` 94+2 desde a base, 142 linhas, abaixo de 150; um comportamento. Cumpre.
- A recomendação do laço do id puro em `caminho_do_pedido` (`is_file` direto) segue como recomendação, não devolve.

## Achados
- Nenhum achado bloqueante. A1 do parecer anterior (bin/forge-check:983) está resolvido no head 2aac676.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática por leitura do diff e reprodução em processo. Ferramentas ausentes no PATH (lacuna, nada instalado): gitleaks, semgrep, osv-scanner, zizmor, actionlint, shellcheck. O diff não tem shell, workflow, dependência nem segredo.
