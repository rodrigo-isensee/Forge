---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-dir28-sandbox
commit: 43d2f378e0b83258a958f24ec97a51c2bbeb9719
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança por delta: v0478 E151.9 (PR #847, diretriz 28 no Jarvis)

Revalidação do parecer anterior (commit `4568c9b7`, aprovado; rodada no git, `c9693016`). Delta lido com `forge-check parecer delta`: `4568c9b7..43d2f378`, sem o que veio da `develop` pelo merge `bb5a6041` (revisado nos PRs de origem).

Gatilhos: texto de agente e skill sobre decisão do dono (`R-DECISAO`) e controle de execução (sandbox do Bash).

## Veredito por mudança: só aperta ou neutro
- `skills/fluxo-do-pedido/SKILL.md:40` (neutro): a regra "Resposta curta (O4)" vira ponteiro para `skills/falar-com-o-dono/resposta-curta.md`. O destino traz o texto idêntico na linha 7, inclusive "`aprovo` só vale para a recomendada `[reversível]`", e é protegido por invariante (`tests/config.json:305-307`, motivo em `:802`). Nenhuma regra some: o trecho removido era cópia; a trava de aprovação fica no arquivo protegido.
- `changelog.d/v0480-dir28-sandbox.md` (neutro): só o tipo do fragmento; fora do domínio.
- Os demais arquivos do parecer anterior (`agents/jarvis.md`, `skills/falar-com-o-dono/nao-trava.md`, teste e fixture) não mudaram no delta; o veredito "aperta" deles segue.

Achados anteriores: nenhum. Achados novos: nenhum.

## Detalhe dos achados
Sem achado. Testes dos arquivos tocados, local no head `43d2f378`: `python3 -m unittest tests.test_jarvis_nucleo` → 45 testes, OK; `python3 -m unittest tests.test_forge.RegrasInviolaveis` → 3 testes, OK. A suíte inteira é do CI do PR #847.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática de texto; nenhuma varredura se aplica a um diff só de texto.
