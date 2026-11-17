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

## Limitação real do bypass (leia antes de aplicar)
- `bypass_actors` aceita papel do repositório, time (só em organização), deploy key, administrador de organização e **integração (GitHub App)**. O `github-actions` é a integração `15368`, mas **não confirmei** que o GitHub a aceita como bypass: a tela costuma não listá-la e a API pode responder 422. Não há como testar sem aplicar, e agente não aplica. **Trate o JSON acima como tentativa**; o dono confere o resultado (próxima seção).
- Se a API responder 422 ou a tela não oferecer "GitHub Actions": **não use o papel Admin como bypass** (libera a conta do dono, contra a decisão). Caminhos, em ordem de preferência, todos sem custo (`R-CUSTO`):
  1. **GitHub App próprio do dono** (grátis), instalado só neste repositório com `contents: write`; o workflow troca a chave do App por um token de instalação (`actions/create-github-app-token` fixada por SHA) e o usa no `gh release create`; o App entra como bypass (`actor_type: Integration`, `actor_id` = id do App). Exige o segredo da chave privada e a mudança do workflow; ambos do dono.
  2. **Deploy key** com escrita, sem outro uso, como bypass (`actor_type: DeployKey`); o workflow empurra a tag por SSH. Exige segredo e mudança do workflow.
  3. Sem nenhum dos dois, não há como separar o `github-actions` da conta do dono por ruleset em repositório de usuário. Resta o ruleset **só com `update` e `deletion`** (ninguém move nem apaga tag; a criação fica livre). Fica abaixo da decisão; só com aceite expresso do dono.
- Efeito colateral: sem bypass funcionando, o job `release` falha ao criar a tag (403/422 em `gh release create`) e a release da `main` não sai até o dono corrigir ou reverter. Aplique **fora de uma release em andamento** e teste (próxima seção).

## Passo a passo na tela do GitHub
1. `https://github.com/rodrigo-isensee/Forge` → **Settings** → **Rules** → **Rulesets** → **New ruleset** → **New tag ruleset**.
2. **Ruleset name:** `tags-v-so-release`. **Enforcement status:** `Active`.
3. **Bypass list** → **Add bypass**: procure **GitHub Actions** (ou o App do dono, se for o caminho 1). Modo **Always**. Se "GitHub Actions" não aparecer, veja "Limitação real"; **não** adicione "Repository admin" nem a conta do dono.
4. **Target tags** → **Add target** → **Include by pattern** → `v*`.
5. **Rules:** marque **Restrict creations**, **Restrict updates** e **Restrict deletions**; desmarque o resto.
6. **Create**.

## Como conferir depois
1. Leitura: `gh api repos/rodrigo-isensee/Forge/rulesets --jq '.[]|select(.target=="tag")|{name,enforcement}'` mostra `tags-v-so-release` `active`; `gh api repos/rodrigo-isensee/Forge/rulesets/<id> --jq '{conditions,bypass_actors,rules:[.rules[].type]}'` bate com o JSON.
2. Recusa (não destrutivo): com a conta do dono, `git tag v9.9.9-teste && git push origin v9.9.9-teste` deve falhar com `GH013: Repository rule violations` (regra de criação). Se **passar**, o ruleset não vale: desative-o, apague a tag de teste e revise. Para a proteção contra apagar, tente só na tag de teste (`git push origin :refs/tags/v9.9.9-teste`); nunca em tag real.
3. Aceite do bypass: na **próxima release** (merge `homolog` → `main` pelo dono), o job `release` do workflow `Release` deve criar a tag e a release. Confira com `gh run list --workflow=release.yml -L 1` (success) e `gh release view vX.Y.Z`. Falhou com 403/422 na criação da tag: o bypass não vale; use o caminho 1 ou 2, ou reverta.

## Como reverter
- Tela: **Settings** → **Rules** → **Rulesets** → `tags-v-so-release` → **Disable** (mantém a configuração) ou **Delete**.
- Linha de comando: `gh api -X PUT repos/rodrigo-isensee/Forge/rulesets/<id> -f enforcement=disabled` ou `gh api -X DELETE repos/rodrigo-isensee/Forge/rulesets/<id>`.
- É também o único jeito de corrigir uma tag errada depois: o dono desativa o ruleset, corrige a tag e reativa (a regra protege de agente e de engano, não de quem administra o repositório).

## O workflow de release precisa mudar?
- **Com o bypass do `github-actions` aceito pelo GitHub: não.** `release.yml` já cria a tag por `gh release create` com `github.token`, ator `github-actions`. O passo "já existe; nada a publicar" só lê a tag e continua válido. Nenhuma permissão nova.
- **Com App ou deploy key (caminhos 1 e 2): sim**, só o passo "Tag e release" (token do App em `GH_TOKEN`, ou `git push` da tag por SSH seguido de `gh release create` sobre ela). Mudança em `.github/` vai em branch `melhoria/*`, com o rótulo `afrouxa-regra` do dono se tocar arquivo protegido, e é enviada pelo dono (o token do bot não tem o escopo `workflow`). Preparo quando o dono escolher o caminho. `R-MAIN` segue: o workflow só roda depois do merge do dono.

## Tags v* que já existem (57)
O ruleset **não** as altera nem as remove. `creation` só vale para refs novas; `update` e `deletion` passam a protegê-las: nenhuma pode ser movida nem apagada sem desativar o ruleset. Antes de aplicar, confira que nenhuma está errada (`git ls-remote --tags origin 'v*'`), porque depois só o dono, desativando o ruleset, a corrige. Tags que não começam com `v` ficam fora.

## Custo e rollback
Custo zero: ruleset de tag e GitHub App são gratuitos em repositório público (`R-CUSTO`); nenhum minuto de CI novo. Rollback em "Como reverter".
