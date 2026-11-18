---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-token-bot
commit: d342dc4a22319237039f54ff188796b564e60a38
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E7.2, token dos agentes)

Escopo: `docs/token-dos-agentes.md` (novo), uma linha na ADR 0009 §9 e o fragmento `changelog.d/v0478-token-bot.md`. Classe T, só texto: sem guarda, sem mutante, sem suíte local (o CI do PR roda a bateria).

## Achados
- A1 (bloqueante) docs/adr/0009-conformidade-dos-agentes.md:89 · A ADR 0008:17 (que a 0009:88 diz seguir valendo) manda token fine-grained só deste repositório; o guia (token-dos-agentes.md:48-56) manda classic com `repo`. A linha nova não registra a troca: diga na §9 que o classic substitui o fine-grained e por quê
- A2 (recomendado) docs/adr/0009-conformidade-dos-agentes.md:63 · Diz "Etapa 2 aplicada ... com o token do bot", mas `gh api user` hoje dá a conta do dono com `"admin":true`; o guia (linha 8) está certo. Ajuste para "pendente da troca do TOKEN-AGENTES-BOT" no mesmo commit do A1
- A3 (recomendado) docs/token-dos-agentes.md:41 · Em repositório de conta pessoal, a lista de exceção do ruleset guarda papéis, não pessoas: o dono procura o nome do robô e não acha. Peça para conferir que nem "Write" nem "Maintain" estão na lista, só o papel de administrador
- A4 (recomendado) docs/token-dos-agentes.md:61 · Leigo não sabe abrir `~/.claude/settings.json` (pasta oculta) "no editor". Dê o comando exato (ex.: `nano ~/.claude/settings.json`, salvar com Ctrl+O, Enter, sair com Ctrl+X) e diga em qual terminal (o do contêiner onde o Claude Code roda)
- A5 (recomendado) docs/token-dos-agentes.md:95 · Sem o escopo `workflow`, o GitHub também recusa o envio de branch que trouxe por merge da `develop` um commit que muda `.github/workflows/` (não reproduzido aqui; comportamento conhecido do GitHub). Cite esse caso na linha da tabela para o time não tratá-lo como defeito

## Parecer
Reprovado por A1 (requisito do pedido: bater com a ADR 0009). O guia em si está correto e seguível; o defeito é a ADR, que continua dizendo outra coisa sobre o tipo de token pela ADR 0008 que ela mantém em vigor. A correção é uma linha na §9; a explicação técnica do guia (fine-grained não alcança repositório de conta pessoal onde o robô é só colaborador) é a que deve ir para lá.

Conferido, sem achado:
- Leigo consegue seguir: cinco passos com tempo, endereço exato, o que aparece no fim de cada um, caminho de volta (linhas 81-85) e "pare e avise o Jarvis" se a tela divergir (linha 11). As exceções são A3 e A4.
- Nada guarda segredo: nenhum valor de token no diff (busca por `gh[pousr]_` e `github_pat_` com corpo: zero; só o prefixo `ghp_` na linha 54). A chave fica no aplicativo de senhas e no `~/.claude/settings.json`, fora do repositório; a linha 59 proíbe colá-la em conversa, arquivo ou commit; a conferência do Passo 5 só lê login e permissões; vazamento tem procedimento (linha 85). Validade de 90 dias, sem `workflow`, `admin:*` nem `delete_repo`.
- ADR 0009: quem executa é o dono (§5, `~/.claude` é caminho protegido nativo do sandbox, linha 19); `R-MAIN` preservada (linha 92 e linha 98); `R-CUSTO` (conta gratuita, linha 3). Fatos conferidos: papel Write devolve `{"admin":false,"maintain":false,"pull":true,"push":true,"triage":true}`; o `GH_TOKEN` está hoje no `~/.claude/settings.json` (1 ocorrência da chave, valor não lido).
- Fragmento do changelog no formato; commit em Conventional Commits, em português.
