---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: 1df3df9ae7715dcf602b6cf7bff8159ecdbc0bf0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E145.6, PR #833, BP14: tabela pedido × não entregue na retro), revalidação

Base `0ed441e9`, head revisado `1df3df9a` (volta E145.5). Revalidação por delta: `forge-check parecer delta docs/reviews/v0480-bp14-retro.md` deu o intervalo `dbc33e5a..1df3df9a` com 3 arquivos no domínio: `docs/retrospectivas/_modelo.md`, `skills/kanban-metricas/SKILL.md` e `templates/projeto/docs/retrospectivas/_modelo.md`. Li só esse delta.

## Achados
- A1 (recomendado) skills/kanban-metricas/SKILL.md:32 · o corte para caber no teto tirou a definição de pedido parado ("sem movimento no quadro"), que não está em nenhum dos dois modelos; recolocar no comentário da seção 1 dos dois `_modelo.md`.

## Sondas
- S1 · modelo do head com `Cobre: v1.0.0`, seções 2 a 4 com uma linha e a seção 1 intacta, em `versoes_que_a_retro_cobre` · espera: secao sem corpo: dados do pedido; nao cobre · obtido: (set(), ['"2026-01-01-x.md": secao sem corpo: dados do pedido; nao cobre'])

## Parecer
Aprovado. Achados da rodada anterior:
- A1 (modelos diferentes): resolvido; os dois `_modelo.md` são iguais byte a byte (`cmp`) e `test_retro_pendentes` passa (20 de 20).
- A2 (tabela de exemplo como corpo da seção 1): resolvido; a tabela saiu e a instrução foi para o comentário HTML; a sonda S1 volta a dar o aviso de seção sem corpo.
- A3 (linha `nenhum`): resolvido no comentário da seção 1.
- A1 do QA (teto de caracteres da skill): resolvido; `test_metricas_texto` passa (2 de 2).

Linha removida da `kanban-metricas` ("Trechos movidos inteiros da skill `kanban-scrum` e do `agile-coach` (diretriz 25, …)"): é nota de procedência, sem regra, sem ID e sem invariante; nenhum teste nem `tests/config.json` a cita, e a diretriz 25 segue na skill `fluxo-do-pedido`. A regra da tabela continua na skill (item 1 da retrospectiva), com a idade, a marca e o `nenhum`.

Testes dos arquivos tocados no head: `test_retro_pendentes` (20), `test_metricas_texto` (2), `test_orcamento_instrucao` (8), `test_modelos_projeto` (25), `test_modelos_citados` (3), `test_jarvis_nucleo` (43), `test_medidas_m14b` (73), `test_forge -k Neutral` (6): todos OK. Suíte inteira: CI do PR #833, pendente na hora do parecer; `bateria (pareceres)` vermelha pelos pareceres reprovados no head anterior, que esta revalidação e as do QA e da segurança atualizam.
