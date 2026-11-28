# 0019 - Parecer como status do commit, fora da branch

Estado: proposta (G2.0 do pedido v0481, E6.1; desenho `docs/propostas/g1-g3-fluxo-rapido.md`, seção 3 e linha G2.0 da seção 5). Emenda a [ADR 0004](0004-contrato-verificavel-entre-agentes.md) (onde o parecer mora e como vale para o head) e a seção 3 da [ADR 0008](0008-governanca-de-contribuicoes.md) (o job `pareceres`). Cada ponto vale a partir do PR do item do corte que traz o código (G2.1 a G2.9); até lá, as ADRs 0004 e 0008 seguem como estão e nada se libera por este texto. O modelo de ameaças é do `security-engineer`, em etapa própria; esta ADR passa a `vigente` só depois dele, e o que ele pedir entra aqui por emenda. Onde esta ADR difere do desenho (sha256 inteiro, origem da herança em 40 hex, código confiável fora do próprio `publicar`), ela prevalece. Data: 2026-11-24.
Propósito: tirar o parecer de portão da branch e gravá-lo como status do commit no GitHub, para que o parecer não mude o head nem peça rodada de portão quando a `develop` é trazida, e para que a integração aconteça quando o CI e os pareceres estiverem verdes no mesmo commit. Público: o dono, quem mantém o Forge, o `tech-lead`, o `qa-engineer`, o `security-engineer` e o `devops-engineer`. Revisão: 2026-12-08.

## Contexto
ORDEM DO DONO de 21/11 22:13 (pedido v0478), item 2: cada portão grava o parecer como status no commit do GitHub, sem commit na branch; o CI roda no primeiro envio, junto com os portões, e a ferramenta integra quando o CI e os pareceres estiverem verdes no mesmo commit. Meta da mesma ordem: mediana de 30 min do primeiro commit até a `develop`, P75 até 60 min. ORDEM DO DONO de 24/11 19:54 (pedido v0481): o G2 vem primeiro depois dos aprovados, e cada item diz a medida que espera mover; a deste é **rodadas de portão por head novo com `revalida: não`** e **tempo por item**.

Hoje o parecer é um arquivo commitado na branch (`docs/reviews/`, `docs/qa/`, `docs/security/`, `docs/devops/`; ADR 0004, item 2). Cada parecer é um commit que muda o head (causa C3 do desenho):
- o CI roda de novo a cada parecer; o próprio workflow registra que o commit que traz o parecer "roda a suíte uma vez a mais" (`.github/workflows/ci.yml:614`), e o job `bateria (pareceres)` existe só para ler pareceres commitados (`ci.yml:739`);
- o parecer de um portão muda o head que o outro revisou; cerca de 15 guardas existem só para separar commit de parecer de commit de autor (AQ-5, VOLTAS-REVISOR-WT com a branch `parecer/<brief>` em `bin/forge-check:2495`, QA-TESTE-E-PARECER-SEPARADOS, o gate "commit só de parecer" em `ci.yml:618`, entre outras listadas no desenho, seção 1);
- o head novo dispara uma rodada de portão mesmo quando a aprovação segue valendo: a regra de hoje (domínio do tipo e merge simulado da ADR 0004; `R-REVIEW`) já mantém o parecer quando a `develop` é trazida sem tocar o domínio, mas cada portão é chamado de novo para ler o `forge-check parecer delta` e registrar o delta lido. Caso de 24/11 no pedido v0481: o #867 trouxe a `develop` 8d7914bc no head 29d87859 sem conflito; os três portões rodaram o delta e os três deram `revalida: não`. A aprovação não venceu; o custo foi a rodada de portão, três chamadas de agente antes de entrar na fila.

## Decisão

### 1. Fluxo
1. **PR em rascunho no primeiro envio** (`gh pr create --draft`; o hook `parecer` já deixa o rascunho passar sem parecer). O CI e a catraca rodam nesse envio. O Jarvis dispara os portões logo depois da entrega conferida, sem esperar o CI: portões e CI correm juntos sobre o mesmo head.
2. **Cada portão grava o parecer como status do commit**, sem commit na branch. O texto é o mesmo documento de hoje (frontmatter da ADR 0004, `## Achados`, `## Sondas`, cenários e bugs do QA), escrito pelo papel com a ferramenta Write fora do git da cópia, em `.forge/pareceres/<pedido>/<tipo>.md` (o `/.forge` já é ignorado). A regra de caminho por papel do `hooks/conformidade.json`, que hoje diz quem escreve em cada pasta de parecer, passa a valer para esse caminho: a regra troca de lugar, nenhuma entra a mais.
3. **A ferramenta integra quando o CI e os pareceres estão verdes no mesmo commit**, por merge direto preso ao head (`gh pr merge <branch> --squash --match-head-commit <sha>`, como o `forge-fechar` já faz em `mesclar_direto`). O merge automático do GitHub segue proibido, e essa proibição já vale hoje pela DECISÃO DO DONO de 21/11 20:15 (o `forge-fechar` recusa `--armar`), não só depois do G2.
4. **Herança.** Commit novo no head (a volta do autor ou a `develop` trazida) não apaga o que vale: o status `success` cujo domínio não mudou é herdado pelo head novo, pela regra de hoje (PARECER-CONTEUDO, `commit_vale` com o domínio do tipo, inclusive o merge simulado da emenda de 2026-10-15 da ADR 0004); o que mudou pede revalidação só no delta (G1.2). A regra de validade não muda; muda quem a aplica: a ferramenta herda o status no lugar da rodada de portão que hoje lê o delta, e trazer a `develop` sem tocar o domínio do parecer não chama portão de novo.

### 2. O status
- **API:** escrita por `POST /repos/{owner}/{repo}/statuses/{sha}` com `state`, `context`, `description` (até 140 caracteres) e `target_url`; leitura por `GET /repos/{owner}/{repo}/commits/{sha}/statuses` (com o `creator` de cada status). Grátis (`R-CUSTO`); o `gh` da sessão já fala com a API.
- **Estado:** `success` para `aprovado` e para `riscos-aceitos` com o aceite do usuário; `failure` para `reprovado`.
- **Contextos, lista positiva e fechada, sem barra no nome** (o `forge-fechar` separa `workflow/nome` na primeira barra): `parecer-review`, `parecer-qa`, `parecer-seguranca`, `parecer-devops`. A lista só cresce por ADR.
- **Agregado `pareceres`:** `success` só quando todos os contextos que a classe e os gatilhos do diff exigem (`exigidos_do_pr`, `bin/forge-check:1828`, a regra de hoje) estão em `success` no mesmo sha; senão `pending`, com o que falta na descrição. É o agregado que pode ir à proteção da `develop` (pendência D3 do dono, seção 8).
- **Descrição:** `<veredito> · sha256 <64 hex do texto> · <n> bloqueantes · <n> recomendados`; na herança, `herdado de <sha40> · sha256 <64>` (sha do commit do parecer original e sha256 do texto dele). O sha256 é sempre inteiro e a origem sempre em 40 hex, nunca prefixo; a ferramenta conta os caracteres e falha fechada acima de 140 (a forma mais longa, `riscos-aceitos · sha256 <64> · 99 bloqueantes · 99 recomendados`, tem 123).

### 3. Quem grava e quem lê
- **Só a ferramenta grava.** O papel do portão roda `forge-check parecer publicar <arquivo local>`. Ela confere o documento (`validar_documento`, bloco de achados e, na revalidação, a regra do delta do G1.2), o registro de autoria do papel (`autoria.jsonl`; o `publicar` recusa se ele falta, sem a folga de hoje do `pr`) e que o `commit:` é o head de um PR aberto da `branch:`; publica o texto como comentário do PR, grava o status com `target_url` no comentário e recalcula o agregado.
- **Código confiável:** a conferência de que quem publica é o código da base não mora no próprio código que ela protege. O portão chama o `forge-check` do plugin carregado, nunca `bin/forge-check` da cópia da branch; o hook `conformidade` barra a chamada por caminho da cópia. O mesmo princípio do CI, que roda a catraca da base.
- **Herança:** `forge-check parecer herdar --ref <branch>`, pelo mesmo caminho confiável, rodada pelo passo 1 do `forge-fechar` e pelo Jarvis depois do envio da volta. Copia só `success`, só de sha ancestral do head, só depois de o status de origem passar pela leitura inteira, e mede o domínio sempre a partir do parecer original (`herdado de <sha40>`), nunca de outro herdado.
- **Ninguém grava status pelo Bash:** o agente não ganha comando novo, e a leitura descarta o que não veio da ferramenta.
- **Quem lê:** `forge-check pr` (e, por ele, o hook `parecer`), o `forge-fechar`, o `brief gerar --volta` e o `forge-check entrega`. A leitura aceita só o status mais novo de cada contexto da lista, com `creator` igual à conta da sessão (lista positiva; o `github-actions[bot]` e qualquer outra conta ficam fora), e confere o sha256 da descrição contra o corpo do comentário do `target_url`. Comentário apagado ou editado depois do status: o parecer não vale. Sem `gh` ou sem rede: nada se publica, nada se lê como aprovado, nada se integra.
- **Onde fica o código:** módulo novo `bin/forge_pareceres.py`, que entra em `PROTEGIDOS` de `tests/catraca.py` no mesmo item que o cria (G2.1).

### 4. Prova e auditoria
| O que o parecer commitado guarda hoje | Onde passa a ficar |
|---|---|
| Veredito, tipo e sha revisado | Status do commit (contexto, estado, sha), que fica no GitHub depois do merge |
| Texto inteiro | Comentário do PR escrito pela ferramenta; o sha256 da descrição prende o texto ao status |
| Quem escreveu (papel) | `autoria.jsonl` da cópia do portão, conferido antes de publicar (a mesma força de hoje) |
| Histórico no git da `develop` | Uma linha por contexto no corpo do commit de squash, escrita pelo `forge-fechar` a partir da leitura: `Parecer: <contexto> <estado> <sha40> sha256 <64> <url do comentário>`; `forge-check metricas`, `voltas` e `forge-placar` passam a ler essas linhas |
| Voltas e revalidações | A sequência de statuses do mesmo contexto nos heads da branch |
| Aceite do usuário para `riscos-aceitos` | Sem mudança: `docs/security/aceites/<pedido>.md`, do dono |

`docs/reviews/`, `docs/qa/`, `docs/security/` e `docs/devops/` deixam de receber parecer de item; o que está lá fica como histórico, e os `_modelo.md` seguem como modelo do texto. Seguem commitados o que não é parecer de item: `docs/security/ameacas/` e `docs/security/aceites/`. Os pareceres da promoção de versão passam a ser status no commit da marca.

### 5. O que sai
O que o desenho lista na seção 3, "O que muda na conferência de entrega" e "Uma entra, uma sai": as guardas de commit de parecer da entrega e do `pr`, a branch `parecer/<brief>`, o job `bateria (pareceres)`, o gate de commit só de parecer, o passo "Testes que leem pareceres" e o `--modo pareceres` da catraca. A etapa de código não muda.

### 6. Emenda à ADR 0004
- **Item 2 (onde o parecer mora):** review, QA, segurança e devops deixam de morar em `docs/<pasta>/<pedido>.md` na branch; o documento vai para `.forge/pareceres/<pedido>/<tipo>.md`, fora do git, e é publicado como comentário do PR com o status. Campos e `contrato: 1` não mudam; `commit` é o sha do status.
- **Item 3 (validade para o head):** a parte "o diff só toca pareceres e quadro" perde os pareceres (não estão mais no diff) e vira a herança por domínio (Decisão 1.4). O merge simulado da emenda de 2026-10-15 segue valendo.
- **Item 4 (validador):** `forge-check pr` lê os statuses em vez das pastas e ganha `parecer publicar` e `parecer herdar`. Durante uma versão (G2.2 a G2.8) lê os dois caminhos; o de arquivo sai no G2.8.

### 7. Emenda à ADR 0008
- **Seção 3, job `pareceres`:** sai no G2.5. A exigência é a mesma (`exigidos_do_pr`, último parecer de cada tipo aprovado ou `riscos-aceitos` com aceite), lida pela ferramenta antes do merge. O G2.5 só entra com a pendência D3 a) resolvida pelo dono e aplicada; sem ela, tirar o job afrouxa e o item não entra.
- **Seção 3, `catraca`:** a ressalva dos pareceres do pedido depois do rótulo deixa de ser necessária (G2.6), porque nenhum parecer muda o head.
- **Camada 1 (identidade):** a lista positiva de `creator` é o ponto onde a conta própria dos agentes entra (G4).

### 8. Pendências do dono (`R-DECISAO`; esta ADR não as decide)
- **D3 do desenho, GitHub** (acesso; só o dono aplica): a) incluir o contexto `pareceres` nos checks exigidos do ruleset da `develop` e da `homolog`; b) dar ao token da sessão a permissão de gravar status de commit e comentar em PR. Esta ADR não escolhe nem aplica nenhuma das duas. Sem a b), o G2.1 não publica; sem a a), nem o G2.4 (o `forge-fechar` espera o agregado `pareceres` exigido na proteção; desenho, seção 5) nem o G2.5 entram. (Não confundir com o item D3 do pedido v0481, teste enfraquecido.)
- **D5 do desenho, projetos:** registrada no desenho (seção 7) como recomendação seguida pelo time: o G2 vale para o Forge nesta versão e para os projetos na seguinte, pela migração da ADR 0005. O dono pode trocar.
- **Rótulo `afrouxa-regra`** nos PRs do corte marcados "sim" na coluna da catraca (desenho, seção 6), depois do último envio.

## Alternativas
- **Manter o arquivo commitado e só podar guardas:** as guardas existem porque o parecer muda o head; podá-las sem tirar a causa reabre os casos que elas fecharam.
- **Parecer em branch separada ou em `git notes`:** não muda o head do PR, mas o CI e a proteção do GitHub não leem notas nem outra branch como check; seria preciso um job que as lê, de volta ao job `pareceres` rodando a cada parecer.
- **Revisão do GitHub (`gh pr review --approve`):** a conta é a mesma do autor, e o GitHub não deixa o autor aprovar o próprio PR; não há contexto por portão nem estado por commit.
- **Check run (Checks API):** exige GitHub App; o token de usuário da sessão não cria check run.
- **Status gravado pelo próprio CI:** o `creator` seria o `github-actions[bot]`, que um PR controla editando o workflow; é o que a leitura exclui.

## Consequências
- Melhora: o parecer não muda o head; o CI roda uma vez por head; portões e CI correm juntos desde o primeiro envio; trazer a `develop` sem tocar o domínio não chama portão de novo; saem o job `pareceres`, o gate de commit só de parecer, o `--modo pareceres` e cerca de 15 guardas (saldo estimado no desenho: mais de 600 linhas a menos, cerca de 450 novas).
- Piora: a integração depende do GitHub e da rede (falha fechada; o merge já depende); o texto inteiro do parecer mora num comentário do PR, e no git fica a linha `Parecer:` do squash com o sha256 e a URL.
- Limite conhecido: a mesma conta para todos os agentes. O GitHub não distingue autor de revisor; é a mesma força de hoje (o arquivo commitado também não prova o papel). Fecha com a conta própria dos agentes (G4), pela lista de `creator`.
- Limite conhecido: um PR pode editar o próprio workflow para gravar um contexto com o `GITHUB_TOKEN`; a leitura aceita só o `creator` da conta da sessão, e o workflow é `PROTEGIDOS`. O detalhe vai ao modelo de ameaças da segurança.
- Transição: branch aberta antes do G2 tem parecer em arquivo; o `pr` lê os dois caminhos durante uma versão; ninguém migra parecer antigo.
- Afrouxa? Esta ADR, sozinha, não: não tira texto de `docs/regras/`, de `tests/config.json` nem de controle. Os itens que a aplicam levam o rótulo onde a catraca pede (desenho, seção 6).

## Por que o existente não basta
O mecanismo novo é o status do commit, com o comentário e o agregado. O que existe para a mesma necessidade é o arquivo commitado na branch. Pela evidência de execução, ele não basta:
- o CI roda uma vez a mais por parecer (`ci.yml:614`), e um job inteiro (`ci.yml:739`) só lê pareceres commitados;
- cerca de 15 guardas separam commit de parecer de commit de autor, várias com 4 a 10 voltas de segurança cada (desenho, seção 1);
- os 8 itens de 21/11 com 6 a 26 voltas levaram de 4 a 66 h, contra 25 a 38 min dos itens sem volta (dados do dono, ORDEM de 21/11 22:13); cada volta com parecer commitado é um head novo e um CI novo;
- o head novo chama portão mesmo sem nada a revalidar: em 24/11, o #867 trouxe a base sem conflito, os três portões rodaram o `parecer delta` e os três deram `revalida: não`; três rodadas de agente que a herança pela ferramenta dispensa.

## Medida que move
- **Rodadas de portão por head novo com `revalida: não`:** chamadas de portão (review, QA, segurança, devops) disparadas por um head novo cujo `forge-check parecer delta` deu `revalida: não`, por PR mesclado. Hoje: toda base trazida sem conflito chama cada portão da classe uma vez (no #867, três rodadas com `revalida: não`). Esperado depois do G2.3 (herança): zero, e nenhum commit de parecer no histórico da branch.
- **Tempo por item:** o que a ferramenta imprime hoje é o `lead_develop_h_p50` do `forge-check metricas` (mediana, em horas, do primeiro movimento do item no Histórico até a `develop`), o `relogios:` do `forge-check voltas` (`aberto_ate_develop` do primeiro movimento do cartão; `pronto_ate_develop` com `meta=30`) e, com `metricas --gh`, o `ci=<execuções>/<falhas>` por item, somado pelas branches dele.
- **O que falta medir (pendência; item de medida a abrir no corte pelo `tech-lead`, depois do G2.4):** a) a contagem de rodadas de portão por causa; o `revalidacoes` do `metricas` conta toda linha do Histórico com `revalid` e não separa base trazida de domínio mudado; b) o P75, que o `metricas` não calcula (só p50); c) o tempo a partir do primeiro commit, meta do dono (mediana 30 min, P75 60 min), que nenhum relógio mede (todos partem do quadro ou do Histórico); d) execuções de CI por head. Até o item, a primeira leitura faz a) e d) à mão, passo a passo: para cada PR mesclado da versão, `gh pr view <n> --json commits` dá os heads; `gh run list --branch <branch> --json headSha,conclusion` dá as execuções por head; os pareceres da branch que registram o delta lido com `revalida: não` dão as rodadas pela base.
- Primeira leitura: na revisão desta ADR (2026-12-08) ou uma versão depois do G2.4, o que vier depois.

## Critério de reversão
Um status de parecer forjado aceito pela leitura (status com `creator` fora da lista aceito pelo `forge-check pr`), ou um parecer perdido (comentário sumido com o PR já mesclado sem a linha `Parecer:` no squash): o Forge volta ao parecer commitado na branch (ADR 0004 e seção 3 da ADR 0008 no texto anterior a esta emenda), com o caminho de arquivo que o `pr` lê até o G2.8.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| AAAA-MM-DD | rodadas de portão por head novo com `revalida: não`, por PR (à mão até o item de medida); `lead_develop_h_p50` e `relogios:` (P75 e o tempo do primeiro commit, meta 30 e 60 min, pendentes do item de medida); execuções de CI por head (à mão até o item de medida); statuses forjados aceitos (meta 0); pareceres perdidos (meta 0) | pendente |
