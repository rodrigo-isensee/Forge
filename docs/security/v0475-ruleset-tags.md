---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ruleset-tags
commit: f224ac62c5dfef667c9f26aea9730d92d63dbb99
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: ruleset de tags v* (v0474, E3.7, revalidação)

Objeto: `docs/devops/ruleset-tags-v.md` no head f224ac62 (resposta E3.6 do devops ao parecer E3.5 em 378733ae, que fica no git). Leitura no GitHub só por `gh api` GET.

## Gatilhos
Gatilhos: CI e release, proteção de branch e tag, credenciais e tokens, cadeia de suprimentos (tag v* é o que a atualização dos projetos consome).

## Achados
- A5 (bloqueante) docs/devops/ruleset-tags-v.md:100 · "o bypass de admin sai da conta dos agentes e a main continua só do dono" é falso: o token fino segue na conta do dono (admin); a main exige 0 aprovações e Contents write mescla PR; o merge na main roda release.yml, que cria v*. Declarar o resíduo e o fechamento real.
- A6 (bloqueante) docs/devops/ruleset-tags-v.md:93 · A conferência do passo 7 está errada: GET rulesets só exige Metadata read (e o repo é público), então responde 200 com o token fino certo; `.permissions.admin` não está provado refletir o token. Trocar por GET keys (403) e current_user_can_bypass.
- A7 (recomendado) docs/devops/ruleset-tags-v.md:91 · Incluir Commit statuses: Read e conferir `gh pr checks --json` (usado em bin/forge-fechar e scripts/promover-homolog.py) no passo 7; e corrigir a linha 100: mesclar PR exige Contents write, não Pull requests.
- A8 (recomendado) docs/devops/ruleset-tags-v.md:92 · Dizer onde guardar o token antigo: fora da máquina ou do usuário dos agentes (não no config do gh nem em variável da sessão), senão o agente o lê e o resíduo volta.

## Sondas

## Detalhe dos achados

**Delta lido:** `forge-check parecer delta` = nenhum arquivo do domínio mudou em `378733ae..f224ac62` (o diff é `docs/devops/ruleset-tags-v.md` e o parecer anterior). Reli o documento inteiro, porque é o objeto do parecer.

**Achados anteriores:**
- A1 resolvido no que pedia: a seção "O que o ruleset fecha e o que fica" (doc:26-33) declara o resíduo do token (workflow editado, ruleset desativado) e a frase falsa da reversão foi corrigida (doc:112). O fechamento proposto, porém, repete o padrão em outro ponto: A5.
- A2 resolvido: segredo em environment `release` só da `main`, job com `environment: release`, limite da deploy key e App preferido (doc:69-71).
- A3 resolvido: conferência do `bypass_actors` na resposta 201 (doc:64).
- A4 resolvido: tag de teste fora de SemVer criada antes de aplicar; mover para HEAD é fast-forward, então o `pre-push` local não barra e o GH013 vem do servidor; apagar não passa pelo hook (`.githooks/pre-push:148-160`).

**Passo a passo do token fino, conferido contra a tabela de permissões de token fino da documentação do GitHub:** `Workflows: No access` barra push em `.github/workflows/` (certo); `Administration: No access` barra POST/PUT/DELETE de rulesets, keys e environments (certo); `rerun` e `dispatches` exigem Actions write (certo, doc:98); `POST releases` e `POST git/refs` exigem Contents write, e o ruleset de tag barra a conta (certo). O que falha: A5, A6, A7, A8.

**A5:** evidência: ruleset 25432260 (`homolog`, `main`, lido): regra `pull_request` com `required_approving_review_count: 0`, bypass `RepositoryRole` 5 `always`, `current_user_can_bypass: always`; `PUT .../pulls/{n}/merge` exige Contents write (tabela do GitHub), que o token fino recebe (doc:91); `.github/workflows/release.yml:6-8` roda em `push` na `main` e cria `v<versão do plugin.json>`. Caminho de ataque: agente desviado, com o token fino, abre PR para a `main` e mescla com os checks verdes, sem aprovação humana; se o bypass do papel admin vale para o token (é por usuário, e o token é do mesmo usuário), empurra direto na `main`. O release cria a tag `v*` desse commit e os projetos a consomem. Só os hooks (`R-MAIN`) seguram, que é a disciplina que A1 apontou. Severidade alta pelo impacto, probabilidade baixa. Correção mínima (devops, texto): (1) a seção do token diz que ele fecha a edição de workflow e a desativação de regras, não a `main`; (2) o fechamento real, sem custo, é uma conta separada para os agentes, colaboradora do repositório (em repositório de usuário, colaborador não é admin), com token fino sem Administration e sem Workflows, mais a regra `update` (Restrict updates) no ruleset 25432260, mantendo o bypass do papel admin (só o dono mescla na `main` e na `homolog`); (3) sem conta separada, o resíduo da `main` fica e é risco aceito do dono (`R-DECISAO`). Conferência: com o token dos agentes, `gh api repos/<repo>/rulesets/25432260 --jq .current_user_can_bypass` deve dar `never`. Esforço P (texto); dono: devops; decisão e aplicação: dono.

**A6:** evidência: tabela de permissões do GitHub, `GET /repos/{owner}/{repo}/rulesets` e `.../rulesets/{id}` = Metadata read; o repositório é público. A conferência "deve ser recusado" falha com o token certo, e o dono, aplicando sozinho, conclui que errou o token. Correção mínima: no passo 7, `gh api repos/<repo>/keys` deve dar 403 (Administration read); `gh api repos/<repo>/rulesets/<id-do-ruleset-de-tag> --jq .current_user_can_bypass` deve dar `never`; o push em `.github/workflows/` recusado continua; tirar `.permissions.admin` ou marcá-lo como não conclusivo. Esforço P; dono: devops.

**A7:** `gh pr checks --json` (`bin/forge-fechar`, `scripts/promover-homolog.py`) lê os checks do PR; com token fino, os status de commit exigem Commit statuses read. Em repositório público a leitura tende a passar sem ela, mas o passo 7 é onde o dono descobre a quebra antes de tirar o token antigo.

**A8:** o `gh` usa `GH_TOKEN` e também o token gravado no config dele; o `git push` usa o `gh` como ajudante de credencial (config lida). Se o token antigo fica no mesmo config ou no mesmo usuário do sistema, o agente o lê e volta a ter admin e workflow.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`; `gh api` GET (rulesets 25432260, 26701749 e a lista; `current_user_can_bypass`; environments); tabela "Permissions required for fine-grained personal access tokens" da documentação do GitHub (leitura); leitura estática de `release.yml`, `.githooks/pre-push`, `bin/forge-fechar`. Lacunas: gitleaks, zizmor e actionlint fora do PATH (não se aplicam a documento sem segredo nem workflow alterado). Suíte: diff só de documentação; sem teste novo de abuso a rodar.
