---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-desenho-g1-g3
commit: ce7be2d64637519562702617b2f1eeb050e7910e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E98.3), desenho do G1 a G3

Diff `2d73a35e..ce7be2d6`: `docs/propostas/g1-g3-fluxo-rapido.md` (180 linhas) e o fragmento `changelog.d/v0480-desenho-g1-g3.md`. Classe T, só documentação; sem suíte a citar (nenhum código, teste nem workflow no diff) e sem PR nesta etapa.

## Achados
- A1 (recomendado) docs/propostas/g1-g3-fluxo-rapido.md:168 · D1, D2 e D4 aparecem abertas, mas já foram decididas: D1 pela regra do dono de 22/11 07:23 e 23/11 14:24 (2.ª e 3.ª volta sem perguntar, que também mudam o "no máximo 1 volta" de :21), D2 pela decisão do time de 22/11 08:49, D4 no #785. Nota de estado em §7.

## Parecer
Aprovado.

- **Fontes:** conferi na base 2d73a35e as citações `arquivo:linha` do quadro C1 a C4 e das seções 2 a 4 (`bin/forge-check` 1035, 1062, 1066, 2101, 3056, 3060, 3181, 3404, 4312; `ci.yml` 612-618 e 739; `bin/forge-fechar` 12 e 860; `tests/catraca.py` 887 e 1833; `hooks/parecer.py` 13 e 786; `R-QA.md` 14 e 17; `R-FLUXO.md` 16; `agents/qa-engineer.md` 17 e 21): todas apontam o trecho descrito. Os limites da API de statuses (1000 por sha e contexto) e o `gh pr merge --match-head-commit` existem como descritos.
- **Neutralidade (`R-NEUTRO`):** `termos_achados` de `tests/neutralidade.py` sobre o arquivo com a lista `termos_proibidos_hash`: conjunto vazio. A extensão aos projetos fica como decisão do dono (D5).
- **`R-DECISAO`:** nenhuma regra entra por este documento; cada trava proposta traz "uma entra, uma sai", "Por que o existente não basta" com evidência do código (G2, G3) e critério de reversão (§8). A seção 6 separa o que afrouxa pela regra e pelo mérito e liga cada item ao rótulo do dono.
- **Coerência com o que entrou:** o G1.1 do #789 (teto de volta, autorização canônica pela linha DECISÃO DO DONO, contagem por item) segue o §2.1 e o corte G1.1 de §5. O corte de 23/11 (G1.2 e G1.3 em branches separadas, `melhoria/v0480-g1-2-delta` e `melhoria/v0480-g1-3-classe`) volta ao corte original deste desenho (§5, linhas 122 e 123, um item cada, em série pelo `bin/forge-check`). O único descompasso é de estado das decisões (A1): o desenho é retrato de 21/11 com a base declarada em :5, e as decisões posteriores do dono prevalecem; não bloqueia, vira cartão.
