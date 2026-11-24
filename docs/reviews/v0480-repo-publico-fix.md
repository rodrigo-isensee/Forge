---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 708c4bb09a6c74716b6897d37a2319575ae591b3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0480-repo-publico-fix (CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E141.12)

Revalidação por delta do PR #829 no head `708c4bb0` (2ª volta, E141.11), contra o parecer reprovado no head `1265fa11`. Delta lido: `forge-check parecer delta docs/reviews/v0480-repo-publico-fix.md` (revalida: sim, este parecer barrou) e `git diff 1265fa11 708c4bb0`: `hooks/conformidade.py` +10 −3, oito fixtures `trava-graphql-*`, mutantes em `-4.json`, `-6.json` e `-7.json` novo (RP49 a RP51), mínimo do teste de 57 para 65.

## Achados
- A1 (recomendado) hooks/conformidade.py:348 · o CR está nas duas guardas (classe de controle, linha 348, e fim do comentário, linha 347), e cada uma sozinha cobre a outra: o mutante de cada linha sobrevive e só o par morre. Declarar um mutante que tire o CR das duas, para a mutação provar o par.

## Sondas
- S1 · `gh api graphql -F query=@q.graphql`, q = `mutation{createRepository(input:{name:"x", description:"""z\\""" visibility:PRIVATE """, visibility:PUBLIC # """` + LF + `}){repository{id}}}` · espera: saída 2 · obtido: saída 2 (no 1265fa11: 0)
- S2 · `gh api graphql -F query=@q.graphql -f z[visibility]=PRIVATE`, q = `mutation{createRepository(input:{name:"x" #c` + CR + `visibility:PUBLIC` + LF + `}){repository{id}}}` · espera: saída 2 · obtido: saída 2 (no 1265fa11: 0)
- S3 · mutante só da linha 347 (`#[^\n]*`) e só da 348 (sem `\x0d`) · espera: um deles morre · obtido: os dois sobrevivem ao `test_fixtures_do_repo_publico`; com os dois juntos, `trava-graphql-comentario-cr-bloqueia` falha (o par morre)

## Parecer
**Aprovado.** Os dois achados do parecer anterior estão fechados no delta; nenhum bloqueante novo.

**A1 anterior (léxico do GraphQL):** fechado. O bloco `"""` agora só aceita `\"""` como escape (BlockStringCharacter da especificação), o comentário fecha no LF ou no CR, e CR, BOM e os demais controles (fora TAB e LF) na query falham fechado antes da leitura (`GRAPHQL_CONTROLE`, linha 3497). S1 e S2 rerrodadas em cópia do head (`git archive`, mesma montagem das fixtures, `forge:node-backend`): as duas saem 2. Extras na mesma rodada: `"""a""""` (quatro aspas fecham no primeiro trio, como o lexer) com `visibility:PUBLIC` depois sai 2; `"""a \""" b"""` com `visibility:PRIVATE` sai 0, sem falso positivo.

**A2 anterior (variável não declarada):** fechado. `usados` só conta o `<var>[visibility]` cuja variável aparece na consulta (linha 3502), e todo `[visibility]` público continua barrando (`publica` lê `da_var` inteiro). `createRepository(input:$z)` com `-f z[visibility]=PRIVATE` sai 0. Limite visto, sem dano: variável usada fora do `input` (`viewer(f:$z)`) e `createRepository` sem `visibility` sai 0; o `visibility` do `CreateRepositoryInput` é obrigatório no servidor, então a mutação falha lá sem criar repositório. Não vira achado.

**Mutantes do CR (pergunta do brief):** concordo em parte. As duas guardas se cobrem de fato (S3): CR barrado na 348 nunca chega ao regex da 347, e sem a 348 a 347 lê o comentário certo. Por isso um mutante por linha seria equivalente, e a falta deles não bloqueia. Mas a catraca não prova o par hoje: um mutante que tire o CR das duas mataria `trava-graphql-comentario-cr-bloqueia` (A1, recomendado). RP49 (bloco), RP50 (variável da consulta), RP51 (criar sem visibilidade lida) e RP30 refeito cobrem as outras linhas mudadas; não rerrodei a mutação do autor.

**Teto H1:** `hooks/conformidade.py` soma 127 linhas de código no item contra a base `216413c9` (`git diff --numstat`), dentro de 150; o resto são fixtures, mutantes e teste.

**Ferramentas (citadas, não refeitas):** teste do item `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` rodado no head com ambiente limpo: as 65 fixtures do item passam. CI do PR #829 no head `708c4bb0`: `bateria (passos)`, `instalação (python 3.14)` e `árvore já provada na develop` verdes; suíte 3.12 e 3.14 e `bateria (verificações longas)` pendentes; `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres. Suíte inteira não rodada (fica no CI). O merge segue o CI verde e os pareceres de QA e segurança no mesmo head.
