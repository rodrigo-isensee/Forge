# 0017 - Forge sempre atual: atualização na abertura, com checagem e volta

Estado: proposta (vale quando o PR da `melhoria/v047-forge-sempre-atual` entrar na `develop`; até lá a ADR 0005 vale como está escrita). Data: 2026-11-15.
Propósito: decidir como o plugin do Forge chega sozinho à última versão publicada na `main`, em todos os escopos instalados, e como os arquivos do modelo chegam aos projetos. Emenda a [0005](0005-migracao-iniciada-pelo-projeto.md). Público: quem mantém o Forge e os projetos. Revisão: 2026-11-15.

## Contexto
Diretriz 30 do dono (ORDEM DO DONO de 2026-11-15, pedido v047, E6): "o Forge fica sempre na última versão, sem que eu precise fazer nada, no Forge e em todos os projetos", só na abertura, nunca no meio de trabalho em curso, sem pedido de ação ao dono e sem reabertura forçada; se a versão nova quebrar a checagem de início, volta à anterior e avisa; nos projetos, os arquivos do modelo chegam por branch e PR na `develop`, feitos pelo `tech-lead`; a `main` continua do dono.

Evidências:
- A 0.47.1 saiu às 08:58 de 15/11 e às 19:48 a sessão do Jarvis ainda rodava a 0.47.0. O escopo de projeto de um projeto desta máquina está na 0.45.2 desde 10/11 (`installed_plugins.json`), com três versões publicadas depois.
- A ADR 0005 diz "o Forge nunca atualiza quem o usa" e que o `forge-upgrade` roda "nunca por automação do Forge". A diretriz 30 pede o contrário para o plugin e muda quem dispara o `forge-upgrade`.
- Prova E6.1 (HOME temporário, catálogo git com tags, sem custo, `~/.forge-contrib/docs/devops/sempre-atual-prova.md`):
  - trocar o `ref` do catálogo em `~/.claude/settings.json` e rodar `marketplace update` **não tem efeito**: a CLI lê `known_marketplaces.json`;
  - `claude plugin marketplace add <url>#<tag> --scope user` sobre o catálogo existente, seguido de `claude plugin update forge@forge --scope <s>`, **sobe e desce** a versão nos escopos de usuário e de projeto, e as entradas de projeto ficam;
  - `claude plugin marketplace remove forge --scope user` **desinstala o usuário e todos os projetos** e reescreve o `.claude/settings.json` versionado do projeto, apagando `enabledPlugins`. É o que o `forge atualizar` faz hoje (`bin/forge_versoes.py:335-341`).

Desenho completo: `docs/arquitetura/forge-sempre-atual.md` em `~/.forge-contrib` (corrigido pela E6.2).

## Decisão
1. **Onde roda.** Uma ferramenta, `bin/forge-sempre-atual` (lógica em `bin/forge_sempre_atual.py`), chamada só pelo atalho (`jarvis`, `jarvis-forge`) antes do `exec claude` e pelo postStart do container. Recusa dentro do Claude. Nenhum hook atualiza nada; o doutor só mostra o aviso pendente.
2. **Alvo.** A maior tag `vX.Y.Z` do repositório do Forge (as tags `v*` são criadas pelo `release.yml` no push da `main`), salvo fixação vigente. A branch padrão do remoto tem de ser `main`; senão, não atualiza e registra. Antes de mexer no catálogo (avanço ou volta), o commit da tag alvo tem de estar na `main` do remoto: a ferramenta busca só os commits da `main` e da tag (`--filter=tree:0`) num repositório vazio temporário e confere com `merge-base --is-ancestor`; fora da `main` ou sem como conferir, registra `falhou:origem-da-tag` e nada muda (parecer de segurança da E1.52, A2).
3. **Um só mecanismo para subir e para voltar:** `claude plugin marketplace add <url>#v<alvo> --scope user` sobre o catálogo existente (só quando o `ref` lido em `known_marketplaces.json` difere do alvo) e, depois, `claude plugin update forge@forge --scope <s>` em cada escopo livre, com cwd no `projectPath` para projeto e local. O catálogo fica sempre fixado numa tag.
4. **Proibido na ferramenta:** `marketplace remove`; gravar `~/.claude/settings.json` ou `known_marketplaces.json` (quem grava é a CLI); matar processo, mandar tecla ao tmux, `/reload-plugins`, `git push` ou `gh`.
5. **Ocupação.** Sessão tmux do projeto aberta: só reanexa. Escopo com processo `claude` vivo e agente vigente, trava `pesado`, suíte do pre-push ou integração em curso: adia e registra. A suíte é conferida pelo `.githooks/pre-push --status` da cópia instalada que roda a ferramenta (a trava é por usuário), nunca por arquivo da pasta do projeto, que um agente pode gravar (parecer de segurança da E1.52, A1). Leitura em dúvida conta como ocupado.
6. **Checagem de início (C-INI)** sobre a versão nova, conduzida pelo código da anterior, local e sem token: pasta existe e `claude plugin validate` sai 0; `py_compile` de `hooks/` e `bin/`; `bash -n` dos scripts de entrada; `forge-doutor --rapido` sem problema novo.
7. **Volta.** C-INI falhou: grava a fixação `volta-automatica`, roda o mecanismo do item 3 com a última boa e confere a versão de cada escopo. A fixação cai quando sair versão maior que a quebrada. Volta que falha: registro e aviso com o comando exato (único caso em que o dono recebe comando).
8. **Estado** (registro, última boa, fixação, aviso, adiamentos) no caminho fixo `~/.claude/plugins/data/forge-forge/forge/sempre-atual/` (0700), que fica no volume `~/.claude`, onde agente não grava. Nunca derivado de `CLAUDE_PLUGIN_DATA` (na sessão `--plugin-dir` a pasta é `forge-inline`).
9. **Âncora de confiança.** O código executado vem só do installPath ativo do escopo do usuário em `~/.claude/plugins/cache`; nunca do work tree, de ref local nem de pasta órfã do cache. Os atalhos em `~/.local/bin` viram trampolins para esse installPath e são recolocados pelo postStart.
10. **Emenda à ADR 0005.**
    - Onde a 0005 diz "o Forge nunca atualiza quem o usa": o **plugin** passa a ser atualizado pela abertura (itens 1 a 7). Os **arquivos do projeto** continuam mudando só por branch e PR no fluxo do projeto.
    - Item 2 da 0005 ("rodado pelo projeto [...] nunca por automação do Forge"): passa a ser rodado também pela abertura automática do atalho, que é o processo do dono, fora do sandbox, com o `forge-upgrade` da versão já aprovada na C-INI. Ele prepara só a branch local `forge/upgrade-<v>` a partir da `origin/develop` (`forge-upgrade --base origin/develop`, sem os hooks de commit do projeto), numa worktree temporária, sem tocar a cópia de trabalho nem o HEAD do projeto, sem `push` e sem `gh`. Idempotente: branch existente, local ou no remoto, não é refeita.
    - No projeto, o Jarvis vê a branch pronta (aviso do `forge-check`) e dispara o `tech-lead`, sem perguntar ao dono: envio, PR na `develop`, portões da classe e merge com tudo verde (R-FLUXO, ADR 0014). O que a catraca do projeto pedir ao dono fica parado e listado (R-CONFORMIDADE). A `main` segue do dono (R-MAIN).
    - O resto da 0005 (migrações idempotentes, um commit por migração, `.forge/versao`, SemVer, testes com fixture) não muda.
11. **`forge atualizar` e `forge voltar-versao`** deixam o `marketplace remove` e usam o mecanismo do item 3; só o `--fixar` e o `voltar-versao` gravam fixação do dono, respeitada pela ferramenta.

## Alternativas
| Opção | Por que não |
|---|---|
| Atualização nativa (`autoUpdate: true`) | Roda depois da primeira mensagem, no meio da sessão, sem trava de ocupação, sem checagem, sem volta e sem registro; ligá-la pede migração em cada projeto. |
| Catálogo sem `ref`, seguindo a `main`, com `marketplace update` | Voltar exige fixar e depois soltar a fixação por `add` sem `#ref` sobre o existente, que não foi provado (E6.1, U2). Dois mecanismos onde um provado basta. |
| Volta trocando o `ref` em `~/.claude/settings.json` | Provado sem efeito (E6.1, U2 item 1). |
| Volta editando `known_marketplaces.json` | Funciona, mas grava em arquivo interno da CLI, em pasta em vigor (`~/.claude/plugins/`). |
| `marketplace remove` + `add` (o que o `forge atualizar` faz) | Desinstala todos os projetos e apaga o `enabledPlugins` deles (E6.1, U3). |
| Hook `SessionStart` que atualiza | Automação do agente sobre arquivo em vigor, dispara em `resume`/`compact`, prazo de 10 s e a sessão já carregou a versão antiga. |
| `tech-lead` roda o `forge-upgrade` no projeto | O `forge-upgrade` grava `.forge/versao`, `.claude/` e `.githooks/`, arquivos em vigor com `quem: []`; dar essa escrita ao agente afrouxaria R-CONFORMIDADE. |

## Consequências
- Melhora: plugin em dia em todos os escopos sem ação do dono; versão quebrada volta sozinha; o projeto recebe o modelo por PR sem o dono rodar nada; o `forge atualizar` para de apagar os projetos da máquina.
- Piora: a abertura ganha um `git ls-remote` (caminho rápido) e, quando há versão nova, um `marketplace add` e um `plugin update` por escopo, com orçamento de 60 s. Quando a fixação é do dono, o Forge fica parado até ele soltar (avisado uma vez por versão).
- A manter: o caminho fixo `forge-forge` acompanha o nome do plugin e do catálogo; as tags `v*` só podem nascer da `main` (parecer de segurança da E6.4/E6.5): a ferramenta confere a origem da tag e o hook `conformidade` barra `git tag` que cria ou apaga e todo envio de tag no repositório do Forge; a regra de tag no GitHub (só o Actions cria `v*`) é decisão do dono, e o código não depende dela; a reconciliação do catálogo na partida da sessão (não provada) é coberta por toda abertura reafirmar o `ref` antes do `plugin update`.
- Segurança: código executado como o dono, fora do sandbox, só da âncora (item 9); nenhuma credencial lida ou repassada (`GH_TOKEN` fora); afrouxa controle: não (nada sai de `docs/regras/`, de `tests/config.json` nem de `hooks/conformidade.json`; nenhum agente ganha escrita em arquivo em vigor).

## Por que o existente não basta
| O que existe | Evidência de execução |
|---|---|
| Aviso de versão nova do doutor (`hooks/doutor.py:76`) | Só avisa e pede ação. O escopo de projeto citado no Contexto está na 0.45.2 desde 10/11, com três versões publicadas depois. |
| `forge atualizar` / `forge voltar-versao` | Interativos e recusam dentro do Claude (`bin/forge-atualizar:210`); só o escopo do usuário; o `marketplace remove` deles desinstalou usuário e dois projetos na prova E6.1 (U3: `installed_plugins.json` -> `{"version": 2, "plugins": {}}`). |
| `atualizar_ao_abrir` do `jarvis-forge` | Atualiza só a cópia vigente da sessão do Forge; não toca o `forge@forge` instalado, que é o que a sessão das 19:48 usou. |
| `autoUpdate` nativo | Desligado no modelo (`templates/projeto/.claude/settings.json:6`); ligado, roda no meio da sessão. |

## Critério de reversão
Uma abertura depois da qual um escopo que constava em `installed_plugins.json` antes dela some do arquivo, ou fica numa versão que não tem, no registro da ferramenta, linha `atualizado` ou `voltou` com a C-INI aprovada. Um caso basta para desligar a ferramenta no atalho e no postStart e voltar ao aviso do doutor.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| AAAA-MM-DD | escopos sumidos ou em versão sem linha aprovada no registro; e, na primeira recriação do container, `command -v claude` no postStart (U5) | pendente |
