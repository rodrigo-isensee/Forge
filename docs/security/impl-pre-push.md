---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c2
commit: 587cc2b6bc4cf69284d645c376a19e5b07e395df
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push (branch c2)

Diff revisado: `234dbe0..587cc2b` (código em `0a21a1a`, fragmento em `f4fadff`, parecer do code review em `587cc2b`). Análise estática contra o modelo de ameaças `docs/security/ameacas/pre-push.md` (controles C-4 a C-7, casos de abuso 4, 5 e 6).

## Gatilhos
`R-SEGURANCA`: controle do Forge (`.githooks/pre-push`, modo `--status`).

## Item entregue e M14
- Entrega a parte do E2 do pedido que cabe ao C2 do desenho (PRE-PUSH-STATUS-RC: erro do `--status` com rc 2, troca exata da asserção de `tests/test_pre_push_trava.py:276`, mensagem que aponta o `--suite`, C-7). A dica do `--suite` com suíte rodando (C3) fica na c3.
- M14: 55 linhas de código e teste (`.githooks/pre-push` 15, `tests/test_pre_push_trava.py` 40), abaixo do teto; um comportamento só (rc do erro do `--status`). Cumpre.

## Conferência dos controles
- C-4: `status_erro` (`.githooks/pre-push:89-92`) só existe e só é chamada dentro do bloco `--status` (`:93`, `:94`, `:97`, `:98`); o caminho do push segue com rc 1, e o teste confere isso para as três causas.
- C-5: 0 = rodando e 1 = nenhuma ficam iguais; a falha do `flock -n` continua lida como "rodando".
- C-6: a asserção vira exatamente `assertEqual(codigo, 2)` (`tests/test_pre_push_trava.py:276`), a do motivo no stderr fica e entra a negativa de "nenhuma suíte" na saída. Não alarga.
- C-7: a mensagem do rc 2 diz para não rodar a suíte à mão e aponta `.githooks/pre-push --suite`; texto fixo, sem dado da trava.
- `exec 9<"$trava" || status_erro`: no bash fora do modo POSIX, a falha do redirecionamento do `exec` não encerra o shell, então o `|| status_erro` é alcançado; o subteste "trava sem leitura" prova o rc 2.
- Remoto chamado `--status` (dois argumentos) não entra no bloco: inalterado.

## Achados
- A1 (recomendado) tests/test_pre_push_trava.py:307 · Falta o subteste da subpasta com modo frouxo no rc 2 do --status (T-C2a, depende do C1, que está na c1). Acrescentar quando c1 e c2 estiverem juntas. Dono: tech-lead.

## Detalhe dos achados
A1: evidência `tests/test_pre_push_trava.py:307-308`; sem caminho de ataque (o código cobre a causa, porque toda falha de `trava_arquivo` cai em `status_erro`; falta só o teste do par); severidade informativa; correção mínima: um subteste com a subpasta 0o777; esforço P; dono `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura do diff e do hook no commit revisado. `shellcheck` e `gitleaks` ausentes do PATH nesta máquina (lacuna; o CI roda o `shellcheck` no hook). Nenhuma ferramenta instalada.
