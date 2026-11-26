---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.19
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: release 0.47.19 (versão inteira), para a promoção

Etapa E12.25 do pedido v0481. Conteúdo: `git diff b224ee09..9487d956`, 109 arquivos, da marca da 0.47.18 até a marca da 0.47.19. São dez itens: oito squashes (#874, #877, #885, #886, #892, #895, #897 e #898) e dois merges (#890 e #896), cada um com os próprios pareceres, mais a marca, coberta por `docs/security/marca-0.47.19.md` no mesmo commit. Aqui confiro a junção, a marca, o CHANGELOG e a versão.

Gatilhos: hooks (`hooks/salvar.py` novo, fora do sandbox, e `hooks/conformidade.py`, `hooks/_comum.py`, `hooks/conformidade.json`, `hooks/hooks.json`), controles do Forge (`bin/forge-check`, `tests/catraca.py`), fluxo de release e cópias (`bin/forge-fechar`, `bin/forge-copia`), skills de portão (`engineering-practices`, `qa-testing`, `checagem-do-brief`), emenda da ADR 0003 e release usada por todos os projetos.

## Junção: cada item com o parecer próprio
Para cada PR, busquei `refs/pull/<n>/head` sem criar ref e conferi três pontos:
- **Árvore:** `git merge-tree --write-tree <pai do squash> <head do PR>` comparada ao squash na develop: vazia nos dez, nos caminhos de código (`bin`, `hooks`, `scripts`, `.githooks`, `.github`, `tests`, `agents`, `skills`, `docs/regras`, `templates`, `patches`, `stacks`, `dev`, `.claude-plugin`). Heads: #874 `b0dd3f90`, #877 `aa2c75a0`, #885 `e49fc166`, #886 `94df3ed9`, #890 `bcd91439`, #892 `382819c9`, #895 `75d6b3ba`, #896 `21914b69`, #897 `d9a070b7`, #898 `7078b2f9`.
- **Pareceres:** os de segurança, review e QA estão `aprovado`, com `pedido: v0481`, e o `commit:` de cada um é ancestral do head. A contribuição de código do item no `commit:` do parecer, refeita sobre o mesmo pai, é igual à do head nos três pareceres de cada item, com duas exceções, as duas só de teste e cobertas pelo review e pelo QA no commit novo:
  - #886: a segurança aprovou em `517f80fd`; `dba51ddf` só realinha o M3 de `tests/mutantes/v0475-mp1-mp7.json`, que era o A2 recomendado dela.
  - #892: a segurança aprovou em `6d71827e`; `2259b235` só acrescenta um teste em `tests/test_forge_copia.py` e o M5 em `tests/mutantes/v0481-docs-ok.json`.
- **Depois do parecer:** além das duas exceções, só pareceres em `docs/` e merges da develop com itens que já têm parecer próprio.

Observação para o QA da release, fora do meu domínio: o #896 entrou na develop (`5587bb5f`, merge pelo site) sem `docs/qa/v0481-copia-base-fechada.md`. O QA aprovou no `483a5614`, o mesmo commit do review e da segurança, mas o parecer ficou só no commit local `9cf45297` do clone `-qa` (Histórico do v0481, 25/11 07:55). O código do #896 é neutro para a segurança: o `bin/forge-copia` só ganha a linha que diz o sha em que a branch nasceu, depois de todas as recusas.

## Marca e versão
- A marca (`cc4376fe..9487d956`) toca só os dois `plugin.json`, o `CHANGELOG.md` e os 10 fragmentos apagados. Ela é idêntica à saída de `forge-changelog release 0.47.19 2026-11-26` sobre `cc4376fe`.
- CHANGELOG: a seção `## [0.47.19] - 2026-11-26` (`CHANGELOG.md:7`) traz as 11 linhas dos 10 fragmentos: Adicionado 4 (#895, #877, #885, #874), Alterado 2 (#897, #892) e Corrigido 5 (#896, #898, #890, #886 em duas linhas). Cada linha é idêntica à do fragmento. `conferir-release` dá `ok` e `tests.test_changelog` roda 91 testes, OK.
- Versão: `0.47.19` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3`. A `origin/main` está em `0.47.18` (`52dc3dcd`), e a base comum com a marca é `b224ee09`. Teto medido como o `forge-fechar`: 522 linhas, classe C.
- Segredos: busquei nas linhas acrescentadas do diff inteiro os padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack. A única ocorrência é texto de fixture descrito em prosa (`ghp_` seguido de 30 `A`, um commit de teste nunca enviado), sem segredo real.
- Texto: a linha do #877 no CHANGELOG ainda diz "exceção ao R-VERIFY, à espera do dono". O dono aprovou o #877 em 25/11 17:37 e a emenda da ADR 0003 está "vigente". É só texto e não muda nenhuma decisão. Fica como nota para a próxima versão, porque a marca precisa ser idêntica à saída do `release`.

Superfície protegida em `b224ee09..9487d956`: nenhum arquivo em `.github/`, `.devcontainer/`, `.githooks/`, `scripts/`, `docs/regras/`, `docs/security/aceites/`, `agents/`, `templates/` ou `stacks/`. No diff entram `hooks/` (`_comum.py`, `conformidade.json`, `conformidade.py`, `hooks.json`, `salvar.py`) e `docs/adr/0003-hooks-deterministicos-e-silenciosos.md`. `tests/config.json` não está no diff, então nenhuma invariante sai. Medida dos hooks: `bin/forge-check comparar b224ee09 9487d956` dá `so-aperta: ... casos=239 aceites-novos=0`. Essa medida cobre só a decisão dos hooks que recusam.

## Só aperta ou neutro, por escrito (para o rótulo afrouxa-regra da promoção)
Rodei a catraca do pai de cada item contra ele, como o CI (script da base, cwd no item, `--base <pai>`):
- Saem 0: #877, #890, #896 e a marca.
- Saem 1, por tocar arquivo de controle protegido (ADR 0008): #874 (`bin/forge-check`), #886 (`hooks/_comum.py`, `hooks/conformidade.py`), #892 (`bin/forge-check`), #895 (`bin/forge-check`) e #897 (`tests/catraca.py`).
- O #885 sai 1 por `hooks/conformidade.py`, pela chave nova `modo_por_grupo` na política e pelos pulos de `tests/` de 38 para 41 (três `skipUnless(mkfifo)`).
- O #898 sai 1 por dois testes do `tests/test_fechar.py` trocados por guardas mais estritas.
- Avisos "valor esperado trocado", conferidos:
  - #874: `tests/test_forge_tamanho.py`, o aviso do brief passa de 90% para 80% do teto, ou seja, avisa antes.
  - #892: 10 testes de `tests/test_forge.py` e de `tests/test_volta_por_delta.py` passam a esperar `docs: ok` no stdout, com o rc igual. O `assertNotIn` novo prende que o ok só sai sem violação.

O PR da promoção vai pedir ao dono o rótulo `afrouxa-regra` por esses arquivos.

Frente à 0.47.18, nos controles que recusam:
- **Aperta:**
  - #885 e #886 (este, o A2 da segurança no #885): o texto da recusa e o `diretorio_comum` leem `.forge/perfil`, `.git`, `gitdir` e `commondir` sem `git`, sem esperar FIFO e só se forem arquivo regular. Antes, um FIFO ali fazia o prazo liberar push na main e `--force` na sessão do Forge. Agora recusa em menos de 0,25 s.
  - #898: o `forge-fechar --dry-run` sem a `origin/<branch>` para com código 1, em vez do antigo "1c: não rodou" com código 0.
  - #874: o aviso de tamanho do brief sai a 80%. O corte e a contradição barram igual antes e depois do arquivamento, e a pasta e o arquivo do arquivo não seguem link.
- **Neutro:**
  - #885: `modo_por_grupo` tem os seis grupos em `barrar`, e grupo fora do mapa, mapa ilegível ou outro valor também barram (falha fechada). A recusa é decidida antes da gravação no `comandos.jsonl`. Passar um grupo a `avisar` exige o rótulo do dono, porque a catraca vigia a política. Os três pulos novos dependem só de `mkfifo` existir e não pulam no CI.
  - #897: só mensagem da catraca. O código de saída e os ramos de decisão não mudam.
  - #892: só a linha `docs: ok` e o texto do brief e da skill. O rc do `forge-check docs` não muda.
  - #896: só a linha do sha no `forge-copia`, depois das recusas.
- **Afrouxa, com aceite do dono:**
  - #877: o hook `salvar` roda fora do sandbox e faz commit WIP na cópia local com `core.hooksPath` vazio, uma exceção ao `R-VERIFY` escrita na emenda da ADR 0003 (regra 4). O commit é só local, nunca em `main`, `master`, `develop` ou `homolog`, sem rede (o item 2 da ADR 0003 segue) e sem a checagem de cada gravação, porque o pre-push confere no envio. O dono aprovou em 25/11 07:37 e 17:37 e autorizou o rótulo do #877 em 25/11 21:32.
  - #895: a forma `via` da linha do CI no parecer, aceita pelo dono em 25/11 07:27. O descendente precisa descender do `commit:`, o diff entre os dois só pode tocar `docs/reviews/`, `docs/qa/` e `docs/security/`, e a falha do git fecha. O merge segue exigindo todos os checks do head.
- **Afrouxa, por desenho, sem regra com ID:** #890, o `forge-fechar --limpar` remove o clone de parecer já mesclado, e só a tag local `refs/tags/arquivo/*` deixa de prender o clone. Outra tag local, stash, branch local ou commit depois do head mesclado seguem prendendo. A catraca sai 0. Sem caminho de ataque realista: só quem já escreve no clone cria essa tag.

Nenhum teste foi apagado sem guarda mais estrita no lugar e nenhuma invariante saiu.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo nem pendente de aceite: o delta não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`. Os dois afrouxamentos com regra (#877 e #895) já têm a decisão do dono no pedido v0481. O merge na main da 0.47.19 tem a autorização do dono de 25/11 21:32 ("autorizo mesclar main versao 0.47.19 ate amanha"). O rótulo da promoção segue como ato do dono ou autorização gravada (ADR 0018).

Cartão, fora do delta da marca (G1.2), sem bloquear: CATRACA-SALVAR-PROTEGIDO. A catraca só vigia a remoção de hook em `hooks/hooks.json` (`tests/catraca.py:453`), e `hooks/salvar.py` não está em `PROTEGIDOS` (`tests/catraca.py:48`). Uma mudança futura nesse hook, que roda git fora do sandbox, passaria sem pedir o rótulo, por exemplo um `push` acrescentado. O PR ainda passaria pelos três pareceres e pelo CI, por isso a severidade é baixa. Correção mínima: incluir `hooks/salvar.py` em `PROTEGIDOS`. Dono: `devops-engineer`, com a revisão do `tech-lead`.

A suíte inteira vale pelo CI. No PR #905, no head `9487d956`, os runs 45803496622 (CI) e 45803496653 (Catraca), com `headSha` conferido, estão em `success`, e todos os checks que contam estão em `pass`, sem nenhum vermelho. O CI de push da develop em `cc4376fe` está verde (run 45750622760). O CI do PR de promoção continua sendo o portão. Localmente rodei só:
- `comparar`, `conferir-release` e `tests.test_changelog`;
- a catraca por item;
- a medida do teto;
- a junção por `merge-tree`;
- `shellcheck` no `bin/forge-fechar`, com o mesmo único SC2015 da base, na linha 672.

- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde

Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` estão fora do PATH. O delta não toca workflow nem dependência, e a busca de segredos foi feita por padrões.
