---
tipo: review
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 683ddcf9db41143858ddb0b633041ff47bd3fa15
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: lote-0307-a

Pedido LOTE-0307-A-REV, etapa E1.1 (`R-REVIEW`), volta 1. Revalidei por delta sobre o meu parecer anterior (234be01, head 38f3f71). Teto M14 da branch inteira (`3b94791...05fd5c5`): 64 linhas de código e teste (`bin/forge-fechar` +14, `tests/test_fechar_base_andou.py` +50). Ficam fora `tests/mutantes/`, os pareceres, o fragmento e os `.md`. O total fica abaixo de 400, e o lote não mexe em `hooks/` nem em `PROTEGIDOS`.

## Achados
- A1 (recomendado) tests/test_fechar_base_andou.py:314 · o teste da pasta apagada só confere que as mensagens não aparecem. Ele não confere rc=0 nem o PR criado, que o A1 anterior pedia. Acrescente `assertEqual(r.returncode, 0)` e `len(self.criacoes()) == 1`, como no teste do lock ausente.
- A2 (recomendado) bin/forge-fechar:543 · continua da volta anterior: o --dry-run ainda não imprime o passo 0 da guarda do index.lock, que o docs/fechamento-integrador.md lista.

## Parecer
Aprovado. O A1 bloqueante da volta anterior foi corrigido. Os dois achados acima são recomendações e não devolvem a entrega.

**O delta lido** (`forge-check delta --parecer docs/reviews/lote-0307-a.md`, intervalo `38f3f71..05fd5c5`):
- `bin/forge-fechar:595`
- `templates/projeto/docs/security/_modelo.md:27`, com a mesma linha no `docs/security/_modelo.md:27` da raiz
- `tests/mutantes/lote-0307-a.json:11-33`
- `tests/test_fechar_base_andou.py:6` e `:295-315`

O resto do diff ficou como "já lido" no parecer 234be01, sem mudança.

**A1 anterior, corrigido.** A linha 595 agora é `[ -n "$arvore_lock" ] && [ -d "$arvore_lock" ]`, a guarda que eu tinha sugerido. O comentário aponta o prune do passo 7. O teste novo `test_worktree_da_branch_com_a_pasta_apagada_nao_para_no_lock` apaga a worktree com `rmtree` sem prune, que é o mesmo cenário da minha sonda. Numa cópia em `$TMPDIR`, acrescentei ao teste as asserções de rc=0 e de um PR criado, e ele passou. Então o comportamento está certo, e o A1 acima pede só que o teste do repositório confira isso.

**Mutantes.** Rodei os três de `tests/mutantes/lote-0307-a.json` numa cópia em `$TMPDIR`, trocando `de` por `para` e rodando os testes listados:
- L1 (`if false`): morto.
- L2 (sem completar o git-dir relativo): morto. Esse mutante fecha o A1 do QA.
- L3 (sem a guarda `[ -d ]`): morto. Ele morre porque, sem a guarda, o stderr traz "pasta git".

O teste do L2 roda o fechamento com o cwd numa outra worktree (`wt-develop`) e o lock em `.git/index.lock` da principal, então o `.git` relativo só acha o lock se for completado com `$arvore_lock`. A mudança no L1 é só de formatação.

**Modelos de segurança.** A linha 27, na raiz e no template, ficou igual nos dois e coerente com os modelos de reviews e de qa: o parecer aprovado leva as recomendações em prosa ou como linhas `(recomendado)` no bloco. O `forge-check docs` só recusa parecer `reprovado` sem `bloqueante`. O mérito é do `security-engineer` (E2.1).

**Sem regressão** do que o parecer 234be01 aprovou:
- A guarda continua sendo o passo 0, só no caminho real.
- Ela só lê e avisa, nunca apaga o lock, e usa `printf %q` no comando sugerido.
- O `awk` compara o nome exato da branch.
- O `set -euo pipefail` continua ligado. O AR-1 (`mascara-do-shell-esconde-codigo`) foi conferido e não se repete aqui.

**Testes do item.** `python3 -m unittest tests.test_fechar_base_andou` passou: 24 testes, OK.

**Ferramenta.** Não refiz o shellcheck nem a suíte completa: ficam com o pre-push e o CI do PR (decisão de 2026-10-24).

**Fora do review.** A segurança é do E2.1 e o QA é do E3.1. Não gravei linha AR: nenhuma classe se repetiu neste pedido.

## Revalidação do merge da develop (volta 2)

Head novo 683ddcf (merge da develop a55ec03, release 0.30.6, sem conflito). Delta lido: `git diff cbd4ab3..683ddcf`, que traz o que a develop andou. Em `bin/forge-fechar` só há uma linha de comentário no `limpar_entrega` (PREPUSH-DELETE); o passo 0 da guarda do index.lock (`bin/forge-fechar:592-605`) continua intacto e antes do passo 1, e `git diff 05fd5c5 683ddcf -- bin/forge-fechar` mostra só essa linha. `tests/test_fechar_base_andou.py` não mudou desde 05fd5c5 e passou de novo (24 testes, OK). O resto do delta (hooks, pre-push, forge-check, pareceres e corpus da develop) é da develop e já foi revisado lá; fica como "já lido". Teto M14 do lote segue em 64 linhas (`bin/forge-fechar` +14, `tests/test_fechar_base_andou.py` +50). Sem regressão do que o parecer anterior aprovou; A1 e A2 seguem recomendados e não devolvem. Sem linha AR.
