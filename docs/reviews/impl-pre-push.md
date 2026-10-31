---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c1
commit: 6eae448bca62cf03caaac800e3ddd10c17cf449c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c1 (TRAVA-MODO-SUBPASTA)

Diff lido: `234dbe0..6eae448` (2 commits: `a7968c1` hook e teste, `6eae448` fragmento).

## O que entrega
Item E1 do pedido, o C1 do desenho (`docs/propostas/lotes-1030/pre-push.md`) com os controles C-1 e C-2 do modelo (`docs/security/ameacas/pre-push.md`): a subpasta `forge-<uid>` do recuo é recusada se tiver qualquer bit de escrita de grupo ou de outros (`/022`, com ou sem sticky). A conferência é falha fechada: `modo_sem_escrita_alheia` só aceita quando o `find` roda e imprime a própria pasta; erro ou saída vazia é recusa, como o C-2 exige (a forma proibida pelo modelo não foi usada). Push, `--suite` e `--status` passam por `trava_arquivo`, logo valem os três.

## M14 (decisão M14, agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 6eae448`): `.githooks/pre-push` 11, `tests/test_pre_push_trava.py` 45; total 56, abaixo de 150. O fragmento `changelog.d/` fica fora.
- Um comportamento só (a recusa da subpasta frouxa). Toca `.githooks/` (PROTEGIDOS) sem precisar de exceção de teto. Cumpre.

## Regras de ferramenta
- Suíte: a branch está no `origin` com o head revisado, logo o pre-push passou no envio do autor; rodei ainda `python3 -m unittest tests.test_pre_push_trava` na worktree: `Ran 32 tests ... OK`.
- shellcheck: não instalado nesta máquina (`shellcheck: command not found`); fica para o passo do CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json` na branch. Pendência do autor (V2).

## Leitura
- Testes cobrem os casos de abuso 1, 2 e 3 do modelo: 0o777, 0o770, 0o702 e 0o1777 recusados no push (rc 1, suíte não roda, nada escrito na subpasta) e no `--status` (sem "nenhuma suíte"); contraprova com 0o700, 0o750 e 0o755 aceitos; `find` falso que falha sem saída recusa.
- O falso de `find` (checklist 12) é mais estrito que o real (sai 1 sem imprimir), exatamente o caso que o C-2 manda recusar.
- Escopo do C1 só (condição, mensagem com o `chmod 700`, comentário); revertido sozinho, volta a aceitar. R-NEUTRO e R-CUSTO preservados; nenhum invariante tocado.

## Achados
- A1 (recomendado) tests/test_pre_push_trava.py:316 · O --status com subpasta frouxa não confere o rc; o caso de abuso 2 do modelo pede rc 2, que vem com a c2. Depois do merge das duas, acrescentar assertEqual(codigo, 2) aqui.

## Parecer
Aprovado. Entrega o C1 do E1 como desenhado e como o modelo de ameaças pede, dentro da M14. A recomendação A1 não devolve.
