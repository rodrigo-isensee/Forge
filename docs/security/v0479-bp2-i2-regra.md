---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 80f4bd1f2912d3222559b954eafde362e9e1a5dc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp2-i2-regra (BP2 I2 e I5, revalidação no head 80f4bd1f, E38.10)

Volta por delta: a rodada anterior (head 0ce5173b, aprovado com A1 e A2 recomendados) fica no git. Delta lido: `forge-check parecer delta` de 0ce5173b..80f4bd1f, no domínio `docs/protecao-de-branch.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md` e `templates/projeto/docs/engineering/protecao-de-branch.md`; fora, `changelog.d/`. A base andou (004ce869 para 8a50379) e o merge 95ed14d6 só trouxe pareceres da própria branch, sem byte de domínio. Só texto: sem suíte local (brief); o CI do PR é o portão dela.

## Gatilhos
Gatilhos: controle do Forge (portão de merge da integração), afrouxa-regra (R-FLUXO, D5 do dono), fluxo de branches.

## Confirmação pedida pela D5 (por escrito)
**Preso ao commit revisado: confirmado.** O item 3 (`skills/trabalho-em-paralelo/ritmo-e-corte.md:26`) agora diz sozinho o que antes dependia do item 2: merge com `--match-head-commit` no head revisado e, com a base trazida, head novo só com pais (revisado, topo) e a árvore do `git merge-tree` dos dois, sem resolução nem edição à mão. O item 2 (`:25`) segue mantendo a cadeia de sempre, com o `forge-check pr --base` recusando byte a mais no merge.

**Com a mesma falha declarada: confirmado.** O item 1 (`:24`) prende o vermelho ao CI de `push` do topo, concluído com falha, e para se o topo andar; o item 4 (`:27`) exige que cada teste que falhou tenha rodado e passado, sem valer o pulado pelo id, pela classe ou pelo módulo nem o apagado, e que o passo vermelho que não é teste fique verde; o item 7 (`:30`) registra run, topo, PR e head.

## Estado dos achados anteriores
- A1 (recomendado, rodada 0ce5173b): corrigido em `ritmo-e-corte.md:26`, com o texto da correção mínima pedida.
- A2 (recomendado, rodada 0ce5173b): corrigido em `ritmo-e-corte.md:27`, com as armadilhas do I1 e o passo que não é teste.

Conferido no delta sem achado: `docs/protecao-de-branch.md:21` e `:45` deixam de dizer que o `bin/forge-fechar` já faz a fila e declaram a conferência à mão do `tech-lead` até a I4, com o limite (o passo 6a só para no conflito); isso tira uma garantia que o texto prometia e o script não dava, o que reduz o risco de confiança indevida. `ritmo-e-corte.md:22` acompanha. O passo 8 do modelo de projeto (`templates/projeto/docs/engineering/protecao-de-branch.md:30`) passa a apontar a fila da `R-FLUXO` e deixa ao dono marcar a caixa do servidor; não mexe em workflow nem em ruleset (`R-CONFORMIDADE`).

## Achados

## Sondas

## Detalhe dos achados
Sem achado novo nesta rodada.

## Riscos aceitos e ferramentas
Sem risco aceito. O item 5 aceitar qualquer arquivo mudado desde o último verde segue sendo a D2 do dono, não achado. Até o I1 e o I4 entrarem, a fila e o conserto ficam na conferência à mão do `tech-lead`, como o texto agora diz nos três arquivos.
Ferramentas: leitura estática do delta; nada a varrer (só texto). Analisador de segredos, de workflows e lint de shell fora do PATH desta estação (lacuna registrada, sem instalação, `R-CUSTO`). Suíte: não rodada aqui (brief); o CI do PR é o portão dela.
