---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 708c4bb09a6c74716b6897d37a2319575ae591b3
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0480-repo-publico-fix (PR #829, 2ª volta E141.11, v0478 E141.13)

Revalidação por delta. `forge-check parecer delta`: intervalo `1265fa11..708c4bb0`; no domínio, `hooks/conformidade.py` (constantes :345 a :349 e `graphql_publica` :3488 a :3505, relidos inteiros com `api_publica` e `campos_da_api`), as 8 fixtures novas e `tests/test_hooks.py:3073` (piso de 57 para 65); fora do domínio, mutantes, `docs/hooks-fixtures.md` e o fragmento do changelog. A rodada anterior fica no git (`1d160afd`). Método igual: o hook desta cópia rodado direto com o JSON de PreToolUse num projeto descartável (`.forge/versao`, branch `feature/x`), `PATH=/usr/bin:/bin`, o gh nunca executado e nada tocou o GitHub; papéis `forge:node-backend`, `forge:tech-lead` e sessão principal. Para comparar, a base `216413c9` e o head anterior `1265fa11` por `git archive`, rodados igual.

**Só aperta ou neutro: sim, contra a base e contra `1265fa11`.** No mesmo conjunto de 28 entradas (S8 a S17, 10 novas de ataque e 8 legítimas), toda entrada que a base ou `1265fa11` barram o head também barra; o head barra a mais S16, S17, o comentário no CR por `--input` e por `-F query=@arq`, o `updateRepository` com CR e o NEL (U+0085). O delta só soma recusas: `GRAPHQL_CONTROLE` (:348) retorna antes da busca, o comentário fecha também no CR (:347), e a variável conta todo `<var>[visibility]` na recusa (:3504), exigindo uso na consulta só para o lado que libera (:3502).

**Sondas S8 a S17 refeitas no head:** todas saem 2 com `R-CONFORMIDADE: tornar o repositório público` nos três papéis. Novas que saem 2: CRLF no comentário, `\"""` no bloco escondendo `visibility:PUBLIC` depois dele, variável com valor padrão `PUBLIC`, `variables` com a chave repetida (`PRIVATE` e depois `PUBLIC`). Legítimas que saem 0: literal `visibility:PRIVATE`, a mutação por variável com `-F 'i[visibility]=PRIVATE'`, consulta sem mutação de repositório com CR, `gh repo new novo --private`, REST com `private=true`, issue. O bloco ou comentário que cita `visibility:PUBLIC` com o valor real privado sai 2 também na base (a busca da base, :3407): custo antigo, neutro.

**A7 fechado.** S16 e S17 saem 2 (`GRAPHQL_CONTROLE`, :348); fixtures `trava-graphql-comentario-cr-*`, `trava-graphql-bom-bloqueia` e o controle `-comentario-lf-`.

**Achado novo (A8), dimensão de tempo do analisador.** A busca de strings em `GRAPHQL_SEM_TEXTO` (:347, a alternativa da string comum, igual desde a rodada anterior) é quadrática numa string aberta com muitos `\"`: cada `"` recomeça uma busca até o fim. Com 40 KB o hook passa do prazo de 3 s da decisão e, como a linha não tem o marcador crítico (`CRITICO`, :61), o vigia libera (saída 0, sem mensagem). Já valia em `1265fa11` (mesma saída), então não é regressão do delta; não foi sondado nas rodadas anteriores, falha minha de varredura (o orçamento de tempo e tamanho é dimensão da matriz). Bloqueia porque fura o controle que o PR entrega: S13, que o PR fecha, passa com o lixo à frente.

Suíte: rodado só `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` (OK, 1 teste, 4,4 s). O CI do PR estava em curso na leitura (suíte pendente; `bateria (pareceres)` e `catraca` vermelhos); o parecer reprova pela sonda S18, sem depender dele.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), exposição de código e histórico, ação irreversível no GitHub.

## Achados
- A8 (bloqueante) hooks/conformidade.py:347 · String GraphQL aberta com muitos `\"` deixa a busca quadrática; com 40 KB num `-f query` à frente, o hook passa dos 3 s e, sem marcador crítico na linha (:61), o vigia libera: a mutação com `i[visibility]=PUBLIC` sai 0 (S18). Já valia em 1265fa11.

## Sondas
- S18 · `<L>` = `"` e 20000 `\"` (40 KB): `gh api graphql -f query='<L>' -f query='mutation($i:CreateRepositoryInput!){createRepository(input:$i){clientMutationId}}' -F i[name]=n -F i[visibility]=PUBLIC` · espera: saída 2 · obtido: saída 0 em 3,1 s

## Detalhe dos achados
**Estado dos anteriores.** A1, A2, A3, A6: seguem fechados (S8 a S12 e os endpoints não canônicos saem 2). A4: S13 a S15 saem 2 no tamanho comum; a família reabre só pela A8. A5: como na rodada anterior (GraphQL fechado; REST fora com razão). A7: fechado (acima).

**A8: orçamento de tempo do léxico GraphQL.** Evidência: `GRAPHQL_SEM_TEXTO` (:347), alternativa `"(?:\\.|[^"\\\n])*"`; numa string sem o `"` de fechamento, a busca anda até o fim e falha, e o `sub` recomeça no `"` seguinte. Com `"` mais N vezes `\"`, o custo é da ordem de N² (100 KB levam 30 s só na expressão; 24 KB ainda decidem em 1,9 s e barram). `graphql_publica` roda essa busca (:3499) antes de ler a variável (:3501 a :3504). Com 40 KB o vigia vence em 3 s; `prazo_vencido` (`hooks/_comum.py:2853`) só recusa com o marcador crítico, e `CRITICO` (:61) não cobre `gh api graphql` nem as outras formas de visibilidade, então libera. Controles da mesma medida: o mesmo tamanho com `#` à frente ou só letras decide em 0,2 s e barra; o lixo dentro de `--input` com `PUBLIC` no corpo barra pela busca da base (:3407). Caminho de ataque: o da A1 do diagnóstico, um agente por erro ou instrução injetada que já conhece a trava; o gh manda só o último `query` (os campos vão num mapa; comportamento lido da ferramenta, não executado, sem rede), e o primeiro, que o servidor nunca vê, só serve para gastar o prazo do hook. Severidade alta. Correção mínima, as três juntas: (1) a string comum sem fechamento não recomeça a busca: casar `"(?:\\.|[^"\\\n])*"?` e falhar fechado se a string casada não fecha (a consulta já é inválida, nada legítimo se perde); (2) mais de um `query` entre os campos e o corpo, com `createRepository`, `cloneTemplateRepository` ou `updateRepository` no texto, falha fechado (o hook não sabe qual vai ao servidor); (3) para a dimensão inteira, pôr no marcador crítico (:61) as formas que o `gh_trava` decide sobre visibilidade, todas: `gh repo create`, `gh repo new`, `gh repo edit`, `gh api` com `graphql`, `user/repos`, `orgs/<o>/repos`, `repos/<o>/<r>/generate` e `repos/<o>/<r>` (PATCH ou PUT), para que o prazo vencido recuse. Fixtures: S18 como `-bloqueia` medida sob o prazo de produção (`producao=True`), e o mesmo lixo com `#` à frente como controle. Dimensão nova na matriz do analisador: entrada adversarial de tamanho, por alternativa da expressão. Esforço P. Dono: o autor do E141.11.

**Cartões (não bloqueiam este item).** C1: `gh api graphql -f query="$Q"` com a mutação inteira na variável segue decisão do dono (`R-DECISAO`), fora deste item. C2: a recusa por valor que o hook não lê (:3429) diz "tornar o repositório público"; trocar pela causa real (valor ilegível). C3: criar com `input:$j` sem visibilidade, com `$i` declarado e `i[visibility]=PRIVATE`, sai 0 (a declaração de `$i` satisfaz :3502); sem caminho de ataque, pois o servidor exige `visibility` em `CreateRepositoryInput` e recusa, mas a regra do docstring ("criar sem ele também") não vale aqui; contar só o uso fora da declaração.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o hook rodado localmente com projetos descartáveis; a base e o head anterior por `git archive`; a expressão medida isolada; o gh fora do PATH das sondas e nunca executado. gitleaks, semgrep e zizmor não foram usados (não se aplicam a este diff).
