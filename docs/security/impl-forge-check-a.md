---
tipo: revisao-seguranca
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a2
commit: 0708213d5b794a5023743293b7e5d65b47518dff
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: impl-forge-check-a (branch a2)

Diff lido: `234dbe0..0708213` (b5f89f1 C3, 0708213 fragmento), contra o modelo de ameaças `docs/security/ameacas/forge-check-a.md` (controles C-12 a C-14, casos D1 a D4).

## Item entregue e M14
- Item: E3 do pedido (FC-E4-FALHA-ABERTA), a falha do git no filtro do E4 reprova em vez de virar escopo vazio com rc 0.
- M14 (agents/tech-lead.md:19): `bin/forge-check` 12+7 e `tests/test_forge.py` 18+0, 37 linhas, abaixo de 150; o fragmento fica fora. Um comportamento. Cumpre.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o filtro do E4 decide o escopo que o conferente vê nas etapas de merge.

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferido:
- C-12: `nomes_do_intervalo` com `estrito=True` devolve None na falha (`bin/forge-check:755-760`); o padrão segue lista vazia, e o único chamador estrito é o E4 (`:1121`); os outros seis chamadores não mudam.
- C-13: com None não filtra, não roda o `|=` dos desfeitos e soma a linha que reprova (`:1122-1123`); com `arquivos` já vazio a linha `escopo: sem commit` entra sem reprova, mas a do E4 reprova e o rc final é 1 (`:1171`), então a reprovação não depende de haver arquivo.
- C-14: o tempo esgotado do git não ganhou captura nova.
- O E4 e o `integrado` são excludentes (um exige o head fora da base, o outro dentro), então o `integrado` não sobrescreve o resultado da falha.
- Teste `FalhaDoGitNoE4` cobre D1 e D3 (as duas etapas de merge); `FalhaDoGitNoE4` e `PrAposMergeDaBase` rodados na worktree, 13 testes, OK. O D2 (com `--desde` válido) não tem caso próprio; o código não roda o `|=` com None, então fica como recomendação de teste, sem devolver.

## Riscos aceitos e ferramentas
Nenhum risco aceito. R-1 do modelo (a mesma classe em `arquivos_da_entrega` e no `integrado`) segue no cartão FC-ENTREGA-GIT-FALHA-ABERTA. Revisão estática. Ferramentas ausentes no PATH (lacuna, nada instalado): gitleaks, semgrep, osv-scanner, zizmor, actionlint, shellcheck. O diff não tem shell, workflow, dependência nem segredo.
