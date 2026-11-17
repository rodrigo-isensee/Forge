---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 6288db934914dcf2ce14bae404987057dbe7b48c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
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

## Revalidação por delta (E2.293): 16b7ca74..cd79a259, junção da develop

`forge-check parecer delta` listou `templates/projeto/CLAUDE.md`, `tests/test_forge.py` e `tests/test_reval_delta.py`. Os dois primeiros vieram da base (#573, #581: seção Sessão do modelo e gh falso com `--version`), fora do escopo deste pedido; li o diff e não mexem em guarda do pedido. A linha própria da junção: em `CITACOES_CONHECIDAS` entrou `("tests/test_sessao_automatica.py", "README.md"): (1, "teste-le")`, e as três entradas anteriores seguem (conferido no diff). O `tests/apoio_jarvis.py` não mudou, então os mutantes de 8a223677 seguem valendo.

- Execução local: `python3 -m unittest tests.test_reval_delta tests.test_sessao_automatica`: `Ran 23 tests ... OK`. O teste novo da base lê o README (linha 81), o que a entrada declara.
- Sem teste novo de regra neste delta: não há vermelho antes do verde a repetir. A suíte inteira fica no CI do PR; sem PR aberto neste head, não cito check-run `bateria`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Citações conhecidas após a junção | `tests.test_reval_delta` | entrada perdida ou citação desconhecida | passou |

## Revalidação por delta (E2.656): cd79a259..2a95b163, parágrafos movidos para arquivos da skill

`forge-check parecer delta` listou no meu domínio `agents/jarvis.md`, as skills `falar-com-o-dono` (arquivos novos `toda-mensagem.md`, `conferir-develop.md`, `pergunta-pendente.md`), `kanban-metricas`, `kanban-scrum`, `tests/config.json` e os testes `test_jarvis_nucleo`, `test_jarvis_n_jar_a`, `test_medidas_m14b`, `test_forge` (esta parte vem da base). As guardas de `tests/apoio_jarvis.py` não mudaram, então os mutantes M1 a M3 seguem valendo.

- Execução local (TMPDIR, só os arquivos tocados): `python3 -m unittest tests.test_jarvis_nucleo tests.test_jarvis_n_jar_a tests.test_medidas_m14b tests.test_metricas_texto tests.test_reval_delta`: `Ran 130 tests ... OK (skipped=1)`; o skip é o pré-existente (arquivo do dono fora do git).
- Mutantes: `forge-mutante tests/mutantes/v047-folga-jarvis.json`: `M1 · morreu · tests/apoio_jarvis.py:84`, `M2 · morreu · tests/apoio_jarvis.py:20`, `M3 · morreu · tests/apoio_jarvis.py:84`; sem sobrevivente.
- Sonda de mutação nos parágrafos movidos (cópia do head em `$TMPDIR`): troquei "mesmo então o passo seguinte do time anda" em `toda-mensagem.md` e "sem delegar" em `conferir-develop.md`: `test_toda_mensagem_tem_resposta_e_o_passo_seguinte` e `test_a_skill_manda_conferir_a_develop_antes_de_abrir_a_etapa` falham (`failures=2`). Sem a troca, passam: o trecho movido não some sem o teste cair.
- Vermelho antes do verde: sem regra nova (os testes só trocam o arquivo onde o mesmo texto é lido, diretriz 25); a sonda faz o papel do vermelho. A suíte inteira fica no CI do PR; sem PR aberto neste head, não cito check-run `bateria`.
- O remoto avançou (d607de96, só `docs/security/`), trazido por junção.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 25: parágrafo movido não some; SKILL.md aponta para o arquivo novo | `RespostaATodaMensagemDoDono`, `EtapaSoAposConferirDevelop`, `test_jarvis_n_jar_a` (3 regras, ID por arquivo) | ponteiro ausente; trecho apagado | passou, a sonda derruba |
| Texto só desce (teto) | `test_metricas_texto`, `test_medidas_m14b` | teto por arquivo | passou |

Parecer: aprovado, sem achados novos.



## Revalidação por delta (E2.676): 2a95b163..6288db93, exemplo neutro no lugar do pulo

`forge-check parecer delta` listou no meu domínio `tests/fixtures/diretrizes-do-dono-exemplo.md` (novo, 29 diretrizes numeradas) e `tests/test_jarvis_nucleo.py` (o teste do arquivo do dono lê o exemplo quando `FORGE_DIRETRIZES_DONO` não existe, em vez de `skipTest`). Os commits seguintes (bebfcc8a, 0fc802e6, 09dcbd6c) só tocam pareceres de review e segurança.

- Execução local (TMPDIR, só o arquivo tocado): `env -u FORGE_DIRETRIZES_DONO python3 -m unittest tests.test_jarvis_nucleo`: `Ran 43 tests ... OK`, sem skip.
- Sonda de mutação: arquivo do dono com a linha extra `30. extra` apontado por `FORGE_DIRETRIZES_DONO`: `FAILED (failures=1)`. O teste não passa por vazio: número sem entrada na tabela do Jarvis reprova.
- Vermelho antes do verde: a sonda do "30." faz o papel; antes o teste era pulado e não provava nada. Suíte inteira no CI do PR; sem PR neste head, não cito `bateria`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz do dono sem entrada na tabela reprova, também no CI | `test_cada_numero_do_arquivo_do_dono_tem_entrada` | número a mais que a tabela (30); arquivo ausente | passou; a sonda derruba |

Parecer: aprovado, sem achados novos.
