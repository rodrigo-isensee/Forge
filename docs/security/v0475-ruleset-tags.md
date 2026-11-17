---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ruleset-tags
commit: 7f7a69424b2bbb2457de070045a2638b9c93963c
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: ruleset de tags v* (v0474, E3.16, revalidação)

Objeto: `docs/devops/ruleset-tags-v.md` no head 7f7a6942 (resposta E3.12 do devops ao parecer E3.7 em f224ac62, que fica no git). Leitura no GitHub só por `gh api` GET e pela documentação pública do GitHub.

## Gatilhos
Gatilhos: CI e release, proteção de branch e tag, credenciais e tokens, cadeia de suprimentos (tag v* é o que a atualização dos projetos consome).

## Achados
- A9 (bloqueante) docs/devops/ruleset-tags-v.md:113 · O passo 3 da conta separada não funciona: o GitHub não aceita token fino de colaborador em repositório de outra conta pessoal. O único fechamento da main fica inaplicável e o dono desiste ou fica no resíduo A5. Usar token clássico só com `repo`.
- A10 (recomendado) docs/devops/ruleset-tags-v.md:97 · Token fino não chama a Checks API, e os checks do CI são check runs: `gh pr checks` pode falhar mesmo com Commit statuses. Dizer o que fazer se a conferência falhar (forge-fechar e promover-homolog dependem dela).
- A11 (recomendado) docs/devops/ruleset-tags-v.md:116 · A conferência por merge real de PR de teste na main, se a regra estiver errada, põe o commit de teste na main e roda o release. Trocar por `rules/branches/main` (regra `update` presente) mais `current_user_can_bypass` = `never`.
- A12 (recomendado) docs/devops/ruleset-tags-v.md:112 · Repositório de conta pessoal não tem seletor de papel (Write, Maintain, Admin): o colaborador recebe o acesso fixo de colaborador, sem administração. Ajustar o texto para o dono não procurar o seletor.

## Sondas

## Detalhe dos achados

**Delta lido:** `forge-check parecer delta` = nenhum arquivo do domínio mudou em `f224ac62..7f7a6942` (o diff é `docs/devops/ruleset-tags-v.md` e o parecer anterior). Reli o documento inteiro, porque é o objeto, e conferi se o dono aplica sozinho cada caminho (ruleset de tag, token fino na conta do dono, conta separada, conferências).

**Achados anteriores:**
- A1 a A4: resolvidos na rodada anterior; o texto se manteve (doc:26-33, 64, 69-71, 122).
- A5 resolvido no texto: a frase falsa saiu; doc:84 e doc:105 declaram que o token fino da conta admin mescla na `main`; doc:118 registra o risco sem a conta separada como risco aceito do dono (`R-DECISAO`); doc:114 avisa que a promoção para a `homolog` passa ao dono. O fechamento proposto, porém, não é aplicável como escrito: A9.
- A6 resolvido: doc:94-98 troca a prova por `keys` (403) e `current_user_can_bypass`, e marca `GET rulesets` e `.permissions.admin` como não conclusivos.
- A7 resolvido: `Commit statuses: Read` (doc:92) e `gh pr checks` (doc:97); doc:105 diz que o merge exige Contents write. Ressalva nova em A10.
- A8 resolvido: doc:93 lista `hosts.yml`, `GH_TOKEN`, `.git-credentials` e manda guardar o token antigo fora do usuário dos agentes.

**Estado lido (GET, 17/11):** ruleset 25432260 `merge-commit-homolog-main` tem alvo só `homolog` e `main` (a `develop` fica fora, então Restrict updates nele não afeta a `develop`, como doc:114 pede); 26701749 cobre `develop` e `main` só com checks obrigatórios. Nenhum workflow empurra em `main` ou `homolog` (`release.yml` cria a tag pela API de release), então Restrict updates com bypass só do admin não quebra a automação.

**A9:** evidência: documentação do GitHub, "Managing your personal access tokens", seção "Fine-grained personal access tokens limitations": entre as lacunas, "Using fine-grained personal access token to contribute to repositories where the user is an outside or repository collaborator"; e "Each token is limited to access resources owned by a single user or organization". A conta dos agentes, colaboradora de `rodrigo-isensee/Forge`, não usa token fino nesse repositório (doc:113 diz que usa). Caminho do risco: o dono, aplicando sozinho, trava no passo 3; ou fica com o token da conta admin (resíduo A5: agente desviado mescla na `main` sem aprovação, o release cria `v*`, os projetos consomem; impacto alto), ou recorre a um token clássico amplo na conta nova sem saber o escopo mínimo. Severidade alta (é o único fechamento proposto para um risco de impacto alto). Correção mínima (devops, texto): no passo 3 da conta separada, token **clássico** da conta nova só com o escopo `repo` (sem `workflow`, sem `admin:org`, sem `admin:repo_hook`, sem `admin:public_key`, sem `delete_repo`), expiração curta; o limite de administração vem do papel de colaborador (não do token) e o de workflow, da falta do escopo `workflow`; a conta nova não tem outros repositórios, então `repo` não alcança mais nada. O token fino continua valendo só para o caminho sem conta separada (doc:83-107). As conferências do passo 6 ficam (`keys` = 403, `current_user_can_bypass` = `never`) e acrescenta-se: push que toque `.github/workflows/` recusado. Esforço P; dono: devops; aplicação e decisão: dono.

**A10:** a mesma seção da documentação lista "Using fine-grained personal access token to call the Checks API"; os checks do CI são check runs do Actions, não status de commit. `gh pr checks` (usado por `bin/forge-fechar` e `scripts/promover-homolog.py`) pode falhar ou vir incompleto com token fino. O passo 7 já faz o dono descobrir; falta dizer o que fazer: se falhar, manter o token atual até decidir, ou adotar a conta separada com token clássico `repo` (A9), em que a leitura funciona. Esforço P; dono: devops.

**A11:** se o Restrict updates não ficou ativo ou o bypass está errado, o "merge de um PR de teste para a `main`" (doc:116) é aceito: um commit de teste entra na `main` (versão de todos os projetos, `R-MAIN`) e roda `release.yml`. Correção: conferir sem escrever, por `gh api repos/rodrigo-isensee/Forge/rules/branches/main --jq '[.[].type]'` (deve conter `update`) e `current_user_can_bypass` = `never` com o token da conta nova; se quiser prova de escrita, um `git push` direto de commit de teste para a `homolog`, nunca para a `main`. Esforço P; dono: devops.

**A12:** em repositório de conta pessoal, "Add people" convida colaborador sem escolha de papel; o acesso é o fixo de colaborador (escreve, não administra). O texto "papel Write (nunca Maintain nem Admin)" (doc:112) manda o dono procurar uma opção que não existe. Correção: dizer que o colaborador recebe acesso de escrita fixo e que a posse do repositório nunca passa à conta nova. Esforço P; dono: devops.

**Caminhos conferidos como aplicáveis pelo dono sozinho:** ruleset de tag (JSON, tela, conferência do `bypass_actors`, teste com tag fora de SemVer criada antes; doc:38-81, 120-123); token fino na conta do dono (doc:87-98: resource owner é a própria conta); Restrict updates no 25432260 com bypass do admin (doc:114). Não aplicável como escrito: passo 3 da conta separada (A9).

## Riscos aceitos e ferramentas
Nenhum risco aceito gravado; o resíduo A5 sem conta separada está escrito como risco a aceitar pelo dono (doc:118), sem aceite em `docs/security/aceites/`. Ferramentas: `forge-check parecer delta`; `gh api` GET (lista de rulesets e 26701749, 24947028, 25432260 com `current_user_can_bypass`); leitura da página "Managing your personal access tokens" da documentação do GitHub; leitura estática de `.github/workflows/*.yml`. Lacunas: gitleaks, zizmor e actionlint fora do PATH (não se aplicam a documento sem segredo nem workflow alterado). Suíte: diff só de documentação; sem teste novo de abuso a rodar.
