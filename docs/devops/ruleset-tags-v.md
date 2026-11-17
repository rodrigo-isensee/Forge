---
tipo: revisao-devops
contrato: 1
pedido: ruleset-tags-v
branch: melhoria/v0475-ruleset-tags
commit: bda457e4b8ed520a9061ed4e306a72acd331499b
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-17
---
# Ruleset de tags v*: proposta para o dono aplicar (v0474, E3.4)

Documento de proposta, não de review de código. Nenhum agente aplica (`R-CONFORMIDADE`): o dono executa. O `commit` do frontmatter é a base da branch (só este arquivo muda).

## Achados

## Decisão do dono e estado lido
Decisão (pedido v0474, 17/11): só a automação de release cria `refs/tags/v*`; ninguém mais (nem administrador, nem a conta do dono que os agentes usam) cria, move ou apaga.

Lido por `gh api` GET em 17/11/2026:
- `repos/rodrigo-isensee/Forge/rulesets`: 3 rulesets, todos `target: branch` (`checks-obrigatorios-develop-main` ativo, `mainRuleset` desativado, `merge-commit-homolog-main` ativo). **Nenhum de tag.** O de `homolog`/`main` tem bypass `RepositoryRole` id 5 (admin), `always`.
- Repositório de usuário (`owner.type: User`), público; `permissions.admin: true` para a conta em uso.
- `.github/workflows/release.yml`: dispara em `push` na `main`; o job `release` (`contents: write`) roda `gh release create "v$versao" --target "$GITHUB_SHA"` com `GH_TOKEN: ${{ github.token }}`. A tag nasce **pela API de release**, ator `github-actions` (integração id `15368`, o mesmo `integration_id` que os checks obrigatórios já usam).
- Há 57 tags `v*` hoje.

## O que o ruleset fecha e o que fica (leia antes de decidir)
**Fecha:** `git push origin vX`, `gh api -X POST .../git/refs`, `gh release create` e `POST .../releases` feitos com a conta do dono (a que os agentes usam), mover e apagar as 57 tags existentes, e o engano de qualquer pessoa ou agente. Os hooks atuais não barram `gh release create` nem `git push` de tag nova; o ruleset fecha esses dois.

**Não fecha (resíduo, achado A1 do parecer `docs/security/v0475-ruleset-tags.md`):** hoje o token dos agentes tem os escopos `repo`, `workflow`, `admin:public_key` e `delete_repo`, e a conta tem `permissions.admin: true`. Enquanto for assim:
- um workflow novo ou editado numa branch `melhoria/*` declara `permissions: contents: write` e roda `gh release create vX` com `github.token`; o ator é `github-actions`, que está no bypass, e o ruleset não distingue o workflow nem a branch de origem;
- a conta administra o repositório e pode desativar ou apagar o ruleset por chamada HTTP direta (o hook `conformidade` barra `gh api` mutante em `rulesets`, mas não outro cliente com o mesmo token); os rulesets de branch também dão bypass `always` ao papel admin.

Conclusão: com o token atual, o ruleset barra o engano e o comando direto, **não** um agente que edite workflow ou desative o ruleset. Caminho de ataque: agente desviado (injeção vinda de conteúdo de um projeto, ou erro) cria `v9.99.0` num commit qualquer e a atualização dos projetos a consome. Impacto alto, probabilidade baixa (vários passos deliberados, contra os hooks). O fechamento está em "Token fino para os agentes" (decisão do dono).

## O que o ruleset faz
Alvo `refs/tags/v*`, regras `creation`, `update`, `deletion`. Sem bypass, **ninguém** passa, inclusive admin e o próprio `github-actions`. Por isso a lista de bypass importa.

## JSON exato
Arquivo `ruleset-tags-v.json` (corpo de `POST /repos/rodrigo-isensee/Forge/rulesets`):

```json
{
  "name": "tags-v-so-release",
  "target": "tag",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["refs/tags/v*"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "creation" },
    { "type": "update" },
    { "type": "deletion" }
  ],
  "bypass_actors": [
    { "actor_id": 15368, "actor_type": "Integration", "bypass_mode": "always" }
  ]
}
```

Aplicar por linha de comando (o dono, com a conta dele): `gh api -X POST repos/rodrigo-isensee/Forge/rulesets --input ruleset-tags-v.json`. A resposta 201 traz o `id` do ruleset; guarde-o.
Confira já na resposta 201 (ou por `gh api repos/rodrigo-isensee/Forge/rulesets/<id> --jq .bypass_actors`) que `bypass_actors` voltou com `{"actor_id":15368,"actor_type":"Integration","bypass_mode":"always"}`. Lista vazia = bypass descartado em silêncio: passe ao caminho 1 antes da próxima release, em vez de esperar a release falhar.

## Limitação real do bypass (leia antes de aplicar)
- `bypass_actors` aceita papel do repositório, time (só em organização), deploy key, administrador de organização e **integração (GitHub App)**. O `github-actions` é a integração `15368`, mas **não confirmei** que o GitHub a aceita como bypass: a tela costuma não listá-la e a API pode responder 422. Não há como testar sem aplicar, e agente não aplica. **Trate o JSON acima como tentativa**; o dono confere o resultado (próxima seção).
- Se a API responder 422 ou a tela não oferecer "GitHub Actions": **não use o papel Admin como bypass** (libera a conta do dono, contra a decisão). Caminhos, em ordem de preferência, todos sem custo (`R-CUSTO`):
  1. **GitHub App próprio do dono (preferido)** (grátis), instalado só neste repositório com `contents: write`; o workflow troca a chave do App por um token de instalação (`actions/create-github-app-token` fixada por SHA) e o usa no `gh release create`; o App entra como bypass (`actor_type: Integration`, `actor_id` = id do App). Exige o segredo da chave privada e a mudança do workflow; ambos do dono.
  2. **Deploy key** com escrita, sem outro uso, como bypass (`actor_type: DeployKey`); o workflow empurra a tag por SSH. Exige segredo e mudança do workflow. Limite: o bypass `DeployKey` vale para **toda** deploy key do repositório, e a conta admin cadastra uma nova; por isso o App é preferido.
  - **Nos caminhos 1 e 2 o segredo (chave privada do App ou da deploy key) fica num environment, nunca como segredo do repositório.** Segredo de repositório é lido por qualquer workflow de qualquer branch (push ou PR do próprio repositório) e o resíduo se repetiria com o App. Crie o environment `release` (Settings > Environments; grátis em repositório público; hoje há 0) com Deployment branches = Selected branches = `main`, guarde o segredo nele, e o job `release` declara `environment: release`. A proteção só fecha junto com o token fino (sem Administration o agente não troca a regra do environment).
  3. Sem nenhum dos dois, não há como separar o `github-actions` da conta do dono por ruleset em repositório de usuário. Resta o ruleset **só com `update` e `deletion`** (ninguém move nem apaga tag; a criação fica livre). Fica abaixo da decisão; só com aceite expresso do dono.
- Efeito colateral: sem bypass funcionando, o job `release` falha ao criar a tag (403/422 em `gh release create`) e a release da `main` não sai até o dono corrigir ou reverter. Aplique **fora de uma release em andamento** e teste (próxima seção).

## Passo a passo na tela do GitHub
1. `https://github.com/rodrigo-isensee/Forge` → **Settings** → **Rules** → **Rulesets** → **New ruleset** → **New tag ruleset**.
2. **Ruleset name:** `tags-v-so-release`. **Enforcement status:** `Active`.
3. **Bypass list** → **Add bypass**: procure **GitHub Actions** (ou o App do dono, se for o caminho 1). Modo **Always**. Se "GitHub Actions" não aparecer, veja "Limitação real"; **não** adicione "Repository admin" nem a conta do dono.
4. **Target tags** → **Add target** → **Include by pattern** → `v*`.
5. **Rules:** marque **Restrict creations**, **Restrict updates** e **Restrict deletions**; desmarque o resto.
6. **Create**.

## Token fino para os agentes (proposta ao dono; fecha a edição de workflow e a desativação de regras, não a `main`)
Sem custo (`R-CUSTO`). **O que o token fino não faz (achado A5 do parecer `docs/security/v0475-ruleset-tags.md`):** ele continua sendo da conta admin do dono. O ruleset 25432260 (`homolog`, `main`) exige 0 aprovações e dá bypass `RepositoryRole` 5 (admin) `always`; lido em 17/11: `current_user_can_bypass: always`, regras `pull_request`, `required_status_checks`, `non_fast_forward`, `deletion` (**sem** `update`). Com `Contents: write` o agente mescla PR na `main` com os checks verdes, sem aprovação humana, e talvez empurre direto (o bypass é por usuário); o merge roda `release.yml`, que cria `v<versão>`. Só os hooks (`R-MAIN`) seguram isso. O token fino fecha workflow e regra, **não a `main`**; o fechamento da `main` está em "Conta separada para os agentes".
 Nenhum agente cria nem troca token; o dono executa e decide (`R-CONFORMIDADE`, `R-DECISAO`).

Passo a passo (tela do GitHub, conta do dono):
1. Anote os escopos do token atual (`gh auth status`) e onde ele está configurado para os agentes, para poder voltar.
2. **Settings** (da conta) > **Developer settings** > **Personal access tokens** > **Fine-grained tokens** > **Generate new token**.
3. **Token name:** `forge-agentes`. **Expiration:** curta (30 a 90 dias; anote a renovação).
4. **Resource owner:** a conta do dono. **Repository access:** **Only select repositories** > `rodrigo-isensee/Forge` (só este).
5. **Repository permissions:** `Contents: Read and write` (push de branch e, também, mesclar PR e criar release/ref), `Pull requests: Read and write`, `Issues: Read and write` (rótulos e comentários), `Actions: Read` (ler execuções), `Commit statuses: Read` (checks do PR) e `Metadata: Read` (automático). **Administration: No access. Workflows: No access.** Todo o resto, sem acesso. Nenhuma permissão de conta.
6. **Generate token**, copie uma vez e coloque-o no lugar do token atual na sessão dos agentes (`GH_TOKEN` ou `gh auth login --with-token`). O token antigo (`admin`, `workflow`, `delete_repo`) **não** fica no config do `gh` (`~/.config/gh/hosts.yml`), em `GH_TOKEN`, no `.git-credentials` nem em qualquer variável ou arquivo do usuário do sistema em que os agentes rodam: o `gh` e o `git push` leem esses lugares e o agente voltaria a ter admin (achado A8). Guarde-o fora da máquina dos agentes ou sob outro usuário do sistema (gerenciador de senhas do dono) e, melhor, revogue-o depois do período de uso sem erro.
7. Conferir, com o token novo ativo (achado A6; `GET rulesets` só pede Metadata read e o repositório é público, então responde 200 mesmo com o token certo e **não** serve de prova; `.permissions.admin` também não prova o token):
   - `gh api repos/rodrigo-isensee/Forge/keys` deve dar **403** (Administration read ausente);
   - `gh api repos/rodrigo-isensee/Forge/rulesets/25432260 --jq .current_user_can_bypass` deve dar `never` (só com a conta separada; com o token fino da conta admin continua `always`, e isso é o resíduo A5);
   - `gh pr checks <n> --json name,state` em um PR aberto deve responder (Commit statuses; achado A7);
   - um `git push` que toque `.github/workflows/` deve ser recusado.

O que isso quebra ou muda no fluxo atual (para o dono decidir):
- **Pushes de branch `melhoria/*`:** continuam (Contents: write). Push que toque `.github/workflows/` passa a ser recusado: já era o desenho (o bot não tem `workflow`), mas hoje o token dos agentes tem o escopo e a recusa dependia de disciplina; agora é estrutural, e o dono segue enviando mudança de workflow.
- **PRs, comentários e rótulos:** abrir, editar e comentar PR continua (Pull requests e Issues em escrita). O rótulo `afrouxa-regra` continua sendo do dono, como hoje.
- **`gh run view` e `gh run list`:** continuam (Actions: Read). **`gh run rerun` e `gh workflow run` deixam de funcionar** (exigem Actions: write). Reexecutar o mesmo sha fica com o dono, ou o dono libera `Actions: Read and write`, sabendo que isso permite disparar `workflow_dispatch` (hoje só `ci.yml`, com jobs `contents: read`); o resíduo não reabre, porque editar workflow continua sem `Workflows`.
- **`gh api` em proteção de branch, rulesets, environments, segredos, deploy keys e configuração do repositório:** deixam de funcionar (Administration). Já eram do dono por `R-CONFORMIDADE`; o resíduo de desativar o ruleset some.
- **Merge de PR:** mesclar PR exige `Contents: write` (não Pull requests). Com o token fino **da conta admin**, o bypass de admin do ruleset 25432260 continua valendo para o agente: ele mescla na `main`, e o release cria a tag desse commit (resíduo A5). A criação direta de release fica barrada pelo ruleset de tag; o merge na `main` não. Fechamento: próxima seção.
- **Outros repositórios:** o token é só deste; se os agentes usam a mesma conta em outros repositórios, cada um precisa do seu token fino ou segue no atual (o resíduo permanece lá).
- **Limites do token fino:** expira e exige renovação; confira pelos GET acima antes de tirar o token antigo da sessão; revogue o antigo só depois de um período de uso sem erro. Reverter é recolocar o token antigo.

## Conta separada para os agentes (fecha a `main`; decisão do dono)
Sem custo (`R-CUSTO`): conta gratuita adicional do GitHub. Nenhum agente cria conta, convida nem aplica regra (`R-CONFORMIDADE`); o dono executa e decide (`R-DECISAO`). Em repositório de usuário, colaborador **não** é admin.
1. Crie uma conta GitHub nova só para os agentes (e-mail próprio, 2FA ligado, nome como `forge-agentes-<dono>`). Confira nos termos do GitHub a regra para conta de máquina no momento.
2. Com a conta do dono: **Settings** > **Collaborators** > **Add people** > a conta nova, papel **Write** (nunca Maintain nem Admin). A conta nova aceita o convite.
3. Na conta nova, gere o token fino da seção anterior (passos 2 a 5). O repositório é do dono: o colaborador o vê em "Only select repositories". Sem Administration e sem Workflows.
4. No ruleset 25432260 (**Settings** > **Rules** > **Rulesets**), marque **Restrict updates** (regra `update`), mantendo o bypass do papel **Repository admin** em **Always**; o mesmo no ruleset de `homolog`, se for outro. Efeito: só o admin (o dono) atualiza `main` e `homolog`; a conta colaboradora, sem bypass, não mescla nem empurra nelas. Atenção: a promoção `develop` > `homolog` hoje é do `tech-lead` (agente); com Restrict updates na `homolog` ela passa a ser do dono, ou pede outro desenho (decisão dele). Não marque `update` na `develop` (os agentes mesclam lá).
5. Troque o token na sessão dos agentes pelo da conta nova e guarde o antigo longe deles (passo 6 da seção anterior).
6. Conferir com o token da conta nova: `gh api repos/rodrigo-isensee/Forge/rulesets/25432260 --jq .current_user_can_bypass` = `never`; `gh api repos/rodrigo-isensee/Forge/keys` = 403; o merge de um PR de teste para a `main` recusado (para a `develop`, aceito); push direto na `main` recusado.

**Risco que sobra sem a conta separada** (risco aceito do dono, se ele não a adotar; `R-DECISAO`): o token fino, da conta admin, mescla PR na `main` com checks verdes e 0 aprovações (e talvez empurra direto, pelo bypass por usuário), e o `release.yml` cria a tag `v*` desse commit, que os projetos consomem. Impacto alto, probabilidade baixa; as únicas barreiras são os hooks e a disciplina do fluxo (`R-MAIN`), que um agente desviado pode contornar. Restrict updates **sem** conta separada não ajuda: o bypass de admin vale para a mesma conta. O token fino fecha só a edição de workflow e a desativação de regra, não a `main`.

## Como conferir depois
1. Leitura: `gh api repos/rodrigo-isensee/Forge/rulesets --jq '.[]|select(.target=="tag")|{name,enforcement}'` mostra `tags-v-so-release` `active`; `gh api repos/rodrigo-isensee/Forge/rulesets/<id> --jq '{conditions,bypass_actors,rules:[.rules[].type]}'` bate com o JSON.
2. Recusa, mover e apagar: com o ruleset valendo, uma tag de teste nunca nasce, então a tag para o teste de apagar é criada **antes de aplicar**. Antes do passo "Create", o dono cria uma tag fora de SemVer num commit antigo (`git tag v0-teste-ruleset <commit-antigo> && git push origin v0-teste-ruleset`; `bin/forge_versoes.py` só lê `vX.Y.Z` inteiro, então ela não chega aos projetos). Depois de aplicar: (a) criar outra, `git tag v0-teste-ruleset-2 && git push origin v0-teste-ruleset-2`, deve falhar com `GH013: Repository rule violations`; se **passar**, o ruleset não vale: desative-o, apague a tag e revise; (b) mover (`git push --force origin HEAD:refs/tags/v0-teste-ruleset`) e (c) apagar (`git push origin :refs/tags/v0-teste-ruleset`) devem falhar do mesmo modo. Nunca em tag real. Para apagar a tag de teste ao fim, o dono desativa o ruleset por um instante e o reativa.
3. Aceite do bypass: na **próxima release** (merge `homolog` → `main` pelo dono), o job `release` do workflow `Release` deve criar a tag e a release. Confira com `gh run list --workflow=release.yml -L 1` (success) e `gh release view vX.Y.Z`. Falhou com 403/422 na criação da tag: o bypass não vale; use o caminho 1 ou 2, ou reverta.

## Como reverter
- Tela: **Settings** → **Rules** → **Rulesets** → `tags-v-so-release` → **Disable** (mantém a configuração) ou **Delete**.
- Linha de comando: `gh api -X PUT repos/rodrigo-isensee/Forge/rulesets/<id> -f enforcement=disabled` ou `gh api -X DELETE repos/rodrigo-isensee/Forge/rulesets/<id>`.
- É também o único jeito de corrigir uma tag errada depois: o dono desativa o ruleset, corrige a tag e reativa. A regra protege do engano e do comando direto; **não** de quem administra o repositório nem, com o token atual, de um agente que edite workflow ou desative o ruleset (ver "O que o ruleset fecha e o que fica").

## O workflow de release precisa mudar?
- **Com o bypass do `github-actions` aceito pelo GitHub: não.** `release.yml` já cria a tag por `gh release create` com `github.token`, ator `github-actions`. O passo "já existe; nada a publicar" só lê a tag e continua válido. Nenhuma permissão nova.
- **Com App ou deploy key (caminhos 1 e 2): sim**, só o passo "Tag e release" (token do App em `GH_TOKEN`, ou `git push` da tag por SSH seguido de `gh release create` sobre ela). Mudança em `.github/` vai em branch `melhoria/*`, com o rótulo `afrouxa-regra` do dono se tocar arquivo protegido, e é enviada pelo dono (o token do bot não tem o escopo `workflow`). Preparo quando o dono escolher o caminho. `R-MAIN` segue: o workflow só roda depois do merge do dono.

## Tags v* que já existem (57)
O ruleset **não** as altera nem as remove. `creation` só vale para refs novas; `update` e `deletion` passam a protegê-las: nenhuma pode ser movida nem apagada sem desativar o ruleset. Antes de aplicar, confira que nenhuma está errada (`git ls-remote --tags origin 'v*'`), porque depois só o dono, desativando o ruleset, a corrige. Tags que não começam com `v` ficam fora.

## Custo e rollback
Custo zero: ruleset de tag e GitHub App são gratuitos em repositório público (`R-CUSTO`); nenhum minuto de CI novo. Rollback em "Como reverter".
