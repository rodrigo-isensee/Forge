---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-sessao-automatica
commit: cd7bd9f833b4f8abec6cb95138889ae51f2fdc8d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047-sessao-automatica

Intervalo `origin/develop...5f0547cc` (base f4b0c2ae, um commit): SESSAO-AUTOMATICA (diretriz 28: `scripts/jarvis`, `scripts/jarvis-forge`, README, `templates/projeto/CLAUDE.md`) e GH-VERSAO-MINIMA (`scripts/preparar-estacao.sh`, passo 1 do `bin/forge-fechar`), com testes e o fragmento do changelog.

## Gatilhos
Muda o modo de permissão de toda sessão do Jarvis (fábrica e projetos) para `--permission-mode auto`: tira o humano do portão de cada comando, gatilho de `R-SEGURANCA`. Toca a instalação de pacote de sistema com chave de repositório externo (cadeia de suprimentos da estação) e o passo 1 do `forge-fechar` (ferramenta de controle). A decisão de abrir sempre no automático é do dono (diretriz 28, `R-DECISAO`) e não é questionada aqui; o que se revisa é o controle compensatório que a própria diretriz pede (conferir o sandbox e avisar o dono).

## Revalidação (delta 5f0547cc..cd7bd9f8)
Lido `forge-check parecer delta` (no domínio: só `scripts/jarvis`; fora: `tests/test_sessao_automatica.py`, `tests/mutantes/v047-sessao-automatica.json`). O A1 (bloqueante da rodada anterior) está corrigido e sai do bloco de achados: `scripts/jarvis:30-46` lê `.claude/settings.json` e `.claude/settings.local.json` do projeto com `python3 -I` (sem interpolação do caminho no código, argumentos por `sys.argv`), aceita só `sandbox.enabled is True` e, fora disso (arquivo ausente, JSON inválido, valor não booleano, `python3` ausente), avisa numa linha no stderr e segue no modo automático, como decidiu o dono (falha para o lado do aviso). Nenhuma interpolação nova no `exec`; shellcheck rc=0.

## Achados
- A2 (recomendado) templates/projeto/CLAUDE.md:11 · A conferência do sandbox está só no modelo (projetos novos) e no README; agents/jarvis.md não a traz, então projetos existentes e o próprio Forge não a recebem. Leve-a ao agente com uma sonda que falhe sem sandbox (leitura de caminho negado).
- A3 (recomendado) scripts/jarvis:33 · O aviso cala quando settings.json tem enabled true e settings.local.json tem false, mas o local prevalece no Claude Code. Considere ler o local primeiro e decidir pelo último valor definido.

## Sondas
- S1 · projeto sem .claude/settings.json, claude falso no PATH, `bash scripts/jarvis --sem-tmux` · espera: aviso de sandbox no stderr · obtido: no head cd7bd9f8, rc=0, stderr `jarvis: sandbox desligado neste projeto: ...`, exec `claude --continue --permission-mode auto ...`
- S2 · mesmo, com `.claude/settings.json` = `{"sandbox":{"enabled":true}}` · espera: sem aviso · obtido: rc=0, stderr vazio
- S3 · `{"sandbox":{"enabled":"true"}}` (texto) · espera: aviso · obtido: aviso
- S4 · `{bad` (JSON inválido) · espera: aviso · obtido: aviso
- S5 · settings.json do modelo (`templates/projeto/.claude/settings.json`) · espera: sem aviso · obtido: rc=0, stderr vazio
- S6 · settings.json enabled true e settings.local.json enabled false · espera: aviso (A3) · obtido: stderr vazio

## Detalhe dos achados
**A1.** Evidência: `scripts/jarvis:28` monta `--permission-mode auto` sem olhar a configuração do projeto; `bin/forge-init:117-136` cria projeto com o sandbox desligado quando falta o bubblewrap ou a credencial do bot (e o `forge-init --sem-sandbox`); o README (`README.md:37`) e o modelo (`templates/projeto/CLAUDE.md:11`) descrevem a conferência como "um comando trivial", que roda com sucesso justamente quando o sandbox está desligado. Caminho de ataque: conteúdo não confiável lido pela sessão (dependência, página buscada, texto de issue ou de PR) injeta instrução; antes, no modo padrão, cada comando fora da lista pedia o dono; agora o classificador do modo automático é a única barreira, e um comando fora do sandbox lê a credencial do `gh` em `~/.config/gh` e a envia pela rede. Severidade: média (exige injeção e passar pelo classificador, mas o ganho é a credencial do repositório). Correção mínima (dono `devops-engineer`, esforço P): em `scripts/jarvis`, antes do `exec`, ler `.claude/settings.json` e `.claude/settings.local.json` do projeto e, se nenhum tiver `sandbox.enabled: true`, escrever no stderr uma linha "sandbox desligado neste projeto: a sessão automática roda sem sandbox; rode `forge adotar` para ligá-lo" e seguir (o modo automático continua, como decidiu o dono); teste com o projeto sem settings e com o settings do modelo. Se o dono preferir aceitar o risco sem o aviso, o caminho é `riscos-aceitos` com aceite dele (`R-SEGURANCA`). Para a fábrica, `jarvis-forge` abre com o `.claude/settings.json` do Forge, que tem `failIfUnavailable: true` e `allowUnsandboxedCommands: false`: falha fechada, sem achado.

**A1 (revalidado).** A correção segue a correção mínima pedida: aviso numa linha, modo inalterado, teste com projeto sem settings e com o settings do modelo (`tests/test_sessao_automatica.py:62-75`, 13 testes OK no head). Severidade residual: nenhuma além do A3.

**A3.** Evidência: `scripts/jarvis:33` sai com 0 no primeiro arquivo com `enabled is True`, olhando `settings.json` antes de `settings.local.json`; no Claude Code o `settings.local.json` tem precedência sobre o do projeto. Caminho de ataque: fraco; o arquivo local é do próprio usuário e o sandbox ligado nega escrita nele, então quem o desliga é o dono, e o aviso é só informativo. Por isso é recomendação, não bloqueio. Correção mínima (dono `devops-engineer`, esforço P): decidir pelo `settings.local.json` quando ele define `sandbox.enabled`, senão pelo `settings.json`; teste com S6.

**A2.** Evidência: `grep -i sandbox agents/jarvis.md` sem resultado no head; a instrução está em `templates/projeto/CLAUDE.md:11`, copiada só na criação do projeto. Sem caminho de ataque próprio além do A1 (nos projetos com o sandbox do modelo, a falha do sandbox já é fechada: nenhum comando roda fora dele); é o requisito da diretriz chegando a todas as sessões. Correção mínima (dono do `agents/jarvis.md`, com a permissão desse arquivo pedida ao dono, `R-DECISAO`; esforço P): uma linha no Jarvis com a conferência no primeiro comando, por uma sonda que só passa com sandbox (por exemplo, ler um caminho de `denyRead` tem de ser recusado) e o aviso com o comando de reabrir.

**Sem achado (conferido):**
- `scripts/preparar-estacao.sh:61-84`: chave do repositório oficial do GitHub CLI baixada por HTTPS (`curl -fsSL`, falha em erro), instalada com modo 644 e presa à lista por `signed-by` (a chave vale só para esse repositório); a lista só é criada se não existir. Sem conferência da impressão digital da chave, como no procedimento oficial (informativa: a confiança é o TLS de cli.github.com). Falha de instalação vira `falta`, nada roda em silêncio; `--simular` não chama comando que altera o sistema (`tests/test_sessao_automatica.py:90`).
- `bin/forge-fechar:854-865`: a versão do `gh` passa por regex `^[0-9]+\.[0-9]+$` antes da comparação aritmética (sem injeção no `[ -lt ]`); versão ilegível para o fluxo (falha fechada), antes de abrir ou mesclar qualquer coisa; o `git fetch origin homolog` é só leitura, com nome fixo; falha da busca é aviso e o `forge-check pr` continua sendo o portão.
- `scripts/jarvis-forge:217`: só acrescenta o modo ao vetor de argumentos, sem interpolação nova.
- README: o link do repositório oficial aponta para github.com/cli/cli. Sem segredo, sem custo (`R-CUSTO`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Na revalidação (cd7bd9f8): leitura do delta do domínio, sondas S1 a S6 com `claude` falso no PATH, `tests.test_sessao_automatica` (13 testes, OK) e shellcheck em `scripts/jarvis` (rc=0); a suíte inteira fica para o CI do PR. Na primeira rodada: revisão estática do diff inteiro; rodei `tests.test_sessao_automatica` e `tests.test_fechar_gh_versao` (19 testes, OK) e a análise estática de shell nos quatro scripts tocados (rc=0). A suíte inteira roda no CI do PR (o workflow dispara só em `pull_request`; o brief manda não abrir PR), então o CI fica a conferir na abertura. Varredura de segredos e de workflows sem ferramenta no PATH (lacuna); o diff foi lido por inteiro e não traz credencial.
