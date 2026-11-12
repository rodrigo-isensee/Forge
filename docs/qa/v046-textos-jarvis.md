---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: afdaa3abf9e27dd195380c1fe01ac631082b4198
parecer: aprovado
escopo: incremental
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

## Revalidação por delta (E21.8, be5bb7ee..afdaa3ab)
`forge-check parecer delta` listou no domínio: `changelog.d/v046-textos-jarvis.md`, `docs/regras/README.md`, `skills/trabalho-em-paralelo/SKILL.md`, `tests/test_jarvis_nucleo.py`. Head conferido: `afdaa3ab` (igual ao Revisar-sha). Sem PR aberto, não há check-run `bateria`; rodei os afetados um por vez (`R-TETO`), numa worktree destacada minha.

- A1 resolvido: a classe `Diretrizes18e19` (3 testes) fixa "anda sozinho", `run_in_background`, o `until` com prazo, a skill `esperar-estado`, "nada novo é disparado", a volta a instância nova com o mesmo brief e as medidas da R-WIP.
- A2 resolvido: a skill linha 9 voltou a dizer "depois de conferir que o anterior não roda mais".
- Sem contradição do "se serializam": o texto agora diz que itens com arquivo em comum vão em lote ou o segundo espera.
- Orçamento: a skill tem 3048 bytes (3006 caracteres, o brief fala 3006/3006); `agents/jarvis.md` sem mudança no delta.

Vermelho à mão (base `be5bb7ee` para `skills/` e `docs/regras/README.md`, testes do head): `Ran 3 tests ... FAILED (failures=2)`: `test_a_espera_em_segundo_plano_traz_o_prazo_no_proprio_comando` e `test_uma_instancia_por_item_com_volta_e_medida` caem na base. `test_o_jarvis_anda_sozinho_e_nunca_pede_para_ser_chamado` passa na base porque guarda frases que já existiam (regressão, não correção nova; aceito, a classe falha).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 18 (instância por item, volta, medidas) | `Diretrizes18e19.test_uma_instancia_por_item_com_volta_e_medida` | volta sem a instância original; medida zero de vaga parada | passou (cai na base) |
| Diretriz 19 (espera com prazo no comando, pausa) | `Diretrizes18e19.test_a_espera_em_segundo_plano_traz_o_prazo_no_proprio_comando` | prazo no próprio comando | passou (cai na base) |
| Jarvis nunca pede "me chame" | `Diretrizes18e19.test_o_jarvis_anda_sozinho_...` | n/a | passou |
| Orçamento e métricas de texto | `test_orcamento_instrucao` (8), `test_metricas_texto` (2) | limite do núcleo | passou |
| Sem duplicação de regra | `test_forge.AntiDuplicacao` (2) | frase da R-WIP reescrita | passou |
| Núcleo do Jarvis | `test_jarvis_nucleo` (17) | n/a | passou |

Resultado: aprovado no head `afdaa3ab`; nenhum bug aberto; sem novos achados.
