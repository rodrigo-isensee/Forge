---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 16b7ca7443c01eb8a8e532d82ac0ea69948e4722
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (E1.169, folga do texto do Jarvis P1 a P4 e FOCO-NAS-DECISOES)

Código testado: ebeb9161 (o remoto c4351c3e só soma pareceres de review e segurança). Diff sobre a base e60183d0: texto do Jarvis e das skills (trechos movidos, diretriz 25), `tests/apoio_jarvis.py` (conjunto calculado, presença), fixtures e testes. Escopo mudado fora do previsto, relatado pelo autor (`agents/agile-coach.md`, `falar-com-o-dono`, testes de texto): lido no diff, coerente com a citação da skill `kanban-metricas`.

## Achados

- A1 (bloqueante) tests/apoio_jarvis.py:82 · a checagem de presença das regras com ID passa sempre na árvore real: o índice docs/regras/README.md entra no conjunto (pela R-WIP) e cita todo ID. Reproduzido por sonda de mutação: tirar `R-MAIN` do Jarvis e das skills dá []. Corrigir fora de docs/regras/
- A2 (recomendado) tests/test_jarvis_nucleo.py:334 · o mutante test_id_fora_do_conjunto_reprova não pega A1: a árvore sintética não põe o índice no conjunto. Somar caso em que o Jarvis cita só a regra de índice e outra regra some do texto; precisa reprovar

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão do dono 13/11: toda regra com ID segue presente no Jarvis ou nas skills citadas | `test_cada_regra_com_id_aparece_e_tem_texto` | ID ausente do texto | NÃO prova: passa com o ID removido (A1) |
| Diretriz 25: trecho movido não some, só muda de arquivo | `test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece`, `test_apagar_o_trecho_reprova_e_diz_onde_procurar` | trecho de 20+ caracteres; trecho apagado | passou |
| Skill citada traz ordem de leitura ("leia"/"antes de") | `test_cada_skill_citada_pelo_jarvis_traz_a_ordem_de_leitura`, `test_citar_sem_leia_nem_antes_de_reprova` | citação sem ordem | passou |
| Conjunto calculado (não lista fixa), com mínimo | `test_o_conjunto_e_calculado_e_traz_as_skills_novas` | mínimo 20 itens (hoje acima) | passou |
| Numeração das diretrizes sem buraco, trecho curto, pendente com cartão e teto | `test_buraco_na_numeracao_reprova`, `test_trecho_curto_reprova`, `test_pendente_*` | vazio, 20 caracteres, máximo de pendentes | passou |
| FOCO-NAS-DECISOES (diretriz 29): resumo no Jarvis, detalhe na skill | `test_o_jarvis_traz_o_resumo_e_manda_ler_a_skill_antes_de_responder`, `test_a_skill_traz_o_detalhe_inteiro` | detalhe só na skill | passou |
| Texto só desce (teto) | `test_metricas_texto`, `test_pesos_teto` | teto por arquivo | passou |

## Cenários e resultado real
- Execução local dos módulos do domínio (`test_jarvis_nucleo`, `test_metricas_texto`, `test_medidas_m14b`, `test_reval_delta`): `Ran 113 tests ... OK (skipped=1)`. O `skipped` é pré-existente, não foi posto por este pedido. A suíte inteira fica no CI do PR; não há PR aberto neste head, então não cito check-run `bateria`.
- Vermelho antes do verde: `forge-testes --vermelho e60183d0a41d28f44ac272197cac744b4891e61e` saiu rc 0: `vermelho: base=e60183d0a41d head=c4351c3efbbc`, com `revertidos à base` os 11 arquivos de texto e `tests/apoio_jarvis.py`, e `mantidos no HEAD` os 8 testes e fixtures. Veredito por teste: ao menos um prova e nenhum cai no HEAD. Aviso da ferramenta: "o mapa não sabe (tests/apoio_jarvis.py sem mapa); suíte completa".
- Sonda de mutação no teste de presença (sobre o código do autor, em `$TMPDIR`): (1) árvore real, `problemas_das_regras` devolve [] (esperado); (2) removi `R-MAIN` de todo texto exceto o índice: devolve [] (esperado: um problema), o mutante sobrevive; (3) árvore sintética com o Jarvis citando só `R-DOIS` (texto só no índice) e `R-UM` fora do Jarvis: devolve [] (esperado: "R-UM: não aparece"). Confirma o achado da segurança com sonda própria.
- Sem rede de proteção alternativa provada por mim: o review nota que o invariante de `tests/config.json` ainda cobre o bloco do Jarvis; não reavaliei isso, e a decisão de 13/11 pede o teste novo como prova.
- Nota para o portão (domínio da segurança, A2 dela): as diretrizes 26 a 28 entram como pendentes (`MAX_PENDENTES = 7`) além das 2, 11, 23 e 24 da decisão; não bloqueio por isso, vai ao dono pelo Jarvis (`R-DECISAO`).
- Bug médio: A1 (controle de guarda vazio). Cartão no quadro pelo tech-lead; correção mínima: procurar o ID só em `agents/jarvis.md` e `skills/*/SKILL.md`. Dono da correção: tech-lead (autor da E1.137).

## Revalidação por delta (E1.184): ebeb9161..8a223677, volta de A1 e A2

`forge-check parecer delta` listou no meu domínio `tests/apoio_jarvis.py`, `tests/mutantes/v047-folga-jarvis.json` e `tests/test_jarvis_nucleo.py`. O remoto avançou só com pareceres (75b459ee), trazido por merge; o código segue em 8a223677.

- A1 resolvido: `problemas_das_regras` filtra o conjunto por `TEXTO_DO_JARVIS` (`agents/jarvis.md` e `skills/*/SKILL.md`), sem o índice. Sonda em cópia do head, árvore real: [] (esperado); `R-MAIN` trocado em Jarvis e skills: `['R-MAIN: não aparece no Jarvis nem nas skills citadas']` (antes: []).
- A2 resolvido: `test_id_que_some_do_jarvis_reprova_com_o_indice_no_conjunto` põe o índice no conjunto e exige a reprovação de `R-UM`, depois a aprovação com `R-UM` numa skill.
- Vermelho antes do verde (manual, em cópia: `apoio_jarvis.py` do ebeb9161 com o teste novo): `FAILED (failures=1)`, `- [] + ['R-UM: não aparece no Jarvis nem nas skills citadas']`. Com o head: `Ran 40 tests ... OK (skipped=1)` em `tests.test_jarvis_nucleo`; o skip é o pré-existente da linha 246 (arquivo do dono fora do git). `forge-testes --vermelho` não terminou no prazo nesta sessão (sem veredito, não conta como prova).
- Mutantes (`forge-mutante tests/mutantes/v047-folga-jarvis.json`, rc 0): `M1 · morreu · tests/apoio_jarvis.py:84`, `M2 · morreu · tests/apoio_jarvis.py:20`, `M3 · morreu · tests/apoio_jarvis.py:84`. Os 3 mutantes cobrem as 2 linhas de guarda mudadas (a regex e o filtro); sem sobrevivente.
- A suíte inteira fica no CI do PR; sem PR aberto neste head, não cito check-run `bateria`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão do dono 13/11: regra com ID presente no Jarvis ou nas skills | `test_cada_regra_com_id_aparece_e_tem_texto`, `test_id_que_some_do_jarvis_reprova_com_o_indice_no_conjunto` | ID só no índice | passou, agora prova |

## Revalidação por delta (E1.193): 8a223677..16b7ca74, merge da develop

`forge-check parecer delta` listou no meu domínio `templates/projeto/CLAUDE.md`, `tests/test_forge.py` e `tests/test_reval_delta.py`, sem o que veio da base. O conflito em `tests/test_reval_delta.py` foi resolvido mantendo as duas entradas de `CITACOES_CONHECIDAS` (a do `apoio_jarvis.py` e a de `test_ambiente_sem_auto_update.py`), conferido no diff; o código de guarda do pedido (`tests/apoio_jarvis.py`) não mudou, então os mutantes de 8a223677 seguem valendo.

- Execução local: `tests.test_reval_delta` e `tests.test_ambiente_sem_auto_update`: `Ran 11 tests ... OK`; `tests.test_forge.PreEnvioDoModelo` e `HookPrePush`: `Ran 27 tests ... OK`. O `push` do `HookPrePush` agora isola HOME e XDG_RUNTIME_DIR numa casa de teste, o que evita a trava real; coerente com o pre-push.local.
- A linha `Ambiente:` do modelo de projeto traz o aviso da atualização automática e a lê o teste `test_ambiente_sem_auto_update`, que passou.
- Sem teste novo de regra neste delta, então não há vermelho antes do verde a repetir. A suíte inteira fica no CI do PR; sem PR aberto neste head, não cito check-run `bateria`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aviso de atualização automática no modelo de projeto | `tests.test_ambiente_sem_auto_update` | n/a | passou |
| Citações conhecidas após o merge | `tests.test_reval_delta` | entrada duplicada ou perdida | passou |
| Pre-push isolado da casa real | `HookPrePush`, `PreEnvioDoModelo` | trava na casa do teste | passou |

Parecer: aprovado, sem achados novos.
