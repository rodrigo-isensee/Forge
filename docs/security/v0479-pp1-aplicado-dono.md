---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 4d60adf4f5d43fc8f55c8a7f27727e0823b18674
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pp1-aplicado-dono (v0478 E52.3, revalidação)

Volta por delta sobre o parecer aprovado em `58da41ec` com A4 recomendado (a rodada anterior fica no git). Delta lido (`forge-check parecer delta`, `58da41ec..4d60adf4`): no domínio, só `bin/forge-check` (`isencao_do_dono`, `patch_revisado_do_dono`, `parecer_cita_o_patch`, chamada em `linhas_de_entrega`). Fora do domínio: `tests/test_conf_escopo.py`, os mutantes e o fragmento do changelog; do teste, li só o `aprovar` da classe `PatchRevisadoDoDono`, para as sondas. A base subiu de `cf09782` para `5ccac0b` por merge, sem mudança no domínio desta entrega. Suíte: não rodada (brief). Rodadas: as sondas S3 e S4 e as variantes S0 e S5 a S10, sobre a classe `PatchRevisadoDoDono` (31 testes, sem falha).

Gatilhos: guarda da conferência de entrega, arquivo em vigor (.githooks/, .claude/, .forge/config.json, .forge/versao), identidade do autor do commit.

## Achados anteriores
- A1 (bloqueante): resolvido em `58da41ec`, sem mudança no delta.
- A2 (recomendado): resolvido em `58da41ec`, sem mudança no delta.
- A3 (recomendado): **resolvido** junto com A4.
- A4 (recomendado): **resolvido.** `bin/forge-check:2297-2310` aceita só arquivo fora de `docs/security/aceites/` e `docs/security/ameacas/` (`PASTAS_RECUSADAS_DE_PARECER`, `bin/forge-check:7326`), com `tipo: revisao-seguranca`, `parecer: aprovado` e `pedido:` e `branch:` iguais aos da entrega conferida, que chegam de `linhas_de_entrega` (`bin/forge-check:3309`). `riscos-aceitos` não vale mais aqui, nem com aceite: é mais estrito do que a correção mínima pedia. S3 e S4 refeitas: recusadas.

## Furo que sobra
Só o do e-mail declarável, aceito pelo dono em 20/11 (opção a). A citação do sha256 agora precisa vir do parecer de segurança aprovado desta branch e deste pedido. Um parecer de outra entrega que chegue pela develop não isenta mais.

Este parecer leu o `forge-check`, não um `.patch` aplicado pelo dono. Por isso não cita sha256 de patch nenhum. A citação do patch real cabe no parecer de segurança da branch que o aplica, depois de lê-lo.

## Sondas
- S0 · controle: parecer aprovado com `pedido: exemplo` e `branch: melhoria/x` (os da entrega), que cita o sha256 · espera: isenta · obtido: `escopo: ok (patch do dono 7685800…, patch "docs/notas/pp1.patch" sha256 9cc62fef…)`
- S3 · parecer aprovado com `pedido: outro` e `branch: melhoria/outra`, que cita o sha256 · espera: não isenta · obtido: não isenta ("nenhum parecer de segurança aprovado da branch e do pedido, no head, cita o sha256 do .patch")
- S7 · igual a S3, mas só a `branch:` difere · espera: não isenta · obtido: não isenta
- S8 · igual a S3, mas só o `pedido:` difere · espera: não isenta · obtido: não isenta
- S4 · `docs/security/aceites/y.md` com `parecer: riscos-aceitos` e o sha256 · espera: não isenta · obtido: não isenta
- S9 · `docs/security/aceites/y.md` com frontmatter completo e aprovado da entrega · espera: não isenta · obtido: não isenta
- S10 · `docs/security/ameacas/y.md` com frontmatter completo e aprovado da entrega · espera: não isenta · obtido: não isenta
- S5 · `riscos-aceitos` da própria branch e pedido · espera: não isenta · obtido: não isenta
- S6 · `tipo: revisao-codigo` da própria branch e pedido · espera: não isenta · obtido: não isenta
