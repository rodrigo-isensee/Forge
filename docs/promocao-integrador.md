# Promoção develop → homolog por script (`scripts/promover-homolog.py`, D5b)

Propósito: tirar da conversa os passos determinísticos da promoção `develop` → `homolog`, sem tirar nenhum portão. Público: `tech-lead` e Jarvis. Regras: `R-FLUXO` (promoção, métodos de merge), `R-MAIN`, `R-VERIFY`, `R-CONTRIB`. Revisão: 2026-11-22.

## Uso
```bash
scripts/promover-homolog.py [--dry-run] [--ref origin/develop] [--base origin/homolog]
```
Rode na raiz do repositório do Forge (fora dele, ou sem `.claude-plugin/plugin.json` com `"name": "forge"`, o script para). Só aceita o par `develop` → `homolog`; qualquer outro, a `main` inclusive, é recusado (`R-MAIN`, `R-FLUXO`).

## Passos (em ordem; para no primeiro erro)
1. Refs: `origin/develop` tem commit que `origin/homolog` não tem; senão para com "nada a promover".
2. Pareceres: cada arquivo de `docs/reviews/`, `docs/qa/`, `docs/security/` e `docs/devops/` que a promoção traz (adicionado ou alterado entre a base e a ref, lido da ref; arquivo que começa com `_` é modelo e fica fora) precisa ter `parecer: aprovado` no frontmatter. Vale o que a ref diz hoje: parecer reprovado que foi regravado como aprovado conta como aprovado.
3. Versão e CHANGELOG, lidos da ref: versão da `develop` maior que a da `homolog`, entrada `## [<versão>]` no `CHANGELOG.md`, `## [Não publicado]` vazio e nenhum fragmento em `changelog.d/` (o `README.md` da pasta não conta). Sem versão nova a promoção não é release e o CHANGELOG não é conferido, a mesma regra do CI (`scripts/conferir-release.py --so-se-versao-mudou`). Na release, o script roda `bin/forge-check pr release-<versão> --ref <ref> --base main` (P-N3) e para, citando a saída dele, se o parecer de review ou de QA da release estiver desatualizado ou faltando contra a `main`; o que ele pede de `docs/devops` e `docs/security` não conta, porque com `--base main` os gatilhos leem a leva inteira e esses pareceres são dos PRs da leva, não da release: o parecer velho aparece antes de a versão entrar na `homolog`, e não no PR `homolog` → `main`. O pedido da release é sempre `release-<versão>` (o slug da `melhoria/release-<versão>`); sem versão nova, essa conferência não roda.
4. PR `develop` → `homolog`: abre (título e corpo gerados) ou reusa o aberto; PR aberto da `develop` com base diferente da `homolog` para (`R-MAIN`).
5. Checks: uma leitura de `gh pr checks <PR> --json name,bucket,event,link`; só contam os checks do evento `pull_request` (logo depois de abrir o PR, só existem os do `push` da `develop`, no mesmo sha, e eles não são a bateria do PR: a promoção #371 os leu como verdes); só `pass` e `skipping` passam; pendente (ou nenhum check do PR ainda) não imprime comando de merge nenhum e sai com 4, sem esperar e sem dizer "checks verdes"; vermelho para; saída que não seja lista JSON para.
6. Rótulo: a Catraca vermelha pede o rótulo `afrouxa-regra` do dono; o script só avisa e sai com 3. Ele nunca aplica rótulo nem marca item do checklist.
7. Merge só com todo check obrigatório verde: os obrigatórios são os de `CHECKS_EXIGIDOS` do `bin/forge-fechar` (a mesma lista que o merge da `develop` confere em `checks_do_head_verdes`, lida de lá, sem cópia), cada um com execução do evento `pull_request` e só em `pass` (`skipping` num obrigatório para; obrigatório que ainda não apareceu sai com 4, como pendente). Só então o script imprime o merge direto do `tech-lead`, preso ao head e sem merge automático (`gh pr merge develop --merge --match-head-commit <sha da develop>`; merge commit, `R-FLUXO`). Merge automático é proibido em qualquer PR (decisão do dono): o script nunca o imprime e o `tech-lead` nunca o liga. O script **não mescla**: o `tech-lead` roda o comando logo depois da leitura verde; se passou tempo, roda o script de novo, que relê os checks, e só então mescla. O rótulo `afrouxa-regra`, quando a catraca pede, continua do dono. Se a `develop` andou depois da leitura, o `--match-head-commit` faz o merge falhar em vez de mesclar o que não foi conferido.

Código de saída: 0 pronta para o merge direto (todos os checks obrigatórios verdes); 1 parou (nada foi mesclado; inclui check vermelho); 3 preparada, com o rótulo do dono por vir (rode de novo); 4 checks pendentes ou ainda sem check, sem comando de merge (rode de novo).

## `--dry-run`
Roda só as leituras locais dos passos 1 a 3, o `forge-check pr` contra a `main` inclusive, sobre as refs que já existem na máquina (nenhum `git fetch`, nenhum `gh`, nenhum PR, nenhuma escrita) e descreve os passos 4 a 7. Sem `--dry-run`, o script começa por `git fetch origin`, a única escrita local (atualiza as refs remotas).

## O que nunca faz
Mescla, aplica rótulo, usa `--force` ou `--no-verify`, toca a `main`, apaga branch, dispensa parecer ou check. Erro passageiro do GitHub (502) repete só as leituras, até 3 vezes; a criação do PR nunca se repete sozinha.

## Teste
`tests/test_promover_homolog.py` usa repositório temporário com remoto local e `gh` falso (`FORGE_GH`, que só vale com `FORGE_PROMOVER_TESTE=1`; sem a variável o script avisa e usa o `gh` real). Prova que `--dry-run` não muda refs nem árvore e não chama o `gh`, que cada passo para no seu erro, que o comando de merge só é impresso, só com os checks obrigatórios verdes e nunca com merge automático, e que o rótulo nunca é aplicado.

## Reversão
Se o script atrapalhar (falso vermelho que trava a promoção, ou PR aberto de forma errada), apague `scripts/promover-homolog.py`, `tests/test_promover_homolog.py` e este guia: a promoção volta ao passo a passo manual de `R-FLUXO`, que continua valendo. Critério: duas promoções seguidas em que o script atrasa em vez de poupar tempo (medida de partida: 50,9 min do check verde ao merge na 0.28.0; alvo até 10 min).

## Por que o existente não basta
O `bin/forge-fechar` só trata a `develop` (a promoção segue manual, `R-FLUXO`) e o `scripts/conferir-release.py` roda só no CI, depois do PR aberto: nenhum confere pareceres, versão, CHANGELOG e checks antes de abrir o PR de promoção. Evidência: retrospectiva da 0.28.0, ação 1 (50,9 min do tudo verde ao merge do #276, dois briefs de merge).
