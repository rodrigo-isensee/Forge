---
tipo: qa
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 0c90721c86b15d89ea0aec0befa1850b45948698
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: lote-unico-032

Pedido de revisão: lote-unico-032-REV (E3.1). Base `b2580c6441549e1f1cf4d153ca8db3247cae8cf3`, head `0c90721c86b15d89ea0aec0befa1850b45948698`, 51 commits, 76 arquivos, +3377 -173. Fases 0+A, B, D e F (L00 a L18, L31 a L37, L49 a L51). Sem especificação de UX: os critérios são as obrigações `C-nn` e as regras do pedido; sem E2E nem acessibilidade (nada de interface). Máquina: load 2 a 6,6 e MemAvailable acima de 9 GB antes de cada tarefa pesada, uma por vez.

Veredito: reprovado por um achado bloqueante (A1: mutante M6 da L31 sem veredito, o teste dele trava em vez de falhar). Todo o resto é verde ou recomendação.

## Achados
- A1 (bloqueante) tests/mutantes/lote-unico-032-l31.json:59 · mutante sem veredito (R-QA): o M6 aponta um teste que trava com o mutante (prazo estoura, spec rc 2); apontar test_o_sleep_das_esperas_roda_em_segundo_plano_com_wait ou dar prazo ao teste.
- A2 (recomendado) bin/forge-check:695 · condição sem mutante (R-QA, AR-1): L03 a L18 sem spec; o --cobertura lista 115 condições, quase todas em bin/forge-check (L03 :695, L10 :4379, L13 :4022, L15 :4662, L17 :4688, L18 :1938).
- A3 (recomendado) bin/forge-check:2621 · mesma classe: suposicao revertida (L11), reversoes_do_pedido (L49 :2675) e o ramo do pr (L05 :6144) sem mutante; forge-fechar sai "não coberto" (shell).
- A4 (recomendado) tests/test_suite_paralela.py:426 · vermelho sem veredito (rc 2, L32): o teste erra na base em vez de falhar por asserção; o mutante M15 da l32-2 o mata.
- A5 (recomendado) tests/test_comportamento.py:1 · vermelho sem veredito (rc 2, L36): módulo novo, sem registro na base; os 8 mutantes da l36 morreram e substituem a prova.
- A6 (recomendado) tests/test_decisoes.py:1 · 14 testes novos passam na base (guardas negativas); quatro sem mutante: test_decisoes, test_fila_ocupacao, test_etapa_do_brief e test_jarvis_nucleo (ver seção do vermelho).
- A7 (recomendado) tests/test_catraca.py:2697 · o merge com a develop atual (c6244ac) conflita aqui (merge-tree rc=1): resolver antes do PR e rodar de novo a spec vel-p6-gate e o test_catraca (o devops já registrou).
- A8 (recomendado) agents/jarvis.md:1 · o git revert isolado conflita em 13 de 28 itens (arquivos compartilhados); reverter o lote em ordem inversa ou por inteiro, não item a item.

## Observações
Os bloqueantes do review (A1 a A6 de docs/reviews/lote-unico-032.md: L16, L18, L13, L15, L49, L35) não repito aqui; o QA não os reproduziu um a um, e os testes dos itens passam porque não exercem esses casos.

Detalhe dos achados: A1, o teste test_l5_term_durante_a_espera_grava_fim_codigo_143 trava com o mutante, inválido também com --prazo 400 (6m52s). A2, A3 e A6: lista e nomes dos testes na seção de cobertura e na do vermelho.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira verde (R-QA) | scripts/suite-paralela.py, 2478 testes, 4 processos | n/a | passou: `Ran 2478 tests in 479.898s (4 processos)` `OK (skipped=1)` rc=0 |
| Mutantes declarados mortos | forge-mutante nas 9 specs (75 mutantes rodados) | guardas das L02, L31 a L33, L36, L37, L49, VEL-P6-GATE | 74 morreram; 1 sem veredito (A1) |
| Segredos e caminho pessoal no diff | scripts/verificar-contribuicao.sh origin/develop | n/a | passou rc=0 |
| Plugin válido | scripts/validar-plugin.sh | n/a | passou (`Validation passed`) |
| L01 gate do CI (VEL-P6-GATE) | test_catraca.GateDoCi.test_so_parecer_de_seguranca_devops_ou_ux_com_bateria_verde_pula, test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde, vel-p6-gate M1 a M9 | parecer misturado com código não pula; sem bateria verde não pula | passou, vermelho provado |
| L02 reuso do rascunho | test_fechar_rascunho (2 provam), l02 M1 a M4 | dois PRs abertos; head diferente do conferido | passou |
| L03 volta grava Etapa e Cobre | test_volta_por_delta.test_volta_grava_a_etapa_do_brief_anterior (+3 de escopo da base) | commit da base fora do escopo | passou |
| L04 coluna fora do quadro | test_sobreposicao_quadro.test_coluna_fora_do_quadro_recusa_sem_gravar | coluna inexistente | passou |
| L05 pr imprime o veredito | test_forge.test_pr_aprovado_imprime_veredito, test_pr_com_violacao_nao_imprime_veredito | com e sem violação | passou |
| L06 Jarvis manda anotar o Histórico | test_anotar.test_jarvis_manda_anotar_o_historico | n/a | passou |
| L07 conferente usa o --pedido | test_forge.Orcamento.test_conferente_usa_o_pedido_da_mensagem | n/a | passou |
| L08 pr aceita id e slug | test_etapa_do_brief.test_id_sem_brief_vira_o_slug_da_branch_com_parecer_dela (+3 da base de release) | id sem brief | passou |
| L09 brief lê só o trecho | test_forge.LerDirigidoDoBrief (2) | merge-integração e código | passou |
| L10 PQ fraco | test_forge.ConferirBrief (grep -c sem arquivo, sha abreviado, com arquivo não avisa) | com e sem arquivo | passou |
| L11 suposição sem muda com | test_forge.test_suposicao_sem_muda_com_e_custo_de_reverter_avisa; test_voltas.test_reversoes_de_suposicao_por_pedido | n/a | passou |
| L12 afirmação absoluta sem saída | test_forge.MedirAlucinacao.test_afirmacao_absoluta_sem_saida_de_teste_conta_sem_lastro | n/a | passou |
| L13 veredito contradiz as linhas | test_forge.MedirAlucinacao.test_veredito_que_contradiz_as_proprias_linhas_conta | n/a | passou (review A3: caso das linhas do conferente não coberto) |
| L14 recusas por papel | test_forge.MedirAlucinacao.test_recusas_por_papel_contam_so_numeros | n/a | passou |
| L15 decisoes | test_decisoes (3 provam) | linha torta, controle escapado, pedido inexistente | passou (review A4: sem --pedido) |
| L16 custo do trecho | test_sobreposicao_quadro (3 provam: grava, soma no Pronto, lacuna nunca zero) | sem transcrição | passou (review A1: formato real do usage) |
| L17 proximo | test_proximo (6 provam) | texto hostil, teto de linhas, sem registro, parecer reprovado | passou |
| L18 fila com a ocupação da trava | test_fila_ocupacao (3 provam) | trava link, livre, ocupada | passou (review A2) |
| L31 prazo do vigia mede só o hook | test_hooks_volta_propriedades.test_a_subida_lenta_do_interpretador_nao_conta_na_parede_do_hook; l31 M1 a M5 | subida lenta do interpretador | passou; M6 sem veredito (A1) |
| L32 suíte vermelha registra | test_suite_paralela (4 provam), l32 e l32-2 M1 a M16 | processo morto, link, id com controle (A4), memória ilegível | passou |
| L33 forge-mutante em k processos | test_forge_mutante (6 provam), l33 M1 a M11 | k fora da faixa, SIGTERM em 20 s, processo que cai | passou |
| L34 todo caminho citado existe | test_forge.Referencias (3 provam) | link para fora do repositório | passou |
| L35 invariante traz regra e porque | test_forge.RegrasInviolaveis (2 provam) | invariante novo sem regra | passou (review A6: motivo por arquivo, não por trecho) |
| L36 casos de comportamento | test_testes_tocados.Mapa e MapaDoForgeCheck (4 provam), l36 M1 a M8 | caso que o detector não acusa | passou (A5) |
| L37 merge da base limpo | test_fechar_base_andou (9 provam), l37 M1 a M9 | conflito, fora de melhoria/*, worktree suja, envio recusado, base que anda de novo | passou |
| L49 dois relógios | test_voltas (2 provam), l49 M1 a M12 | pedido que nunca esteve em pronto | passou (review A5: sem --pedido) |
| L00 ADRs, L50 e L51 textos | test_jarvis_nucleo (3 provam), test_forge invariantes | núcleo curto do Jarvis | passou; L00 e L50 sem teste próprio (só texto) |

## Cenários e resultado real
### Suíte inteira (uma vez, só o QA)
Comando: `FORGE_SUITE_SEM_REUSO=1 python3 scripts/suite-paralela.py` sobre 0c90721, load 2,2 na partida.
```
Ran 2478 tests in 479.898s (4 processos)
OK (skipped=1)
rc=0
```
O skip é herdado (não foi marcado neste lote).

### Mutantes (`bin/forge-mutante`, uma rodada por spec, resultado real)
- lote-unico-032-l02: M1 a M4 morreram, rc 0.
- lote-unico-032-l31: M1 a M5 morreram; `M6 · inválido · bin/forge-fechar:259 · erro de carga ou de execução do teste`, rc 2. Repeti com `--prazo 400`: mesmo resultado em 6m52s. Reproduzi a mutação à mão: `sleep "$1"` em primeiro plano e o teste nomeado trava até o `timeout`. O teste de texto `test_o_sleep_das_esperas_roda_em_segundo_plano_com_wait` mataria o mesmo mutante na hora (A1).
- lote-unico-032-l32 + l32-2 (numa rodada): M1 a M16 morreram, rc 0.
- lote-unico-032-l33: M1 a M11 morreram, rc 0 (E1 equivalente declarado, não roda).
- lote-unico-032-l36: M1 a M8 morreram, rc 0.
- lote-unico-032-l37: M1 a M9 morreram, rc 0.
- lote-unico-032-l49: M1 a M4 e M6 a M12 morreram (11; a spec não tem M5), rc 0.
- vel-p6-gate: M1 a M9 morreram, rc 0.

### Cobertura de condições (`forge-mutante --cobertura --base b2580c6`, rc 1)
115 linhas `sem mutante`, todas em bin/forge-check (L03 a L18, sem spec, como o brief previa); `não coberto`: .github/workflows/ci.yml, bin/forge-fechar (shell, as L02 e L37 têm spec à mão) e tests/comportamento/*. Distribuição por faixa de linha: 12 abaixo de 1200, 28 entre 1200 e 2200, 2 entre 2200 e 3000, 18 entre 3000 e 4200 e 55 acima. A lista completa saiu da execução; os pontos principais estão no A2 e no A3. As condições de bin/forge-mutante e scripts/suite-paralela.py estão `coberta`, `isenta` (5, com motivo) ou `só equivalente` (2: forge-mutante:600 E1 e suite-paralela:498 E1); uma `apagada`.

### Vermelho antes do verde (`bin/forge-testes --vermelho b2580c6441549e1f1cf4d153ca8db3247cae8cf3 --modulos <módulo>`)
Cada saída abre com `vermelho: base=b2580c644154 head=0c90721c86b1 módulos=<módulo> (restrito por --modulos)`; abaixo, a contagem e o rc de cada item.
| Item | Módulos | contagem | rc |
|---|---|---|---|
| L01 | test_catraca | não prova=267; prova (asserção)=4 | 0 |
| L02 | test_fechar, test_fechar_rascunho | não prova=90; prova (asserção)=2 | 0 |
| L03, L08 | test_volta_por_delta, test_etapa_do_brief | herdada=62; passa na base=64; prova (API ausente)=4; prova (asserção)=1 | 0 |
| L04, L16 | test_medidas_m14b, test_pedido_fora, test_sobreposicao_quadro | herdada=73; passa na base=8; prova (API ausente)=4 | 0 |
| L05, L07, L09 a L14, L34, L35 | test_forge | herdada=466; prova (API ausente)=16 | 0 |
| L06 | test_anotar | herdada=12; prova (API ausente)=1 | 0 |
| L11, L49 | test_voltas | passa na base=17; prova (asserção)=3 | 0 |
| L15 | test_decisoes | passa na base=1; prova (asserção)=3 | 0 |
| L17 | test_proximo | prova (asserção)=6 | 0 |
| L18 | test_fila_ocupacao | passa na base=1; prova (asserção)=3 | 0 |
| L31 | test_fechar_sinal, test_hooks_volta_propriedades | prova (API ausente)=1 (+herdada) | 0 |
| L32 | test_suite_paralela | passa=39; API ausente=1; asserção=3; **sem veredito=1** | 2 (A4) |
| L33 | test_forge_mutante | passa=71; API ausente=1; asserção=5 | 0 |
| L36 | test_comportamento, test_testes_tocados | passa=82; asserção=4; **sem veredito=1** (`test_comportamento · sem veredito (prazo, sinal ou executor sem registro em B)`) | 2 (A5) |
| L37 | test_fechar_base_andou | passa=25; asserção=9 | 0 |
| L50, L51 | test_jarvis_nucleo, test_clareza | herdada=7; passa=1; API ausente=1; asserção=2 | 0 |
Sem teste novo, por serem só texto: L00 (ADRs) e L50 (agentes). Os testes que provam, por nome, estão na tabela critério → teste.

### Reversão por item (`git revert --no-commit` em clone descartável em $TMPDIR, commits do item do mais novo ao mais antigo, módulos do item)
Primeira passada sem tratar o fragmento do changelog (conflita em todo item, porque a chore dd51c0a o reescreveu); segunda com esse arquivo resolvido por "ours".
- Revertem limpos e o módulo do item passa (rc 0): L00 (482 testes), L01 (267), L03 (65), L05 (480), L07 (481), L09 (480), L14 (481), L16 (37), L31 (13), L32 (35), L33 (71), L34 (479), L49 (18), L50 (482), L51 (502, sem o módulo que o revert apaga).
- Conflito real no revert (arquivo): L02 (bin/forge-fechar), L04 (bin/forge-check), L06 e L08 (agents/jarvis.md), L10 e L12 (tests/test_forge.py), L11, L13 e L15 (bin/forge-check), L17 e L18 (agents/jarvis.md), L35 (tests/config.json), L37 (tests/test_fechar_base_andou.py). Isso é ordem de pilha, não defeito (A8).
- L36: revert limpo; o único erro é o módulo test_comportamento que o próprio revert apaga (esperado, 86 testes).

### Demais verificações
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0, "nenhum segredo nem caminho pessoal no diff" (origin/develop está em c6244ac, 3 PRs à frente da base b2580c6).
- `scripts/validar-plugin.sh`: `Validation passed`.
- Simulação do merge com origin/develop (`git merge-tree --write-tree HEAD origin/develop`): rc=1, conflito em tests/test_catraca.py (A7).
- PA-7 (docs/engineering/achados-recorrentes.md), conferido no diff: AR-1 (lista de mutantes incompleta) ocorre outra vez: A2 e A3; AR-5 (python sem -I): o único python novo em código que decide é o Popen de `sys.executable` no forge-mutante (L33), com o executor próprio, e o CI usa `python3 -m unittest` de teste, sem decisão; sem ocorrência nova. Linha AR-1 a atualizar pelo tech-lead no mesmo PR (o QA só commita o parecer, conforme o brief).
- Sem E2E e sem acessibilidade: o lote não tem interface.

## Bugs
Nenhum arquivo em docs/qa/bugs/ neste parecer; o único bloqueante (A1) é defeito de teste e está no bloco de achados. Os defeitos de comportamento do código estão no parecer do review (A1 a A6).
