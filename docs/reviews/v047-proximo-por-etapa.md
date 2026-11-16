---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-proximo-por-etapa
commit: 7d675afaa992f35ac6030fbf232c2b8fcc77b47a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (forge-check proximo rápido, --etapa e PR mesclado, E2.72; review E2.119)

## Achados
- A1 (recomendado) bin/forge-check:6961 · a etapa sai feita pelo nome da branch, sem olhar se o commit dela está na develop: no v047 a E1.83 tem 489d249e na melhoria/v047-develop-verde depois do squash #538, fora da develop, e sai feita (PR mesclado). Sugestão: cartão para cruzar com o rev-list.
- A2 (recomendado) tests/test_proximo.py:245 · o diff tem 233 linhas de código e teste (forge-check 87, test_proximo 146) e três cartões num PR; o corpo do PR precisa de `teto: excedido, 233 linhas, <motivo>` (M14).

## Sondas

## Parecer
Aprovado no 7d675afa, parecer completo (não havia parecer anterior). Diff contra a base bf475209: `bin/forge-check`, `tests/test_proximo.py`, três specs de mutante e o fragmento de changelog.

O que o lote pede (brief v047-tech-lead-261, E2.72) e o que entrega:
- FORGE-CHECK-PROXIMO-LENTO: `etapas_conferidas` lê um `rev-list` por branch (memorizado em `alcance`) no lugar de `rev-parse` e `merge-base` por par selo × conferida; a semântica se mantém (commit contido na branch, branch sem ref não entrega). O índice `por_termo` com `[\w.]+` equivale à busca antiga `(?<![\w.])id(?![\w.])`: o id casa só como corrida máxima inteira, e um ponto final colado (`E2.72.`) segue sem casar nos dois. `test_git_por_branch_nao_por_par_de_selo_e_conferida` conta os `git` por um falso de PATH que repassa ao git real (menos de 40 contra mais de 300 na base). O tempo do v047 (menos de 20 s) não foi medido aqui: o brief proíbe rodar `forge-check proximo v047`; fica a palavra do fragmento (uns 8 s).
- PROXIMO-POR-ETAPA: `--etapa` valida por `fullmatch` com `ETAPA_DO_BRIEF` (rc 2 fora da forma ou fora do `## Etapas`, uma linha, nome por `sem_controle`/`nome_seguro`); sem ela, só as etapas fora de `FECHADAS`, com a contagem das fechadas e o corte antes do passo e dos bloqueios (o teto de 40 continua, agora com `mais N etapas omitidas`). O passo também pula as etapas `FEITA`.
- PROXIMO-BRANCH-PR-MESCLADO: sem rede, pelo nome exato (`fullmatch` no assunto `Merge pull request #N from <dono>/<branch>` e linha inteira `branch:` nos pareceres da árvore da develop). Testes cobrem merge, squash com parecer, parecer só na branch, nome parecido (`um-dois`, `tres-b`, `u`), entregue que segue entregue e repositório sem develop. Na sonda sobre o repositório real, 251 das 558 etapas do v047 saem feitas, em 26 branches; o A1 é o caso de borda achado nela (no registro, a E1.83 foi descartada depois do merge, então o rótulo não engana aqui, mas a regra não distingue).

Regras e checklist: R-NEUTRO sem termo de projeto; sem shell tocado (sem shellcheck); sem I/O de rede (R-CUSTO). A saída segue limitada em linhas e largura e passa por `sem_controle` (C-17a). Texto de documentação: `agents/jarvis.md` e a ADR 0003 citam o comando e o teto de 40 linhas, que continuam valendo. Commits em Conventional Commits, um por cartão e o fragmento.

Verificadores (rodados aqui, só o item): `python3 -m unittest tests.test_proximo` com ambiente limpo, 23 testes OK. `bin/forge-mutante --cobertura --base bf475209` rc=0, toda condição mudada coberta por mutante declarado (uma isenção justificada, o índice por termo). `bin/forge-mutante --processos 1` nas três specs: PE-M1 a PE-M20, 20 mortos, rc=0. Suíte completa: fica para o CI do PR (ainda não há PR nesta etapa).

Achados recorrentes (PA-7): conferidos AR-1/AR-2 (mutantes completos e ramo de falha de `--etapa` testado), AR-4 (o `AMBIENTE` do teste é anterior a este diff e o subprocesso novo usa `-I`), AR-12 (as specs batem com as linhas do head, pelos 20 mutantes mortos). Nenhuma classe repetida neste diff.
