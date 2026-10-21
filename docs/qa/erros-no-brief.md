---
tipo: qa
contrato: 1
pedido: erros-no-brief
branch: melhoria/erros-no-brief
commit: 8f03c9c43e84752cf596ce36142eb9fb09e83727
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - erros recorrentes no brief (ERROS-NO-BRIEF, E1 a E5)

Links: `docs/reviews/erros-no-brief.md`, `docs/security/erros-no-brief.md`, pedido `erros-no-brief`. Sem UX nem API; as obrigações são OK-7, OK-8 (B) e PA-7 do pedido. Offline, sondas em `$TMPDIR` (raiz própria, `KANBAN.md` e `conferencias.md` falsos). O HEAD `028947a` só acrescenta o parecer de review sobre `8f03c9c`.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Suíte completa `python3 -m unittest discover -s tests -q` | n/a | Passou: 1234 testes, OK |
| CT-02 | `scripts/validar-plugin.sh` | n/a | Passou: "Validation passed", rc 0 |
| CT-03 | `tests.test_erros_no_brief` e `tests.test_conferencia_registrar` | n/a | Passou: 47 testes OK |
| CT-04 | Vermelho antes do verde: os dois módulos contra o `bin/forge-check` de `10c838f` (cópia em `$TMPDIR`) | n/a | Falharam sem a implementação: 42 falhas e 16 erros em 47 testes |
| CT-05 | `conferencia registrar` reprovado sem `--classe` | classe vazia | Passou: rc 1, lista as 10 classes, nada gravado (`docs/kanban/` não criado) |
| CT-06 | `registrar` com classe fora do catálogo, `--autor` inválido, classe em resultado aprovado | classe/autor fora do vocabulário | Passou: rc 1 nos três, sem gravar |
| CT-07 | `registrar` reprovado com `--classe forma --autor jarvis` | classe do catálogo | Passou: rc 0, linha de 10 colunas |
| CT-08 | `conferencia classes`: linha antiga de 8 colunas, linha de 40 dias, classe `outra`, 3 briefs de `forma/jarvis`, 2 de `prova/destino` | janela de 30 dias; limiar 3 | Passou: antiga, fora da janela e `outra` não contam; proposta só para `forma` (3 briefs); `prova` com 2 sem proposta; rc 0 |
| CT-09 | `brief gerar` com 4 classes do destino (prova 4, citacao 2, escopo 2, etapa 2) e nota com marcador | no máximo 3 linhas; só texto do catálogo | Passou: 3 linhas por contagem, texto só do catálogo, a nota não aparece no brief; linha do Jarvis (`forma`) não entra como erro do destino |
| CT-10 | `brief mensagem` e `forge-check brief <arquivo>` com e sem registros de `forma` do Jarvis (2 briefs) | stdout idêntico | Passou: stdout igual byte a byte (`cmp`), `jarvis-recorrente:` só em stderr, nunca em stdout, rc 0 |
| CT-11 | `brief gerar --etapa codigo` com `docs/engineering/achados-recorrentes.md` | só etapa de código | Passou: o arquivo entra em `## Ler` na etapa `codigo` e não entra na `qa` |

## Achados

## Recomendações (não bloqueiam)
- R1 (review) `agents/jarvis.md:64`: o comando de registro do Jarvis não traz `--classe`; até o PR da E6 toda reprovação registrada por ele recebe rc 1 (a recusa lista as classes). Primeiro item da E6.
- R3 (review) `bin/forge-check:3930`: `conferencia classes --dias 0` é aceito e imprime "janela de 0 dias" sem contagem (confirmado na sonda). Recusar `< 1`.
- R4 (review, volta 1) fica para o PR da E6.
- Observado, sem bug: `conferencia classes` numa raiz sem `KANBAN.md` dá rc 0 ("nenhuma falha classificada"), enquanto a doc em `docs/transcricoes.md` põe a recusa sob essa seção (é o R4).

## Resultado da execução
Ambiente: worktree `erros-no-brief`, Python 3.10, sem rede. Mutação: a stack do Forge não tem ferramenta gratuita; os módulos novos foram vistos vermelhos (CT-04). Nenhum bug aberto.
