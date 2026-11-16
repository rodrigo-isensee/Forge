---
tipo: revisao-seguranca
contrato: 1
pedido: v047-conferencia-juncao-limpa
branch: melhoria/v047-conferencia-juncao-limpa
commit: d093ee8109b461d2521ba58f54b6211570800141
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-conferencia-juncao-limpa

Parecer completo (não havia parecer anterior) do intervalo `d4b5dac6..d093ee81` (v047 E2.330): `bin/forge-check` (`juncao_limpa` e o ramo novo em `linhas_de_entrega`, as âncoras passadas por `cmd_entrega_conferir`), o fragmento do changelog, os mutantes J1 a J5 e a classe `JuncaoLimpa`. Pergunta do pedido: a regra nova deixa passar merge com mudança à mão? Não.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): a conferência de entrega é o portão que grava `entrega conferida`; a regra nova troca um `pendente` (reprova) por cumprido. Afrouxamento de controle, por isso o portão.

## Achados
- A1 (recomendado) bin/forge-check:2480 · o merge-tree da conferência lê o .gitattributes da árvore de trabalho da raiz (sonda: merge=union torna limpo um conflito); só junta linhas dos dois pais, sem conteúdo novo; fixar --attr-source na árvore vazia tira essa entrada

## Sondas

## Detalhe dos achados
Por que a regra fecha (análise do grafo, `bin/forge-check:2469-2483`): o ramo novo (`bin/forge-check:2842`) só corre com `arquivos` vazio, sem `falhas`, com o `valido` numa linha `entrega conferida` da forma da ferramenta e com `juncao_limpa` verdadeira. Esta exige, para cada commit do primeiro pai de `valido..head`: dois pais exatos, o segundo ancestral da `origin/<base>` e de um Base-sha selado (a ref local sozinha não basta, mesma âncora da Volta 1 A2 do `ponto_da_integracao`), e a árvore do commit igual, por hash, à do `git merge-tree --write-tree` dos dois pais (conflito sai com código 1 e recusa). Como o `valido` precisa ser ancestral do head e nenhum segundo pai o alcança (todos estão na base), o `valido` está no próprio caminho do primeiro pai: o laço confere exatamente os commits entre ele e o head, e todo o resto do grafo é da base ancorada. Qualquer byte à mão no merge muda a árvore e recusa; falha do git, base ausente ou lista de âncoras vazia recusam. O `cmd_entrega` sem `--pedido` não passa âncoras, então o ramo novo nunca cumpre fora da conferência.

Sondas executadas (repositório descartável no TMPDIR, chamando `juncao_limpa` direto): merge limpo da develop → True; merge com uma linha mudada à mão num arquivo do autor → False; merge limpo seguido de commit comum → False; `merge -s ours` → False; âncora anterior ao segundo pai → False. Todas como esperado; nenhuma prova bloqueante, por isso o bloco `## Sondas` fica vazio.

A1, evidência `bin/forge-check:2480`; sonda: com `f merge=union` no `.gitattributes` não versionado da árvore de trabalho (ou em `.git/info/attributes`), um conflito de linha vira `merge-tree` rc=0; o mesmo atributo só no commit do autor não muda nada (rc=1). Caminho de ataque: quem escreve na árvore de trabalho da raiz onde o Jarvis roda a conferência resolve um conflito pela união e a conferência aceita. Severidade baixa: a união só tem linhas dos dois pais (sem conteúdo novo), o driver de merge próprio exige `.git/config` (protegido, ADR 0009) e quem escreve nessa árvore já tem caminhos mais curtos; os portões seguem lendo o head. Correção mínima: `git --attr-source=<árvore vazia> merge-tree ...` (sonda: com a árvore vazia o conflito volta a rc=1; o `.git/info/attributes` segue lido). Esforço P. Dono: tech-lead.

Custo: um `merge-tree` por commit do primeiro pai, cada um com o limite de tempo do `git()`; sem achado (o laço para no primeiro commit que recusa).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item rodados na raiz do clone: `python3 -m unittest tests.test_selo_e_entrega.JuncaoLimpa tests.test_selo_e_entrega.MergeDaBaseDepoisDoBrief` → 15 testes OK em 58 s. Suíte inteira: só no CI do PR, que ainda não existe para esta branch (o PR vem depois dos pareceres); o merge na develop depende dele verde. Ferramentas: git 2.43 local; varreduras de segredo e de workflow não se aplicam ao intervalo (sem workflow nem credencial tocados).
