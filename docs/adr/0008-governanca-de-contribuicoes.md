# 0008 - Governança de contribuições: portões para todos

Estado: vigente. Data: 2026-10-12. Decisões do dono em 2026-10-13: conta de máquina para os agentes (A); preparar já e tornar público quando chegar o primeiro colaborador (A); licença MIT (A).
Propósito: impedir que contribuições, de qualquer pessoa ou agente e inclusive do dono, piorem a fábrica. Público: quem mantém o Forge e quem contribui de um projeto. Revisão: 2026-10-12.

## Contexto
A ADR 0006 abriu o Forge para contribuições de qualquer projeto e registrou que a proteção real das branches precisa ser do servidor. Hoje nada no servidor protege `develop`, `homolog` e `main`: o repositório é privado numa conta pessoal do plano gratuito, e a API recusa proteção de branch e rulesets ("Upgrade to GitHub Pro or make this repository public"). O GitHub Pro custa dinheiro e fica descartado (`R-CUSTO`). As proteções atuais estão do lado do cliente ou dependem de o agente obedecer: o `.githooks/pre-push` (ativado em cada clone), os hooks do plugin (ADR 0003) e as instruções do Jarvis e do `tech-lead`.

Incidente: uma sessão de outro projeto, com o mesmo login do GitHub do dono, mesclou dois PRs na `develop` sem code review nem QA do Forge; um deles alterava `invariantes`, e os dois trouxeram commits de lixo para o histórico. Três lacunas permitiram isso: (1) o hook de parecer não cobre `gh pr merge`; (2) os hooks não agem no próprio repositório do Forge, que não tem `.forge/versao`; (3) com o mesmo login, o GitHub não distingue o dono de um agente.

Premissas do dono: PR do dono dispensa aprovação de outra pessoa; PR de qualquer outra pessoa só entra com a aprovação do dono. Os portões de qualidade valem para todos, inclusive o administrador: o que piora o Forge é barrado mesmo vindo do dono. Nada pode custar dinheiro.

## Decisão
Defesa em camadas, todas sem custo; cada camada parte do princípio de que a anterior pode falhar.

### 1. Identidade: agentes não usam o login do dono
Os agentes (Jarvis, `tech-lead` e sessões de projeto) usam uma **conta de máquina** gratuita, colaboradora com escrita, com token próprio (fine-grained, só este repositório, `contents` e `pull_requests` de escrita). O dono usa a própria conta só para aprovar, aplicar o rótulo `afrouxa-regra` e mesclar na `main`. Sem isso, nenhuma regra baseada em "quem" separa o dono de um agente; é o pré-requisito das outras.

### 2. Servidor (vale com o repositório público; definida como código em `.github/rulesets/`)
1. **Ruleset `portoes`** em `develop`, `homolog` e `main`, **sem ator de bypass, nem administrador**: PR obrigatório; checks obrigatórios fixados à origem GitHub Actions; branch atualizada com a base; bloqueio de force push e de deleção.
2. **Métodos de merge:** `develop` só squash, com histórico linear (um PR vira um commit); `homolog` e `main` só merge commit (squash na promoção faz as branches divergirem).
3. **Ruleset `aprovacao`**: 1 aprovação e revisão de code owner; aprovação descartada a cada push; bypass **só deste ruleset**, só para o dono, no modo "somente pull request" — o dono mescla o próprio PR sem segunda pessoa, mas nunca sem os checks do `portoes`, nem por push direto.
4. **Ruleset `main-do-dono`**: "restringir atualizações" na `main`, bypass só do dono; a conta de máquina não mescla na `main` (`R-MAIN` garantida pelo servidor).
5. **`.github/CODEOWNERS`** com o dono em `*`: PR de quem não é o dono exige a aprovação dele.
6. **Actions:** aprovação obrigatória para executar workflows de PR de colaboradores externos; `GITHUB_TOKEN` padrão só leitura; Actions proibidas de criar ou aprovar PR; nenhum `pull_request_target` nem `workflow_run` privilegiado executando código do PR (ADR 0006).

### 3. CI anti-piora (catraca)
Jobs em `ci.yml` (e `catraca.yml`, para `catraca` e `pr-texto`), só biblioteca padrão do Python ou ferramentas gratuitas de versão fixa, sem segredos; todos entram na lista de checks obrigatórios. Os de regras ficam em `tests/catraca.py`, que lê a base com `git show $BASE:<arquivo>`.

| Job | O que barra | Como |
|---|---|---|
| `catraca` | Regras que somem ou afrouxam: padrão de `invariantes`, `termos_proibidos_hash` ou termos de neutralidade que existiam na base e sumiram; aumento de `limite_linhas`; exceções novas de neutralidade ou anti-duplicação; hook removido de `hooks/hooks.json`; mudança da chave `dono` | Comparação de conjuntos base × PR. Exceção só com o rótulo `afrouxa-regra` aplicado **pelo dono depois do último push** (eventos da issue: `actor.login` = `dono` de `tests/config.json`) |
| `catraca` | Testes que somem: contagem de `def test_*` (AST) e de fixtures em `tests/hooks/**` cai em relação à base | Contagem estática nas duas versões; o mesmo rótulo é a única exceção |
| `catraca` | Hooks que engordam: linhas de `hooks/*.py` acima de `limite_linhas.hooks`; mediana por fixture acima de 100 ms (ADR 0003) com margem de CI de 3× | Linhas no PR; tempo medido nos fixtures |
| `catraca` | Custo: `secrets.*` diferente de `GITHUB_TOKEN` em workflows; chave de API paga, `claude plugin eval`, `claude -p` ou URL de API paga em `hooks/`, `bin/`, `scripts/` e `.github/` | Busca por padrões, com lista de permissão em `tests/config.json` |
| `workflows` | Workflow inseguro (injeção por `${{ }}` em `run`, permissões amplas, ação sem SHA, `pull_request_target`) | `actionlint` e `zizmor` em versões fixas, sem token |
| `pareceres` | PR que toca `hooks/`, `bin/`, `scripts/`, `migrations/`, `.github/workflows/` ou `tests/catraca.py` sem parecer de review (revisor diferente do autor) e, para a `homolog`, sem parecer de QA do mesmo commit | `bin/forge-check pr` sobre `docs/reviews/` e `docs/qa/` |
| `pr-texto` | Corpo do PR sem "Projeto de origem" e "Como medir" | Corpo lido de `env:` (nunca interpolado no `run`); reage a `edited` |
| `segredos` | Segredo, `.env` ou caminho pessoal no diff | `scripts/verificar-contribuicao.sh` no CI |

Mensagens de bloqueio: uma linha, começando pelo ID da regra, com o quê, por quê e como corrigir (`<R-ID>: <o quê>. Por quê: <motivo>. Corrigir: <ação> (<doc>)`); nunca o valor de um segredo. O CI publica um comentário único por PR, atualizado a cada execução, com a tabela de portões; em PR de fork, sem permissão de escrita, o resumo vai para `GITHUB_STEP_SUMMARY`.

Notas da implementação (rodada de correções do review e do QA):
- **Promoções fora do `pareceres`:** PR `develop` → `homolog` e `homolog` → `main` não passa pelo job: o parecer é exigido na entrada de cada PR na `develop`, e na promoção o `ramo` seria `develop` ou `homolog`, sem parecer possível.
- **"Depois do último push":** o instante vem do servidor (a execução mais antiga do Actions para o `head.sha`, `actions: read`), nunca da data do commit, que o cliente define. Sem execução registrada, o rótulo não vale.
- **`R-CUSTO` não tem rótulo:** a exceção de custo é só `custo_permitido`, com autorização do usuário.
- **Versão da base:** os jobs `catraca` e `pareceres` executam `tests/catraca.py` e `bin/forge-check` da base (checkout separado), avaliando os arquivos do PR; só a introdução usa a versão do PR.
- **Dependabot:** PR de `dependabot[bot]` que só troca SHA de `uses:` em workflows passa sem rótulo e sem parecer; qualquer outra mudança segue as regras normais.
- **Rótulo e texto do PR:** `catraca` e `pr-texto` ficam em `.github/workflows/catraca.yml` para reagir a `labeled`, `unlabeled` e `edited` sem rodar a bateria pesada.

Limite conhecido: no evento `pull_request`, o workflow roda na versão do PR, que pode editar o próprio `ci.yml` ou `tests/catraca.py`. Mitigações: a `catraca` exige `afrouxa-regra` para mudança em `.github/workflows/`, `.github/rulesets/`, `.github/CODEOWNERS` e `tests/catraca.py`; um job removido deixa o check obrigatório pendente; para quem não é o dono, a aprovação do code owner é o portão final.

### 4. Agentes
1. **Nova regra `R-CONTRIB`** ("Contribuição ao Forge: projeto abre PR, nunca mescla; nenhum portão tem exceção, nem para o dono"), citada pelo Jarvis, pelo `tech-lead` e pela skill `contribuir-com-o-forge`.
2. **Jarvis e `tech-lead` recusam mesclar** na `develop` ou na `homolog` sem todos os checks verdes, pareceres válidos (`forge-check pr`) e o rótulo do dono quando a `catraca` exigir; na `main`, nunca mesclam (`R-MAIN`).
3. **Hook `parecer` estendido** (ADR 0003, sem rede): reconhece `gh pr merge` e `gh api .../pulls/<n>/merge`. Merge no Forge vindo de sessão cuja raiz não é um clone do Forge: bloqueado (`R-CONTRIB`); base `main`: bloqueado (`R-MAIN`); base `develop`/`homolog`: exige parecer; PR indicado só por número é bloqueado com o pedido "use o nome da branch".
4. **Hooks ativos no próprio Forge:** a raiz com `.claude-plugin/plugin.json` de nome `forge` também conta como projeto.
5. **Clone de contribuição** (`~/.forge-contrib/<projeto>`): a skill ativa `core.hooksPath` ao criar o clone.

### 5. Transição enquanto o repositório é privado e gratuito
- **Vale já:** camada 1 (conta de máquina é gratuita também em repositório privado); camada 3 inteira (os checks rodam e aparecem, só não são obrigatórios no servidor); camada 4; limite de gasto do Actions em US$ 0; nenhum colaborador com escrita além do dono e da conta de máquina.
- **Não vale:** camada 2. O merge com check vermelho fica barrado só pelos agentes e pelos hooks.
- **Gatilho para tornar público:** antes de dar escrita a outra pessoa ou aceitar o primeiro PR de fork, e só depois de: (a) `termos_proibidos_hash` no lugar de termos em claro (hash SHA-256 de cada termo normalizado); (b) varredura do histórico e dos corpos de PRs antigos por segredos, caminhos pessoais e nomes de projeto (gitleaks, gratuito), com decisão do dono sobre reescrever o histórico; (c) licença MIT (decidida; `LICENSE` na raiz); (d) rulesets e CODEOWNERS prontos em `.github/rulesets/`, aplicados no mesmo dia.
- Até o gatilho, contribuição de outra pessoa entra como proposta ao dono, nunca como acesso.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| GitHub Pro ou Team | Proteção no servidor com o repositório privado | Pago; descartado por `R-CUSTO` |
| Outra forja gratuita com branches protegidas em repositório privado | Proteção sem tornar público | A fábrica usa `gh`; migração grande |
| Bypass do dono num ruleset único | Simples | O bypass vale para os checks também: o dono, ou um agente com o login dele, passaria por cima da catraca |
| Catraca com `pull_request_target` lendo o PR só como dado | O PR não consegue desligar o workflow | Contexto privilegiado; um checkout futuro do PR expõe o token. Descartado |
| Só agentes e hooks, sem servidor | Já existe | Falhou no incidente |

## Consequências
- **Mais fácil:** afrouxar uma regra vira um ato explícito e auditável do dono (o rótulo); testes e regras só andam para frente; o merge de uma sessão de projeto no Forge para no hook.
- **Mais difícil:** o dono aplica o rótulo e aprova PRs de terceiros; reorganizações legítimas (mover invariantes, juntar testes) também pedem o rótulo; os agentes dependem de um token próprio.
- **Riscos que continuam:** até o repositório ser público, nada no servidor impede merge com check vermelho; quem tiver o token do dono pode aplicar o rótulo e mesclar; o campo `revisor` dos pareceres não prova independência; o PR pode editar o próprio workflow (mitigado); a catraca barra piora medida, não piora de mérito — o portão de mérito continua sendo a revisão do dono e as transcrições da ADR 0007; contas comprometidas fora do GitHub estão fora do escopo.
