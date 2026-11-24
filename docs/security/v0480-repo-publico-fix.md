---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 1265fa11ec5e75d16df8402d32664fd2d683538e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0480-repo-publico-fix (PR #829, volta E141.7, v0478 E141.9)

Revalidação por delta. `forge-check parecer delta`: intervalo `2806ca57..1265fa11`; no domínio, `hooks/conformidade.py` (lido inteiro no trecho do diff: constantes :331 a :346, `gh_trava` :3382, `api_publica` e auxiliares :3412 a :3505) e as 34 fixtures novas; fora do domínio, mutantes, `docs/hooks-fixtures.md` e o fragmento do changelog. A rodada anterior fica no git (`b1f93153`). Método igual: o hook desta cópia rodado direto com o JSON de PreToolUse num projeto descartável (branch `feature/x`), `PATH=/usr/bin:/bin`, o gh nunca executado e nada tocou o GitHub; papéis `forge:node-backend`, `forge:tech-lead` e sessão principal, mesmo resultado nos três. Para comparar, a base `216413c9` e o head anterior `2806ca57` rodados igual, de cópias por `git archive`.

**Só aperta ou neutro: sim, contra a base.** `gh_trava` mantém as recusas da base (`VISIBILIDADE_PUBLICA` sobre os argumentos e `input_publica`, :3407) e o resto é um `self.barrar` a mais. Contra o head anterior `2806ca57` há uma perda (A7): o GraphQL agora tira os comentários antes da busca, e uma forma que `2806ca57` barrava passa.

**Sondas S8 a S15 refeitas no head:** todas saem 2 com `R-CONFORMIDADE: tornar o repositório público` nos três papéis; `gh repo new novo` (sem visibilidade) também 2. Legítimas: `gh repo new novo --private`, `gh api user/repos -f name=novo -f private=true`, a mutação por variável com `-F 'i[visibility]=PRIVATE'`, `PATCH ... -f private=true` e `-f description=ok` saem 0. Corpus REST fora do repositório (`POST repos/o/r/issues`, `PATCH .../issues/1`, comentário com barra final) segue 0. Corpo `--input` com JSON inválido ou com comentário sai 2 (falha fechado).

**A5 REST fora: com razão.** `-f 'description=$HOME'` no PATCH segue 2 (:3429). Liberar exige que o leitor único `textos_do_gh_api` saiba a citação do shell, e a expansão sem aspas vira outros campos (o próprio GraphQL falha fechado nisso, :3491): não é barato nem neutro, como o brief da volta pedia. O comportamento falha fechado; o custo é de uso. A mensagem que aponta "tornar público" para um valor ilegível fica como cartão (abaixo), sem bloquear.

**`gh api graphql -f query="$Q"` com a mutação inteira na variável:** confirmado, sai 0 na base, em `2806ca57` e no head. É cartão novo, não bloqueante deste item: não é regressão do PR, o texto da consulta não existe para o hook (o mesmo limite de `python -c`, `curl` com o token e qualquer outro cliente), e fechar exige recusar toda mutação GraphQL com a consulta ilegível, uma política com custo em uso legítimo que é decisão do dono (`R-DECISAO`). A garantia de fundo segue o token sem o escopo de criar repositório.

Suíte: rodado só `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` (OK, 1 teste, 7,6 s). O CI do PR estava em curso na leitura (suíte pendente; `bateria (pareceres)` e `catraca` vermelhos); o parecer reprova pela sonda S16, sem depender dele.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), exposição de código e histórico, ação irreversível no GitHub.

## Achados
- A7 (bloqueante) hooks/conformidade.py:345 · GRAPHQL_SEM_TEXTO termina o comentário só no LF; o GraphQL termina também no CR. `visibility:#c<CR>PUBLIC` com `PRIVATE:` como alias na linha seguinte cria público e sai 0 (S16); `2806ca57` barrava. O BOM entre a chave e o `:` também passa (S17).

## Sondas
- S16 · forge:node-backend, Bash, `<CR>` é o CR cru e `<LF>` o LF: `gh api graphql -f query='mutation { createRepository(input:{name:"n", visibility:#c<CR>PUBLIC}) {<LF>PRIVATE: clientMutationId } }'` · espera: saída 2 · obtido: saída 0
- S17 · forge:node-backend, Bash, `<BOM>` é o U+FEFF cru: `gh api graphql -f query='mutation { a: createRepository(input:{name:"a", visibility:PRIVATE}) { clientMutationId } b: createRepository(input:{name:"b", visibility<BOM>:PUBLIC}) { clientMutationId } }'` · espera: saída 2 · obtido: saída 0

## Detalhe dos achados
**Estado dos anteriores.** A1 (`repo new`): fechado, S8 sai 2 (`REPO_CRIAR`, :333; fixtures `trava-repo-new-*`). A2 (isca em outro campo): fechado, S9 e S10 saem 2 (decisão por campo, `privado_rest`). A3 (opção colada): fechado, S11 e S12 saem 2 (`CAMPO_COLADO`, :334). A4 (GraphQL por texto): S13 a S15 saem 2, mas a família reabre pela A7. A5: GraphQL fechado (`i[visibility]=PRIVATE` sai 0); REST fora com razão, acima. A6 (endpoint não canônico): fechado, `user//repos`, `user/./repos` e `user/x/../repos` saem 2 (`API_SEGMENTO_ESTRANHO`, :338).

**A7: comentário GraphQL que termina no CR.** Evidência: `GRAPHQL_SEM_TEXTO` (:345) usa `#[^\n]*`; na especificação do GraphQL o comentário termina em qualquer LineTerminator, e o CR sozinho é um. O hook apaga de `#c` até o LF, e com ele o `PUBLIC`; a primeira palavra depois do LF vira o valor lido por `GRAPHQL_VISIBILIDADE` (:346, :3495), e um alias `PRIVATE:` no campo de retorno satisfaz a checagem. A busca da base (`VISIBILIDADE_PUBLICA`, :3407) não vê `visibility:#c`. O mesmo vale para o BOM (U+FEFF), ignorado pelo GraphQL e fora do `\s` do hook: `visibility<BOM>:PUBLIC` não casa a chave, e um segundo `createRepository` privado na mesma mutação dá o valor lido. O lado do servidor não foi sondado (sem rede); a prova é o hook mais a especificação. Caminho de ataque: o da A1 do diagnóstico, um agente por erro ou instrução injetada que já conhece a trava cria o repositório público pela mutação literal. Severidade alta. Correção mínima: em `graphql_publica`, com `createRepository`, `cloneTemplateRepository` ou `updateRepository` no texto, falhar fechado se a consulta tiver CR, BOM ou outro caractere de controle fora do LF e do TAB; e, por consistência, o comentário em `#[^\r\n]*`. Fixtures: S16 e S17 como `-bloqueia`, e a mesma mutação com LF no lugar do CR (já sai 2) como controle. Dimensão nova da matriz do analisador: os caracteres que o GraphQL ignora ou trata como fim de linha (CR, CRLF, BOM). Esforço P. Dono: o autor do E141.7.

**Cartões (não bloqueiam este item).** C1: `gh api graphql -f query="$Q"` com a mutação inteira na variável passa desde a base; decidir com o dono se toda mutação GraphQL com a consulta ilegível falha fechado (dono do hook, decisão `R-DECISAO`). C2: a recusa por valor que o hook não lê (:3429) diz "tornar o repositório público"; trocar pela causa real (valor ilegível).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o hook rodado localmente com Python e projetos descartáveis; a base e o head anterior por `git archive`; o gh fora do PATH das sondas e nunca executado. gitleaks, semgrep e zizmor não foram usados (não se aplicam a este diff).
