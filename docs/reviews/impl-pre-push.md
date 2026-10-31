---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c2
commit: f4fadff46d8859d27b7010c00bdca643aef41cc9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c2 (PRE-PUSH-STATUS-RC)

Diff lido: `234dbe0..f4fadff` (2 commits: `0a21a1a` hook e teste, `f4fadff` fragmento).

## O que entrega
Item E2 do pedido, o C2 do desenho (`docs/propostas/lotes-1030/pre-push.md`) com os controles C-4 a C-7 do modelo (`docs/security/ameacas/pre-push.md`): no bloco `--status`, todo erro de conferência (subpasta recusada, trava link, trava ilegível, `trava_confere`) sai por `status_erro`, com rc 2 e a mensagem que manda não rodar a suíte à mão e aponta `.githooks/pre-push --suite` (C-7). 0 = rodando e 1 = nenhuma ficam iguais (C-5); a falha do `flock` segue lida como rodando. O caminho do push não muda e segue com rc 1 (C-4). A dica do `--status` com suíte rodando (C3) está na c3, não aqui.

## M14 (decisão M14, agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 f4fadff`): `.githooks/pre-push` 15, `tests/test_pre_push_trava.py` 40; total 55, abaixo de 150. O fragmento `changelog.d/` fica fora.
- Um comportamento só (o rc 2 do erro do `--status`, com a mensagem dele). Toca `.githooks/` (PROTEGIDOS) sem precisar de exceção de teto. Cumpre.

## Regras de ferramenta
- Suíte: a branch está no `origin` com o head revisado, logo o pre-push passou no envio do autor; rodei ainda `python3 -m unittest tests.test_pre_push_trava` na worktree: `Ran 30 tests ... OK`.
- shellcheck: não instalado nesta máquina (`shellcheck: command not found`); fica para o passo do CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json` na branch. Pendência do autor (V2).

## Leitura
- A troca de `tests/test_pre_push_trava.py:276` é exatamente a que o C-6 pede: `assertEqual(codigo, 2)`, a asserção da mensagem de `:277` mantida e a negativa `assertNotIn("nenhuma suíte", saida)` acrescentada; a do push (`:271`) segue 1. Distingue mais e não aceita mais.
- O teste novo cobre os casos de abuso 4 e 5 do modelo: subpasta link, trava link e trava sem leitura dão rc 2 no `--status`, sem "nenhuma suíte", com a dica do `--suite`, e rc 1 no push, sem suíte.
- Escopo do C2 só (bloco `--status`, comentário da linha 7, teste); revertido sozinho, volta o rc 1 no erro. R-NEUTRO e R-CUSTO preservados; nenhum invariante tocado.

## Achados

## Parecer
Aprovado. Entrega o C2 do E2 como desenhado e como o modelo de ameaças pede, dentro da M14. Sem achados.
