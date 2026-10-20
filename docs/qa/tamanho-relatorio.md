---
tipo: qa
contrato: 1
pedido: tamanho-relatorio
branch: melhoria/tamanho-relatorio
commit: afab806680a138bd4e9ee00cb60102d74fb7c125
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA - um só limite de tamanho do relatório do agente

Links: pedido `tamanho-relatorio` (E1), `docs/reviews/tamanho-relatorio.md`. Sem UX nem API; a obrigação é a do pedido E1. Mudança só de texto (regra 7 de `docs/economia-de-tokens.md` e o fragmento de changelog). Código testado: afab806 (HEAD f190449 só acrescenta o parecer de review).

## Resultados
| ID | Cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Regra 7 cita o item 6 "Relatório" do prompt-padrão (`agents/jarvis.md`) como fonte única e não diz mais "≤ 5 linhas" | limite antigo removido | Passou: texto da regra 7 conferido no diff; item 6 existe em `agents/jarvis.md:62` |
| CT-02 | Jarvis continua "só o que decide ou depende do usuário" | texto preservado | Passou |
| CT-03 | Nenhum outro limite de linhas do relatório de agente em docs/, agents/ ou bin/ que contradiga o item 6 | fonte única | Passou: grep de "N linhas" não acha "5 linhas" para agente; restam "até 8 linhas" iguais ao item 6 (`bin/forge-check:2754`, texto do brief, e a retomada do Jarvis em `docs/retomada-de-sessao.md`) e formatos próprios do conferente (10 e 13 linhas), que não são o relatório do prompt-padrão |
| CT-04 | Fragmento `changelog.d/tamanho-relatorio.md` presente e válido | n/a | Passou (testes de changelog na suíte) |
| CT-05 | `python3 -m unittest discover -s tests -q` | n/a | Passou: 865 testes, OK (203 s) |
| CT-06 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (rede para api.anthropic.com negada pelo sandbox; não afeta o resultado) |

Teste novo de regra: nenhum (mudança de texto sem teste novo); vermelho antes do verde e mutação não se aplicam.

## Achados
