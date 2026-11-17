---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ruleset-tags
commit: 712c0c917143e2298a6faec06ee4c2be9b022f33
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: ruleset de tags v* (v0474, E3.19, revalidação)

Objeto: `docs/devops/ruleset-tags-v.md` no head 712c0c91 (resposta E3.18 do devops ao parecer E3.16 em 7f7a6942, que fica no git). Leitura no GitHub só por `gh api` GET e pela documentação pública do GitHub.

## Gatilhos
Gatilhos: CI e release, proteção de branch e tag, credenciais e tokens, cadeia de suprimentos (tag v* é o que a atualização dos projetos consome).

## Achados
- A9 (recomendado) docs/devops/ruleset-tags-v.md:113 · RESOLVIDO em 712c0c91: conta nova com token clássico só `repo`, sem `workflow`, `admin:*` nem `delete_repo`; a documentação do GitHub confirma a lacuna do token fino de colaborador e que `workflow` é escopo à parte de `repo`.
- A10 (recomendado) docs/devops/ruleset-tags-v.md:97 · RESOLVIDO em 712c0c91: se `gh pr checks` falhar, não afrouxar check nem ler por outro meio; manter o token atual até decidir ou adotar a conta separada.
- A11 (recomendado) docs/devops/ruleset-tags-v.md:116 · RESOLVIDO em 712c0c91: conferência só por leitura (`rules/branches/main` com `update`, `current_user_can_bypass` = `never`, `keys` = 403); sem merge de teste na main; prova de escrita só na homolog.
- A12 (recomendado) docs/devops/ruleset-tags-v.md:112 · RESOLVIDO em 712c0c91: conta pessoal tem só dono e colaborador, sem seletor de papel; a posse não passa à conta nova.
- A13 (recomendado) docs/devops/ruleset-tags-v.md:113 · "repo não alcança mais nada" vale enquanto a conta nova não entrar em organização: pela documentação, `repo` também gerencia recursos de organização. Acrescentar: não pôr a conta dos agentes em organização nem aceitar convite de outro repositório.

## Sondas

## Detalhe dos achados

**Delta lido:** `forge-check parecer delta` = nenhum arquivo do domínio mudou em `7f7a6942..712c0c91`; o diff é `docs/devops/ruleset-tags-v.md` (8 linhas) e o parecer anterior. Reli o documento inteiro (objeto) e conferi na documentação do GitHub o que ele afirma.

**Afirmações conferidas na documentação do GitHub (17/11):**
- "Managing your personal access tokens", limitações do token fino: "contribute to repositories where the user is an outside or repository collaborator", "call the Checks API" e "Each token is limited to access resources owned by a single user or organization" (doc:97, doc:113).
- "Scopes for OAuth apps": `repo` dá acesso a código, commit statuses, convites, colaboradores e webhooks; `workflow` é escopo separado ("add and update GitHub Actions workflow files"), então `repo` sem `workflow` não altera workflow (doc:113, doc:116). Ressalva da própria página: arquivo de workflow idêntico (caminho e conteúdo) a um de outra branch do repositório pode ser enviado sem o escopo; não reabre o resíduo A1, porque só replica workflow que já existe no repositório.
- "Permission levels for a personal account repository": dois níveis, dono e colaborador; convidar colaborador, mesclar em branch protegida sem aprovação e configurações ficam com o dono (doc:110, doc:112).
- "Available rules for rulesets": Restrict updates deixa só quem tem bypass empurrar na ref; a conta colaboradora, sem bypass, não mescla nem empurra em `main` e `homolog` (doc:114).

**Estado lido (GET, 17/11):** `rules/branches/main` responde e hoje dá `required_status_checks`, `pull_request`, `non_fast_forward`, `deletion` (sem `update`), então a conferência de doc:116 distingue o antes do depois. 25432260 cobre `homolog` e `main`, com `current_user_can_bypass` = `always` para a conta atual (resíduo A5 até o dono aplicar). Push na `homolog` só dispara `ci.yml`; `release.yml` só em `main`: a prova de escrita em `homolog` (doc:116) não publica nada. Os projetos consomem tags `vX.Y.Z` pelo git (`bin/forge_versoes.py`), não o objeto release; o colaborador pode criar e editar releases, mas a criação de tag `v*` fica barrada pelo ruleset de tag (sem bypass para ele).

**A13:** caminho: se a conta dos agentes um dia entrar numa organização, o token `repo` passa a alcançá-la; não afeta este repositório. Severidade baixa; correção: uma frase no passo 1 ou 3. Esforço P; dono: devops. Cosmético para o `tech-lead`: doc:112 "a conta nova, A conta nova".

**Caminhos conferidos como aplicáveis pelo dono sozinho:** ruleset de tag (doc:38-81, 120-123); token fino na conta do dono (doc:87-98); conta separada com token clássico `repo` e Restrict updates com bypass do admin (doc:109-116).

## Riscos aceitos e ferramentas
Nenhum risco aceito gravado; sem a conta separada, o resíduo A5 está escrito como risco a aceitar pelo dono (doc:118), sem aceite em `docs/security/aceites/`. Ferramentas: `forge-check parecer delta`; `gh api` GET (`rulesets`, `rulesets/25432260`, `rules/branches/main`); documentação do GitHub (quatro páginas acima); leitura de `.github/workflows/*.yml`. Lacunas: gitleaks, zizmor e actionlint fora do PATH (documento sem segredo nem workflow alterado). Suíte: diff só de documentação; sem teste de abuso a rodar.
