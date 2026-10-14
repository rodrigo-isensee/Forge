---
tipo: plano-tecnico
contrato: 1
pedido: primeiro-uso
estado: proposta
ux: docs/propostas/primeiro-uso/ux.md
adrs: []
agentes: [devops-engineer, qa-engineer, tech-lead]
---
# Primeiro uso do Forge: do plugin ao projeto configurado, sem quebrar nada

Conferência com a constituição: não há `docs/constituicao.md` na fábrica; conforme `R-NEUTRO`, `R-CUSTO`, `R-MAIN`, `R-VERIFY`, `R-CONTRIB`, `R-DECISAO`. Escopo D3 = B (8 cuidados). Suposições do time adotadas: commit inicial na `main` pelo script, como ato do usuário no terminal (`R-MAIN`); pasta padrão `~/<nome>`, perguntada a cada vez. Só biblioteca padrão do Python e shell.

## 1. Base do primeiro uso (proposta anterior, mantida)
- `bin/forge` (despachante sem lógica: `forge <sub>` → `bin/forge-<sub>`) e `bin/forge-novo-projeto`: roda **no terminal, antes do Claude** (o sandbox não lê `~/.config/gh`). Confere `git` (identidade), `gh auth status`, escopo `repo`; dono vem de `gh api user`, nunca fixo; nome validado `^[A-Za-z0-9._-]{1,100}$`; `gh repo create --private` (ou usa a URL de um repositório existente, sem sobrescrever); commit inicial na `main`, `develop` e `homolog`; clone; `forge-init`; `exec claude --agent forge:jarvis "<prompt>"`.
- Skill nova `forge:novo-projeto` conduz a conversa (contexto → `CLAUDE.md`, PR "adota o Forge" na `develop`); `iniciar-projeto` vira a etapa final. Rede de segurança: uma linha em `agents/jarvis.md` (pasta sem `.forge/versao` → oferece a skill).
- Retomada: estado em `.forge/novo-projeto.json` (antes do clone, em `~/.local/state/forge/novo-projeto/<nome>.json`), etapas idempotentes gravadas depois do efeito; nunca guarda segredo. Token nunca passa pelo chat.
- Proteção de branch no GitHub não é configurada (privado gratuito não tem); a salvaguarda é o `pre-push` do modelo e o hook `conformidade`.

## 2. Os 8 cuidados
### 2.1 Perfil de experiência
- `.forge/perfil` com uma palavra, `iniciante` ou `experiente`, perguntado na etapa de contexto ("Você já programa?"). É da pessoa, não do projeto: entra no `.gitignore` do modelo. Ausente = `experiente` (projetos atuais não mudam).
- Mudança só por `forge perfil <valor>` (assistido, ver 2.2); o caminho entra em `caminhos` com `quem: []`.
- Efeito: o `vigia` (SessionStart) injeta **uma linha** só quando `iniciante` ("Perfil iniciante: siga a skill forge:modo-iniciante"), ~20 tokens; experiente = 0. A skill `modo-iniciante` (carregada sob demanda, não engorda o `jarvis.md`) traz: glossário de troca (PR → "pedido de revisão", branch → "linha de trabalho", merge → "juntar"); decisões técnicas o time toma e registra (`R-DECISAO` já manda); à pessoa só vão produto, escopo, custo, acesso e exceção, em linguagem simples, com uma recomendação; toda recusa de hook é traduzida (2.2).

### 2.2 Instalação intocável
- **Já protegido** (`conformidade.json`, `caminhos`): `.claude/`, `.githooks/`, `.forge/versao`, `.forge/config.json`, `.forge/run/`, `.git/config`, `.git/hooks/`, `~/.claude/{settings*.json,CLAUDE.md,agents,skills,hooks,commands,plugins}`, `~/.claude.json`; no Bash, `--no-verify`, `core.hooksPath`, `--force`, push e merge na `main`.
- **Falta:** `.forge/perfil`; `claude plugin (uninstall|disable|update|marketplace remove|marketplace add)` e `claude config set` dentro da sessão; `git config --global` que troque `core.hooksPath` ou `user.*`; apagar `.forge/` ou `.githooks/` por `rm` (o Bash é lido como texto: barrado em regra, o sandbox é a garantia).
- **Recusa explicada:** a mensagem do hook já traz ID e dica; ganha o sufixo "se achar que deveria ser permitido: forge sugerir". No iniciante, o Jarvis traduz ("isso protege a sua instalação; fazer assim poderia ...") e oferece registrar como sugestão (2.7).
- **Configuração só por comando assistido:** `forge config|perfil|...` exige terminal interativo (`sys.stdin.isatty()`) e confirmação `s/N`; um agente não tem TTY, então não consegue rodar. Antes de gravar, copia o arquivo para `~/.local/state/forge/backup/<projeto>/<AAAAMMDD-HHMMSS>/` e mostra como restaurar (`forge config --restaurar`).

### 2.3 `forge doutor`
- **Confere (sem rede no modo rápido):** `.forge/versao` × versão do plugin (migração pendente, ADR 0005); `core.hooksPath=.githooks` e hooks executáveis; `.claude/settings.json` válido com `"agent": "forge:jarvis"`; `.forge/perfil` válido; `python3`, `git`, `gh` presentes; branch atual e alterações não salvas há muito tempo. **Modo completo** (terminal): `gh auth status`, acesso ao remoto, `develop`/`homolog` no remoto, atalho `jarvis`.
- **Conserta sozinho** só o que é idempotente e restaurável a partir do plugin, com backup (2.2): reativar `core.hooksPath`, restaurar `.githooks/` e chave `agent` a partir do modelo, permissão de execução. Todo conserto exige TTY e confirmação; o resto vira instrução em uma frase (ex.: "rode forge atualizar").
- **Ao abrir:** (a) o atalho `jarvis` roda `forge doutor --rapido` antes do `claude`, custo **0 token**; (b) o `vigia` (SessionStart, ADR 0003) chama a mesma função rápida, fica **silencioso** se tudo está bem e emite no máximo **uma linha** (~50 tokens) se algo falhou; nunca conserta dentro da sessão. Orçamento: < 100 ms, sem rede, dentro dos 10 s do hook.

### 2.4 Atualização segura
- `forge atualizar` (terminal): 1) `forge-upgrade --simular` e mostra o resumo em linguagem simples; 2) `forge doutor --rapido` antes; 3) **ponto de retorno**: tag local `forge/antes-<versão>` no projeto e versão do plugin gravada em `~/.local/state/forge/versoes.log`; 4) `claude plugin update forge@forge` + `forge-upgrade` (branch e PR, como hoje; nunca push nem merge); 5) doutor de novo; falhou → oferece voltar.
- **Fixar a versão:** marketplace adicionada na tag `vX.Y.Z` (ref da URL do Git) e atualização automática desligada; o Jarvis só avisa que há versão nova. **Spike da F5 (claude 2.x local, sem rede para o GitHub):** `claude plugin marketplace add --help` não documenta ref; testado com `https://<host>/<repo>.git#v1.0.0`, o `#v1.0.0` é aceito como parte da fonte (a CLI tenta clonar o endereço sem o fragmento e a falha é só de rede) e caminho local com `#` é recusado ("Path does not exist"). O checkout da tag em si não pôde ser observado sem rede: por isso a troca é sempre `remove` + `add <endereço>#vX.Y.Z` + `update` (ou `install`), com devolução ao endereço anterior se falhar, e o `forge atualizar` confere a versão pelas tags do próprio Forge (`git ls-remote`), sem depender da marketplace. `.forge/versao-plugin` não foi necessário. A conferir na primeira atualização real.
- `forge voltar-versao`: lê a última entrada de `versoes.log`, re-adiciona a marketplace na tag anterior e reinstala; no projeto, o PR de upgrade não mesclado é só fechado; se já mesclado, `git revert` do merge numa branch nova e PR (nunca reset nem `--force`).

### 2.5 Travas
Hook `conformidade`, Bash, todos os papéis. Já barrados (deny): `push --force` (`R-VERIFY`), push/merge na `main` (`R-MAIN`). Novos, com `permissionDecision: "ask"` e a consequência em linguagem simples (a confirmação é da pessoa, na janela de permissão, nunca de um agente):
| Ato | Mensagem (exemplo) |
|---|---|
| `gh repo delete`, `gh repo archive` | "Isso apaga o projeto inteiro no GitHub, com todo o histórico. Não tem volta." |
| `gh repo edit --visibility public`, `gh api` com `private=false` | "Qualquer pessoa na internet poderá ver todo o código e o histórico." |
| `git reset --hard`, `git clean -fd*`, `git checkout -- .`, `git restore .` | "Isso descarta mudanças não salvas. Prefira 'desfazer' (forge desfazer)." |
| `filter-branch`, `filter-repo`, `rebase` em branch publicada, `push --delete`/`:ref`, `branch -D` de `develop`/`homolog` | "Isso reescreve ou apaga histórico; outras cópias deixam de bater." |
No perfil `iniciante`, apagar repositório e reescrever histórico viram **deny** com a instrução de fazer pelo site do GitHub, se for mesmo a intenção.

### 2.6 Salvar e desfazer
- `forge salvar ["mensagem"]`: se estiver na `main`/`develop`/`homolog`, cria `trabalho/<AAAAMMDD-HHMM>` antes; `git add -A` (respeitando `.gitignore`), commit e `git push -u` da própria branch, sem `--force`. No iniciante, o Jarvis salva ao fim de cada etapa concluída; o `vigia` (Stop) avisa uma linha se há alterações não salvas há mais de 30 min.
- `forge desfazer`: alterações não salvas → `git stash push -u -m "desfeito <data>"` (recuperável por `forge desfazer --recuperar`); último commit → `git revert HEAD --no-edit` e push normal (`R-VERIFY`: história só cresce). Commit de merge ou na `main` → recusa e explica.

### 2.7 Problema vira contribuição anônima
- `forge sugerir` (ou o Jarvis, ao ver recusa, falha do doutor ou erro de comando do Forge): monta problema observado, proposta e como medir; anonimiza com `forge-check transcricao anonimizar` + lista de `termos_proibidos` + nome do projeto, caminhos, login e e-mail; **mostra o texto inteiro** e só segue com "sim" (`R-NEUTRO`).
- Bot e `Forge-contrib` adiados: grava em `~/.local/state/forge/sugestoes/<data>-<tema>.md`. Envio opcional pelo fluxo `R-CONTRIB` atual, num clone de nome neutro `~/.forge-contrib/anon-<hash6>` (o prefixo `melhoria/anon-<hash6>-` não revela o projeto), pela conta da própria pessoa: **não é anônimo no GitHub** e a mensagem diz isso (P1).

### 2.8 Primeiro pedido guiado
Fim da skill `novo-projeto`: o Jarvis propõe um pedido-exemplo pequeno e neutro ("um README que explica o projeto em 5 linhas") que percorre o ciclo inteiro em escala mínima (discovery curto, plano, implementação, review, QA, PR na `develop`, promoção e o PR para a `main` que **a pessoa** mescla), narrando cada etapa em uma frase. Pode pular; usa os agentes normais, sem custo extra além dos tokens da sessão.

## 3. Fatias de entrega
| # | Fatia (PR para `develop`) | Itens | Depende | `afrouxa-regra` | Testes |
|---|---|---|---|---|---|
| F1 | Primeiro uso básico: `bin/forge`, `forge-novo-projeto`, skill `novo-projeto`, `.forge/perfil` + skill `modo-iniciante`, linha no `jarvis.md` | base, 1 | — | Não (toca `bin/`: parecer de review) | e2e com `gh`/`claude` falsos (ordem, `--private`, 3 branches, `.forge/versao`), falhas, retomada, perfil gravado e ignorado pelo git, shellcheck |
| F2 | Primeiro pedido guiado + `forge salvar`/`desfazer` | 8, 6 | F1 | Não | repositório temporário: salvar fora da `main`, desfazer por revert e stash, nunca `--force`, recusa em merge |
| F3 | `forge doutor` + atalho `jarvis` + linha no `vigia` | 3 | F1 | Não (toca `hooks/`: parecer; fixtures novas, nenhuma removida) | fixtures de cada falha e conserto com backup; sem TTY não conserta; SessionStart silencioso quando ok e < 100 ms |
| F4 | Instalação intocável e travas: `caminhos` e `acoes` novos, `ask`/deny, sufixo da recusa, `forge config` assistido | 2, 5 | F3 | Não, se só adiciona; **sim** se mudar o resultado de fixture existente (avaliar no review) | fixtures em `tests/hooks/` por ato (ask × deny por perfil), backup e restauração, invariantes novos em `tests/config.json` |
| F5 | `forge atualizar` e `forge voltar-versao` (spike da ref da marketplace) | 4 | F3 | Não | marketplace e `claude` falsos: simular → doutor → tag → update; voltar restaura a versão do log; revert em vez de reset |
| F6 | `forge sugerir` com anonimização e fila local | 7 | F4 | Não | anonimização remove nomes, caminhos, login, e-mail e `termos_proibidos`; nada sai sem "sim"; branch `melhoria/anon-*` aceita pelo hook |
Todas: versão minor em `plugin.json` + `CHANGELOG.md`; F1, F2 e F6 podem seguir em paralelo a F3–F5 depois da F1.

## 4. Riscos
| Risco | Tratamento |
|---|---|
| Hook lê o Bash como texto: script ou ofuscação passa | Sandbox é a garantia; comandos assistidos exigem TTY |
| `ask` treina a pessoa a clicar "sim" | Só nos atos da tabela 2.5, mensagem com a consequência; os irreversíveis viram deny no iniciante |
| Iniciante esconde decisão que era dela | `modo-iniciante` lista o que sempre vai à pessoa (`R-DECISAO`) |
| Versão fixada atrasa correções de segurança | O doutor avisa versão nova; `forge atualizar` é seguro e reversível |
| `R-CUSTO`, `R-NEUTRO` | Só `git`, `gh` e GitHub gratuito; nada fixo de conta; anonimização testada |

## 5. Perguntas ao dono
**P1. Contribuição "anônima" enquanto o bot está adiado.** (a) fila local e envio opcional pela conta da pessoa, avisando que o GitHub mostra o autor; **recomendada** (com D1 = A, só o dono usa); (b) segurar o envio até o bot, só a fila local.
**P2. Versão do plugin fixada por padrão em novos projetos.** (a) fixada, o Jarvis avisa e `forge atualizar` aplica; **recomendada** (nada muda sem a pessoa); (b) atualização automática, com o doutor ao abrir como rede.
