---
tipo: review
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 48e2c5d331914a7c15da31d942da85951e2b6e80
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-forge-check-a (branch a1)

Diff lido na rodada 1: `234dbe0..0ba0a57` (1844275 C1, d4eea24 C2, 0ba0a57 fragmento). Revalidação (rodada 2): `forge-check delta --parecer` sobre o parecer anterior, intervalo `0ba0a57..48e2c5d`; li só o que ele listou: `bin/forge-check:983-984` (+2) e `tests/test_forge.py:4846-4853` (+8). Já lido na rodada 1 e não relido: C1, C2, o fragmento e o resto de `mesmo_pedido`.

## Item entregue
E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO e FC-PEDIDO-CAMINHO-DUPLO): o Pedido do brief vale pelo realpath do arquivo do pedido, só absoluto ou com `~/`, e `caminho_do_pedido` expande `~/` sem montar caminho duplo. A volta (615544b teste, 48e2c5d correção) fecha o A1.

## M14 (agents/tech-lead.md:19)
Cumpre. `git diff --numstat --no-renames origin/develop...HEAD`: `bin/forge-check` 39+7 e `tests/test_forge.py` 94+2, 142 linhas de código e teste, abaixo de 150; pareceres e fragmento ficam fora. Um comportamento só (a leitura do caminho do Pedido). Sem exceção a pedir.

## Verificação
- A correção é `if not valor: return False` no começo de `mesmo_pedido`, como sugerido: brief sem `Pedido:` deixa de levantar e volta a reprovar a união com a linha de escopo. O teste novo `test_brief_sem_a_linha_pedido_reprova_com_linha_limpa` cobre rc 1, sem `Traceback` e com a linha `escopo: união de briefs de entregas diferentes`; o commit do teste precede o da correção, a ordem esperada.
- `EntregasParalelas` e `CaminhoDoPedido` rodados na worktree no head: 16 testes, OK.
- Shell: nenhum no diff. Mutação: sem spec em `tests/mutantes/` para o pedido; pendência do autor (V2), não achado.
- Segurança: parecer próprio em `docs/security/impl-forge-check-a.md` (do security-engineer); não refeito aqui.

## Achados
- A1 (recomendado) bin/forge-check:983 · resolvido em 48e2c5d (guarda de valor vazio) com o teste em tests/test_forge.py:4846; nenhum bloqueante aberto.

## Parecer
Aprovado no head 48e2c5d. A regressão do A1 está corrigida e travada por teste; nada mais a devolver.
