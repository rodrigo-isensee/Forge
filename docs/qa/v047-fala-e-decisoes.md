---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-fala-e-decisoes
commit: 1c330fe64c8687225e4847f84cf17b030c2a4353
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 · fala só no marco e foco nas decisões (E1.282)

Intervalo `origin/develop..05797223` (base c5c3a449): `agents/jarvis.md`, `skills/falar-com-o-dono/SKILL.md`, `skills/modo-iniciante/SKILL.md`, `tests/config.json`, fragmento de changelog. Só texto e invariantes; nenhum código executável mudou, então não há mutante de `forge-mutante` nem pedido de controle. Os critérios vêm das diretrizes 24 e 29 (`docs/diretrizes-do-dono.md`) e do item E1.282 do pedido.

## Achados
- A2 (bloqueante) tests/config.json:696 · RESOLVIDO em 1c330fe6: `invariantes_sem_motivo` de `agents/jarvis.md` segue 48, mas o invariante "diga sempre ao usuário…" voltou: 58 padrões - 9 com motivo = 49; `tests.test_forge -k nvariante` falha. Subir para 49.
- A1 (recomendado) skills/falar-com-o-dono/SKILL.md:18 · a Resposta curta perdeu o apontamento a `decisoes --resposta` e aos campos de corte; a ferramenta ainda os exige (64 testes verdes), mas quem lê só a skill deixa de saber deles (R-DECISAO).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 (dir. 24) fala só em decisão/ação, problema que muda prazo ou risco, marco fechado | invariantes `**Falar só no marco:**` e `quando algo dá errado e muda prazo ou risco` em `agents/jarvis.md` | texto sumir | passou |
| CA-2 (dir. 24) resumo no máximo a cada 30 min, uma linha por item, nada mudou nada a dizer | invariante `no máximo um resumo a cada 30 min`; leitura do texto | limite de 30 min | passou |
| CA-3 (dir. 24) recibo e perguntas sempre completos | invariante `recibo e perguntas, sempre completos` | corte do andamento encolher recibo | passou |
| CA-4 (dir. 24) modo foco do VSCode orientado | invariantes `Fale só no marco` e `modo foco da extensão do VSCode \(Focus view` em `modo-iniciante` | texto sumir | passou |
| CA-5 (dir. 29) pedido das decisões: foco total, ler só perguntas abertas, lista por peso, primeira pergunta completa | invariantes `**Pedido das decisões**`, `foco total`, `só ler as perguntas abertas`, `a primeira\s+pergunta completa` | quebra de linha no meio da frase (`\s+`) | passou |
| CA-6 (dir. 29) cada resposta gravada por `forge-check anotar`; time segue; sem aviso entre perguntas | invariantes `forge-check anotar`, `O time segue no que não depende delas`, `entre as perguntas, nenhum aviso` | correção de 14/11 08:18 (time não para) | passou |
| CA-7 (dir. 29) sem pendência: linha única | invariante `Não há decisão sua pendente\.` | vazio (zero pendências) | passou |
| CA-8 Jarvis aponta a skill no pedido das decisões | invariante `ou ao pedido das decisões` | apontamento sumir | passou |
| CA-9 15 invariantes novos válidos, com motivo e regra | script próprio (abaixo) | padrão que não casa ou casa duas vezes | passou |
| CA-10 nada que já era protegido foi perdido | `tests.test_jarvis_nucleo`, `tests.test_modelos_projeto`, `tests.test_forge -k nvariante -k Neutral -k Regra` | invariantes antigos | passou |

## Cenários e resultado real
- **CT-01 invariantes novos (CA-9):** script próprio leu `tests/config.json` do head contra o de `origin/develop`: 15 invariantes novos (jarvis 5, falar-com-o-dono 8, modo-iniciante 2); os 15 casam no arquivo (0 sem casar) e nenhum casa uma segunda vez depois de retirado o trecho casado (cada um guarda um trecho único). As 7 entradas de `invariantes_motivo_trecho` (jarvis 5, modo-iniciante 2) trazem `regra: R-DECISAO` e o porquê.
- **CT-02 testes de texto e dono (local):** `python3 -m unittest tests.test_textos_dono_f10` (3 OK), `tests.test_textos_dono_f7` (2 OK), `tests.test_textos_034` (6 OK), `tests.test_forge_dono` (64 OK, 115 s), `tests.test_jarvis_nucleo` (20 OK), `tests.test_modelos_projeto` (17 OK), `tests.test_forge -k nvariante -k Neutral -k Regra` (15 OK). `tests.test_catraca` estourou o prazo local de 280 s (sem veredito, não conta como verde); fica para o CI do PR.
- **CT-03 coerência com a diretriz 29 corrigida:** a primeira redação parava o time; o texto do head diz que o time segue no que não depende das decisões e que o aviso fica para o resumo do fim. Confere com a correção de 14/11 08:18.
- **CT-04 conteúdo retirado:** saíram da skill a linha "Custo e origem" e os detalhes do formato curto (`decisoes --resposta`, campos `origem:`/`procurado:`/`seguir:`/`não seguir:`). A ferramenta segue impondo os campos (`tests/test_forge_dono.py:325,488`, 64 testes verdes), então o comportamento não regrediu; só o texto da skill ficou mais enxuto. Registrado como recomendação.
- **CT-05 conflito já conhecido:** o invariante "diga sempre ao usuário para qual agente passou" (`agents/jarvis.md:34`) segue no texto e contradiz em parte a diretriz 24; o autor registrou a pergunta ao dono (pedido, 14/11 23:14), sem bloqueio. Não é defeito desta entrega.
- **Não executado:** a suíte inteira (roda no CI do PR; a branch ainda não tem PR, então não há check-run `bateria` para citar); vermelho-antes-do-verde e mutação não se aplicam (sem código nem teste novo, só invariantes de texto).

## Revalidação (delta 05797223..a4a47661, `escopo: completo` mantido)
`forge-check parecer delta` listou 8 arquivos de domínio: 3 arquivos novos (`skills/falar-com-o-dono/resposta-curta.md`, `skills/modo-iniciante/numeros.md`, `skills/kanban-scrum/experimentos.md`), 3 `SKILL.md` com ponteiro, `tests/config.json` e o fragmento de changelog. Só texto e invariantes; sem código, sem mutante.
- **A1 resolvido:** `resposta-curta.md` traz inteiro o texto antigo mais `decisoes --resposta` e `origem:`, `procurado:`, `seguir:`, `não seguir:`; a skill aponta por `${CLAUDE_PLUGIN_ROOT}`.
- **Diretriz 25 (nada apagado nem resumido):** o diff dos 3 `SKILL.md` só troca o trecho movido por ponteiro; o texto movido existe nos arquivos novos (numeros.md: 3 itens medido/estimado/não medido idênticos; experimentos.md: tabela e regra idênticas). A única reescrita de conteúdo é a linha C do exemplo ("custo, não dá para dizer se é maior ou menor"), que é o A4 do review. O técnico do `tech-lead` e o `agile-coach` entraram na `kanban-scrum`.
- **Invariantes:** 44 padrões de `invariantes` dos 6 arquivos tocados casam (0 sem casar); `tests.test_forge -k nvariante -k Neutral -k Regra`: 15 OK. Os 3 arquivos novos têm invariante e motivo `R-DECISAO`.
- `forge-check docs`: rc=0. A suíte inteira roda no CI do PR (sem PR ainda, sem check-run `bateria`). Vermelho e mutação não se aplicam (texto).

## Revalidação 2 (delta a4a47661..fd0a0172, decisão 2 do dono de 15/11, `escopo: completo` mantido)
`forge-check parecer delta` listou 4 arquivos de domínio: `agents/jarvis.md`, `changelog.d/v047-fala-e-decisoes.md`, `tests/config.json`, `tests/test_jarvis_nucleo.py`. Só texto, invariante e lista de retirados; sem código executável, sem mutante, vermelho-antes-do-verde não se aplica.
- **CT-05 resolvido:** o trecho "diga sempre ao usuário para qual agente passou" saiu de `agents/jarvis.md` (0 ocorrências) e entrou "diga qual agente faz o quê só nos marcos, num resumo" (1 ocorrência no texto, 1 em `invariantes`), com entrada em `invariantes_motivo_trecho` (`R-DECISAO` e porquê). Contagem de `agents/jarvis.md` no teto 49 para 48, coerente com a troca.
- **Afrouxamento declarado:** `RETIRADOS_047` em `tests/test_jarvis_nucleo.py` lista só o trecho trocado (decisão do dono, referenciada no comentário e no fragmento de changelog); os demais invariantes seguem exigidos.
- **Testes locais:** `tests.test_jarvis_nucleo` 20 OK; `tests.test_invariante_gatilho` + `tests.test_modelos_projeto` + `tests.test_textos_dono_f10` 21 OK; `tests.test_forge -k nvariante -k Neutral -k Regra` 15 OK. A suíte inteira roda no CI do PR (sem PR, sem check-run `bateria`).
- Sem bug novo; achados abertos: nenhum.

## Revalidação 3 (delta fd0a0172..14a29d8f, invariante do Jarvis de volta com o momento, E2.315)
`forge-check parecer delta` listou 4 arquivos: `agents/jarvis.md`, `changelog.d/v047-fala-e-decisoes.md`, `tests/config.json`, `tests/test_jarvis_nucleo.py`. Só texto, invariante e lista de retirados; sem mutante, vermelho não se aplica.
- O invariante "diga sempre ao usuário para qual agente passou, no recibo e no aviso de marco, nunca em mensagem extra" está em `agents/jarvis.md:34` (1 ocorrência); `RETIRADOS_047` saiu e `tests.test_jarvis_nucleo` passa (20 OK); `tests.test_orcamento_instrucao` + `test_invariante_gatilho` 9 OK; `tests.test_modelos_projeto` + `test_textos_dono_f10` OK; `forge-check docs` rc=0.
- **Falha provada:** `python3 -m unittest tests.test_forge -k nvariante -k Neutral -k Regra` = 1 falha em `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe`: `agents/jarvis.md: trecho novo em arquivo do legado sem regra e porque`. Causa: `tests/config.json:696` diz 48 e o arquivo tem 58 - 9 = 49 (o trecho antigo voltou ao legado). Bug `docs/qa/bugs/v047-legado-jarvis-contagem.md`; corrige o autor (tech-lead/dev).
- A suíte inteira roda no CI do PR (sem check-run `bateria` no head).

## Bugs
- Nenhum aberto; o alto docs/qa/bugs/v047-legado-jarvis-contagem.md foi corrigido em 1c330fe6.

## Revalidação 4 (delta 14a29d8f..1c330fe6, regra e porque no trecho devolvido, teto do legado em 48, E2.397, `escopo: completo` mantido)
`forge-check parecer delta` listou 1 arquivo de domínio: `tests/config.json` (nova entrada em `invariantes_motivo_trecho` para "diga sempre ao usuário para qual agente passou", `R-DECISAO` e porquê). Sem código, sem mutante; vermelho não se aplica.
- **A2 e o bug do legado resolvidos:** o trecho agora tem regra e porquê, sai do legado e o teto de `agents/jarvis.md` (`tests/config.json:696`) em 48 bate; `python3 -m unittest tests.test_forge -k nvariante -k Neutral -k Regra`: 15 testes, OK (antes 1 falha).
- `tests.test_jarvis_nucleo` + `test_invariante_gatilho` + `test_modelos_projeto` + `test_textos_dono_f10`: 41 OK; `forge-check docs` rc=0. Suíte inteira no CI do PR (sem check-run `bateria` no head).
- Achados abertos: nenhum.
