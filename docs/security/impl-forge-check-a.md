---
tipo: revisao-seguranca
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a3
commit: eec3565bb0f8d3703e4018a210ba2147f40a7463
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: impl-forge-check-a (branch a3)

Diff lido: `234dbe0..eec3565` (e6d4b12 C4, eec3565 fragmento), contra o modelo de ameaças `docs/security/ameacas/forge-check-a.md` (controles C-15 e C-16, casos E1 a E3).

## Item entregue e M14
- Item: E4 do pedido (FC-VERSAO-BASE-AVISO), `--base origin/develop` deixa de virar `refs/remotes/origin/origin/develop` no aviso de versão.
- M14 (agents/tech-lead.md:19): `bin/forge-check` 1+1 e `tests/test_forge.py` 10+0, 12 linhas, abaixo de 150; o fragmento fica fora. Um comportamento. Cumpre.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o aviso de versão da cópia vigente no `bin/forge-check`.

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferido:
- C-15: `removeprefix("origin/")` só no começo e uma vez (`bin/forge-check:5283`); a função continua lendo só a ref remota, sem cair na base local.
- A ref segue por `sha_do_commit`, com verificação e fim de opções: valor como `-c` ou `develop..main` não vira opção nem intervalo do git (E3).
- C-16: o veredito não muda, só o aviso; a guarda de rc fica coberta por `test_o_aviso_nao_muda_o_codigo_de_saida`.
- O teste novo cobre E1 (cópia igual e antiga) e E2/E3 (sem pilha de erro); `FerramentaDefasadaNoForge` rodada na worktree, 12 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática. Ferramentas ausentes no PATH (lacuna, nada instalado): gitleaks, semgrep, osv-scanner, zizmor, actionlint, shellcheck. O diff não tem shell, workflow, dependência nem segredo.
