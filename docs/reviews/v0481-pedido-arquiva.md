---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 8b3124465d4c1a3c0b31e100731a5b9935d8a223
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E9.10, #874, pedido que se arquiva sozinho antes do teto, por delta)

Delta lido: `git diff ec38cbc4..8b312446`, domínio código e testes: `bin/forge-check` (comentário de `ETAPA_ARQUIVADA`, `ENTREGUE_DA_ETAPA` e `etapa_entregue_na_linha`), `tests/test_brief_tamanho.py` (3 testes novos), `tests/mutantes/v0481-pedido-arquiva-3.json` (M22 refeito), `-6.json` e `-7.json` (M40 a M48) e o fragmento do changelog. O parecer anterior (ec38cbc4, E9.6) reprovou com A1 bloqueante (neutralidade) e A2 recomendado; ele ficou só no clone de review e é regravado aqui por cima.

## Achados
- A1 (recomendado) bin/forge-check:8061 · `ENTREGUE_DA_ETAPA` aceita `entregue` seguido de hífen: "E1.1 entregue-parcial" fecha a E1.1 (S2). Sem ocorrência no Histórico real e o --cobre fica protegido; vale incluir `-` no lookahead (`(?![\w?-])`) com um mutante.

## Sondas
- S1 · etapa_entregue_na_linha nas formas recusadas pelo A2 anterior ("não foi entregue", "a ser entregue", "será entregue", "Entregue? não", "volta entregue", "(papel) não entregue", "E1.1: entregue", "(E1.1, E1.2) entregue") no head 8b312446 · espera: None · obtido: None em todas
- S2 · etapa_entregue_na_linha("E1.1 entregue-parcial") · espera: None · obtido: E1.1
- S3 · linhas do `## Histórico` do pedido v0481 real, antes (ec38cbc4) e depois (8b312446) · espera: a forma estrita só tira fechamento, nunca acrescenta · obtido: antes E2.5, E3.5, E6.3, E7.1, E7.4, E9.1, E9.5, E10.1; depois as mesmas sem a E2.5 ("volta E2.5 do D3 entregue", que fica aberta: falha segura)

## Parecer
Aprovado. Os dois achados do parecer anterior fecham:

- A1 anterior (bloqueante, R-NEUTRO): o comentário de `ETAPA_ARQUIVADA` (bin/forge-check:8058) passou a citar `E1.1 (tech-lead)`, papel neutro; a reprova "stack no núcleo" do pre-push saiu, e o envio deste parecer passa pelas checagens baratas.
- A2 anterior (recomendado, tratado na volta): `etapa_entregue_na_linha` só fecha com `ENTREGUE_DA_ETAPA.match` no trecho logo após o primeiro id (parêntese de fecho, papel opcional entre parênteses e `entregue` sem letra nem `?` depois). Negação, futuro, texto livre e interrogação não fecham (S1); a forma real `volta (E1.1) entregue no <sha>` segue fechando (`test_forma_estrita_de_entregue_fecha`).

O A1 acima é novo e fora do que o parecer anterior apontou (G1.2): vira cartão depois do merge.

Ferramentas: `tests/test_brief_tamanho.py` e `tests/test_forge_tamanho.py` (47 testes) rodados aqui no 8b312446 (rebase do clone sobre o remoto), OK. Mutantes: rodei os do delta, `bin/forge-mutante --processos 1` nas specs -6 e -7 (M40 a M48) e `--ids M22` na -3: os 10 morreram. M41 a M48 mutam a mesma linha de guarda (8061) com prefixos diferentes, um por forma recusada; aceito. CI do #874: catraca pendente na leitura; a suíte inteira fica com o CI, não rerrodei.

Medida do item: `bin/` da branch desde a base com 127 inserções e 14 remoções, abaixo do teto de 150, um comportamento.
