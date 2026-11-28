---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: f00c3da26d6be9051f14ad0b1cfad212b41998b4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E6.12, revalidação do lote de devops)

Revalidação por delta (`R-REVIEW`). A rodada anterior (E6.8, commit `f9356caf`, aprovado, A1 a A3 corrigidos) está no git.

Gatilhos: dependência nova (o modo `--ferramentas` e o preparo completo baixam e executam binários e pacotes de terceiros na estação do dono).

## Delta lido
`forge-check parecer delta docs/security/v0478-devops-lote.md`, intervalo `f9356caf..f00c3da2`: nenhum arquivo do domínio mudou. Fora do domínio (não relido): `tests/mutantes/v0478-devops-lote.json`, `tests/test_ferramentas_portoes.py` (teste da falha do install sem tar e mutantes M5 e M6), além dos pareceres de review e QA. `scripts/preparar-estacao.sh` segue igual ao lido na rodada E6.8.

## Achados anteriores
- A1, A2 e A3: seguem corrigidos (código do domínio inalterado desde `f9356caf`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas da skill fora do PATH desta estação, lacuna registrada como na rodada anterior. Suíte inteira: só no CI do PR, não rodada aqui (brief).
