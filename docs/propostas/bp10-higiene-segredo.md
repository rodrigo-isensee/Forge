# BP10: higiene de segredo (desenho)

Pedido v0478, etapa E138.4 (cartão BP10-HIGIENE-SEGREDO, origem `docs/propostas/boas-praticas-1911.md`, linha BP10). Só desenho: nenhum hook, script, teste, CI nem modelo de projeto foi alterado. Público: o dono e o time. Revisão: 2026-12-23. Base lida: develop 0e59c446.

Três frentes, neutras para todo projeto: (1) varredura de segredo antes de o commit sair da máquina; (2) aviso quando uma chave aparece no chat; (3) nenhum link de sessão em commit de repositório público. Custo zero (`R-CUSTO`): só biblioteca padrão, shell e ferramentas gratuitas já instaladas pelo `scripts/preparar-estacao.sh`. Regra do dono de 21/11 (item 3): trava nova de processo só entra se outra sair ou simplificar; cada fatia diz se é trava e qual sai.

## 1. O que já existe

| Frente | Evidência | O que cobre |
|---|---|---|
| 1 | `scripts/verificar-contribuicao.sh:16-23` | padrões de token (`sk-`, `gh?_`, `github_pat_`, `AKIA`, chave privada PEM, senha atribuída), `.env` versionado (`:30-36`); imprime arquivo e linha, nunca o valor (`:2`) |
| 1 | `.githooks/pre-push:210-234` | no Forge, cada ref enviada é varrida pelo script lido da `develop` (a branch não julga a si mesma); achado recusa o envio |
| 1 | `.githooks/pre-push:360-372` | segunda passada, com o script da própria árvore (SENTINELA-CAMINHO-LOCAL) |
| 1 | `.github/workflows/ci.yml:727-737` | o CI do Forge roda o mesmo script no diff do PR |
| 1 | `scripts/preparar-estacao.sh:76-119` | instala `gitleaks` com sha256 conferido (opcional, `--ferramentas`) |
| 1 | `skills/engineering-practices/SKILL.md:65` | instrução: `git diff --staged` antes do commit, nunca versionar `.env` nem segredo |
| 1 | `templates/projeto/.githooks/pre-push:1-30` | no **projeto**, o hook só protege a `main` e o histórico; **não varre segredo** |
| 2 | `skills/novo-projeto/SKILL.md:12` e `:38` | nunca pedir token, senha ou chave no chat; login só por `gh auth login` |
| 2 | `hooks/conformidade.py:2460-2464`; `templates/projeto/.claude/settings.json` (`permissions.deny`, `Read(./.env*)`) | o agente não lê `.env` |
| 2 | `bin/forge-sugerir:35-39` | regex de segredo (`SEGREDO`, `TOKENS`, `PEM`) que já redige texto antes de sair para o Forge |
| 2 | `hooks/hooks.json` | não há gancho `UserPromptSubmit`: nada olha o que o usuário cola |
| 3 | `hooks/conformidade.py:328` e `:3366-3388` | tornar o repositório público (`gh repo create/edit --visibility public`, `gh api` com `private:false`) é ato confirmado |
| 3 | `bin/forge-novo-projeto:144` | projeto novo nasce `--private` |
| 3 | `docs/adr/0008-governanca-de-contribuicoes.md:72` | antes de tornar o Forge público: varrer histórico e corpos de PR por segredo, caminho pessoal e nome de projeto (gitleaks); não cita o link de sessão |
| 3 | `git log origin/develop` | 819 de 2631 commits trazem o trailer de link de sessão, posto pelo ambiente remoto do Claude Code |

## 2. O que falta e o risco real

- **F1, projeto sem varredura local.** Caminho: o agente ou o usuário commita uma chave e envia; no remoto ela fica no histórico e precisa ser rotacionada. Severidade média (repositório privado por padrão; vira crítica se público). O Forge já tem a barreira; o projeto não.
- **F2, chave colada no chat.** Caminho: o usuário cola um token para "ajudar"; ele fica na transcrição local e na do serviço, e o agente pode repeti-lo num arquivo, num commit ou no Telegram. Nada avisa o usuário para rotacionar. Severidade média; a correção é aviso, não bloqueio (o texto já foi enviado).
- **F3, link de sessão em commit público.** O link só abre com o login do dono, então não dá acesso; expõe o identificador da sessão e fica para sempre no histórico. Severidade baixa: é recomendação, sem caminho de ataque com ganho. Hoje todos os repositórios nascem privados.

## 3. Corte (fatias independentes, nesta ordem)

**C1, F2 aviso de chave no chat (não é trava).** Gancho `UserPromptSubmit` novo em `hooks/hooks.json`, script curto que importa as regex de `bin/forge-sugerir` (uma fonte só; mover para `hooks/_comum.py` se a importação cruzada pesar). Achou formato de chave: devolve contexto ao modelo ("o usuário colou algo com formato de <tipo>; não repita, não grave; diga para rotacionar") e nunca bloqueia nem imprime o valor. Dono: `devops-engineer`.
- Pronto quando: (a) prompt com `ghp_` + 36 caracteres gera o aviso com o tipo e sem o valor; (b) prompt com `sk-` dentro de crase e marcado `forge:exemplo` não gera; (c) corpus de 20 prompts legítimos (hash hexa de commit de 40 caracteres, UUID, base64 curto, URL do PR) sem aviso; (d) entrada de 1 MB responde em menos de 200 ms; (e) erro interno sai 0 sem aviso (falha aberta, é só aviso).

**C2, F1 varredura no envio do projeto (trava nova; precisa de uma que sai).** O `templates/projeto/.githooks/pre-push` passa a varrer o delta de cada ref enviada: `gitleaks git --redact` com o intervalo do envio quando está no PATH; senão o script de segredo do Forge pelo `bin/` do plugin (uma fonte só; hoje ele está em `scripts/`, e o projeto não o recebe). Sem nenhum dos dois: aviso e segue. O ponto é o envio, não o commit: o commit local ainda se corrige sem reescrever histórico remoto, e o `pre-commit` seria um gancho a mais. Dono: `devops-engineer`; o `forge-upgrade` leva o modelo aos projetos.
- Trava que sai, em troca (pergunta ao dono, `R-DECISAO`): a segunda passada do Forge (`.githooks/pre-push:360-372`). A primeira (`:210-234`) já varre com o script da `develop`, e o CI (`ci.yml:727-737`) roda o da árvore; a segunda só antecipa o que o CI barra. Se o dono recusar a troca, C2 entra como aviso, não recusa.
- Pronto quando: (a) envio com `AKIA` + 16 caracteres num arquivo novo é recusado com arquivo e linha, sem o valor; (b) `.env` adicionado é recusado; `.env.example` passa; (c) linha com `forge:exemplo` passa; (d) envio de branch nova sem base comum avisa e segue; (e) corpus de legítimos (hash de commit, `package-lock` ou equivalente, chave pública SSH) passa; (f) `bash -n` e `shellcheck` verdes; (g) na mesma PR, a passada `:360-372` saiu e a suíte do pre-push segue verde.

**C3, F3 sem link de sessão em repositório público (não é trava).** Uma linha em `## Regras da fábrica` de `templates/projeto/CLAUDE.md` e em `.claude/CLAUDE.md` do Forge: "repositório público: commit e PR sem a linha de link de sessão; a de coautoria fica". A instrução do projeto tem precedência sobre a do ambiente. E o item (b) de `docs/adr/0008-governanca-de-contribuicoes.md:72` ganha "link de sessão" na lista do que se varre antes de tornar público (emenda, decisão do dono). A confirmação de tornar público (`hooks/conformidade.py:3376`) passa a citar o item na mensagem, sem nova recusa. Dono: `software-architect` (ADR) e `devops-engineer` (modelo).
- Pronto quando: (a) a linha está nos dois `CLAUDE.md` e o teste de neutralidade segue verde; (b) a emenda da ADR 0008 está gravada; (c) a mensagem da confirmação cita o link de sessão; (d) nenhum teste novo de recusa.

## 4. Casos de abuso (para o `qa-engineer`, quando cada fatia for aberta)

- C1: token colado no meio de um parágrafo longo · prompt → gancho · aviso com o tipo, sem o valor.
- C1: token partido por espaço ou quebra de linha · prompt → gancho · sem aviso (fora do alcance; limite declarado, não falha).
- C2: chave num arquivo binário ou renomeado · envio → pre-push · `gitleaks` acha; no script de fallback, limite declarado.
- C2: `forge:exemplo` em linha com chave real · envio → pre-push · passa (exceção auditável no diff; o review de segurança lê as marcas).
- C2: commit com a chave e commit seguinte que a remove, enviados juntos · envio → pre-push · recusa (o histórico ainda tem a chave).

## 5. Fora do corte

Reescrever o histórico atual (819 commits com o link) só vale se o Forge ou um projeto virar público e é decisão do dono (ADR 0008, item b). Secret scanning nativo do GitHub fica como opção do dono (gratuito em repositório público; confira o custo em privado). Varrer a transcrição local já gravada fica fora: a correção é rotacionar a chave.
