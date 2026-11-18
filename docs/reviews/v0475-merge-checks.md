---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: d8f33e1b54ef2c19e51a43bd3140c813211819e0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.218, branch melhoria/v0475-merge-checks)

## Revalidação
Li o delta com `forge-check parecer delta docs/reviews/v0475-merge-checks.md`, no intervalo cc4934de..d8f33e1b, só no domínio de código e testes. Ele tocou `bin/forge-check`, `bin/forge-testes`, `tests/test_forge_tamanho.py` e `tests/test_testes_tocados.py`.

O delta é só o merge d8f33e1b da develop (791d94e8). Os trechos de `bin/forge-check`, `bin/forge-testes` e `tests/test_forge_tamanho.py` vêm do E3.48 (#647), que já está na develop. Nada do autor mudou fora do merge.

Fiz o `git merge-tree --write-tree` de cc4934de com 791d94e8. Ele mostra um único conflito, em `tests/test_testes_tocados.py`. Também comparei a árvore dele com d8f33e1b: fora dos pareceres, a única diferença é a linha da contagem.

A resolução soma os dois lados e chega a 97: são os 96 da develop (com `test_brief_tamanho`) mais o `test_forge_check_pr`, que esta branch põe em `FORGE_CHECK`. O comentário da linha registra a junção.

O A3 do parecer anterior está resolvido: o corpo do PR #653 agora diz `teto: excedido, 492 linhas`, que bate com o `git diff --numstat` medido sobre origin/develop (492).

## Verificação
- **`tests.test_testes_tocados`:** 162 testes OK (1 pulado).
- **`tests.test_forge_tamanho`:** 24 testes OK.
- **`tests.test_ambiente_git`:** OK.
- **Catraca** (`--base origin/develop`): nenhuma linha R-QA. O rc=1 vem só do aviso R-CONFORMIDADE de `bin/forge-check`, porque o rótulo `afrouxa-regra` tem de ser aplicado depois do último push.
- **CI do PR #653 no head d8f33e1b:** a suíte ainda está rodando. A `bateria (pareceres)` falha porque os pareceres ainda estão no head anterior. A suíte fica com o CI.

## Parecer
Aprovado no head d8f33e1b. Ficam pendentes o CI verde e o rótulo do dono aplicado depois do último push (R-CONFORMIDADE).
