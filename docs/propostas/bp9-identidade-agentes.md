# BP9: identidade separada para os agentes (desenho)

Pedido v0478, etapa E153.1 (cartão BP9-IDENTIDADE-AGENTES, origem `docs/propostas/boas-praticas-1911.md`, linha BP9). Só desenho: nenhum hook, script, teste, workflow, ADR nem modelo de projeto foi alterado. Público: o dono e o time. Revisão: 2026-12-24. Base lida: develop e15c8566.

Objetivo: o que um agente faz no GitHub fica separado do que o dono faz, com o menor escopo possível, sem esperar o dono a cada arquivo de workflow e sem custo em dinheiro (`R-CUSTO`). Regra do dono de 21/11 (item 3): trava nova de processo só entra se outra sair ou simplificar; cada fatia diz se é trava e qual sai.

## 1. O que já existe

| Tema | Evidência | O que cobre |
|---|---|---|
| Decisão de identidade | `docs/adr/0008-governanca-de-contribuicoes.md:17` | agentes usam conta de máquina gratuita, colaboradora com escrita; o dono usa a sua só para aprovar, rotular `afrouxa-regra` e mesclar na `main` |
| Passo a passo da conta robô | `docs/token-dos-agentes.md` (passos 1 a 5) | conta gratuita, papel Write sem Admin, token classic só com `repo`, validade de 90 dias, sem `workflow`; quem executa é o dono |
| Estado real | `docs/adr/0009-conformidade-dos-agentes.md:63` e `:89` | em 0009 a troca ainda estava pendente (o `GH_TOKEN` era da conta do dono, com administrador); classic porque o fine-grained não alcança repositório de conta pessoal onde o robô é só colaborador |
| Limite do `workflow` | `agents/devops-engineer.md:30`, `agents/security-engineer.md:32`, `docs/adr/0010-agentes-devops-e-seguranca.md:16` | o token do bot não tem o escopo `workflow`, de propósito; o devops prepara a branch e o dono envia |
| Onde o token mora | `docs/adr/0009-conformidade-dos-agentes.md:63`; `~/.claude/settings.json` (protegido) | `GH_TOKEN` no `env` do dono, `GIT_CONFIG_*` no `env` do projeto; `denyRead` de `~/.ssh`, `~/.config/gh`, `~/.git-credentials` |
| Autor dos commits | `docs/adr/0009-conformidade-dos-agentes.md:63` | continua o do `~/.gitconfig` do dono; o squash da `main` leva o autor dele |
| Agente não muda proteção | `R-CONFORMIDADE` | proteção de branch, rulesets, segredos e `environments` são do dono |

Sem conferência direta nesta etapa (o sandbox nega `~/.config/gh`): se a troca de 0009 já foi feita, o dono confirma com `gh api user --jq .login`; o desenho vale nos dois casos (ver seção 6).

## 2. O que falta e o risco real

- **F1, auditoria agente × pessoa.** Caminho: o autor do commit é o do `~/.gitconfig` do dono, então `git log` e o histórico do PR não separam o que foi dito por ele do que um agente fez. Severidade média: é rastreabilidade, não acesso; pesa na retro e na investigação de incidente.
- **F2, token longo no disco.** Caminho: o token classic vale até 90 dias e `repo` alcança todo repositório que o robô acessa, não só o Forge. Se vazar (chat, log, commit), o ganho é escrever em qualquer repositório do robô até o vencimento. Severidade média; a barreira atual é o `denyRead` e o sandbox.
- **F3, espera pelo `workflow`.** Caminho: toda mudança em `.github/workflows/` para até o dono executar o envio. Severidade baixa (atrito, não risco); a trava é correta e o desenho não a remove, só a torna explícita e curta.
- **F4, renovação manual a cada 90 dias.** Token que vence no meio de um pedido para a fábrica. Severidade baixa; hoje depende do lembrete do dono.

## 3. Alternativas de identidade (gratuitas)

| Opção | Escopo | Validade | Custo | Contras |
|---|---|---|---|---|
| A. Conta robô + classic `repo` (hoje, ADR 0009) | todo repositório do robô | 90 dias | zero | escopo largo; renovação manual; sem `workflow` só por escolha |
| B. Conta robô + fine-grained | um repositório, `contents` e `pull_requests` | até 1 ano | zero | só funciona com o Forge numa organização ou na conta dona do token; hoje o robô é colaborador de conta pessoal |
| C. GitHub App própria, instalada só no Forge | um repositório; `contents` e `pull_requests` de escrita, `metadata` de leitura | token de instalação de 1 hora | zero (App privada, sem Marketplace) | precisa de chave privada e de gerador de token; mais passos únicos para o dono |

C é a única que dá escopo mínimo e validade curta ao mesmo tempo na conta pessoal, e autor próprio (`<nome>[bot]`). O App também não ocupa vaga de colaborador e não pode ser o "administrador" por construção (sem permissão `administration`).

## 4. Corte (fatias independentes, nesta ordem)

**C1, F1 autor separado (não é trava).** Os agentes passam a commitar com nome e e-mail do robô (`GIT_AUTHOR_*` e `GIT_COMMITTER_*` no `env` do projeto, ao lado dos `GIT_CONFIG_*` que já existem), e o dono segue com o dele. Vale para A, B e C. O `forge-check` ganha, em modo só leitura, a contagem de commits da branch por autor, para o relato da retro; sem recusa. Dono: `devops-engineer`; a mudança do `env` de `~/.claude/settings.json` é do dono (arquivo protegido).
- Pronto quando: (a) commit feito por agente sai com o autor do robô e commit do dono com o dele; (b) o `forge-upgrade` leva a variável aos projetos sem tocar no `~/.gitconfig`; (c) `bin/forge-check docs` e a suíte seguem verdes; (d) nenhum teste novo de recusa.

**C2, F2 e F4 token curto e estreito (trava que sai: a renovação manual).** Troca de A por C, só se o dono escolher (seção 6, D1). Passos do dono, uma vez: criar o App privado em Settings > Developer settings > GitHub Apps, com **só** `Contents: write`, `Pull requests: write`, `Metadata: read`; sem `Workflows`, sem `Administration`, sem `Secrets`; instalar apenas no repositório do Forge; guardar a chave privada fora do repositório e fora do alcance do agente (mesmo cuidado do `GH_TOKEN`). Um gerador `bin/forge-token-app` (biblioteca padrão: JWT RS256 por `openssl`, uma chamada `POST /app/installations/<id>/access_tokens`) troca a chave por token de 1 hora, que vive só em memória ou em arquivo `0600` sob `.forge/run/`. Dono: `devops-engineer` escreve; `security-engineer` revisa; o dono instala. Sai: o lembrete de 90 dias e o passo 3 de `docs/token-dos-agentes.md`.
- Pronto quando: (a) `gh api repos/<dono>/<repo> --jq .permissions` com o token do App mostra `admin:false`; (b) o mesmo token recebe 403 ao criar ou editar arquivo em `.github/workflows/`; (c) o token expira em até 1 hora e o gerador renova sem pedir o dono; (d) a chave privada não aparece em log, em `git status` nem em mensagem de erro (`--redact`); (e) sem chave ou sem rede, o gerador falha fechado com mensagem em uma linha; (f) `bash -n` e `shellcheck` verdes se houver shell; teste em Python com `urllib` simulado, sem rede real.

**C3, F3 `workflow` só sob pedido (não é trava nova, formaliza a atual).** Nenhum agente recebe `workflow`, nem por A, B ou C. O pedido tem dois caminhos, escolhidos pelo dono (D2): (i) o atual, em que o devops prepara a branch local com commit e o `tech-lead` entrega o comando exato de envio, que o dono executa com a própria credencial; ou (ii) um segundo App `forge-workflow`, com **só** `Workflows: write` e `Contents: write`, instalado no Forge mas **sem chave guardada na estação**: o dono gera o token de instalação na hora, por pedido, com validade de 1 hora, e o entrega por `gh auth` no terminal dele, nunca no chat. Recomendação: (i). O ganho de (ii) é pequeno (o dono ainda age a cada pedido) e a chave de um segundo App é superfície nova. Dono: `devops-engineer` (texto) e o dono.
- Pronto quando: (a) uma linha em `docs/token-dos-agentes.md` e em `agents/devops-engineer.md` diz qual caminho vale; (b) o comando exato de envio é o mesmo de hoje, sem passo novo; (c) nenhum teste novo de recusa.

## 5. Casos de abuso (para o `qa-engineer`, quando cada fatia for aberta)

- C1: agente tenta commitar com o autor do dono (`-c user.email=`) · commit local → push · fora do alcance da fatia (aviso na contagem por autor, sem recusa; limite declarado).
- C2: token do App usado contra outro repositório do dono · API → GitHub · 404 ou 403 (instalação só no Forge).
- C2: token do App tenta `PUT /repos/.../contents/.github/workflows/x.yml` · API → GitHub · 403 (sem `Workflows`).
- C2: token de 1 hora reutilizado depois de expirar · API → GitHub · 401 e o gerador emite outro; nenhum token antigo em arquivo.
- C2: chave privada lida pelo agente · `Read` ou `cat` → arquivo · negado pelo `denyRead`; a chave fica no mesmo grupo de `~/.ssh`.
- C3: agente tenta `git push` de commit que altera `.github/workflows/` com o token de agente · push → GitHub · recusa do GitHub (`workflow` ausente), sem contorno por outro token (`R-CONFORMIDADE`).

## 6. Pede decisão do dono (`R-DECISAO`)

Formato fixo: cada pergunta traz as opções, a recomendação e o motivo.

- **D0, estado atual.** O robô de `docs/token-dos-agentes.md` já está em uso? Confirme com `gh api user --jq .login` numa sessão nova. Se não, executar aquele passo a passo (opção A) é pré-requisito de qualquer fatia abaixo e custa zero. Recomendação: sim, fazer antes de C1.
- **D1, conta robô ou App.** (a) ficar na opção A (conta robô, classic `repo`, 90 dias); (b) ir para a opção B se o Forge passar para uma organização; (c) ir para a opção C (App privado, token de 1 hora). Recomendação: **(c)**, em C2, porque é a única que dá escopo de um só repositório e validade curta na conta pessoal; fica (a) até lá, sem pressa. Custo de (c): um cadastro único de uns 15 minutos e o gerador. Risco de (c): a chave privada do App é um segredo longo; mora no mesmo lugar protegido do `GH_TOKEN` de hoje, sem piorar o quadro.
- **D2, caminho do `workflow`.** (i) o dono envia o que o devops preparou, como hoje; (ii) segundo App com token gerado pelo dono por pedido. Recomendação: **(i)**, pelo motivo da fatia C3. O agente nunca recebe `workflow`.
- **D3, troca que paga a trava.** C2 só entra se sair algo: o lembrete de renovação a cada 90 dias e o passo 3 de `docs/token-dos-agentes.md` (token classic). Se o dono recusar a troca de A por C, C2 não é aberta e as outras fatias seguem.
- **D4, autor do commit do agente.** Vale a pena o autor próprio (C1)? Efeito: o squash do PR para `develop` passa a ter o autor do robô; o do PR `homolog` → `main` segue com o do dono, como decidido na ADR 0009. Recomendação: sim, é o ganho de auditoria de menor custo.

## 7. Custo e esforço (`R-CUSTO`)

Nada pago: conta e App gratuitos, App privado fora do Marketplace, nenhum runner nem serviço novo. Esforço: C1 pequeno (variável de ambiente e uma contagem); C3 pequeno (duas linhas de texto); C2 médio (gerador, teste, passo a passo para o dono, parecer de segurança). Nenhum CI novo: os testes do gerador simulam a API, sem rede.

## 8. Fora do corte

Permissão de administrador do robô (nunca). Mudar rulesets ou a lista de exceção (do dono; o cartão AV1-BYPASS-RULESET segue à parte). Tornar o repositório público e as regras que isso traz (ADR 0008). OIDC para nuvem: não há nuvem no Forge. Assinatura de commit (GPG ou SSH) pelo robô: fica como recomendação para depois de C1.
