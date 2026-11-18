---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-adotar-vermelho
commit: 60782c174474ecc203b5a01defcb7a58a038785c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-adotar-vermelho (E21.6, revalidação)

Delta lido (`forge-check parecer delta`, intervalo `3f526e8b..60782c17`): no domínio, `skills/briefs-e-conferencia/teste-vermelho-alheio.md` (linha 6) e `tests/config.json:768-772` (quatro invariantes novos); fora do domínio, `tests/test_teste_vermelho_alheio.py`, lido por ser a prova das duas correções. Já lido na rodada anterior (E21.3, head `3f526e8b`, no git): o resto do diff `0c47762a...3f526e8b`.

## Gatilhos
Gatilhos: controles do Forge (`tests/config.json`, invariantes de regra)

## Resumo
Os dois recomendados da rodada anterior foram corrigidos, e o delta não afrouxa nenhum controle: `tests/config.json` só ganha linhas.
- **A1 (corrigido):** `teste-vermelho-alheio.md:6` define alheio só como "o teste já cai na base, sem o diff do item" e diz que o teste que cai só com o diff é regressão do item, mesmo em código que o diff não toca. O critério subjetivo saiu. Há um invariante (`tests/config.json:769`) e um teste (`test_criterio_de_alheio_e_so_herdado_da_base`, que também barra a volta do "ou cai em código que o diff não toca").
- **A2 (corrigido):** os três trechos da correção mínima viraram invariantes (`tests/config.json:770-772`): a enumeração das formas proibidas (`:14`), a linha do autor (`:19`) e a do bloqueante do tech-lead (`:20`). O teste `FormasProibidasEPapeis` tira cada trecho do texto e prova que algum invariante cai; outro teste confere que o texto inteiro casa todos os invariantes.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Suíte: não rodada localmente (brief: sem suíte local). A bateria inteira é do CI do PR, e `gh run list --commit 60782c17` não mostra nenhum run. Rodado: `python3 -m unittest tests.test_teste_vermelho_alheio` deu 8 testes OK.
Ferramentas: o varredor de segredos não está no PATH, o que fica como lacuna. O delta é só texto de processo, invariantes e teste, sem nenhuma credencial.
