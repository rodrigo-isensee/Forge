---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 2806ca57ea41a48ea3e5ecaf1bda785b3f8c8dcb
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0480-repo-publico-fix (PR #829, CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E141.4)

Revisão do commit `2806ca57` (E141.2) contra o diagnóstico `docs/security/v0480-repo-publico-diag.md` (E141.1, branch `melhoria/v0480-repo-publico-diag`). Método igual ao do diagnóstico: `hooks/conformidade.py` desta cópia rodado direto com o JSON de PreToolUse, `CLAUDE_PROJECT_DIR` e `cwd` num projeto descartável com `.forge/versao` (git, branch `feature/x`), `PATH=/usr/bin:/bin`; o gh nunca foi executado e nada tocou o GitHub. Papéis: `forge:node-backend`, `forge:tech-lead` e sessão principal, com o mesmo resultado nos três. Saída 2 = barrado, 0 = passa. Cerca de 230 formas no total.

**Só aperta: sim.** O diff de `hooks/conformidade.py` só acrescenta constantes (:332 a :341), o ramo `repo create` (:3392) e uma chamada `self.barrar` a mais no ramo `api` (:3404, `api_publica` em :3407); nenhuma condição de recusa existente foi removida nem trocada, e as 8 formas que o diagnóstico já via barradas seguem barradas (1, 2, 10, 11, 13, 18, 19, 24). O custo do aperto está em A5.

**Formas do diagnóstico:** as 18 formas de criar ou tornar público no projeto (3 a 7, 9 a 20, mais as de controle) agora saem 2; a 8 (`--private`, legítima) sai 0. S1 a S7 refeitas: todas 2 com `R-CONFORMIDADE: tornar o repositório público`. Seguem abertas, fora do escopo por decisão registrada no commit (ficam com o dono): A3 do diagnóstico (formas 21 a 23, gist público, saída 0) e A4 (sessão do Forge: `gh repo create novo --public` e `gh api user/repos -f name=novo` saem 0 em `forge:tech-lead`).

**Resposta: ainda há formas novas que criam ou tornam público e passam**, quatro famílias, todas no próprio alvo da correção (A1 e A2 do diagnóstico).

Suíte: rodado só `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` (OK, 1 teste, 6,4 s). O CI do PR não foi conferido aqui (o brief proíbe rodar o gh); o parecer reprova pelas sondas, sem depender dele.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), exposição de código e histórico, ação irreversível no GitHub.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3392 · `gh repo new` (alias do gh para `repo create`) cai fora do ramo: `gh repo new novo --public` e `gh repo new novo` saem 0 nos três papéis; a criação pública com `--source . --push` segue aberta (S8).
- A2 (bloqueante) hooks/conformidade.py:3429 · VISIBILIDADE_PRIVADA procura `private=true` em qualquer texto, não no campo: `-f description=private=true`, `-F x=private=true`, `homepage=...?private=true` e `--input` com a isca no description criam público e passam (S9, S10).
- A3 (bloqueante) hooks/conformidade.py:328 · opção curta com o valor colado: `-Fprivate=false`, `-fvisibility=public`, `-Fvisibility=@v.txt` passam (o `\b` falha entre `F` e `p`); torna público o repositório existente pelo PATCH (S11, S12).
- A4 (bloqueante) hooks/conformidade.py:341 · GraphQL por texto: a isca `visibility:PRIVATE` num description, comentário ou outro campo satisfaz GRAPHQL_PRIVADA, e `i[visibility]=PUBLIC` ou `visibility,:PUBLIC` não casa GRAPHQL_NAO_PRIVADA; createRepository e cloneTemplateRepository públicos passam (S13 a S15).
- A5 (recomendado) hooks/conformidade.py:3425 · custo do aperto em legítimos: `-F 'i[visibility]=PRIVATE'` no GraphQL barra; `-f 'description=$HOME'` (aspas simples, literal) e `homepage='https://x.dev/$a'` no PATCH do repositório barram como público; o texto da recusa engana.
- A6 (recomendado) hooks/conformidade.py:3421 · endpoint com segmento vazio ou de ponto (`user//repos`, `user/./repos`, `user/x/../repos`) não casa API_CRIA_REPO e passa sem visibilidade; o servidor não foi sondado (sem rede), então falhe fechado em mutante com `//`, `/./` ou `/../`.

## Sondas
- S8 · projeto, forge:node-backend, Bash `gh repo new novo --public` · espera: saída 2, R-CONFORMIDADE tornar o repositório público · obtido: saída 0, sem mensagem
- S9 · projeto, forge:node-backend, Bash `gh api user/repos -f name=novo -f description=private=true` · espera: saída 2 (sem campo private, padrão público) · obtido: saída 0
- S10 · projeto, forge:node-backend, Bash `gh api user/repos --input isca.json` (isca.json: {"name":"novo","description":"private: true"}) · espera: saída 2 · obtido: saída 0
- S11 · projeto, forge:node-backend, Bash `gh api -X PATCH repos/dono/proj -Fprivate=false` · espera: saída 2 · obtido: saída 0
- S12 · projeto, forge:node-backend, Bash `gh api -X PATCH repos/dono/proj -fvisibility=public` · espera: saída 2 · obtido: saída 0
- S13 · projeto, forge:node-backend, Bash `gh api graphql -f query='mutation($i: CreateRepositoryInput!) { createRepository(input:$i) { clientMutationId } }' -F 'i[name]=n' -F 'i[visibility]=PUBLIC' -F 'i[description]=visibility:PRIVATE'` · espera: saída 2 · obtido: saída 0
- S14 · projeto, forge:node-backend, Bash `gh api graphql -f query='mutation($i: CreateRepositoryInput!) { createRepository(input:$i) { clientMutationId } } # visibility:PRIVATE' -F 'i[name]=n' -F 'i[visibility]=PUBLIC'` · espera: saída 2 · obtido: saída 0
- S15 · projeto, forge:node-backend, Bash `gh api graphql -f query='mutation { createRepository(input:{name:"n", visibility,:PUBLIC, description:"visibility:PRIVATE"}) { clientMutationId } }'` · espera: saída 2 · obtido: saída 0

## Detalhe dos achados
**A1: alias `repo new`.** Evidência: o ramo novo testa `sub == "create"` (:3392) e `gh_trava` não resolve aliases embutidos do gh (o `repo create` declara o alias `new` no próprio comando, documentado no manual do gh; não conferido rodando o gh, por ordem do brief). Caminho de ataque: o mesmo da A1 do diagnóstico, um agente por erro ou instrução injetada roda `gh repo new <conta>/<nome> --public --source . --push` e publica o histórico. Severidade alta. Correção mínima: tratar `sub in ("create", "new")` no ramo de `repo` (e, por consistência, os aliases embutidos dos outros ramos de `gh_trava`); fixtures `trava-repo-new-*` com `--public`, sem visibilidade, e `--private` como legítima. Esforço P. Dono: o autor do E141.2.

**A2: isca no texto de outro campo (REST).** Evidência: `api_publica` aplica `VISIBILIDADE_PRIVADA.search` (:332) a cada texto inteiro (:3429), inclusive ao argumento `-f description=private=true`, ao corpo JSON de `--input` e ao texto de arquivo; o `\b` casa no meio do valor. O gh envia `description` e nenhum `private`, e a API cria público. Caminho de ataque: igual à A1; a forma é natural para instrução injetada que já conhece a trava. Severidade alta. Correção mínima: decidir por campo, não por texto: separar cada `-f/-F/--field/--raw-field` em `chave=valor` (com o valor de `@arq` lido) e exigir chave exatamente `private` com valor `true`, ou `visibility` com `private|internal`; no `--input`, ler o JSON e olhar só as chaves de topo `private` e `visibility`. Esforço M. Dono: o autor do E141.2.

**A3: `-Fcampo=valor` colado.** Evidência: o pflag do gh aceita a opção curta com o valor colado (`-Fprivate=false` = `-F private=false`); `VISIBILIDADE_PUBLICA` (:328) exige `\b` antes de `private`/`visibility`, que não existe entre `F` e `p`, e `desagrupa_i` (`hooks/parecer.py:886`) só separa o `-i`. Também `-Fvisibility=@v.txt` (arquivo com `public`): o texto sintetizado em :3428 herda o `-F`. É anterior ao PR para o PATCH, mas está na família que o PR diz fechar ("criar e editar recusam o público"). Severidade alta. Correção mínima: normalizar `-F<x>`, `-f<x>` e `--field=<x>`/`--raw-field=<x>` para a forma separada antes de qualquer busca (a mesma normalização serve à A2). Esforço P. Dono: o autor do E141.2.

**A4: GraphQL por regex no texto.** Evidência: `GRAPHQL_PRIVADA` (:340) casa em qualquer lugar do texto juntado (:3415), inclusive dentro de string, comentário `#` ou outro campo; `GRAPHQL_NAO_PRIVADA` (:341) só casa `visibility` seguido de `:`, e não vê o campo da variável de entrada `i[visibility]=PUBLIC` nem a vírgula, que no GraphQL é separador ignorado (`visibility,:PUBLIC`). Também passam o comentário `# visibility:PRIVATE` com o input em variável (S14) e o `cloneTemplateRepository` com as mesmas iscas. Severidade alta. Correção mínima: no GraphQL, com `createRepository`, `cloneTemplateRepository` ou `updateRepository` no texto, falhar fechado sempre que o input vier por variável (`input:$x`) ou o valor de visibility não for um literal lido fora de string e comentário; tirar strings `"..."`/`"""..."""` e comentários `#...` antes da busca e tratar `,` como espaço; nos campos `-F/-f`, chave terminada em `[visibility]` com valor fora de `PRIVATE|INTERNAL` recusa. Esforço M. Dono: o autor do E141.2.

**A5: legítimos barrados.** Evidência: S-legítimas em prosa: `gh api graphql ... createRepository(input:$i) ... -F 'i[name]=n' -F 'i[visibility]=PRIVATE'` sai 2; `gh api -X PATCH repos/dono/proj -f 'description=$HOME'` e `-f homepage='https://x.dev/$a'` saem 2 com "tornar o repositório público" (o `$` entre aspas simples é literal; `textos_do_gh_api` vê `$` e dá ilegível). Sem caminho de ataque; custo de uso e mensagem que aponta a causa errada. Correção mínima: com a decisão por campo da A2, só o campo de visibilidade ilegível falha fechado; a recusa de valor ilegível diz "valor que o hook não lê", não "tornar público". Esforço P.

**A6: endpoint não canônico.** Evidência: `API_CRIA_REPO.fullmatch` (:3421) sobre `endpoint_normalizado`, que não colapsa `//` nem resolve `.`/`..`. Se o servidor da API normalizar o caminho, `gh api user/./repos -f name=novo` cria público. Não provado (sondar o servidor seria tocar o GitHub). Correção mínima: em `gh api` mutante, endpoint com segmento vazio, `.` ou `..` falha fechado. Esforço P.

**Limite do hook** (sem achado, repete o diagnóstico): o Bash é lido como texto; a garantia de fundo é o token do gh sem escopo de criar repositório. As quatro famílias acima mostram por que: cada isca nova é uma regra nova no regex. A correção de A2 a A4 por campo, e não por texto, fecha a família em vez da forma.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o hook rodado localmente com Python e um projeto descartável; o gh fora do PATH das sondas e nunca executado. gitleaks, semgrep e zizmor não foram usados (não se aplicam a este diff).
