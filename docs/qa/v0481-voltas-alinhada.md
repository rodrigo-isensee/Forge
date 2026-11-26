---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: e871982cedd65cf23e497336cb388bc173a3d3e1
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E14.73), #902 por delta `46000ed5..e871982c` (R-QA)

Classe C, sem UX. Revalidação: só o domínio do QA no delta (`forge-check parecer delta`): `bin/forge-check`, `tests/test_volta_por_delta.py`, specs de mutantes, R-QA, jarvis.md, skill, changelog. Referência: ordem do dono de 25/11 17:07 (resolver, não cortar; sem teto; da 4ª tech-lead e revisor juntos), mais a restrição da 3ª (07:31).

## Achados
- A1 (bloqueante) bin/forge-check:4437 · A remoção de voltas_autorizadas deixou o `de` de M21 e M23 de tests/mutantes/v0480-g1-1-uma-volta-3.json fora da fonte: test_forge_mutante.ConferirTodas...confere_com_a_fonte falha. Alinhe ou retire os dois (e confira a -4).
- A2 (bloqueante) bin/forge-check:4679 · A f-string `volta: Entregar (volta {real} do item) sem "{texto_da_volta}"` tem interpolação crua: `test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador` falha. Passe o valor por `sem_controle` ou `nome_seguro`.

## Achados da rodada anterior
- A1 do QA em 46000ed5 (teto e corte): resolvido. `recusa_da_volta`, `voltas_autorizadas` e `VOLTA_NA_DECISAO` saíram; `brief gerar --volta` não recusa mais; `VOLTA_EM_DUPLA = 4` cobra `TRABALHO_EM_DUPLA` na geração e na conferência (VA-M9, VA-M10, VA-M14 mortos). R-QA:17, jarvis.md:31, autor-ate-o-merge.md:10 e o changelog dizem "sem teto; da 3ª só o apontado; da 4ª tech-lead e revisor juntos", coerente com 17:07.
- A2 da segurança (contagem só com `Tipo: codigo`): corrigido por `TIPOS_DE_PORTAO` e lista de exclusão (VA-M5 morto); domínio dela, só conferi o mutante.
- A3 da segurança (medida por soma): `forca_por_teste` mede por teste, com a asserção constante contada (VA-M16 a VA-M20 mortos); domínio dela, só conferi os mutantes.
- A3 do review (VA-M7 morria por erro): VA-M7 ainda sai `morreu ... (erro)`; segue recomendado do review, não bloqueio meu (morre com controle verde).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem teto: a 4ª volta é gerada sem decisão do dono, sem oferta de corte | testes de `BriefDeVolta` da 4ª (a de recusa saiu) | volta 3 e volta 4 geradas; sem `recusa_da_volta` | passou (módulos verdes) |
| 4ª volta traz o trabalho em dupla; a conferência o cobra pela contagem do item | `test_conferencia_da_quarta_volta_cobra_o_trabalho_em_dupla_sem_decisao` | volta 3 sem a marca de dupla passa; volta 4 sem ela reprova; numeração contornada | passou; vermelho: prova (asserção) |
| 3ª volta: restrição no brief; teste removido ou enfraquecido reprova, por teste | `test_volta_alinhada.TerceiraVoltaNaConferencia`, `test_terceira_volta_recusa_teste_removido_ou_enfraquecido` | 2 para 1 testes; asserção trocada por `assert True` noutro teste; `catraca` None | passou |
| Brief que não é de portão em branch reprovada é volta e conta | `test_brief_de_codigo_na_branch_com_parecer_reprovado_e_volta` | `TIPOS_DE_PORTAO` por exclusão; `review`/`qa`/`merge`/`ato-github` isentos | passou; vermelho: prova (asserção) |
| Textos alinhados à ordem de 17:07 | leitura do diff (R-QA, jarvis.md:31, skill:10, changelog) | sem "3 voltas"/"cortar" restantes | consistente |
| Suíte inteira estruturalmente verde (specs de mutante conferem com a fonte; f-strings sanitizadas) | `test_forge_mutante.ConferirTodas...`, `test_forge.SaidaSanitizada...` | `de` de toda spec na fonte; todo valor em f-string sanitizado | FALHA (A1, A2) |

## Cenários e resultado real
- Módulos tocados no head `e871982c`: `bin/forge-testes tests/test_volta_alinhada.py tests/test_volta_por_delta.py tests/test_voltas.py` -> `Ran 168 tests ... OK (skipped=1)` (o pulado é da base).
- Os dois testes que o CI acusa, reproduzidos à mão no head: `python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` -> FAILED (spec `v0480-g1-1-uma-volta-3.json`: M21, M23); `python3 -m unittest tests.test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador` -> FAILED (`bin/forge-check:4679`, a f-string de `real`/`texto_da_volta`). A causa do 1º: o autor ajustou as specs `v0480-g1-1-uma-volta.json` e `-2`, mas não a `-3` (nem conferiu a `-4`).
- Vermelho (`bin/forge-testes --vermelho 46000ed5 --modulos test_volta_por_delta`): `vermelho: base=46000ed50e00 head=e871982cedd6`; provam por asserção `test_brief_de_codigo_na_branch_com_parecer_reprovado_e_volta`, `test_conferencia_da_quarta_volta_cobra_o_trabalho_em_dupla_sem_decisao`, `test_conferencia_recusa_a_numeracao_contornada`, entre outros; o resto "passa na base" (testes que o delta só renomeou).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-voltas-alinhada.json ...-2.json ...-3.json --processos 2` -> rc 0, VA-M1 a VA-M20 `morreu` (VA-M7 por erro do teste com controle verde; recomendado do review). `--cobertura --base 34ab6714`: as condições do diff `coberta`; `apagada` para as 5 condições removidas; `não coberto` só `tests/pesos-d4.json` (dado); as specs `v0480-g1-1-uma-volta*.json` aparecem `spec editada`.
- CI (`gh pr checks 902`, head `e871982c`): verdes `bateria (passos)`, `bateria (verificações longas)`, instalação, árvore já provada. Vermelhos: `suíte (python 3.12, partes 3 e 4)` e `(python 3.14, parte 4)` pelos mesmos dois testes (anotações dos check-runs); outras partes pendentes na leitura; `bateria (pareceres)` e `catraca` esperam os pareceres e o rótulo. Sem `ci: <sha> verde`: o CI do head não está verde por defeito do diff (A1, A2), então a linha não se grava (G3).

## Parecer
Reprovado. A ordem de 17:07 está implementada e provada (A1 anterior resolvido), mas o head quebra duas guardas estruturais da suíte (spec de mutante fora da fonte; f-string sem sanitizador). Corrigir A1 e A2 e reenviar; na revalidação, reteste só esses dois testes e o delta.
