---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-sessao-automatica
commit: 5f0547cc0864a1830cd32f51f6695b35fc772703
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-sessao-automatica

Intervalo `origin/develop...5f0547cc` (base f4b0c2ae, um commit): SESSAO-AUTOMATICA (diretriz 28: `scripts/jarvis`, `scripts/jarvis-forge`, README, `templates/projeto/CLAUDE.md`) e GH-VERSAO-MINIMA (`scripts/preparar-estacao.sh`, passo 1 do `bin/forge-fechar`), com testes e o fragmento do changelog.

## Gatilhos
Muda o modo de permissão de toda sessão do Jarvis (fábrica e projetos) para `--permission-mode auto`: tira o humano do portão de cada comando, gatilho de `R-SEGURANCA`. Toca a instalação de pacote de sistema com chave de repositório externo (cadeia de suprimentos da estação) e o passo 1 do `forge-fechar` (ferramenta de controle). A decisão de abrir sempre no automático é do dono (diretriz 28, `R-DECISAO`) e não é questionada aqui; o que se revisa é o controle compensatório que a própria diretriz pede (conferir o sandbox e avisar o dono).

## Achados
- A1 (bloqueante) scripts/jarvis:28 · Projeto sem sandbox (o forge-init o deixa desligado sem o bubblewrap ou a credencial do bot) abre em modo automático sem sandbox e sem aviso: o comando trivial do Jarvis passa. Avise numa linha quando o settings do projeto não tem sandbox.enabled, sem mudar o modo.
- A2 (recomendado) templates/projeto/CLAUDE.md:11 · A conferência do sandbox está só no modelo (projetos novos) e no README; agents/jarvis.md não a traz, então projetos existentes e o próprio Forge não a recebem. Leve-a ao agente com uma sonda que falhe sem sandbox (leitura de caminho negado).

## Sondas
- S1 · projeto vazio sem .claude/settings.json, claude falso no PATH, `HOME=$S/home PATH=$S/bin:/usr/bin:/bin bash scripts/jarvis --sem-tmux` · espera: aviso de sandbox ausente no stderr · obtido: rc=0, stderr vazio, `claude --continue --permission-mode auto --remote-control Jarvis - proj`

## Detalhe dos achados
**A1.** Evidência: `scripts/jarvis:28` monta `--permission-mode auto` sem olhar a configuração do projeto; `bin/forge-init:117-136` cria projeto com o sandbox desligado quando falta o bubblewrap ou a credencial do bot (e o `forge-init --sem-sandbox`); o README (`README.md:37`) e o modelo (`templates/projeto/CLAUDE.md:11`) descrevem a conferência como "um comando trivial", que roda com sucesso justamente quando o sandbox está desligado. Caminho de ataque: conteúdo não confiável lido pela sessão (dependência, página buscada, texto de issue ou de PR) injeta instrução; antes, no modo padrão, cada comando fora da lista pedia o dono; agora o classificador do modo automático é a única barreira, e um comando fora do sandbox lê a credencial do `gh` em `~/.config/gh` e a envia pela rede. Severidade: média (exige injeção e passar pelo classificador, mas o ganho é a credencial do repositório). Correção mínima (dono `devops-engineer`, esforço P): em `scripts/jarvis`, antes do `exec`, ler `.claude/settings.json` e `.claude/settings.local.json` do projeto e, se nenhum tiver `sandbox.enabled: true`, escrever no stderr uma linha "sandbox desligado neste projeto: a sessão automática roda sem sandbox; rode `forge adotar` para ligá-lo" e seguir (o modo automático continua, como decidiu o dono); teste com o projeto sem settings e com o settings do modelo. Se o dono preferir aceitar o risco sem o aviso, o caminho é `riscos-aceitos` com aceite dele (`R-SEGURANCA`). Para a fábrica, `jarvis-forge` abre com o `.claude/settings.json` do Forge, que tem `failIfUnavailable: true` e `allowUnsandboxedCommands: false`: falha fechada, sem achado.

**A2.** Evidência: `grep -i sandbox agents/jarvis.md` sem resultado no head; a instrução está em `templates/projeto/CLAUDE.md:11`, copiada só na criação do projeto. Sem caminho de ataque próprio além do A1 (nos projetos com o sandbox do modelo, a falha do sandbox já é fechada: nenhum comando roda fora dele); é o requisito da diretriz chegando a todas as sessões. Correção mínima (dono do `agents/jarvis.md`, com a permissão desse arquivo pedida ao dono, `R-DECISAO`; esforço P): uma linha no Jarvis com a conferência no primeiro comando, por uma sonda que só passa com sandbox (por exemplo, ler um caminho de `denyRead` tem de ser recusado) e o aviso com o comando de reabrir.

**Sem achado (conferido):**
- `scripts/preparar-estacao.sh:61-84`: chave do repositório oficial do GitHub CLI baixada por HTTPS (`curl -fsSL`, falha em erro), instalada com modo 644 e presa à lista por `signed-by` (a chave vale só para esse repositório); a lista só é criada se não existir. Sem conferência da impressão digital da chave, como no procedimento oficial (informativa: a confiança é o TLS de cli.github.com). Falha de instalação vira `falta`, nada roda em silêncio; `--simular` não chama comando que altera o sistema (`tests/test_sessao_automatica.py:90`).
- `bin/forge-fechar:854-865`: a versão do `gh` passa por regex `^[0-9]+\.[0-9]+$` antes da comparação aritmética (sem injeção no `[ -lt ]`); versão ilegível para o fluxo (falha fechada), antes de abrir ou mesclar qualquer coisa; o `git fetch origin homolog` é só leitura, com nome fixo; falha da busca é aviso e o `forge-check pr` continua sendo o portão.
- `scripts/jarvis-forge:217`: só acrescenta o modo ao vetor de argumentos, sem interpolação nova.
- README: o link do repositório oficial aponta para github.com/cli/cli. Sem segredo, sem custo (`R-CUSTO`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do diff inteiro; rodei `tests.test_sessao_automatica` e `tests.test_fechar_gh_versao` (19 testes, OK) e a análise estática de shell nos quatro scripts tocados (rc=0). A suíte inteira roda no CI do PR (o workflow dispara só em `pull_request`; o brief manda não abrir PR), então o CI fica a conferir na abertura. Varredura de segredos e de workflows sem ferramenta no PATH (lacuna); o diff foi lido por inteiro e não traz credencial.
