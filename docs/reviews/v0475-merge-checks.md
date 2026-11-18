---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: 27c4c5672f8dda2d9381c04179b8d028fabfaaef
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.142, branch melhoria/v0475-merge-checks)

## Achados
- A3 (recomendado) tests/test_forge_check_pr.py:1 · M14: 476 linhas de código e teste sobre origin/develop (135 em bin/); o corpo do PR deve trazer `teto: excedido, 476 linhas, <motivo>`

## Revalidação
Delta lido: `forge-check parecer delta docs/reviews/v0475-merge-checks.md`, intervalo 9f497b0f..27c4c567, só o domínio de código e testes. O delta também traz o que entrou da develop pelo merge 27c4c567 (E3.49: `ref_publicada`, `documento_sem_parecer`, a recusa do PR mesclado e o mapa do `forge-testes`). Esse trecho já foi revisado no PR #646 e não foi revisto aqui.

- **A1 corrigido.** O passo 1 do `forge-fechar` (bin/forge-fechar:1222) chama o `pr` com `FORGE_FECHAR_PASSO_1=1`.
  - A variável dispensa só o `checks_do_head` (`previo_dos_checks`, bin/forge-check:1539).
  - Com ela, o `executar` não grava o resultado para o hook (bin/forge-check:10254). Por isso a variável não forja um aprovado para o `gh pr merge`: o hook segue decidindo pela conferência de hoje ou por um resultado gravado antes.
  - Só o valor exato `1` liga a dispensa. O mutante M24 do -4.json cobre isso, e o teste passa os valores "", "0" e "sim".
- **A2 corrigido.** `FecharComChecksPendentes` usa o `forge-check` real com um `gh` falso que responde ao `pr view` e ao `pr checks`.
  - Um teste prova que, sem a variável, o `pr` reprova pelo check pendente.
  - Outro prova que o `--armar` passa do passo 1 e arma o auto-merge. O mutante M28 amarra esse teste.
- **Entrou também a correção E3.80 da segurança e do QA.** Quando o `gh pr view` falha, o `pr` avisa e grava reprovado para o hook. Sem PR, sem remoto do GitHub, sem gh ou sem login, não há o que conferir. Os dois ramos têm teste, e o `gh_json` distingue o gh ausente do teto.

**Testes**, rodados com o ambiente limpo: `test_forge_check_pr`, `test_fechar_forge_check_real` e `test_testes_tocados`, 195 OK e 1 pulado.

**Catraca** (`--base origin/develop`): nenhuma linha R-QA. O rc=1 vem só do aviso R-CONFORMIDADE: a mudança em bin/forge-check pede o rótulo `afrouxa-regra` do dono depois do último push.

Não há PR nem CI para citar; a suíte fica com o CI.

## Parecer
Aprovado no head 27c4c567. Ficam pendentes o rótulo do dono (R-CONFORMIDADE) e a linha `teto:` no corpo do PR (A3).
