# NNNN - Checagem do brief: skill neutra e lista local do projeto

Estado: proposta (vale quando o PR da `melhoria/checagem-do-brief` entrar na `develop`; o número é tomado na integração, em ordem, depois do E6c da 0.37). Data: 2026-11-06.
Propósito: registrar a skill `checagem-do-brief` e a lista local `docs/engineering/brief-checklist.md` (CHECAGEM-DO-BRIEF, B3). Público: quem mantém o Forge e quem escreve brief. Revisão: 2026-11-06.

## Contexto
O que só um projeto exige no brief ficava na memória de quem escreve o brief. No Forge foram 9 omissões em 13 pedidos (STATUS-HOOK-DEVELOP, BRIEF-DIFF-COMMIT, WORKFLOW-SCOPE e outras; discovery-2, CHECAGEM-DO-BRIEF). O dono decidiu a B3 (2026-10-20): uma skill neutra no plugin para todos os projetos, com uma lista local opcional. A decisão 24 (2026-11-06) encerrou a SK-1 (brief-do-forge) como coberta por esta.

## Decisão
1. `skills/checagem-do-brief/SKILL.md`: quando usar (todo brief, antes de `forge-check brief mensagem`), a lista neutra do que o script não confere e a leitura de `docs/engineering/brief-checklist.md` quando o projeto o tiver.
2. `templates/projeto/docs/engineering/brief-checklist.md`: modelo vazio e opcional; projeto existente não precisa migrar (ADR 0005).
3. `docs/engineering/brief-checklist.md` do Forge: os itens da SK-1.
4. `skills/briefs-e-conferencia/SKILL.md` manda ler a skill antes de mandar o brief.
5. A lista local só acrescenta: nenhum item dispensa conferente, review, QA, segurança nem rótulo do dono; item assim vira pergunta ao dono (`R-DECISAO`). Item que o `forge-check` passar a cobrir sai da lista no mesmo PR.

## Alternativas
- Skill só do Forge (`forge-dev:brief-do-forge`, SK-1): deixa os projetos sem lugar para a própria lista; encerrada pela decisão 24.
- Seção no `.claude/CLAUDE.md` do Forge: lida por todo subagente da sessão, e não só por quem escreve brief; custo maior por acionamento.
- Pôr os itens no `agents/jarvis.md` ou na `R-BRIEF`: vão para todos os projetos e ferem a `R-NEUTRO`.

## Consequências
- Custo aceito pelo dono: +1,0k a +1,5k tokens de entrada por sessão que escreve brief.
- Ganho estimado: 1 a 10 min por pedido, média 4 (9 omissões em 13 pedidos × 2 a 14 min).
- A manter: a lista local encolhe quando o `forge-check` ganha a checagem; o teste `ChecagemDoBrief` (`tests/test_modelos_projeto.py`) prende a citação à lista local, os itens da SK-1, a neutralidade da skill e a frase do limite.

## Por que o existente não basta
A skill `briefs-e-conferencia` descreve o fluxo e uma autoconferência genérica, sem lugar para os itens de um projeto. O `forge-check brief` cobre forma, corte, decisões e citações e não conhece regra local. Evidência de execução: as 9 omissões em 13 pedidos de 2026-10-20 passaram pelos dois.

## Critério de reversão
Se, nas três versões seguintes à entrada, as linhas `ERRO-JARVIS` de omissão no brief de item já listado em `docs/engineering/brief-checklist.md` não caírem abaixo de 1 a cada 5 pedidos, a skill sai e os itens que ainda faltam viram checagem do `forge-check`.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| AAAA-MM-DD | omissões de item listado por pedido | pendente |
