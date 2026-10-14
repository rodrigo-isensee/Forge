# Primeiro uso do Forge (rascunho do dono + Jarvis, 2026-10-13)

1. Abrir terminal e Claude (pré-requisitos: Claude Code, conta GitHub com acesso; estação nova: preparar-estacao.sh).
2. Trazer o Forge como plugin: `claude plugin marketplace add rodrigo-isensee/Forge` + `claude plugin install forge@forge` (sem clonar; clone só para desenvolver o Forge).
3. Comando `forge novo-projeto` abre o Claude com o Jarvis numa pasta nova; sem `.forge/versao`, o Jarvis se apresenta como orquestrador e explica o roteiro.
4. Repositório e acesso: Jarvis pede a URL do repositório vazio; confere gh auth, identidade do git e acesso; clona; cria develop e homolog.
5. Contexto: nome e objetivo, quem usa, stack, regras invioláveis, comando de pronto — uma pergunta por vez — vira o CLAUDE.md.
6. Configurações: forge-init, Jarvis como agente principal, hooks, KANBAN, modelo de CI, atalho `jarvis`; primeiro PR "adota o Forge"; pergunta o primeiro pedido.

Decisões do dono:
- D1 (distribuição) = A: por enquanto só o dono usa o Forge.
- D2 (repositório) = A: o Jarvis oferece e CRIA o repositório para a pessoa (`gh repo create`, privado, na conta dela), já com develop e homolog; se ela já tiver, usa a URL. Desenho já pensado para outras pessoas no futuro: nada fixo da conta do dono.
- Suposições do time (2026-10-13): commit inicial na main pelo script, como ato do usuário no terminal (R-MAIN); pasta fixa `~/<nome-do-projeto>`, avisada na tela (BUG-03, limite de 10 interações; quem quiser outra pasta move depois); regras invioláveis com padrão "nenhuma por ora"; tempo medido no e2e com gh falso e cronometrado no próximo projeto real.
- D3 (escopo) = B: o pedido "primeiro uso" inclui os 8 itens de cuidado com quem não programa: (1) perfil de experiência (iniciante: sem jargão, sem decisão técnica); (2) instalação do Forge intocável (recusa explicada vira sugestão; configuração só por comando assistido com backup); (3) `forge doutor` (diagnóstico e conserto seguro, roda ao abrir); (4) atualização segura com simulação, doutor e `forge voltar-versao`; (5) travas para atos perigosos (apagar repo, tornar público, force push, main direto, apagar histórico) e confirmação com consequência em linguagem simples; (6) salvar com frequência e "desfazer a última mudança"; (7) problema vira contribuição anônima ao Forge, com autorização; (8) primeiro pedido guiado de exemplo.
- Dono (2026-10-13): o doutor roda de tempos em tempos no projeto, não só ao abrir. Desenho do time: ao abrir a sessão; durante a sessão uma vez por dia (decisão do dono) (hook barato, silencioso se tudo bem, cache com data em .forge/run/); antes de atualizar o Forge e antes de abrir PR. Sem custo, local.
- P1 (envio da sugestão anônima, F6) = A: pela conta da própria pessoa, com aviso e confirmação, conteúdo sem dados do projeto; quando o bot e o Forge-contrib existirem, passa a ser pelo bot.
- P2 (versão do Forge nos projetos novos) = A: fixada por padrão; o Jarvis avisa quando sai versão nova e oferece `forge atualizar` (simulação, doutor, ponto de retorno).
