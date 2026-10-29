---
tipo: qa
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: b9426d8b35215c985c91ced3d571e61504876346
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA - t1-conf-escopo (lote 1, T1-CONF-ESCOPO-REV, E3.1)

Sem UX nem API. Diff testado: `87e32b6...b9426d8` (8 arquivos: `bin/forge-check`, `bin/forge-testes`, `agents/conferente.md`, `tests/test_conf_escopo.py`, `tests/test_testes_tocados.py`, as duas specs de mutantes, o fragmento). Não escrevi o diff. QA em paralelo com review e segurança (decisão ACELERA-RODADA, item 4); os dois já reprovaram o mesmo ponto sobre este head.

## Achados
- A1 (bloqueante) bin/forge-check:1119 · requisito: na etapa merge-integracao o ramo `elif revisados and not violacoes` marca `escopo: ok` também `tests/config.json` e `docs/security/aceites/*`, que o `agents/conferente.md` (item 2) manda como `escopo: fora`/nunca anexo; faltam teste e mutante dos dois arquivos (classe: lista negativa em trava, AR-3; confirma o A1 de review e segurança)

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste / comando | Fronteira protegida | Resultado |
|---|---|---|---|---|
| E1 | merge-integracao com os pareceres aprovados no head: escopo é a branch (`ok`) | `test_branch_com_parecer_aprovado_no_head_nao_marca_arquivo_fora` | parecer aprovado no head | verde |
| E1 | sem parecer ou reprovado: reprova e o arquivo segue `confira` | `test_sem_parecer_ou_com_parecer_reprovado_continua_reprovando` | parecer ausente / reprovado | verde |
| E1 | ref apagada: o head é o mergeCommit e o escopo é `pai..head` | `test_ref_apagada_le_o_merge_commit_do_squash`, `test_merge_commit_sem_parecer_reprova` | primeiro pai diferente do Base-sha; squash sem review | verde |
| E1 | `--desde` mantém a leitura do delta | `test_volta_por_delta...test_desde_nas_etapas_de_branch_inteira_le_so_o_delta` (mutante M17) | delta | verde |
| E2 | fragmento do changelog da própria branch, só por acréscimo | `test_fragmento_do_changelog_da_propria_branch`, `test_anexo_com_remocao_continua_confira` | fragmento de outra branch; remoção | verde |
| E2 | parecer da própria branch só vale trazido por merge, com os mesmos bytes | `test_parecer_da_propria_branch_so_vale_trazido_por_merge` | edição depois do merge | verde |
| E3/E4 | módulo novo no mapa do forge-check (29); suíte do mapa | `test_testes_tocados`, `test_forge_check_roda_os_modulos_dele` | contagem do mapa | verde |
| Regra existente | `tests/config.json` nunca é anexo; aceite do usuário é `escopo: fora` (`conferente.md`, item 2; `R-SEGURANCA`) | nenhum teste no diff cobre; sonda minha (abaixo) | arquivo protegido com pareceres aprovados | VERMELHO: A1 |

## Execução (módulos do item, `forge-testes --listar bin/forge-check`: 29 módulos, em lotes, carga abaixo de 7 antes de cada lote)
- `test_conf_escopo`, `test_testes_tocados`, `test_volta_por_delta`, `test_conferencia_base_dono`, `test_conferencia_registrar`: `Ran 181 tests` / `OK`.
- `test_anotar`, `test_brief_gravar`, `test_catraca`, `test_citacao`, `test_doutor_relogio`, `test_erros_no_brief`, `test_hook_ansi_c`, `test_estado_da_branch`, `test_etapa_do_brief`, `test_guarda_conferente`, `test_guarda_git`, `test_isencoes`, `test_medida_cpu`, `test_medidas_m14b`, `test_pedido_fora`, `test_portao_diff_proprio`, `test_sobreposicao_quadro`, `test_voltas`, `test_hooks_parecer_pasta`: `Ran 579 tests` / `OK`.
- `test_forge`, `test_hooks`: `OK` (5m08s).
- `test_hooks_volta_corpus`, `test_hooks_volta_lancador`, `test_hooks_volta_propriedades`: `Ran 46 tests` / `OK`.
- Os 29 módulos verdes; não rodei a suíte completa nem `scripts/validar-plugin.sh` (fora do item, pelo brief).

## Vermelho antes do verde
`bin/forge-testes --vermelho 87e32b6b254137b3a55e3796d6aac997f43b0e20 --modulos test_conf_escopo`:
```
vermelho: base=87e32b6b2541 head=b9426d8b3521 módulos=test_conf_escopo (restrito por --modulos)
revertidos à base: agents/conferente.md, bin/forge-check, bin/forge-testes, changelog.d/t1-conf-escopo.md
tests.test_conf_escopo.AnexosImplicitos.test_fragmento_do_changelog_da_propria_branch · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.AnexosImplicitos.test_parecer_da_propria_branch_so_vale_trazido_por_merge · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_branch_com_parecer_aprovado_no_head_nao_marca_arquivo_fora · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_merge_commit_sem_parecer_reprova · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_ref_apagada_le_o_merge_commit_do_squash · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_sem_parecer_ou_com_parecer_reprovado_continua_reprovando · H=ok · B=falha · prova (asserção)
```
Os seis testes novos provam por asserção. (A mesma rodada com `test_testes_tocados` lista os testes antigos como "não prova (passa na base)", o esperado para teste que já existia.)

## Mutantes
`bin/forge-mutante --cobertura --base 87e32b6b254137b3a55e3796d6aac997f43b0e20`: rc 0; toda condição Python mudada em `bin/forge-check` (1013, 1015, 1016, 1018, 1025, 1031, 1033, 1036, 1089, 1090, 1092, 1093, 1094, 1119, 1121) `coberta`; uma `isenta` (1006, frontmatter ilegível vira `{}` e cai em `not pedido`, que o M2 cobre; aceito). `bin/forge-testes` e `agents/conferente.md` não têm condição Python mudada. Lista conferida contra o diff: um mutante por linha de guarda, e o M15 (1119) tira o ramo inteiro, mas nenhum mutante cobre a condição ausente do A1, pois ela não existe.

`bin/forge-mutante tests/mutantes/t1-conf-escopo.json tests/mutantes/t1-conf-escopo-2.json`: rc 0, 17 de 17 `morreu` (M1 a M17), sem sobrevivente nem equivalente declarado.

## Sonda do A1 (repositório temporário do `tests/test_conf_escopo.py`, script em `$TMPDIR/qa-engineer-t1-conf-escopo/sonda/sonda_a1.py`)
Branch com `tests/config.json` e `docs/security/aceites/x.md` num commit e, no seguinte, os três pareceres (review, segurança, QA) aprovados com `commit:` igual ao do commit dos arquivos; `forge-check entrega --etapa merge-integracao`, sem `--desde`:
```
RC 0
escopo: ok (merge-integracao: branch com os pareceres aprovados no head) "docs/security/aceites/x.md"
escopo: ok (merge-integracao: branch com os pareceres aprovados no head) "tests/config.json"
```
Esperado (`conferente.md`, item 2): os dois seguem `escopo: confira`/`fora`. Sem `tests/config.json` e aceite na branch, o resto da sonda sai `ok`, como deve. Os pareceres válidos não dispensam essa exceção: o `forge-check pr` não olha o aceite pelo mesmo critério da conferência de escopo, e a conferência é a segunda camada.

## Parecer
Reprovado por um bloqueante (A1), o mesmo de review e segurança, provado pela sonda acima e sem teste no diff. Todo o resto do item passa: 29 módulos verdes, seis testes novos com vermelho provado, 17 mutantes mortos, cobertura sem linha de guarda descoberta. Correção sugerida: o ramo E1 só vale com `not nome.startswith(ACEITES_DO_USUARIO) and nome != "tests/config.json"`, com teste (ref viva e mergeCommit) e mutante que tire a condição; ajuste do texto do `conferente.md` citando as duas exceções. Responsável: `tech-lead` (código), com este QA para teste e mutante na revalidação.
Não toquei `docs/engineering/achados-recorrentes.md`: a classe AR-3 é de segurança e o brief limita a entrega ao parecer; fica a atualizar pelo autor do parecer de segurança.
