---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-token-bot
commit: d3dc41a534dae61117917c25993574afd2e4417a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E7.2, token dos agentes)

Escopo: `docs/token-dos-agentes.md` (novo), uma linha na ADR 0009 §9 e o fragmento `changelog.d/v0478-token-bot.md`. Classe T, só texto: sem guarda, sem mutante, sem suíte local (o CI do PR roda a bateria).

## Revalidação (d3dc41a5)
Delta lido: `forge-check parecer delta docs/reviews/v0478-token-bot.md`, intervalo d342dc4a..d3dc41a5, no domínio só `docs/adr/0009-conformidade-dos-agentes.md` e `docs/token-dos-agentes.md`.
- A1 resolvido: 0009:89 registra que o classic com `repo` substitui o fine-grained da ADR 0008:17, com o motivo (conta pessoal, robô colaborador) e a volta ao fine-grained numa organização.
- A2 resolvido: 0009:63 diz "aplicada em parte", token ainda do dono com administrador, troca pendente (TOKEN-AGENTES-BOT).
- A3 resolvido: token-dos-agentes.md:41 manda conferir papéis ("Write" e "Maintain" fora; só "Repository admin").
- A4 resolvido: token-dos-agentes.md:61-62 dá o terminal do contêiner, `nano ~/.claude/settings.json`, Ctrl+O/Enter e Ctrl+X; a linha 83 (voltar atrás) repete o comando.
- A5 resolvido: token-dos-agentes.md:96 cita a branch que trouxe por merge um commit em `.github/workflows/`.
Nenhum segredo no delta. Aprovado no head d3dc41a5.

## Parecer da rodada anterior (d342dc4a)
Reprovado por A1 (requisito do pedido: bater com a ADR 0009). O guia em si está correto e seguível; o defeito é a ADR, que continua dizendo outra coisa sobre o tipo de token pela ADR 0008 que ela mantém em vigor. A correção é uma linha na §9; a explicação técnica do guia (fine-grained não alcança repositório de conta pessoal onde o robô é só colaborador) é a que deve ir para lá.

Conferido, sem achado:
- Leigo consegue seguir: cinco passos com tempo, endereço exato, o que aparece no fim de cada um, caminho de volta (linhas 81-85) e "pare e avise o Jarvis" se a tela divergir (linha 11). As exceções são A3 e A4.
- Nada guarda segredo: nenhum valor de token no diff (busca por `gh[pousr]_` e `github_pat_` com corpo: zero; só o prefixo `ghp_` na linha 54). A chave fica no aplicativo de senhas e no `~/.claude/settings.json`, fora do repositório; a linha 59 proíbe colá-la em conversa, arquivo ou commit; a conferência do Passo 5 só lê login e permissões; vazamento tem procedimento (linha 85). Validade de 90 dias, sem `workflow`, `admin:*` nem `delete_repo`.
- ADR 0009: quem executa é o dono (§5, `~/.claude` é caminho protegido nativo do sandbox, linha 19); `R-MAIN` preservada (linha 92 e linha 98); `R-CUSTO` (conta gratuita, linha 3). Fatos conferidos: papel Write devolve `{"admin":false,"maintain":false,"pull":true,"push":true,"triage":true}`; o `GH_TOKEN` está hoje no `~/.claude/settings.json` (1 ocorrência da chave, valor não lido).
- Fragmento do changelog no formato; commit em Conventional Commits, em português.
