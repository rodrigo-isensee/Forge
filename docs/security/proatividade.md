---
tipo: revisao-seguranca
contrato: 1
pedido: proatividade-melhoria
branch: melhoria/proatividade
commit: 640f304da65c32375ea1d9cedac3fac0db06405a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: proatividade-melhoria

Diff revisado: e9c81e0..640f304 (9 arquivos de D1 a D8 mais o fragmento de changelog). Revisão estática, sem execução da suíte. Observação de formato: o brief pede `tipo: security`, mas o validador (`bin/forge-check:102`) só aceita `revisao-seguranca`; usei o segundo.

## Gatilhos
Controles do Forge (`docs/regras/R-DECISAO.md`, agentes), `bin/forge-check` e `tests/config.json` (`R-SEGURANCA`).

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferências pedidas:
- **Limites do dono, literais:** dinheiro real nunca, sem exceção, está em `docs/regras/R-DECISAO.md:34` (c) e (d: "melhoria que custa dinheiro real não entra na fila"); aumento de tokens ou de tempo vai ao dono em `R-DECISAO.md` item 1 (lista de decisões), (c), (d) e em `agents/jarvis.md` ("Continuam sendo do usuário"). D1 a D8 aplicados como desenhados.
- **`tests/config.json`:** comparação por script contra e9c81e0: 0 itens removidos ou alterados, 9 itens novos (inclui a chave `bin/forge-check`).
- **`bin/forge-check`:** o diff muda uma única chamada de `saida` (texto do bloco Relatório de `cmd_brief_gerar`); nenhuma checagem, condição ou código de saída é tocado.
- **Entrada direta não abre caminho para afrouxar controle, custo ou regra:** as quatro condições são cumulativas, "na dúvida" vai ao usuário, e `agile-coach` e Jarvis mantêm como do usuário o registro no `CLAUDE.md`, custo, controle e tokens/tempo.

Recomendações (sem caminho de ataque realista, não bloqueiam; dono: tech-lead, em PR futuro):
- R1: em `R-DECISAO.md:34`, o parêntese "(passo, rodada, agente ou texto lido a cada delegação)" é uma lista fechada e mais estreita que o limite do dono ("o que aumenta token ou tempo de entrega"). Trocar por "por exemplo" evita que um aumento de outra natureza (ex.: CI mais longo) passe como entrada direta.
- R2: "controle" na condição (c) não é definido. Citar `R-CONFORMIDADE` (hook, sandbox, permissões, rulesets) como a lista de controles tira a decisão do juízo do próprio classificador (o Jarvis classifica a melhoria que ele mesmo vê).
- R3: `agents/agile-coach.md:19` removeu "mudança nas instruções de qualquer agente, skill ... precisa de aprovação do usuário"; agora instrução de agente pode entrar direto se passar o critério. Foi o pedido do dono e resolve a contradição com a linha 21; a defesa é o item "não afrouxa regra" e a revisão do PR. Registrado como risco conhecido.

## Riscos aceitos e ferramentas
Nenhum risco aceito formal. Ferramentas: leitura do diff, `git show` e script Python local para a comparação das invariantes; `gitleaks`, `zizmor` e outras não se aplicam (sem segredo, workflow ou dependência no diff).
