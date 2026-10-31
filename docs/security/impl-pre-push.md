---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c1
commit: eef8cd0a5db09b1d26115102f3d5bd9de03d054b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push (branch c1)

Diff revisado: `234dbe0..eef8cd0` (código em `a7968c1`, fragmento em `6eae448`, parecer do code review em `eef8cd0`). Análise estática contra o modelo de ameaças `docs/security/ameacas/pre-push.md` (controles C-1 a C-3, casos de abuso 1 e 3).

## Gatilhos
`R-SEGURANCA`: controle do Forge (`.githooks/pre-push`) e permissões da pasta da trava.

## Item entregue e M14
- Entrega o E1 do pedido (TRAVA-MODO-SUBPASTA, C1 do desenho, C-1 e C-2 do modelo), e só ele.
- M14: 56 linhas de código e teste (`.githooks/pre-push` 11, `tests/test_pre_push_trava.py` 45), abaixo do teto; um comportamento só (recusa da subpasta com escrita alheia). Cumpre.

## Conferência dos controles
- C-1: `.githooks/pre-push:39` aplica a conferência a todo candidato que passa pela subpasta, depois das conferências de dono e de link, antes de devolver o caminho; o push, o `--suite` e o `--status` passam todos por `trava_arquivo`. A máscara `/022` cobre escrita de grupo e de outros com ou sem sticky bit.
- C-2: `.githooks/pre-push:13-14` só aceita quando o `find` imprime exatamente o caminho; erro, ferramenta ausente ou máscara não entendida dão saída vazia e recusa. A forma proibida pelo modelo não aparece.
- C-3: a recusa sai com `return 1` sem tentar outro candidato; a mensagem aponta `chmod 700` ou apagar, sem sugerir outra pasta.
- Testes T-C1a (0o777, 0o770, 0o702, 0o1777; nada escrito na subpasta; `--status` também recusa), T-C1b (0o700, 0o750, 0o755 aceitas) e T-C1c (`find` falso primeiro no `PATH`, push rc 1, suíte não roda) presentes em `tests/test_pre_push_trava.py:298-341`.
- Sem janela útil entre a conferência e o uso: só o dono da subpasta pode mudar o modo dela, e o descritor aberto segue conferido por `trava_confere`.

## Achados
- A1 (recomendado) tests/test_pre_push_trava.py:316 · O --status da subpasta frouxa não confere o rc. Quando c1 e c2 estiverem juntas na develop, fixar assertEqual(codigo, 2) nesse ponto (caso de abuso 2, C-6). Dono: tech-lead.

## Detalhe dos achados
A1: evidência `tests/test_pre_push_trava.py:316-318`; sem caminho de ataque (lacuna de cobertura, não defeito: o rc 2 é do item da c2, outra branch); severidade informativa; correção mínima: uma asserção no PR que juntar os dois itens ou num cartão logo depois; esforço P; dono `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura do diff e do hook no commit revisado. `shellcheck` e `gitleaks` ausentes do PATH nesta máquina (lacuna; o CI roda o `shellcheck` no hook). Nenhuma ferramenta instalada.
