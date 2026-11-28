# G1 a G3: uma revisão completa só, parecer como status do commit, testes uma vez só

Pedido v0478, etapa E98.1, ORDEM DO DONO de 21/11 22:13 (meta: mediana de 30 min do primeiro commit até a `develop`, P75 até 60 min). Só desenho: nenhum código, teste, hook, workflow nem configuração do GitHub alterado. Público: o dono (seções 6 e 7), o `tech-lead`, o `devops-engineer` e o `security-engineer` (corte da seção 5). Regras citadas só pelo ID. Neutro (`R-NEUTRO`): o desenho vale para o Forge; a extensão aos projetos é decisão do dono (D5).

Base lida: `develop` 2d73a35e. Os números `arquivo:linha` são dessa base.

## 1. O que no código faz o item demorar

Dados do dono (21/11): itens sem volta, 25 a 38 min; 8 itens com 6 a 26 voltas, 4 a 66 h. No código, quatro causas que os três itens atacam:

| # | Causa | Onde está | Item |
|---|---|---|---|
| C1 | Não há teto de voltas: o `brief gerar --volta` só numera a volta e segue (`bin/forge-check:4312`); o `R-QA` aceita até 3 voltas por bug (`docs/regras/R-QA.md:17`). A revalidação pode trazer bloqueante novo em código que não mudou; nada o impede. | `gerar_volta`, `conferir_volta`, `problemas_do_bloco` | G1 |
| C2 | Texto de controle (`agents/`, `skills/`, `templates/projeto/`, `CLAUDE.md`) e teste de controle caem na classe C, com review, QA e segurança (`MD_DE_CONTROLE` em `bin/forge-check:1035`, `TESTE_DE_CONTROLE` em `:1062`, `PARECERES_DA_CLASSE` em `:1066`). | `classe_das_mudancas`, `motivo_de_controle` | G1 |
| C3 | O parecer é um commit na branch. Cada parecer muda o head: o CI roda de novo (o próprio `ci.yml:612-617` diz que o commit do parecer "roda a suíte uma vez a mais"), o outro portão vê o domínio mexer e cresce um aparato só para distinguir commit de parecer de commit de autor: AQ-5 (`commit_de_pareceres_paralelos`), VOLTAS-REVISOR-WT (`pareceres_conferidos`, branches `parecer/<brief>`, linhas `parecer conferido` no Histórico), E23.36, E50.1, E50.5, E50.6, E62.1 e CONFERENCIA-DOIS-PEDIDOS (`bin/forge-check:3056-3170`), QA-TESTE-E-PARECER-SEPARADOS (`:2060-2065`), o gate "commit só de parecer" do CI (`ci.yml:618-647`) e o job `bateria (pareceres)` (`ci.yml:739-777`). O merge usa o `--auto` do GitHub (`bin/forge-fechar:12`, `:860`), que o dono proibiu em 21/11 20:15. | `cmd_pr`, `cmd_entrega`, `ci.yml`, `tests/catraca.py:1833-1893`, `bin/forge-fechar` passo 6 | G2 |
| C4 | O mesmo teste roda várias vezes: o autor roda a mutação e prova o log na entrega (META85-ENTREGA-COM-MUTANTES, `bin/forge-check:3404-3424`); o QA roda a mesma mutação e o `forge-testes --vermelho` e cola a saída (`agents/qa-engineer.md:17`, `:21`); o parecer aprovado exige CI verde ou a linha `- suíte:` (PARECER-SO-COM-CI-VERDE, `:2101-2144`); e o CI roda de novo a cada commit de parecer (C3). | `provas_da_entrega`, `suite_do_parecer`, textos dos agentes | G3 |

## 2. G1: uma revisão completa só

### O que muda
1. **Teto de voltas.** Desenho original (21/11): no máximo 1 volta; o `brief gerar --volta` recusa a volta 2 e manda levar ao dono (`R-DECISAO`) com três opções (cortar e reabrir menor; aceitar com cartão, só sem bloqueante de segurança; autorizar mais uma volta pela linha `DECISÃO DO DONO` que cita a branch, lida por `decisoes_cobradas`); o `conferir_volta` recusa o brief que contorna a numeração. Foi o que entrou no G1.1 (#789). **Regra atual do dono** (22/11 07:23, reafirmada na ORDEM DO DONO de 23/11 14:24): a 2.ª volta sem perguntar; a 3.ª também, desde que corrija só o que o portão apontou, não mude a lógica e não afrouxe nenhum teste, registrada na métrica do item; se a 3.ª falhar, cortar o item e reabrir menor, sem perguntar. A ferramenta e o `R-QA` ainda dizem 1 volta; alinhá-los à regra atual é item próprio, fora deste desenho. CI vermelho e conflito com a base não contam como volta de portão: entram no mesmo brief de volta, como hoje (`autor-ate-o-merge.md`).
2. **Revalidação só no que mudou.** Numa revalidação (existe parecer anterior do mesmo tipo e branch com outro `commit:`), cada achado `bloqueante` precisa estar num trecho mudado entre o `commit:` anterior e o atual (os hunks do `parecer delta`, com margem de 3 linhas) ou repetir um bloqueante da rodada anterior ainda não resolvido. Fora disso, a ferramenta recusa o parecer com o motivo "achado novo fora do que mudou: vira recomendado e cartão". Exceção única: parecer de segurança com a marca `explorável:` no achado e a sonda `S<n>` em `## Sondas` (formato PAR-P1 que já existe) provando o caminho de ataque no ambiente real. O parecer anterior vem da versão anterior do arquivo na branch enquanto o G2 não entra, e do status anterior do mesmo contexto depois dele (seção 3).
3. **Primeira rodada completa.** Texto nos três agentes de portão: a primeira rodada lista todos os achados, porque a segunda não pode mais acrescentar. A medida sai de graça da regra 2: achado recusado por estar fora do delta conta como "faltou na primeira rodada" (o `agile-coach` soma por semana, junto das voltas por item, decisão do dono de 20:54).
4. **Item só de texto ou só de teste tem um parecer só, o review.** A classe T passa a cobrir: (a) diff só de `.md`, em qualquer pasta, inclusive `agents/`, `skills/`, `stacks/*/agents|skills`, `templates/projeto/` e `CLAUDE.md`; (b) diff só de testes, inclusive os de controle (`tests/test_hooks*`, `tests/test_catraca*` e os da lista `TESTE_DE_CONTROLE`). Ficam fora da T: `docs/regras/` e o resto de `CONTROLES_DO_FORGE` (gatilho explícito do `R-SEGURANCA`; ver D2), código de controle que mora em `tests/` (`tests/catraca.py`, `tests/neutralidade.py`, `tests/guarda_git.py`), `tests/config.json`, `.json` de configuração e qualquer gatilho de segurança. A catraca continua medindo enfraquecimento de teste (`regra_testes_enfraquecidos`, `regra_controles_enfraquecidos`), sem depender de parecer.

### Arquivos e funções
- `bin/forge-check`: `gerar_volta` e `conferir_volta` (teto); uma função nova de "achados fora do delta" chamada onde o bloco `## Achados` é validado (`problemas_do_bloco` e o caminho do `pr`); `classe_das_mudancas`, `motivo_de_controle` e `isencoes_do_diff` (a isenção M13 de QA fica contida na T e sai).
- `hooks/parecer.py`: só a docstring e a mensagem que hoje dizem ".md de controle não tem isenção" (`:13`).
- `docs/regras/R-REVIEW.md`, `R-QA.md` (linha 17: 3 voltas por 1; linha 14 já diz que documentação não passa por QA), `R-SEGURANCA.md` (linha 17: o recomendado novo fora do delta vira cartão, salvo `explorável:`); `skills/briefs-e-conferencia/autor-ate-o-merge.md`; `skills/engineering-practices/rigor-por-classe.md`; `agents/tech-lead.md`, `qa-engineer.md`, `security-engineer.md` (uma frase cada).
- Testes: `tests/test_classe_risco.py`, os módulos de `forge-check` que cobrem volta e achados, e as specs de mutante das guardas mudadas.

### O que sai ou simplifica
- Sai: a 2.ª e a 3.ª volta por bug do `R-QA`; o bloqueante novo fora do delta; o QA e a segurança em item só de texto de agente ou skill e em item só de teste; a isenção M13 (`isencoes_do_diff`), absorvida pela T.
- Trava nova: o teto de voltas e a recusa do achado fora do delta. Saem no lugar: o caminho de "volta sem fim" e a isenção M13. Nenhuma conferência nova no envio, no hook ou no CI.

### Riscos
- **Defeito causado pelo delta mas visível fora dele** (o conserto quebra um chamador que não mudou). Mitigação: o achado cita a linha mudada que causa o defeito, que está no delta; a regra é sobre a linha citada, não sobre onde o sintoma aparece.
- **Bug real vira cartão** e escapa até o cartão sair. Critério de reversão: 2 escapes (`forge-check escape registrar`) em 14 dias cuja origem é achado rebaixado pela regra 2.
- **Texto de agente ou skill sem segurança** pode mudar comportamento do time (é instrução). Mitigação: o review continua, a catraca de invariantes continua, e `docs/regras/` segue com segurança. Critério de reversão: 1 escape de segurança em item T de texto de controle.

## 3. G2: parecer como status do commit, fora da branch

### O que muda
1. **O autor abre o PR em rascunho no primeiro envio** (`gh pr create --draft`, que o hook `parecer` já deixa passar sem parecer). O CI e a catraca rodam nesse envio. O Jarvis dispara os portões logo depois da entrega conferida, sem esperar o CI: os portões e o CI correm juntos no mesmo head.
2. **Cada portão grava o parecer como status do commit**, sem commit na branch. O texto continua sendo o mesmo documento de hoje (frontmatter da ADR 0004, `## Achados`, `## Sondas`), escrito pelo papel com a ferramenta Write num caminho fora do git da cópia: `.forge/pareceres/<pedido>/<tipo>.md` (o `/.forge` já é ignorado no `.gitignore`). A regra de caminho por papel do `hooks/conformidade.json`, que hoje diz quem escreve em `docs/reviews/`, `docs/qa/`, `docs/security/` e `docs/devops/`, passa a valer para esse caminho (uma regra troca de lugar; nenhuma entra a mais).
3. **A ferramenta integra quando o CI e os pareceres estão verdes no mesmo commit**, por merge direto preso ao head (`gh pr merge <branch> --squash --match-head-commit <sha>`, sem `--auto`), nunca pelo merge automático do GitHub (DECISÃO DO DONO 21/11 20:15). Sem o verde, o `forge-fechar` espera até o prazo ou para e diz o que falta.
4. **Commit novo do autor (a volta) não apaga o que vale:** o parecer cujo domínio não mudou é herdado pelo head novo (a regra PARECER-CONTEUDO de hoje, `commit_vale` com o domínio do tipo); o que mudou pede revalidação pelo delta (G1).

### (c) Como o status é gravado
- **API:** `POST /repos/{owner}/{repo}/statuses/{sha}` (commit statuses) com `state` (`success` para `aprovado` e para `riscos-aceitos` com o aceite do usuário; `failure` para `reprovado`), `context`, `description` (até 140 caracteres) e `target_url`. Leitura: `GET /repos/{owner}/{repo}/commits/{sha}/statuses` (lista com o `creator` de cada status, do mais novo ao mais antigo). Grátis (`R-CUSTO`); o `gh` da sessão já fala com a API. Limite do GitHub: 1000 statuses por sha e contexto, longe do uso.
- **Contexto por portão**, lista positiva e fechada, sem barra no nome (o `forge-fechar` separa `workflow/nome` na primeira barra, e um nome com barra repetiria a classe de erro do AR-11): `parecer-review`, `parecer-qa`, `parecer-seguranca`, `parecer-devops`. Mais um **agregado**, `pareceres`: `success` só quando todos os contextos que a classe e os gatilhos do diff exigem (`exigidos_do_pr`, a regra de hoje) estão em `success` no mesmo sha; senão `pending` com a lista do que falta. É o agregado que vai à proteção da `develop` (D3): o GitHub não sabe exigir contexto por classe, a ferramenta sabe.
- **Descrição:** `<veredito> · sha256 <12 hex do texto> · <n> bloqueantes · <n> recomendados`, ou `herdado de <sha7>` na herança.
- **Quem grava:** só a ferramenta. O papel do portão roda `forge-check parecer publicar <arquivo local>` na cópia dele; ela confere o documento (`validar_documento`, bloco de achados, a regra do G1 na revalidação), o registro de autoria do papel (`autoria.jsonl`, o mesmo de hoje) e que o `commit:` é o head de um PR aberto da `branch:`; publica o texto como comentário do PR e grava o status com o `target_url` apontando o comentário; recalcula o agregado. A herança é `forge-check parecer herdar --ref <branch>`, rodada pelo passo 1 do `forge-fechar` e pelo Jarvis depois do envio da volta; ela só copia `success` (nunca `failure`) e recalcula o agregado. Ninguém grava status pelo Bash: o agente não ganha comando novo, e a leitura (abaixo) descarta o que não veio da ferramenta.
- **Quem lê:** `forge-check pr` (e, por ele, o hook `parecer` pelo resultado gravado, como hoje, `hooks/parecer.py:786`), o `forge-fechar`, o `brief gerar --volta` e o `forge-check entrega`. A leitura aceita só o status mais novo de cada contexto da lista, com `creator` igual à conta da sessão (lista positiva, AR-3; o `github-actions[bot]` e qualquer outra conta ficam fora), e confere o sha256 da descrição contra o corpo do comentário do `target_url`. Comentário apagado ou editado depois do status: falha fechada, o parecer não vale.
- **Onde fica o código:** um módulo novo, `bin/forge_pareceres.py` (escrita e leitura pela API, nos moldes do `forge_tamanho` que o `forge-check` já carrega), entra em `PROTEGIDOS` de `tests/catraca.py` no mesmo item que o cria: é controle, e não pode ficar fora da proteção que o `bin/forge-check` tem.

### (c) Onde ficam a prova e a auditoria
| O que o parecer commitado guarda hoje | Onde passa a ficar |
|---|---|
| Veredito, tipo e sha revisado | No status do commit (contexto, estado, sha); fica no GitHub depois do merge |
| Texto inteiro: frontmatter, achados, sondas, cenários do QA, bugs abertos | Comentário do PR escrito pela ferramenta; o GitHub mostra o autor, a hora e o histórico de edição; o sha256 na descrição do status prende o texto ao status |
| Quem escreveu (papel) | `autoria.jsonl` da cópia do portão, conferido pela ferramenta antes de publicar (a mesma força de hoje: ver risco R2) |
| Histórico no git da `develop` (o parecer entrava pelo squash) | O `forge-fechar` escreve no corpo do commit de squash uma linha por contexto: `Parecer: <contexto> <estado> <sha7> sha256 <12> <url do comentário>`. O `forge-check metricas`, `voltas` e o `forge-placar` passam a ler essas linhas do `git log` em vez das pastas |
| Voltas e revalidações | A sequência de statuses do mesmo contexto nos heads da branch (`failure` em A, `success` em B) |
| Aceite do usuário para `riscos-aceitos` | Sem mudança: arquivo `docs/security/aceites/<pedido>.md` escrito à mão pelo dono (caso raro; o commit dele roda o CI uma vez a mais, aceito) |

### (c) O que muda na conferência de entrega
- A etapa de portão (`review`, `qa`, `seguranca`, `devops`) não tem mais commit a conferir: a prova é o status do contexto do papel no `Revisar-sha` do brief, com o comentário íntegro. O `forge-check entrega` passa a tratá-la como já trata o ato no GitHub (`entrega_ato_github`, `bin/forge-check:3181`): PQ `pr`, conferido pelo estado no GitHub. O `brief gerar` do portão escreve esse PQ.
- Saem da conferência: `parecer_de_portao_da_branch`, `parecer_mandado_pelo_portao`, `commit_so_de_parecer`, `parecer_mesclado_na_volta`, `bug_do_qa_na_volta`, `autores_da_volta`, `veredito_trocado`, a branch `parecer/<brief>` (`PREFIXO_DE_PARECER`) e a `linha-final: parecer-conferido`; no `pr`, `parecer_commitado`, `pareceres_conferidos` e as linhas `parecer conferido` do Histórico (VOLTAS-REVISOR-WT), `commit_de_pareceres_paralelos` (AQ-5), `commit_junto_do_parecer` (QA-TESTE-E-PARECER-SEPARADOS) e `pareceres_divergentes` (FC-PR-PARECER-FORJADO: com um status vigente por contexto, não há dois arquivos a divergir).
- A etapa de código não muda: escopo pelo intervalo, provas do brief, `entrega conferida <sha40>`.

### (c) O que muda nos pareceres em `docs/`
- `docs/reviews/`, `docs/qa/`, `docs/security/` e `docs/devops/` deixam de receber parecer de item. O que já está lá fica como histórico; os `_modelo.md` seguem como modelo do texto (o `forge-check docs` continua validando o arquivo local). `docs/qa/bugs/` deixa de receber registro: bug alto ou crítico vai no texto do parecer; médio e baixo viram cartão (`R-QA`).
- Ficam como arquivo commitado o que não é parecer de item: `docs/security/ameacas/` (modelo de ameaças, peça de desenho), `docs/security/aceites/` (do dono) e os pareceres da promoção de versão, que passam a ser status no commit da marca (mesma ferramenta, mesmo contexto), sem PR de parecer.
- `LIVRES` e `ANEXOS_DO_PORTAO` continuam valendo para o histórico; deixam de ser caminho do dia a dia.

### Arquivos e funções
`bin/forge_pareceres.py` (novo), `bin/forge-check` (`parecer publicar` e `parecer herdar`; `cmd_pr`, `pr_da_cli`, `pareceres_da_volta`, `incluidas_da_volta`, `cmd_entrega` e as funções que saem, listadas acima), `bin/forge-fechar` (passos 1, 4 e 6, `--promover`, `mesclar_auto`, `--armar`, `CHECKS_EXIGIDOS`), `hooks/conformidade.json` (caminho por papel), `hooks/parecer.py` (só texto e a mensagem de `exigidos_sem_pedido`, que cita pastas e passa a citar contextos), `.github/workflows/ci.yml` (sai o job `pareceres`, o gate de commit só de parecer e o passo "Testes que leem pareceres"; o agregador perde o `needs` de `pareceres`), `tests/catraca.py` (sai o `--modo pareceres`: `violacoes_de_pareceres`, `_violacoes_de_pareceres`, `pareceres_que_nao_aprovam`; simplifica `pareceres_do_pedido` do rótulo, porque nenhum parecer muda a branch depois do rótulo; entra `bin/forge_pareceres.py` em `PROTEGIDOS`), `tests/test_ci_local.py` (hash do gate), textos dos agentes de portão e do `tech-lead`, `docs/regras/R-REVIEW.md`, `R-QA.md`, `R-SEGURANCA.md`, `R-PROVA.md`, `R-FLUXO.md` (linha 16: a `homolog` "com merge automático" passa a "merge direto preso ao head"), `skills/briefs-e-conferencia/`, ADR nova que emenda a ADR 0008 (seção 3, o job `pareceres`) e a ADR 0004 (onde o parecer mora).

### Por que o existente não basta
O mecanismo novo é o status do commit (e o comentário). O que existe para a mesma necessidade é o arquivo commitado na branch, e a evidência de que ele não basta está no próprio código: cada parecer é um commit que reabre o CI (`ci.yml:612-617`, comentário do E1.75) e cerca de 15 guardas existem só para separar commit de parecer de commit de autor (lista da seção 1, C3), várias com 4 a 10 voltas de segurança cada (E50.5 A1, E50.6 A4, "volta 4, segurança A10" em `bin/forge-check:3060`). O status no commit não muda o head, então nada disso precisa existir.

### Uma entra, uma sai
Entram: o status por contexto, o agregado `pareceres` e a herança. Saem: o job `bateria (pareceres)` do CI, o gate de commit só de parecer, o `--modo pareceres` da catraca, o `--armar` e o `--auto` do `forge-fechar`, e as guardas de commit de parecer listadas acima. Saldo de código: negativo (estimado em mais de 600 linhas a menos, contra cerca de 450 novas).

### Riscos
- **R1. Status forjado por workflow.** Um PR pode editar o próprio workflow para pedir `statuses: write` e gravar `parecer-review` com o `GITHUB_TOKEN`. Mitigação: a leitura aceita só o `creator` da conta da sessão, nunca o `github-actions[bot]`; o workflow é `PROTEGIDOS` (rótulo do dono). Vai ao modelo de ameaças do `security-engineer` (item G2.0).
- **R2. Mesma conta para todos os agentes.** O GitHub não distingue o autor do revisor: qualquer agente com o token pode chamar a ferramenta. É a mesma força de hoje (o arquivo commitado também não prova o papel; a autoria é local). A conta própria dos agentes é o G4; o desenho já deixa a lista positiva de `creator` como o ponto onde ela entra.
- **R3. `forge-check` da branch publicando.** O portão que roda o `forge-check` da cópia da branch rodaria código do autor. Mitigação: o `publicar` recusa rodar de árvore cujo `bin/forge-check` e `bin/forge_pareceres.py` diferem dos da `origin/develop` (o mesmo princípio do CI, que roda a catraca da base).
- **R4. Transição.** Branch aberta antes do G2 tem parecer em arquivo. O `pr` lê os dois caminhos durante uma versão (G2.2) e o de arquivo sai no G2.8; ninguém migra parecer antigo.
- **R5. Sem rede, sem GitHub.** Sem `gh` ou sem rede, nada se publica nem se integra (falha fechada); hoje o merge também precisa do GitHub.

## 4. G3: testes uma vez só

### O que muda
1. **O autor roda só os afetados:** `bin/forge-testes` (o plano dirigido) uma vez antes do primeiro envio, mais as checagens baratas do envio (ENVIO-LEVE, sem mudança) e o `forge-mutante --cobertura`, que é estático e roda em segundos (só lista a guarda sem mutante declarado). Sai a prova de mutação do autor na entrega (META85-ENTREGA-COM-MUTANTES, `--mutantes` em `PROVAS_DO_PQ` e `provas_da_entrega`).
2. **A mutação e a prova do vermelho rodam uma vez, no CI do PR:** job novo `mutantes do diff`, em paralelo às partes da suíte, que roda `bin/forge-mutante` em cada spec de `tests/mutantes/` do diff e o `forge-testes --vermelho` quando o diff traz teste novo, com a saída no resumo do job; entra no agregador `bateria`. Roda o `forge-mutante` da base, como a catraca, com `contents: read` e sem token.
3. **QA, review e segurança leem o resultado do CI** (as partes da suíte e o job de mutantes) em vez de rodar a bateria, a mutação ou o vermelho. Local, cada um roda só o cenário ou a sonda do próprio achado. Sai PARECER-SO-COM-CI-VERDE (`PROVA_DA_SUITE`, `falta_na_prova`, `modulos_tocados`, `suite_do_parecer` e o uso de `ci_verde_no_head` no `pr`): com o G2, a integração já exige o CI e os pareceres verdes no mesmo commit, e o parecer não precisa carregar prova de suíte.
4. **O CI do PR cabe em 10 minutos.** Com o G2, o CI roda uma vez por head em vez de uma vez por parecer. A medida vem primeiro (G3.1); se o P90 passar de 10 min depois do G2.5, as opções vão ao dono (D4).

### Arquivos e funções
`.github/workflows/ci.yml` (job novo e o `needs` do agregador), `bin/forge-check` (`provas_da_entrega`, `PROVAS_DO_PQ`, `gerar_volta`, que hoje acrescenta o PQ do `forge-mutante`, e as funções de PARECER-SO-COM-CI-VERDE), `tests/test_ci_local.py`, `agents/qa-engineer.md` (itens 4, 17 e 21), `agents/tech-lead.md` (itens 16 e 26), `agents/security-engineer.md` (item 14), `skills/qa-testing/SKILL.md` (linhas 46 e 96), `docs/regras/R-QA.md` (linhas 12 e 15).

### Por que o existente não basta
O job novo é mecanismo novo de CI. O que existe: a mutação roda na máquina do autor e de novo na do QA, e o CI só confere que a spec existe (`regra_guardas_dos_hooks`, `tests/catraca.py:887`), sem rodar o mutante. Duas execuções locais do mesmo comando, nenhuma no CI que todos leem: é a duplicação que o dono pediu para tirar.

### Uma entra, uma sai
Entra o job `mutantes do diff`. Saem a prova de mutação do autor na entrega, a rodada de mutação e do vermelho do QA, e PARECER-SO-COM-CI-VERDE.

### Riscos
- **CI mais longo.** O job novo corre em paralelo; só entra no caminho crítico se passar do tempo de uma parte da suíte (medida da proposta `ci-rapido`: 2:30 a 5:00 por parte). O `forge-mutante` já tem prazo por mutante; o job leva `timeout-minutes` de 8.
- **Fila de runners.** O plano gratuito limita 20 jobs simultâneos (proposta `ci-rapido`, item 6); o G2 tira o job `pareceres` e as rodadas repetidas, o G3 põe um job. Saldo de jobs por PR: zero; saldo de rodadas: menos uma por parecer.
- **Custo.** Zero enquanto o repositório for público (minutos gratuitos); o `bin/forge-cota-ci` confere o uso.

## 5. (b) O corte, na ordem G1, G2, G3

Teto de cada item: cerca de 150 linhas de código (H1; testes e documentação fora da conta) e até 10 arquivos (META85). Linhas são `estimado`. Item com arquivo em comum com outro entra na fila em ordem (`R-FLUXO`, `forge-check sobreposicao`); sem arquivo em comum, pode correr em paralelo, mantida a prioridade do dono.

| Item | O quê | Arquivos | Código (est.) | Depende de |
|---|---|---|---|---|
| G1.1 | Teto de 1 volta no `brief gerar --volta` e no `conferir_volta`; a 2.ª só com DECISÃO DO DONO que cite a branch | `bin/forge-check`, teste do forge-check, `docs/regras/R-QA.md`, `docs/regras/R-REVIEW.md`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, spec de mutantes, `changelog.d/` | 50 | nada |
| G1.2 | Revalidação só no delta: achado bloqueante fora dos hunks recusado, salvo `explorável:` com sonda na segurança | `bin/forge-check`, teste, `docs/regras/R-REVIEW.md`, `docs/regras/R-SEGURANCA.md`, `agents/tech-lead.md`, `agents/qa-engineer.md`, `agents/security-engineer.md`, spec de mutantes | 110 | G1.1 (mesmo arquivo) |
| G1.3 | Classe T para só texto e só teste (inclusive controle), fora `docs/regras/` e `CONTROLES_DO_FORGE`; sai a isenção M13 | `bin/forge-check`, `hooks/parecer.py` (texto), `tests/test_classe_risco.py`, `docs/regras/R-QA.md`, `docs/regras/R-SEGURANCA.md`, `skills/engineering-practices/rigor-por-classe.md`, spec de mutantes | 60 | G1.2 (mesmo arquivo); D2 |
| G2.0 | ADR "parecer como status do commit" (emenda as ADRs 0004 e 0008) e modelo de ameaças do `security-engineer` (R1 a R3) | [`docs/adr/0019-parecer-como-status.md`](../adr/0019-parecer-como-status.md), `docs/security/ameacas/g2-parecer-status.md` | 0 | nada (paralelo ao G1) |
| G2.1 | Escrita: texto local em `.forge/pareceres/`, `forge-check parecer publicar` (status, comentário, agregado), módulo novo em `PROTEGIDOS` | `bin/forge_pareceres.py`, `bin/forge-check`, `hooks/conformidade.json`, `tests/catraca.py` (só `PROTEGIDOS`), `tests/test_forge_pareceres.py`, spec de mutantes | 140 | G2.0; D3 (permissão do token) |
| G2.2 | Leitura: `cmd_pr` lê os statuses (lista positiva de `creator`, sha256 do comentário), nos dois caminhos durante a transição | `bin/forge_pareceres.py`, `bin/forge-check`, teste, spec de mutantes | 130 | G2.1 |
| G2.3 | Volta e herança: `parecer herdar`; `pareceres_da_volta` e `incluidas_da_volta` leem o comentário; o G1.2 passa a achar o parecer anterior pelo status | `bin/forge_pareceres.py`, `bin/forge-check`, teste, spec de mutantes | 120 | G2.2 |
| G2.4 | `forge-fechar`: merge direto preso ao head (sai `--auto` e `--armar`, também no `--promover`), espera CI e `pareceres` verdes no mesmo sha, `herdar` no passo 1, linhas `Parecer:` no corpo do squash | `bin/forge-fechar`, `tests/test_fechar_auto_merge.py` (passa a provar o merge sem `--auto`), `tests/test_fechar_checks_exigidos.py`, `docs/regras/R-FLUXO.md`, `agents/tech-lead.md` | 100 | G2.3; D3 (contexto na proteção) |
| G2.5 | CI: sai o job `pareceres`, o gate de commit só de parecer e o passo dos testes que leem pareceres; o agregador perde o `needs` | `.github/workflows/ci.yml`, `tests/test_ci_local.py` | 120 removidas | G2.4 e D3 aplicada (o agregado `pareceres` já exigido na `develop`) |
| G2.6 | Catraca: sai o `--modo pareceres`; simplifica `pareceres_do_pedido` do rótulo | `tests/catraca.py`, testes da catraca, spec de mutantes | 110 removidas | G2.5 |
| G2.7 | Entrega do portão pelo status (PQ `pr` no `brief gerar` do portão); saem as guardas de parecer na branch (`bin/forge-check:3056-3170`, `PREFIXO_DE_PARECER`) | `bin/forge-check`, testes da entrega, spec de mutantes | 60 novas, 150 removidas; corta em G2.7a e G2.7b se passar do teto | G2.3 |
| G2.8 | `pr` sem o caminho de arquivo: saem `parecer_commitado`, `pareceres_conferidos` e as linhas `parecer conferido`, AQ-5, QA-TESTE-E-PARECER-SEPARADOS e FC-PR-PARECER-FORJADO; mensagem do hook `parecer` cita contextos | `bin/forge-check`, `hooks/parecer.py`, testes, spec de mutantes | 150 removidas; corta em dois se passar | G2.7, e uma versão inteira depois do G2.2 (R4) |
| G2.9 | Textos: PR em rascunho no primeiro envio, portões publicam em vez de commitar, conferência pelo status | `agents/tech-lead.md`, `agents/qa-engineer.md`, `agents/security-engineer.md`, `agents/devops-engineer.md`, `agents/jarvis.md`, `docs/regras/R-REVIEW.md`, `R-QA.md`, `R-SEGURANCA.md`, `R-PROVA.md`, `skills/briefs-e-conferencia/SKILL.md` | 0 | G2.4 (pode sair junto do G2.4 se couber) |
| G3.1 | Medida do CI do PR: P50 e P90 de 20 execuções e a espera na fila, pela API (só leitura) | nenhum (relatório do `devops-engineer`) | 0 | nada (paralelo ao G1) |
| G3.2 | Job `mutantes do diff` no CI, com `forge-testes --vermelho` para teste novo | `.github/workflows/ci.yml`, `tests/test_ci_local.py` | 70 | G2.5 (mesmo arquivo) |
| G3.3 | Saem a prova de mutação do autor e PARECER-SO-COM-CI-VERDE | `bin/forge-check`, testes, spec de mutantes | 30 novas, 120 removidas | G3.2, G2.8 (mesmo arquivo) |
| G3.4 | Textos: autor só afetados; QA, review e segurança leem o CI | `agents/qa-engineer.md`, `agents/tech-lead.md`, `agents/security-engineer.md`, `skills/qa-testing/SKILL.md`, `docs/regras/R-QA.md` | 0 | G3.3 |
| G3.5 | Só se o G3.1, medido de novo depois do G2.5, der P90 acima de 10 min: a opção que o dono escolher na D4 | `.github/workflows/ci.yml` (e talvez `tests/pesos-d4.json`) | até 60 | G3.1, G2.5, D4 |

Portões de cada item pela classe de hoje: quase todos são C (tocam `bin/`, `hooks/`, `.github/`, `tests/catraca.py` ou `docs/regras/`), com review, QA e segurança; o G1.3, quando entrar, torna T os itens só de texto seguintes (G2.9, G3.4, se não tocarem `docs/regras/`). G2.0 e G3.1 são só documentação.

## 6. (d) O que afrouxa regra com ID

Duas leituras: pela regra do Forge (tirar ou trocar texto de `docs/regras/`, item de `tests/config.json` ou controle é "sim") e pelo mérito (`R-DECISAO` (d): a qualidade medida cai ou sai controle sem medida). Rótulo `afrouxa-regra`: além do mérito, a catraca o pede em toda mudança de arquivo de `PROTEGIDOS` (`bin/forge-check`, `hooks/parecer.py`, `hooks/conformidade.py`, `.github/workflows/`, `tests/catraca.py`), aplicado pelo dono depois do último envio (`R-LIMITES`, R-CONTRIB).

| Item | Pela regra do Forge | Pelo mérito | Rótulo da catraca |
|---|---|---|---|
| G1.1 | sim, `R-QA` (3 voltas por 1) | não: o bug que sobra vai ao dono, nunca segue aberto | sim (`bin/forge-check`) |
| G1.2 | sim, `R-REVIEW`, `R-QA`, `R-SEGURANCA` | **sim**: defeito provado ou recomendação de segurança achados fora do delta deixam de bloquear e viram cartão | sim |
| G1.3 | sim, `R-QA`, `R-SEGURANCA` | **sim**: texto de agente e skill e teste de controle perdem QA e segurança | sim (`bin/forge-check`, `hooks/parecer.py`) |
| G2.0 | não (ADR nova, emenda) | não | não |
| G2.1 a G2.3 | sim, controle (`hooks/conformidade.json`, `bin/forge-check`) | não: troca o lugar do parecer, mesmos exigidos, leitura com falha fechada | sim |
| G2.4 | sim, `R-FLUXO` (texto da `homolog`) | não: aperta (sai o merge automático) | não (`bin/forge-fechar` não é `PROTEGIDOS`) |
| G2.5 | sim, `R-REVIEW`, ADR 0008 (sai um check do CI) | não, se a D3 for aplicada antes: o agregado `pareceres` exigido no servidor substitui o job; **sim** sem ela | sim (`.github/workflows/`) |
| G2.6 a G2.8 | sim, controle | não: as guardas que saem protegiam um caminho que deixa de existir | sim |
| G2.9 | sim, `R-REVIEW`, `R-QA`, `R-SEGURANCA`, `R-PROVA` (texto) | não | não |
| G3.1 | não | não | não |
| G3.2 | sim, controle (workflow) | não: acrescenta verificação | sim |
| G3.3 | sim, `R-QA` (prova de mutação do autor; PARECER-SO-COM-CI-VERDE) | não, com o G3.2 no lugar | sim |
| G3.4 | sim, `R-QA` (texto) | não | não |
| G3.5 | depende da opção | opção (b) da D4: **sim** | sim |

A ORDEM DO DONO de 22:13 é a decisão de mérito do G1.2, do G1.3 e do G2; ela não substitui o rótulo de cada PR nem a escolha das decisões D1 a D5 abaixo.

## 7. (e) O que só o dono pode fazer

Estado em 23/11: as decisões do dono de 22/11 e 23/11 (pedido v0478) prevalecem sobre as recomendações escritas em 21/11; D1, D2 e D4 estão fechadas, e a D3 segue com o dono.

1. **Rótulo `afrouxa-regra`** em cada PR marcado "sim" na coluna da catraca (seção 6), sempre depois do último envio. Decidido: a autorização de rótulo valeu até 23/11 09:00 (DECISÃO DO DONO 22/11 05:21); o G1.2 e o G1.3 têm o rótulo autorizado (DECISÃO DO DONO 23/11 15:25, opção 2a), com todos os checks verdes e merge nunca automático; até 27/11 23:59, o time põe o rótulo sem perguntar quando a segurança confirma por escrito que o item só aperta, e o item listado no aviso de marco (DECISÃO DO DONO 23/11 15:25). Item que afrouxa regra fora dessas autorizações continua indo ao dono.
2. **D1. Saída da 2.ª volta** (G1.1): decidida pelo dono (22/11 07:23, reafirmada na ORDEM DO DONO de 23/11 14:24), pela regra de voltas da seção 2, item 1: 2.ª volta sem perguntar; 3.ª também, se corrigir só o que o portão apontou, sem mudar a lógica nem afrouxar teste; se a 3.ª falhar, cortar o item e reabrir menor. A recomendação de 21/11 (recusar a 2.ª e trazer ao dono) fica superada.
3. **D2. Alcance do G1.3:** decidida pelo time em 22/11 08:49 (reversível, só aperta em relação à ORDEM DO DONO de 21/11 22:13), pela recomendação: `docs/regras/` segue com review e segurança, sem QA; texto de agente, skill e modelo e teste de controle só com review.
4. **D3. GitHub:** aberta, com o dono: (a) incluir o contexto `pareceres` nos checks exigidos do ruleset da `develop` (e da `homolog`, para os pareceres da versão) antes do G2.5; (b) dar ao token da sessão a permissão de gravar status de commit e comentar em PR (escopo `repo:status` no token clássico, ou "Commit statuses" e "Pull requests" com escrita no de granularidade fina), sem custo; com o G4, a mesma permissão vai à conta dos agentes.
5. **D4. CI do PR acima de 10 min no P90:** fechada sem escolha de opção: o G3 (#785) pôs o CI do PR em 8 min 35 s, dentro da meta de 10 min do dono; as opções (a) mais partes da suíte, (b) Python 3.14 só com os afetados no PR e (c) instalação no 3.14 só no push da `develop` só voltam se a medida do G3.1 passar de 10 min de novo, e a (b) afrouxa, portanto vai ao dono.
6. **D5. Projetos:** o time segue a recomendação (registro de 23/11 14:36): o G2 vale para o Forge nesta versão e para os projetos na seguinte, depois de uma versão de uso (o projeto pode não ter GitHub ou `gh` com essa permissão). O dono pode trocar para todos juntos.
7. **Merge do PR `homolog` → `main`** de cada versão que leve estes itens (`R-MAIN`), como sempre.

## 8. Medida e critério de reversão

- **Medida do conjunto:** mediana e P75 do primeiro commit até a `develop`, por versão (E11.6, `agile-coach`); voltas por item e achados recusados por estarem fora do delta (semanal, decisão de 20:54); execuções de CI por PR; P50 e P90 do CI do PR.
- **G1:** reverte o G1.2 com 2 escapes em 14 dias vindos de achado rebaixado; reverte o G1.3 com 1 escape de segurança em item T de texto de controle.
- **G2:** reverte para o arquivo commitado se um status forjado passar pela leitura (prova: status com `creator` fora da lista aceito pelo `pr`) ou se um parecer se perder (comentário sumido com o PR já mesclado sem a linha `Parecer:` no squash).
- **G3:** reverte o G3.3 (volta a prova de mutação do autor) se o job do CI deixar passar mutante sobrevivente que a rodada local pegaria (1 caso provado); reverte o G3.5 (b) com 1 vermelho do 3.14 na `develop` que o PR não viu.
