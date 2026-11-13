---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/diretrizes-decisao
commit: 39c163cc5d2fdfd69982e1eb3e80815aea0202e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: diretrizes-decisao (E26.13, review da E26.1)

Escopo: diretrizes 1, 8 e 9 do dono em `docs/regras/R-DECISAO.md` e `skills/falar-com-o-dono/SKILL.md` (classe C, head 39c163cc). O texto novo cobre o pedido: custo em tokens e ganho de velocidade por opção, origem por decisão e o critério "decisão ruim não passa calada". O corte para caber no orçamento, porém, apagou trechos que `tests/config.json` protege como invariantes.

Prova: `python3 -m unittest tests.test_forge.RegrasInviolaveis.test_trechos_obrigatorios` no head, 6 falhas (2 tentativas não foram necessárias, a falha é determinística). Os 6 trechos faltam no texto, conferidos também por `re.search` direto.

Restauração sugerida (sem aumentar o orçamento além do necessário): devolver as expressões literais cortadas, ou, se o dono quer o corte, atualizar os invariantes no mesmo PR com destaque no título (afrouxar invariante exige isso, `CLAUDE.md`). Fora isso, nada sumiu: nenhuma regra com ID foi removida e os demais invariantes das duas fontes passam.

Recomendados: o formato `decidido: <porta> — <critério> — <fato>` saiu do texto da "Decisão óbvia"; nenhum teste o protege, mas confira com `forge-check decisoes registrar` se a ferramenta o imprime (ela vale pelo ID). "(não amplia autorização)" saiu da regra, mas segue testado em `bin/forge_dono.py`.

## Achados
- A1 (bloqueante) docs/regras/R-DECISAO.md:17 · invariantes de tests/config.json sumiram: `na entrega, `pendente:``, `a próxima espera a resposta`, `origem: <coluna>; ação: <o que o usuário faz>; comando:`, `um comando, um efeito`, `evidência no motivo`; test_trechos_obrigatorios falha (R-DECISAO) · resolvido em 39c163cc
- A2 (bloqueante) skills/falar-com-o-dono/SKILL.md:13 · invariante `Sem resposta, fica pendente.` removido da skill (o corte moveu a frase); test_trechos_obrigatorios falha (R-DECISAO) · resolvido em 39c163cc
- A3 (recomendado) docs/regras/R-DECISAO.md:24 · formato `decidido: <porta> — <critério> — <fato>` saiu da decisão óbvia sem teste que o proteja; confirme que `forge-check decisoes registrar` o descreve

## Sondas

## Parecer (original, head 3a86bd38)
Reprovado por A1 e A2: o CI do PR rodaria o mesmo teste e falharia (RegrasInviolaveis). Volta ao autor: restaurar os seis trechos literais (ou ajustar `tests/config.json` com destaque no título do PR e o motivo). As diretrizes 1, 8 e 9 em si estão bem escritas e completas. Mudança do changelog (`changelog.d/diretrizes-decisao.md`) presente. Sem PR aberto na branch, então não há CI para citar; a suíte inteira fica para o CI.

## Revalidação (E26.20, delta 3a86bd38..39c163cc, volta E26.19)
Delta lido por `forge-check parecer delta`: só `docs/regras/R-DECISAO.md` e `skills/falar-com-o-dono/SKILL.md`. Os seis trechos protegidos voltaram (`a próxima espera a resposta`, `origem: <coluna>; ação: <o que o usuário faz>; comando:`, `um comando, um efeito`, `evidência no motivo`, `na entrega, \`pendente:\``, `Sem resposta, fica pendente.`); o formato `decidido: <porta> — <critério> — <fato>` e `(não amplia autorização)` também. `python3 -m unittest tests.test_forge.RegrasInviolaveis.test_trechos_obrigatorios`: OK. A1, A2 e A3 resolvidos.
Custo declarado aceito, recomendado: a diretriz 8 perdeu "nem a do dono" no título e "origem" na lista de itens levados; a skill mantém "decisão ruim do dono volta a ele" e a regra continua pedindo evidência, então o alcance sobre decisão do dono segue coberto. Sem bloqueante novo. Tamanho do código: nenhum arquivo contado (só `.md` e fragmento). Suíte inteira fica para o CI do PR.
**Aprovado em 39c163cc.**
