---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: be5bb7ee32898578994ab389c8b257cf54ba7034
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 textos do Jarvis (E21.4, classe C)

Mudança só de texto (4 arquivos, 18 linhas a mais, 16 a menos). Não há teste novo nem regra de código, então não há vermelho antes do verde nem mutante a conferir (`R-QA`: n/a). Não há PR aberto: não existe check-run `bateria`; rodei os testes afetados, um por vez (`R-TETO`).

## Achados
- A1 (recomendado) tests/test_jarvis_nucleo.py:1 · nenhum teste fixa as frases novas das diretrizes 18 e 19 (`run_in_background`, `until`, "me chame", "uma instância por item"); a medida "zero me chame" não tem guarda e o texto pode sumir sem queda.
- A2 (recomendado) skills/trabalho-em-paralelo/SKILL.md:9 · "Portão sem retorno em 53 min: pare e relance quando o anterior não rodar mais" perdeu o "depois de conferir"; a ordem (conferir, depois relançar) ficou ambígua.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 18 em R-WIP (uma instância por item, até o teto, volta à mesma instância, CI do PR, um por vez em arquivo comum/merge/`KANBAN.md`/pipeline/módulo-ADR-ameaças-tela) | leitura do diff `docs/regras/README.md:29` e da skill (linha 10) contra o cartão DIRETRIZ-18-PARALELO; `test_forge.RegrasComId`, `AntiDuplicacao` | uma só linha `**R-WIP**` no índice; teto de `R-TETO` mantido | passou |
| Diretriz 19 em jarvis.md e na skill (espera em segundo plano, `until` com prazo, encher vagas, ao dono só decisão/rótulo/merge na main/comando travado, medida zero) | leitura do diff `agents/jarvis.md:47` e skill linha 19 contra o cartão DIRETRIZ-19 | n/a | passou (cobre todos os itens do cartão) |
| Orçamento do jarvis.md e do núcleo | `test_orcamento_instrucao` (8), `test_metricas_texto` (2) | limite de 7795 caracteres (jarvis.md 7795/7795 por contagem de caracteres; 7958 bytes) | passou |
| Frases exigidas por testes de texto continuam | `test_jarvis_nucleo` 14, `test_jarvis_n_jar_a` 2, `test_aq1_texto` 6, `test_skills_v0442` 4, `test_textos_034` 6, `test_textos_dono_f10` 3, `test_textos_dono_f7` 2, `test_clareza` 9, `test_citacao` 10, `test_modelos_citados` 3, `test_permissao_agentes_md` 1 | IDs de regra citados (`R-TETO`, `R-WIP`, `R-FLUXO`, `R-REVIEW`) | passou |
| Frases cortadas do jarvis.md não eram exigidas | idem; nenhum teste citou "honesto", "como Jarvis", "sozinhas", parêntese dos lotes | n/a | passou |

## Cenários e resultado real
- Head conferido: `be5bb7ee32898578994ab389c8b257cf54ba7034` (igual ao Revisar-sha e à origin).
- `bin/forge-testes --listar` apontou 28 módulos; rodei os de texto acima, em série, na worktree destacada. Todos OK.
- `tests.test_forge` inteiro estourou meu prazo de 550 s (Terminated, sem veredito, não conta como verde); rodei o que toca a mudança (`AntiDuplicacao`, `RegrasComId`: OK, 5 testes). A suíte inteira fica para o CI do PR.
- Nenhum bug aberto.

## Resultado da execução
Aprovado no head `be5bb7ee`; achados só recomendados (viram cartão, sem devolver).
