---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-adotar-vermelho
commit: 3f526e8b98a26e7e35d2b6ee5706e98dae687841
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-adotar-vermelho (E21.3)

Diff lido: `0c47762a...3f526e8b` (8 arquivos): o detalhe novo `skills/briefs-e-conferencia/teste-vermelho-alheio.md`, os apontamentos em `autor-ate-o-merge.md`, `engineering-practices/SKILL.md`, `agents/qa-engineer.md`, a troca do "vira cartão" em `qa-testing/SKILL.md:75`, os invariantes novos em `tests/config.json:757-774` e `tests/test_teste_vermelho_alheio.py`.

## Gatilhos
Gatilhos: controles do Forge (`tests/config.json`, invariantes de regra)

## Resumo
A regra nova não abre caminho para apagar, pular ou afrouxar teste: a proibição está explícita (`teste-vermelho-alheio.md:14`, com as quatro formas: `skip`, tirar asserção, trocar o esperado pelo obtido, tirar da lista que roda), o único desvio ("teste errado de verdade", `:15`) exige a explicação do QA no parecer do conserto e a mutação do trecho com sobrevivente bloqueando (`:16`), e o conserto nunca entra na branch parada (`:10`, `:19`, `:20`). O texto segue as duas condições da DECISÃO DO DONO de 18/11 13:45 (pedido v0478, Histórico). Os 8 invariantes novos casam com o texto (conferido: lista de não casados vazia nos dois arquivos) e têm `invariantes_motivo` com `R-QA`; o teste do ramo de falha (`test_invariante_reprova_o_texto_sem_a_condicao`) prova que apagar a condição 2 quebra os invariantes. Nenhum controle existente foi afrouxado: o diff em `tests/config.json` só acrescenta.

Ficam duas recomendações, sem caminho de ataque que justifique bloqueio: a regra é texto de processo, aplicada no review, e o teste continua inteiro no CI.

## Achados
- A1 (recomendado) skills/briefs-e-conferencia/teste-vermelho-alheio.md:6 · O critério "ou cai em código que o diff não toca" deixa o autor classificar como alheia a regressão indireta do próprio diff (teste de B cai porque B chama A, que o diff mudou); o critério objetivo é só o herdado da base (`forge-testes --vermelho`).
- A2 (recomendado) tests/config.json:762 · Os invariantes cobrem só o prefixo em negrito da condição 2; a enumeração das formas proibidas (`teste-vermelho-alheio.md:14`), o "não mexe no teste na sua branch" (`:19`) e o bloqueante do tech-lead (`:20`) podem sumir sem teste vermelho.

## Sondas

## Detalhe dos achados
**A1** · evidência `skills/briefs-e-conferencia/teste-vermelho-alheio.md:6` · caminho: um autor (agente com pressa de ver o PR andar) vê cair um teste em módulo que o diff não toca, mas que depende do código mudado; pelo segundo critério declara o vermelho alheio e o PR "espera a correção". O conserto, feito sobre a base onde o teste passa, só fica verde mexendo no teste, o que `:14` proíbe e o CI da base barra; o dano realista é atraso e uma regressão mal atribuída, não teste afrouxado. Severidade baixa · correção mínima: definir "de outro item" só como "cai também na base" (no Forge, o "herdada da base" do `forge-testes --vermelho`) e tirar o "ou cai em código que o diff não toca", ou exigir as duas condições juntas · esforço P · dono: `tech-lead` (E21.1).

**A2** · evidência `tests/config.json:757-766` · caminho: uma edição futura de enxugamento de texto remove a lista "sem `skip`, sem tirar asserção, sem trocar o valor esperado pelo obtido, sem tirá-lo da lista que roda" ou as linhas de "Quem faz o quê" e nenhum teste falha, porque os invariantes param em `...para ficar verde:\*\*`. Severidade baixa · correção mínima: acrescentar a `invariantes["skills/briefs-e-conferencia/teste-vermelho-alheio.md"]` os trechos `sem \`skip\`, sem tirar asserção, sem trocar o valor esperado pelo obtido, sem tirá-lo da lista que roda`, `avisa o \`tech-lead\` e não mexe no teste na sua branch` e `é achado bloqueante o PR parado que traz o conserto e o conserto que apaga, pula ou afrouxa o teste` (com o escape de regex do arquivo) · esforço P · dono: `tech-lead` (E21.1).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Suíte: não rodada localmente (brief: sem suíte local); a bateria inteira é do CI do PR, que ainda não tem run neste sha (`gh run list --commit 3f526e8b` vazio). Rodado: o módulo `tests/test_teste_vermelho_alheio.py` isolado → 5 testes OK; conferência direta dos invariantes do arquivo novo e de `autor-ate-o-merge.md` contra o texto (nenhum sem casar).
Ferramentas: o varredor de segredos não está no PATH (lacuna; o diff é só texto de processo e um teste sem credencial).
