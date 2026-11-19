---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-promocao-pr
commit: 6ab1228acf7d1560b1d43541c59438a9e01ffcac
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-promocao-pr

Revalidação (E31.11) no head 6ab1228a, por delta. A rodada anterior (E31.7, head 1e0c50a7) fica no git.

## Gatilhos
Gatilhos: controle do Forge (portão do `forge-check pr`: quando a conferência E7 e o teto H1 deixam de valer).

## Resumo
- Delta lido (`forge-check parecer delta`, `1e0c50a7..6ab1228a`): no domínio, `bin/forge-check` (a chamada em `:1568`, a nova `avisar_rebase_merge` em `:1586-1593` e a docstring de `ponta_da_integracao` em `:1596-1601`) e `docs/fechamento-integrador.md:102`. Fora do domínio: o fragmento do changelog, o mapa de mutantes e `tests/test_promocao_por_marca.py`. Deste li só o teste novo do aviso (`:111-121`). O merge e12c8d0 trouxe só `docs/reviews/`, que está fora do domínio.
- A2 (recomendado, rebase-merge): **resolvido**. Segue a correção mínima proposta. A premissa agora está escrita no guia de promoção (`docs/fechamento-integrador.md:102`) e na docstring (`bin/forge-check:1598-1600`). O `pr` avisa na promoção quando `allow_rebase_merge` é `true` (`:1586-1593`).
- O aviso é só leitura. Usa `gh_json` com teto de tempo e stdin fechado (`:1452-1463`), e a mensagem é fixa, sem dado do remoto interpolado. Se faltar `gh`, a rede ou o campo, ou se a resposta tiver forma inesperada, não sai nada e o veredito não muda. O GitHub só devolve o campo `allow_rebase_merge` a quem tem permissão de escrita. Sem ela não há aviso, e a garantia fica na premissa documentada. Isso é aceitável para um aviso que não decide nada.
- O teste `test_promocao_avisa_quando_o_repositorio_permite_rebase_merge` cobre `true`, `false`, campo ausente, `None` e lista.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodado no head 6ab1228a: `tests/test_promocao_por_marca.py`, 6 testes OK em 8,2 s. Suíte inteira: não rodada (brief). O CI do PR continua como portão. Ferramentas: o varredor de segredos e os linters de workflow não estão no PATH (lacuna). O delta não toca em workflow nem em segredo.
