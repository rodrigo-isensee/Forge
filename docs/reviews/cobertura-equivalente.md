---
tipo: review
contrato: 1
pedido: cobertura-equivalente
branch: melhoria/cobertura-equivalente
commit: dec6630de1e247677edf0d0ad278dbabab01e511
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: cobertura-equivalente

Code review (`R-REVIEW`) do FM1 PR 2 (pedido COBERTURA-EQUIVALENTE, E1.1 do COBERTURA-EQUIVALENTE-REV): commits 1a4dc53, db9cb78 e dec6630 sobre a develop 3fec04b, head dec6630.

## Achados
- A1 (recomendado) bin/forge-mutante:232 · equivalente com chave faltando recebe "precisa das chaves ..., testes", mas `testes` é opcional nele; a mensagem deveria separar as obrigatórias das aceitas (classe: texto antigo que não acompanhou a regra nova).
- A2 (recomendado) bin/forge-mutante:480 · a isenta que cruza condição coberta só por equivalente passa a ser consultada e usada (antes ficava sem uso, rc 2); comportamento correto, mas sem teste que o fixe.

## O que foi lido
- `bin/forge-mutante`, as três mudanças:
  - (a) `analisar` separa os casados em mutante com teste (`coberta`) e equivalente; a condição só com equivalente sai `só equivalente · arq:L · <spec>:<id> · não provado` e `cobertura` a conta no rc 1 (linhas 477-487 e 552). A equivalente com `testes` também fica fora de `coberta` no `--cobertura`, o que está certo: sobreviver ao teste não prova nada sobre a condição.
  - (b) `principal` marca `rodou` só depois de um veredito real; com nenhum teste rodado e código 0, sai 2 com a mensagem em stderr (linhas 570, 603 e 620-622). A checagem vem antes da de árvore mudada, que continua saindo 2 de qualquer jeito.
  - (c) o equivalente com `testes` segue o caminho comum (controle, `de` único, troca, testes); `veredito` só devolve `morreu`, `sobreviveu` ou `inválido` (linhas 202-209), então o remapeamento da linha 604-606 cobre todos os casos: `sobreviveu` vira `equivalente` (rc inalterado), `morreu` vira `inválido` com o motivo, rc 2. O `sem veredito` e o controle vermelho saem antes, com rc 2.
  - Validação: `CHAVES_DO_EQUIVALENTE` passa a aceitar `testes`, as obrigatórias do equivalente são as chaves menos `testes` (linhas 81 e 230-231), e os `testes` presentes são validados como os do mutante comum (linha 250). O mutante comum segue exigindo o conjunto exato.
- `tests/test_forge_mutante.py`: o teste antigo que recusava equivalente com `testes` foi invertido com motivo (o equivalente com `testes` precisa passar na validação para poder rodar) e ganhou os casos mal formados (`[]`, id sem `tests.`, string). Testes novos de (a), com a spec comum que não muda no mesmo teste, de (b) e de (c), este com os dois lados (morto = inválido rc 2; sobrevivente = `equivalente` rc 0).
- `tests/mutantes/cobertura-equivalente.json`: 11 mutantes (Q1 a Q11), um por condição mudada; a `--cobertura` abaixo lista as 10 condições como `coberta`, sem `sem mutante`, `só equivalente` nem `apagada`. Rodar a spec é do QA (E3.1, em paralelo).
- `skills/qa-testing/SKILL.md:85`: a linha nova descreve o equivalente com e sem `testes`, a spec só de equivalentes (rc 2) e o `só equivalente` (rc 1), coerente com o código e com a docstring; a linha 90 da mesma skill (sobrevivente vira teste ou equivalente aceito pelo QA) segue valendo. Conferido o AR-9 (limite antigo no texto): `agents/tech-lead.md:22` não descreve o comportamento mudado; sem texto antigo nas docs.
- Docstring de uso e do código de saída atualizada nos três pontos; fragmento `changelog.d/cobertura-equivalente.md` presente (seção `Corrigido`).

## Pontos pedidos no brief
- A isenta que segue liberando a condição coberta só por equivalente: a ordem em `analisar` é coberta, isenta, só equivalente, sem mutante. A isenta tem trecho exato e motivo de 20+ caracteres impresso para o review e o QA, então liberar por ela é a mesma decisão explícita que vale para a condição sem mutante; aceito. Falta só o teste (A2).
- Risco declarado (spec antiga só de equivalentes passa a sair 2): conferido em `tests/mutantes/*.json` desta árvore, nenhuma spec é só de equivalentes sem `testes`; o efeito fica para specs de projetos, e é o objetivo do pedido. Registrado no fragmento do changelog.
- Teto por PR (decisão M14): `git diff --numstat --no-renames 3fec04b...dec6630` dá `bin/forge-mutante` 34+17 e `tests/test_forge_mutante.py` 33+2, total 86 de 150; fora da conta a spec `tests/mutantes/` (117), o fragmento e o `.md`. Não toca `hooks/` nem `PROTEGIDOS`. Um comportamento: o equivalente declarado deixa de valer como prova, nas três saídas que o liam como prova; aceito como um só, como o pedido o escopou.
- Linha AR: nenhuma nova nesta rodada (decisão técnica 2026-10-29 15:28 do pedido T1-CONF-ESCOPO-REV); a classe do A1 é a do AR-9 (texto que não acompanhou a regra nova), a do A2 é teste faltando para comportamento mudado.

## Ferramentas (saída citada, não refeita)
- `python3 -m unittest tests.test_forge_mutante` na worktree em dec6630: `Ran 71 tests in 20.554s`, `OK`.
- `bin/forge-mutante --cobertura --base 3fec04b9d7b8e8916b0eef486a9253a854f227e7`: 10 linhas `coberta` (Q1 a Q4 e Q6 a Q11), rc=0.
- Shell: nenhum arquivo de shell no diff. Segurança: sem gatilho (ferramenta de teste local, sem entrada externa nova, sem hook); nenhum cartão para o `security-engineer`. Pipeline e IaC: não tocados.

## Parecer
Aprovado. As três mudanças fazem o que o pedido pede, sem afrouxar o mutante comum: (a) `só equivalente` em linha própria e rc 1; (b) spec só de equivalentes sem `testes` sai 2; (c) equivalente com `testes` roda e, morto por eles, sai inválido com rc 2. Testes cobrem os três e a spec comum inalterada; a spec de mutantes cobre cada condição mudada. Os dois achados são recomendações e não devolvem: A1 (bin/forge-mutante:232 · mensagem lista `testes` como obrigatória para o equivalente · separar obrigatórias e aceitas · recomendado) e A2 (bin/forge-mutante:480 · precedência da isenta sobre `só equivalente` sem teste · um caso em `Cobertura` · recomendado).
