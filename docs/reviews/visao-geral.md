---
tipo: review
contrato: 1
pedido: visao-geral
branch: melhoria/visao-geral
commit: a0f05b8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Code review: visão geral do Forge (big picture com diagramas)

Escopo: `docs/visao-geral.md` (novo), `README.md` (uma linha com o link) e `CHANGELOG.md` (linha em `## [Não publicado]`); commit revisado `a0f05b8` sobre `develop`.

Conferido:
- Os agentes da tabela "O time" batem com `agents/` (seis agentes) e com a seção "Como conduzir um pedido" do `agents/jarvis.md` (passos 1 a 9). Os agentes da stack batem com `stacks/node-react/agents/`. `security-engineer` e `devops-engineer` estão marcados como previstos, porque não existem em `agents/`.
- As regras citadas existem em `docs/regras/` (`R-MAIN`, `R-FLUXO`, `R-CONTRIB`, `R-CONFORMIDADE`, `R-CUSTO`, `R-NEUTRO`, `R-DISCOVERY`, `R-QA`, `R-REVIEW`, `R-TETO`, `R-WIP`, `R-DECISAO`). As ADRs citadas existem com os títulos corretos (0003, 0006, 0008, 0009).
- Hooks: `hooks/hooks.json` tem `conformidade`, `parecer`, `pesado`, `quadro`, `vigia` e `agentes`; a tabela de guardas descreve cada um com o que faz.
- Catraca: os modos `regras`, `pareceres` e `pr-texto` existem em `tests/catraca.py`; afrouxar pelo rótulo do dono está correto.
- Links relativos: todos os alvos existem (verificado por script, incluindo a âncora `#sandbox-do-bash` do README).
- Nenhum nome real de fonte ou de projeto aparece: a fonte externa aparece só pelo código `F1`, como manda `docs/fontes-de-praticas.md`.
- Diagramas: sintaxe mermaid revisada à mão (não houve renderização). Nós por diagrama: 13 e 12, dentro do limite de 15. Legenda e alternativa em lista presentes, com título em `###`.
- ADR 0002: os IDs são citados pelo nome curto, sem repetir o texto das regras; a `AntiDuplicacao` passa.

Correções feitas nesta revisão (fato, não estilo), já incluídas em `a0f05b8`:
- `docs/visao-geral.md` (diagrama 1): a nota "(tabela 3)" apontava para a tabela errada; agora "(seção 4)", onde estão as guardas.
- `docs/visao-geral.md` (diagrama 2): "fonte de harness F1" virou "fonte de práticas F1", que é o termo usado em `docs/fontes-de-praticas.md`.
- Tabela "O time", linha do Jarvis: o Jarvis não abre PR (quem prepara o PR é o `tech-lead`, passo 8); a linha agora diz "resumo de entrega ao dono".
- Tabela de guardas, sandbox: "rede restrita" superava o que está em vigor. Pelo README, a rede só é restrita com `strictAllowlist` ligado pelo dono; sem ele, a barreira é só a negação das APIs de modelo. Ficou "APIs de modelo negadas".
- Tabela de guardas, hooks: os hooks não disparam só "em cada chamada de ferramenta"; há também eventos de sessão (`SessionStart`, `Stop`) e de subagente. Ficou dito assim.
- Tabela de guardas, token: "sem admin" não estava comprovado nas fontes lidas; ficou só o que o parecer do rótulo registra (sem escopo `workflow`), e a linha virou "Token da conta de máquina".
- `CHANGELOG.md`: linha nova em `## [Não publicado]`, no formato das seções anteriores.

Dúvidas registradas (não bloqueiam):
- `docs/reviews/_modelo.md` não existe em `develop` nem nesta branch, embora o pedido diga que existe. Usei como modelo o frontmatter de `docs/reviews/catraca-ci.md` (mesmos campos da ADR 0004). Sugestão para o arquiteto e para mim: criar o modelo numa melhoria própria, ou corrigir a referência nas instruções.
- A linha da tabela de guardas sobre o token ("conta de máquina") usa o nome que o `README.md` dá à identidade do bot. Se o dono distingue token local e conta de máquina, a linha deve dizer isso; hoje o texto é o mínimo verificado.
- O diagrama não foi renderizado pelo GitHub nesta revisão (CI de Actions indisponível). Se houver erro de sintaxe, aparece na página; não há teste automático para mermaid no Forge.

Parecer: **aprovado**. Nenhum achado bloqueante restante.
