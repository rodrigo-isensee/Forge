---
tipo: review
contrato: 1
pedido: pergunta-tokens-tempo
branch: melhoria/pergunta-tokens-tempo
commit: df1b1b450f1296c27a50d41fccbe6cbabe499cbe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: PERGUNTA-TOKENS-TEMPO, afrouxa, tempo e tokens por opção na pergunta ao dono

Escopo: `82c11c0...df1b1b4` (base 82c11c03dfcbe7dfe521c6500ef8c976e49995c5), 5 arquivos em 2 commits, 29 linhas acrescentadas e 7 removidas. Quem revisa não é o autor (E1.1 foi de outra instância). Comparei o diff com E1, E2 e E3 do pedido, com o desenho `docs/propostas/aq/pergunta-tokens-tempo.md` e com a DECISÃO TÉCNICA de 14:06 e de 14:32.

Veredito sobre `df1b1b4`: **APROVADO**, sem bloqueante.

## Ferramentas (saída citada, não refeita)
- `python3 -m unittest tests.test_clareza -q`, rodado aqui: `Ran 6 tests` / `OK`.
- Suíte completa, segundo o relatório da E1.1 no pedido: 1312 OK. O pre-push deste parecer a roda de novo. O `scripts/validar-plugin.sh` fica com o QA e o CI.

## Conferência linha a linha das 7 linhas trocadas
- `skills/modo-iniciante/SKILL.md:35` (item 4): o texto antigo tinha "Afrouxa o processo?" (sim ou não, por opção), "custo de eficiência", tempo a mais ou a menos por demanda, faixa e média, e "não medido". Tudo continua no texto novo. Os dois trechos em negrito que a lista `invariantes` de `tests/config.json:181` protege estão intactos. O que entrou: tokens, as marcas `medido` e `estimado` e a remissão para "Números da pergunta".
- `skills/modo-iniciante/SKILL.md:41-43` (exemplo): o rótulo "Eficiência:" virou "Tempo:" com os mesmos números (0 a 1 h, média 0,5 h; 1 a 3 h, média 2 h; sem diferença). O efeito de cada opção e "Afrouxa o processo? Não." seguem nas três. Entraram a base do número e o campo Tokens. A recomendação e "Faltam 2 perguntas" não mudaram.
- `docs/regras/R-DECISAO.md:11`: o texto antigo (contexto, opções A, B, C com prós e contra, recomendação com motivo) continua palavra por palavra, e o acréscimo vem no meio. A linha 8 só muda a data de revisão. A regra fica mais exigente, não mais frouxa.
- `agents/jarvis.md:109`: só uma inserção depois de "custo de eficiência". A saída "decidam vocês" com as exceções de `R-DECISAO` ("Complemento") e "Ordem ampla não confirma" continuam iguais.
- Conclusão: nada do texto antigo se perdeu. A troca acrescenta campos, o que confirma a DECISÃO TÉCNICA de 14:32.

## Checklist
1. Escopo: cobre E1 (skill nos dois perfis, regra e Jarvis), E2 (texto em skill, regra e agente, que chegam aos projetos pela release, sem marca de "só no Forge") e E3 (`tests/test_clareza.py:43-56`). A medição automática ficou fora, como o pedido manda, e virou o cartão CUSTO-MEDIA-POR-AGENTE.
2. Regras: `R-NEUTRO` respeitada, o exemplo é neutro (encomenda). `R-CUSTO` respeitada, a fonte dos números é `forge-check transcricao custo --entregas`, local e sem custo (o comando existe em `bin/forge-check:7` e `:2804`). `R-DECISAO` é citada pelo ID, e o texto dela fica só na fonte.
3. Legibilidade: "Números da pergunta" cabe em três itens. Os caminhos citados existem no modelo de projeto (`templates/projeto/docs/kanban/entregas.md` e `historico.md`).
7. Teste: exige pelo menos 2 opções (`assertGreaterEqual`, mínimo de itens, item 11), cada uma com os três campos, e as três marcas na seção, na regra e no Jarvis. Segundo o pedido, ficou vermelho antes do verde.
9. Commits: dois, em Conventional Commits em português, cada um coerente. O fragmento `changelog.d/pergunta-tokens-tempo.md` bate com a branch, e o `CHANGELOG.md` não foi tocado.
10. Não é mecanismo novo: é formato de texto. A reversão é o revert dos dois commits.
- Segurança: parecer próprio em `docs/security/pergunta-tokens-tempo.md`. Não refiz.

## Achados

## Recomendações (não bloqueiam)
- `skills/modo-iniciante/SKILL.md:47`: a fonte de tempo `medido` aponta a janela do pedido em `historico.md`, que registra movimentos de cartão. A coluna "Duração" de `entregas.md` já traz o tempo por agente. Vale citar as duas para não deixar a medição de tempo só no cálculo manual da janela.
- `skills/modo-iniciante/SKILL.md:35` e `tests/test_clareza.py:43`: o teste confere as marcas na seção, mas não confere "tokens" no item 4. Uma linha a mais protegeria o item além do exemplo. Pode ir num próximo lote que já mexa no arquivo.
