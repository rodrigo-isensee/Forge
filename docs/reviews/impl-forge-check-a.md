---
tipo: review
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 0ba0a57a138dab4390afb9362047ee69da4f4506
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-forge-check-a (branch a1)

Diff lido: `234dbe0..0ba0a57` (3 commits: 1844275 C1, d4eea24 C2, 0ba0a57 fragmento).

## Item entregue
E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO e FC-PEDIDO-CAMINHO-DUPLO): o Pedido do brief vale pelo realpath do arquivo do pedido, só absoluto ou com `~/`, e `caminho_do_pedido` expande `~/` sem montar caminho duplo.

## M14 (agents/tech-lead.md:19)
- Teto: `bin/forge-check` +37 -7 e `tests/test_forge.py` +86 -2, 132 linhas, abaixo de 150; o fragmento em `changelog.d/` fica fora. Sem exceção a pedir (o `bin/forge-check` é PROTEGIDO e a exceção nem valeria).
- Um comportamento: aceito. C1 e C2 são a mesma leitura do caminho do Pedido (`~/` só no começo, absoluto, realpath), e o C1 compara com o arquivo que o C2 resolve.

## Verificação
- Testes do item rodados na worktree: `EntregasParalelas` e `CaminhoDoPedido`, 15 testes, OK.
- Shell: nenhum arquivo de shell no diff. Mutação: não há spec em `tests/mutantes/` para o pedido; fica como pendência do autor (V2), não como achado.

## Achados
- A1 (bloqueante) bin/forge-check:983 · mesmo_pedido chama valor.removeprefix sem guarda: brief em docs/briefs/ sem a linha Pedido: dá AttributeError com Traceback e saída vazia; na base saía a reprova da união (o if achados["Pedido"] saiu). Reproduzido com --brief. Guarde None e teste o caso.

## Parecer
Reprovado por A1. Regressão provada: na 234dbe0 o `if achados["Pedido"]:` deixava o `None` seguir e a união reprovava com a linha `escopo: união de briefs de entregas diferentes`; agora `mesmo_pedido(None, ...)` levanta `AttributeError` em `uniao_de_briefs` (bin/forge-check:1009) e a conferência sai sem nenhuma linha de veredito, só com o Traceback no stderr (o rc é 1, falha fechada, mas o contrato de saída do forge-check se quebra). Reprodução: o brief `p1-z-1.md` com o cabeçalho de `EntregasParalelas.cabecalho()` sem a linha `Pedido:`, conferido com `entrega ... --brief <ok> --brief docs/briefs/p1-z-1.md`. Sugestão: `if not valor: return False` no começo de `mesmo_pedido` e um caso "sem Pedido" no `test_pedido_do_brief_por_caminho_vale_so_pelo_realpath_do_pedido_conferido`, com `assertNotIn("Traceback", erro)`. O resto do desenho (C-1 a C-6, C-8, C-10, C-11) está no código e nos testes.
