---
tipo: revisao-seguranca
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: a2cb36d03c266fcfd3bbb643bcb900ecb64ae25a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: conferente-c2c3 (C2, C3 e C1 do CONFERENTE-VELOCIDADE)

Pedido de revisão: CONFERENTE-VELOCIDADE-REV (E2.1). Base `develop`, Base-sha `ce1a341b9874143cf3fb8c998a76eb473adc1df3`, head revisado `a2cb36d`. Diff lido inteiro: `bin/forge-check`, `agents/conferente.md`, `changelog.d/conferente-c2c3.md`, `tests/` (mutantes e testes do item).

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): `bin/forge-check` (o conferente de entrega e o `forge-check pr`) e `agents/conferente.md`.
- O C1 afrouxa em parte `R-PROVA` por decisão do dono (2026-10-27, "A"); o que se confere aqui é se o afrouxamento ficou no tamanho decidido: "o escopo é conferido pelo delta desde a última `conferida`, lido na íntegra; PQ de ato e ordem intactos" (E4 do CONFERENTE-VELOCIDADE).

## Achados
- A1 (bloqueante) bin/forge-check:503 · defeito provado e requisito (E4, gatilho controles do Forge): com --desde, arquivo que a branch mudou até a conferida e que um commit posterior devolve ao estado da base (teste apagado) some do escopo em pr e merge; linha 937 repete o corte

## Detalhe dos achados
**A1 · delta do C1 esconde o commit que desfaz o que já foi conferido.**
- Evidência: `bin/forge-check:503` (`arquivos_da_entrega` com `desde`: os nomes de `base...head` cruzados com os de `desde..head`, ou seja, só o que muda depois da conferida e que ainda difere da base) e `bin/forge-check:937` (nas etapas de merge, o filtro por conteúdo contra `origin/<base>` tira de novo o arquivo que voltou ao conteúdo da base). Com o C1 (`bin/forge-check:920`), esse caminho passa a valer nas etapas `pr`, `merge-integracao` e `pedido-de-merge-ao-dono`.
- Prova (repositório de sonda em `$TMPDIR/security-engineer-conferente-c2c3/repo`): a branch acrescenta `teste.py` e `cod.py` no commit conferido; depois vêm um merge da `develop`, um commit `git rm teste.py` e um commit em `cod.py`. `forge-check entrega P1 ... --etapa pr --desde <conferida>` lista só `cod.py` e `dev.txt`; `--etapa pedido-de-merge-ao-dono` lista só `cod.py`. A remoção de `teste.py`, que está dentro do intervalo `desde..head`, não sai em nenhuma linha `escopo:`. O mesmo vale para um parecer apagado por inteiro depois da conferida.
- O que ficou provado do resto do pedido: o merge da base depois da conferida não deixa nada de fora (aparece como `confira`, sobra e não falta; nas etapas de merge sai pelo conteúdo, como antes); commit de parecer que remove linha sem apagar o arquivo sai com `-r` acima de 0 (a contagem é `desde..head` em dois pontos); o `--desde` segue validado por `desde_valido` em todas as etapas (o mesmo caminho de código; com `--desde` igual ao Base-sha a saída foi `escopo: --desde sem conferência anterior`, rc 1, e o intervalo voltou ao Base-sha); `pedido_na_entrega` também vale nas etapas novas.
- Caminho de ataque: o autor (agente ou pessoa com push na branch) entrega o item conferido, a linha `conferida` é gravada, e num commit seguinte apaga o teste ou o controle que cumpria um item do "Entregar". Na etapa de PR ou de merge, o conferente lê só o delta (é o que o C1 manda), não vê o arquivo, e não sai `pendente:` nem `escopo: fora` para o item desfeito. Antes do C1, nessas etapas, a leitura da branch inteira mostrava o item ausente. A defesa que sobra é o `forge-check pr` (parecer com diff efetivo diferente do commit dele não vale) e a leitura do review e do QA, se os pareceres forem feitos depois da remoção; o conferente, que é o controle que o C1 afrouxa, fica cego para essa classe. A decisão do dono afrouxa "ler a branch inteira", não "deixar de ver um commit do delta".
- Severidade: média (controle do Forge; precisa de push na branch, e há defesa em profundidade no `forge-check pr`). Bloqueante por ser defeito de comportamento provado contra o requisito do E4 e o pedido desta revisão, com gatilho.
- Correção mínima: com `desde`, somar aos nomes de hoje os de `desde..head` que já estavam em `base_sha...desde` (o que a branch tinha mudado até a conferida e mudou de novo depois); e, na linha 937, não tirar pelo conteúdo da base o arquivo que está em `base_sha...desde`. Teste: o caso da sonda (arquivo acrescentado antes da conferida e apagado depois) nas sete etapas, mais o mesmo com um parecer apagado. O corte é anterior ao C1 nas etapas de código (`review`, `seguranca`, `qa`), mas a mesma correção o fecha lá também. Esforço: P. Dono: `tech-lead` (autor do lote).

**Conferido sem achado:**
- C2, recusa do `forge-check pr` com id de pedido (`bin/forge-check:617-624`, `5206-5208`): só recusa (rc 2) quando o argumento casa `[A-Za-z0-9._-]+`, existe `docs/pedidos/<arg>.md` e não existe `melhoria/<arg>` local nem remota; nunca troca o argumento nem a `--ref`, e o caminho do `cmd_pr` fica o mesmo quando não recusa. O padrão sem `/` impede subir de pasta. Não abre caminho para conferir outra branch: a ref conferida continua sendo a `--ref` dada, e o erro é fechado.
- C2, linha `etapa: comando forge-check pr ...` (`bin/forge-check:4272-4280`): slug e `--ref` saem do mesmo `Branch:` do cabeçalho, com caracteres restritos a `[A-Za-z0-9._/-]` (sem metacaractere de shell); `--base <Base>` passa pela validação do `pr_da_cli` (só bases do fluxo, lidas de `origin/`).
- C3, `volta: bloco ... idêntico ao anterior (exigido)` e `rótulo do verificador: ok` (`bin/forge-check:3858`, `4169-4177`): as duas linhas são informativas (não reprovam e não aprovam); a comparação é byte a byte menos as quebras do fim; as linhas `volta:` que reprovam seguem iguais; `agents/conferente.md` mantém a leitura da contradição literal contra a decisão do dono.
- Testes do item (`tests.test_volta_por_delta`, `tests.test_etapa_do_brief`, `tests.test_conferencia_base_dono`): 120 testes, OK. Nenhum cobre o caso do A1.

## Riscos aceitos e ferramentas
- Risco aceito pelo dono: o afrouxamento parcial de `R-PROVA` do C1 (decisão de 2026-10-27), no tamanho do E4. O A1 fica fora desse aceite.
- Ferramentas: leitura estática do diff e sonda local com o próprio `forge-check` num repositório descartável em `$TMPDIR`. Não há dependência, segredo nem workflow no diff; `gitleaks`, `osv-scanner`, `zizmor` e `actionlint` não se aplicam a este lote.
