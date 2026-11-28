---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-forge-check-fc2
commit: e1aff90260eba1e97fa153ddcd9b5e8127e5945f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-forge-check-fc2 (E2.181, portão na E2.437)

Parecer completo, o primeiro desta branch. Sem especificação de UX nem contrato de API: o pedido de correção não tem plano antecipado; os critérios são os dois itens do lote FC2 do pedido v047 (CA-1 BRIEF-VOLTA-FORA-COMPACTO, CA-2 PARECER-DELTA-SEM-MERGE-DA-DEVELOP). Diff conferido contra eles: `bin/forge-check`, `tests/test_volta_por_delta.py`, `skills/qa-testing/SKILL.md`, `changelog.d/` e duas specs de mutante; escopo igual ao dos itens. BRIEF-SELAR-LINHA-DA-ETAPA (terceiro item da E2.181) não está nesta branch, e o review já o registrou (A2); o cartão segue aberto.

## Achados
- A1 (recomendado) bin/forge-check:2989 · Rodado no head: `parecer delta` sobre a própria branch, com o merge dos pareceres vindo do remoto (1911e6b), imprime `aviso: ... não está na origin/develop local` apesar do fetch. Falha fechada correta, mas o texto acusa "outra branch ou sem rede" em merge da própria branch.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 pedido grande cabe no teto | `BriefDeVolta.test_volta_de_pedido_grande_cabe_no_teto_e_passa_na_conferencia` | máximo: 604 ids em 16 linhas de 40, abaixo de `TETO_DE_CARACTERES_DO_BRIEF`; último id `E4.600` | passou; vermelho na base |
| CA-1 lista vazia não some | `BriefDeVolta.test_volta_sem_outra_etapa_diz_que_o_pedido_nao_tem` | vazio | passou; mutante FC2-M1 morre |
| CA-1 corte lê id a id | `test_conferencia_reprova_anterior_bloco_e_achado`, `test_gera_blocos_copiados_decisoes_achados_e_prova`, `test_volta_tira_o_fora_do_escopo_do_pedido` (mudados) | id que sai da linha agrupada reprova | passaram; vermelho na base |
| CA-2 base atrasada é buscada, só o do autor no delta | `DeltaComBaseAtrasada.test_busca_a_base_atrasada_e_mostra_so_o_do_autor` | base já em dia: sem segunda linha `base:` | passou; vermelho na base |
| CA-2 sem rede o merge fica, com aviso | `DeltaComBaseAtrasada.test_sem_rede_o_merge_fica_no_delta_com_aviso` | falha de rede (falha fechada) | passou; vermelho na base |
| CA-2 git que falha dá rc 2 | terceiro teste de `DeltaComBaseAtrasada` + FC2-M4/M8 | erro do git | passou; mutantes morrem |

## Cenários e resultado real
- Testes do item, na raiz do clone (head b7a180d6 mais merge dos pareceres): `python3 -m unittest tests.test_volta_por_delta.DeltaComBaseAtrasada` e os dois testes novos de `BriefDeVolta`: `Ran 5 tests in 4.085s · OK`. O módulo inteiro roda no CI do PR; a falha de `test_reval_delta` vem do #576 na develop, fora deste diff.
- Vermelho antes do verde (`bin/forge-testes --vermelho 58dfa2ab016fbc10c730b369995b0f1e75b000d6 --modulos test_volta_por_delta`, rc=0; sem `--modulos` a execução foi interrompida pelo ambiente e não deu veredito, por isso restrita ao único módulo do diff):
```
vermelho: base=58dfa2ab016f head=0a92c00dc757 módulos=test_volta_por_delta (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v047-forge-check-fc2.md, docs/reviews/v047-forge-check-fc2.md, docs/security/v047-forge-check-fc2.md, skills/qa-testing/SKILL.md
mantidos no HEAD: tests/mutantes/v047-forge-check-fc2-2.json, tests/mutantes/v047-forge-check-fc2.json, tests/test_volta_por_delta.py
...BriefDeVolta.test_conferencia_reprova_anterior_bloco_e_achado · H=ok · B=falha · prova (asserção)
...BriefDeVolta.test_gera_blocos_copiados_decisoes_achados_e_prova · H=ok · B=falha · prova (asserção)
...BriefDeVolta.test_volta_de_pedido_grande_cabe_no_teto_e_passa_na_conferencia · H=ok · B=falha · prova (asserção)
...BriefDeVolta.test_volta_tira_o_fora_do_escopo_do_pedido · H=ok · B=falha · prova (asserção)
...DeltaComBaseAtrasada.test_busca_a_base_atrasada_e_mostra_so_o_do_autor · H=ok · B=falha · prova (asserção)
...DeltaComBaseAtrasada.test_sem_rede_o_merge_fica_no_delta_com_aviso · H=ok · B=falha · prova (asserção)
rc=0
```
- Mutação (`bin/forge-mutante --processos 2 tests/mutantes/v047-forge-check-fc2.json tests/mutantes/v047-forge-check-fc2-2.json`), rc=0, 9 de 9 morreram:
```
forge-mutante: pedido=v047 rev=0a92c00dc757 spec=08a5cb04... spec=0bf3f5b7...
FC2-M1 · morreu · bin/forge-check:3652   FC2-M2 · morreu · bin/forge-check:3643
FC2-M3 · morreu · bin/forge-check:2973   FC2-M4 · morreu · bin/forge-check:2976
FC2-M5 · morreu · bin/forge-check:2978   FC2-M6 · morreu · bin/forge-check:2979
FC2-M7 · morreu · bin/forge-check:2986   FC2-M8 · morreu · bin/forge-check:3194
FC2-M9 · morreu · bin/forge-check:3197
```
- Lista de mutantes contra o diff (`forge-mutante --cobertura --base 58dfa2ab...`): as 8 linhas de guarda aparecem `coberta · declarado, não provado`; nenhuma sem mutante, nenhuma `não coberto`.
- Revalidação lida: `forge-check parecer delta docs/security/v047-forge-check-fc2.md`: `delta: nenhum arquivo do domínio mudou` (só os pareceres de review e segurança vieram por merge).
- AR (PA-7): conferidos; nenhuma classe repetida neste pedido, sem linha nova em `achados-recorrentes.md`.
- Abuso: sem gatilho de segurança neste item; a análise é do parecer de segurança (aprovado, 5e06e892).

## Bugs
Nenhum aberto.

## Revalidação por delta (head d3429349)
`forge-check parecer delta docs/qa/v047-forge-check-fc2.md` (intervalo b7a180d6..d3429349, sem o que veio da develop) listou no domínio: `bin/forge-check`, `skills/qa-testing/SKILL.md`, `tests/mutantes/v0432-integracao-2.json`, `tests/test_volta_por_delta.py`.
- `bin/forge-check` e a spec de mutante: vieram da develop (merge); fora do diff do autor e sem mudança nos testes dos CA-1 e CA-2.
- `skills/qa-testing/SKILL.md` (e1aff902): só reescrita de palavras na linha "Teste e parecer" (`aponta (commit:) para o commit que o inclui` virou `aponta (commit:) o commit que o inclui`; `revalidação` virou `volta`; `sem ler o código do autor (independência)`); toda regra e ID segue no texto (diff lido).
- `tests/test_volta_por_delta.py`: `remoto_sem_manutencao(self.origem)` no `setUp` de `DeltaComBaseAtrasada`, com o import de `ambiente_git`; só isola o remoto bare, não relaxa asserção.
- Rodado no head, sem `-I`: `test_metricas_texto` Ran 2 · OK; `test_ambiente_git` Ran 20 · OK; `test_volta_por_delta.DeltaComBaseAtrasada` Ran 3 · OK.
- Suíte inteira: CI do PR. Os achados e a tabela acima seguem valendo; A1 continua recomendado, sem bloqueio. Bugs: nenhum aberto.
