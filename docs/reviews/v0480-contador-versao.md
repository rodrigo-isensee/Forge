---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: fb4d5390b925256caa28286bef2f997d8af66489
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E103.3, CONTADOR-DA-VERSAO)

Escopo lido: `bin/forge-contador`, `tests/test_forge_contador.py`, as três specs `tests/mutantes/v0480-contador-versao*.json`, `skills/fluxo-do-pedido/SKILL.md:48`, `changelog.d/v0480-contador-versao.md`, `tests/pesos-d4.json`. Diff único (fb4d5390 sobre 900bfdfe).

Ferramentas citadas, sem refazer: `forge-check pr v0478` no head: classe C (`bin/forge-contador` sensível da catraca) e "tamanho: 154 linhas de código, acima do teto de 150 por item". Teste do item: `python3 -m unittest tests.test_forge_contador`, 16 testes, OK. Suíte inteira: fica no CI do PR.

Conferência com o quadro real do Forge (só leitura): `forge-contador --raiz /workspaces/Forge --quadro KANBAN.md --historico historico.md --data 2026-11-22` dá `0.47.15: 6 de 20`, igual à contagem do Jarvis no Histórico (05:59), e a visão do backlog com 163 abertos por coluna.

## Achados
- A1 (bloqueante) bin/forge-contador:58 · N conta só fragmentos changelog.d; o modelo de projeto não os tem, e a skill (fluxo-do-pedido:48) manda todo projeto usar a linha: projeto com 3 PRs mesclados desde v1.2.0 lê "1.2.1: 0 de 20" (S1). Ordem do dono 20/11 09:56: Forge e todos os projetos, contagem pelos PRs mesclados.
- A2 (bloqueante) bin/forge-contador:1 · 154 linhas de código, acima do teto de 150 (H1, saída do forge-check pr); só a docstring tem 12 linhas, então cortar não quebra a suíte e o `teto: excedido` não se aplica: enxugue até 150.
- A3 (recomendado) bin/forge-contador:86 · a guarda da linha separadora (`not set(celulas[0]) <= set("-:")`) não tem mutante declarado; o test_so_quadro a mata, mas a classe C pede um mutante por linha de guarda.
- A4 (recomendado) skills/fluxo-do-pedido/SKILL.md:48 · cita `bin/forge-contador`, caminho que só existe no repositório do Forge; no projeto o comando chega pelo PATH do plugin como `forge-contador`.

## Sondas
- S1 · repo develop com tag v1.2.0 e 3 commits "feat: item N (#N)", sem changelog.d; `forge-contador --raiz <repo>` · espera: 1.2.1: 3 de 20 · obtido: 1.2.1: 0 de 20

## Parecer
Reprovado. O cálculo no Forge está correto e conferido contra o quadro real; os guardas têm teste de comportamento do ramo de falha, subprocesso com ambiente limpo e `-I`, e só leitura sem rede.

- A1: `bin/forge-contador:58` · em projeto o N é sempre 0, e a skill estende a linha a todos os projetos · contar os PRs mesclados na ref desde a última marca (first-parent, `marca..ref`) quando não houver `changelog.d/`, ou restringir a linha da skill ao Forge até o item de projeto existir, com cartão · bloqueia (requisito da ordem do dono com gatilho provado em S1).
- A2: `bin/forge-contador:1` · teto H1 apontado pela ferramenta · encurtar a docstring ou o `main` · bloqueia.
- A3 e A4 viram cartão depois do merge.
