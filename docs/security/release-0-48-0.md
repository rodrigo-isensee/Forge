---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.48.0
branch: melhoria/release-0-48-0
commit: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: release-0.48.0 (E2.2), leva da 0.48.0 contra a main

1ª rodada completa da leva, `origin/main..74d2a59c` (merge-base `1a9568b3`; a main só traz merges de promoção, `git diff HEAD origin/main` é o inverso exato da leva). Itens: #938 (C1b, `hooks/conformidade.py`), #945 (C2a, `bin/forge_pareceres.py`), #946 (`scripts/gerar-derivados.py`), #948 (espera amarela: `tests/catraca.py`, `catraca.yml`, `ci.yml`, `scripts/ci-local`), #949 (só teste), #950 (`hooks/agentes.py`), #951 (`bin/forge-contador`, `bin/forge-changelog`) e a marca (E1.1). Cada item tem o seu parecer aprovado em `docs/security/`; aqui vale a combinação.

Gatilhos: hook de controle (conformidade, agentes), workflow de CI (nome do check exigido), catraca (rc de espera), autoria de parecer (ADR 0019), regra afrouxada no título (#948).

## Conferência da combinação
- **#948 x #938 (o nome do check exigido e o status gravado por token).** Na espera, o check run `catraca` ou `bateria` deixa de existir no head (`.github/workflows/catraca.yml:70`, `.github/workflows/ci.yml:681`); o nome exigido passa a depender só da fonte fixada no ruleset. Lido pela API (`rules/branches/<b>`): develop e main exigem `bateria` e `catraca` com `integration_id` 15368 (ruleset 26701749); a homolog só tem o ruleset 25432260, com `bateria` e `catraca` sem fonte fixada. O caminho de um agente gravar `statuses/<sha>` com contexto `catraca` pelo terminal é fechado pelo #938 (`hooks/conformidade.py:173`, trava também na sessão do Forge; teste `tests/test_conformidade_pareceres.py:156`, classe `PeloTerminalNoForge`). A main segue fixada, e a catraca do PR homolog -> main recalcula o afrouxamento contra a main: sem caminho realista até a main. Fica como cartão C1 (abaixo), não como achado da leva.
- **#945 x os demais.** `vigentes` (`bin/forge_pareceres.py:265`) não tem chamador fora dos testes (o C2b liga); lê `statuses`, não check runs, e só contextos `parecer-*` (`CONTEXTOS`, `:12`), disjuntos de `bateria` e `catraca`. Sem interação com a espera.
- **#950 x #938.** `GitEmLote` só troca a forma das perguntas do aviso de brief vencido (só avisa, nunca libera); ref só sha40, sem faixa nem quebra de linha; ambiente sem `GIT_*`, como o `git` do forge-check (`bin/forge-check:606`).
- **#946.** Roda à mão, na cópia do próprio autor, geradores de lista fechada com `python3 -I`; nenhum hook, pre-push ou workflow o chama.
- **#951.** Recusa antes de gravar; contador e release concordam no corte.
- Workflows: permissões no topo `contents: read`; o novo job agregador da catraca herda isso; `checks: read` só nos jobs que leem o check run; título do PR só por `env:` (`PR_TITULO`).

## GIT-CONTROLE-CONFIG-DA-COPIA
A leva não o piora. A única chamada git de controle nova que roda hoje é a do `GitEmLote` (`hooks/agentes.py:1108`, `cat-file --batch-check`, e `rev-list` pelo `fc.git`), na mesma raiz e no lugar do `merge-base`/`rev-parse` de antes: só leitura de objetos, sem atualização de ref (não dispara `reference-transaction`) nem índice (sem `core.fsmonitor`). O `ancestral` novo (`bin/forge_pareceres.py:245`, `merge-base` sem limpar `GIT_*`) não roda até o C2b: cartão C2, para entrar no corte GC1.

## Plano (cartões, fora do delta, G1.2)
- C1 (dono, configuração; baixa; P): no ruleset 25432260 (`portoes`, homolog e main), fixar a fonte GitHub Actions (15368) em `bateria` e `catraca`, como o passo 9 de `docs/protecao-de-branch.md` já pede, ou incluir a homolog no ruleset 26701749. Nenhum agente altera ruleset (`R-CONFORMIDADE`).
- C2 (tech-lead, com o GC1 da v048; baixa; P): `bin/forge_pareceres.py:245` passar pelo git de controle neutralizado (sem `GIT_*`, sem hooks, config e fsmonitor da cópia) antes de o C2b ligar o `vigentes`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: CI do head 74d2a59c todo verde (`gh pr checks 953`, rc=0: as 5 partes, instalação, verificações longas, passos, pareceres, teto de pulados, catraca e `catraca (conferência)`). Local: `tests.test_conformidade_pareceres` e `tests.test_hooks_agentes_autor`, 40 testes OK. Ferramentas: leitura do diff da leva, API de leitura dos rulesets e dos checks, varredura por padrão de segredo no diff (vazia). Ausentes na estação, sem instalar (lacuna, `R-CUSTO`): gitleaks, actionlint, zizmor, semgrep, osv-scanner.
