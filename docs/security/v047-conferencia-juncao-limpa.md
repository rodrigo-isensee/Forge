---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-juncao-limpa
commit: 1477a480d39ff926143246c5c0ed1c72d2e71bfd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-conferencia-juncao-limpa

Revalidação por delta no head `1477a480` (v047 E2.347), lida em `forge-check parecer delta` sobre `d093ee81..1477a480`: no domínio só `bin/forge-check` (`juncao_limpa`, a correção de A1); fora dele, o teste do segundo pai ancorado fora da base, o teste dos atributos e os mutantes. A1 corrigido; sem bloqueante.

Parecer original: completo, do intervalo `d4b5dac6..d093ee81` (v047 E2.330): `bin/forge-check` (`juncao_limpa` e o ramo novo em `linhas_de_entrega`, as âncoras passadas por `cmd_entrega_conferir`), o fragmento do changelog, os mutantes J1 a J5 e a classe `JuncaoLimpa`. Pergunta do pedido: a regra nova deixa passar merge com mudança à mão? Não.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): a conferência de entrega é o portão que grava `entrega conferida`; a regra nova troca um `pendente` (reprova) por cumprido. Afrouxamento de controle, por isso o portão.

## Achados
- A2 (recomendado) bin/forge-check:2483 · resíduo de A1: com --attr-source o merge-tree ainda lê .git/info/attributes e o arquivo global de atributos (sonda: merge=union neles torna limpo o conflito); -c core.attributesFile=/dev/null tira o global; o info/attributes pede escrita no .git

## Sondas

## Detalhe dos achados
Por que a regra fecha (análise do grafo, `bin/forge-check:2469-2487`): o ramo novo só corre com `arquivos` vazio, sem `falhas`, com o `valido` numa linha `entrega conferida` da forma da ferramenta e com `juncao_limpa` verdadeira. Esta exige, para cada commit do primeiro pai de `valido..head`: dois pais exatos, o segundo ancestral da `origin/<base>` e de um Base-sha selado (a ref local sozinha não basta, mesma âncora da Volta 1 A2 do `ponto_da_integracao`), e a árvore do commit igual, por hash, à do `git merge-tree --write-tree` dos dois pais (conflito sai com código 1 e recusa). Como o `valido` precisa ser ancestral do head e nenhum segundo pai o alcança (todos estão na base), o `valido` está no próprio caminho do primeiro pai: o laço confere exatamente os commits entre ele e o head, e todo o resto do grafo é da base ancorada. Qualquer byte à mão no merge muda a árvore e recusa; falha do git, base ausente ou lista de âncoras vazia recusam. O `cmd_entrega` sem `--pedido` não passa âncoras, então o ramo novo nunca cumpre fora da conferência.

Sondas do parecer original (repositório descartável no TMPDIR, chamando `juncao_limpa` direto): merge limpo da develop → True; merge com uma linha mudada à mão num arquivo do autor → False; merge limpo seguido de commit comum → False; `merge -s ours` → False; âncora anterior ao segundo pai → False. Nenhuma prova bloqueante, por isso o bloco `## Sondas` fica vazio.

A1 (parecer em `d093ee81`, recomendado): o `merge-tree` lia o `.gitattributes` da árvore de trabalho da raiz, e `merge=union` tornava limpo um conflito. Corrigido em `bin/forge-check:2476-2484`: a árvore vazia vem de `git hash-object -t tree /dev/null` (só calcula, não grava; o git conhece o objeto mesmo fora do banco) e entra como `--attr-source` no `merge-tree`. Sondas da revalidação (repositório descartável no TMPDIR, git 2.43): `.gitattributes` não versionado com `f merge=union` e conflito de linha → sem a opção rc=0, com a árvore vazia rc=1; `--attr-source=` vazio (o caso de falha do `hash-object`) → rc=128, recusa; git anterior à opção também falha e recusa. Fecha na dúvida. O comentário do mutante Q3 (o `cod or` redundante) confere: o conflito escreve árvore com marcadores, de hash diferente da commitada. O teste novo do segundo pai ancorado num Base-sha mas fora da `base_ref` recusa, como pede a guarda.

A2, evidência `bin/forge-check:2483`; sondas: com a árvore vazia, `f merge=union` em `.git/info/attributes` → rc=0, e no arquivo global de atributos (`$XDG_CONFIG_HOME/git/attributes`) → rc=0. Caminho de ataque: o mesmo de A1, agora só por arquivos fora da árvore de trabalho (o global está em sistema de arquivos só leitura no sandbox; o `info/attributes` pede escrita na pasta do git da raiz). Severidade informativa: a união só junta linhas dos dois pais, sem conteúdo novo, e quem escreve ali já tem caminhos mais curtos. Correção mínima: `git -c core.attributesFile=/dev/null --attr-source=<vazia> merge-tree ...` (o `info/attributes` não tem opção que o desligue; fica como resíduo). Esforço P. Dono: tech-lead.

Custo: um `hash-object` por chamada e um `merge-tree` por commit do primeiro pai, cada um com o limite de tempo do `git()`; sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item rodados na raiz do clone no head `1477a480`: `python3 -m unittest tests.test_selo_e_entrega.JuncaoLimpa` → 9 testes OK em 31 s (inclui os dois novos: segundo pai fora da base e `.gitattributes` não versionado, ambos recusam). Suíte inteira: só no CI do PR, que ainda não existe para esta branch; o merge na develop depende dele verde. Ferramentas: git 2.43 local; varreduras de segredo e de workflow não se aplicam ao intervalo (sem workflow nem credencial tocados).
