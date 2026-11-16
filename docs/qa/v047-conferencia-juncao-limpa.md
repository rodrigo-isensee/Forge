---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-juncao-limpa
commit: 1477a480d39ff926143246c5c0ed1c72d2e71bfd
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 · conferência de junção limpa (E2.302, parecer E2.331)

Pedido de correção sem especificação de UX. Obrigações: E2.302 (o intervalo só de merges limpos da develop, ancorado em Base-sha selado, com a entrega conferida no primeiro pai, cumpre sem commit novo) e `R-PROVA` (resolução à mão, merge sem âncora e conferida fora da forma seguem pendentes).

## Achados
- A1 (bloqueante) bin/forge-check:2478 · resolvido em 1477a480: teste `test_segundo_pai_ancorado_mas_fora_da_base_recusa` e mutante J6 (Q2) morrem.
- A2 (recomendado) bin/forge-check:2481 · resolvido: Q3 declarado equivalente na spec e comentado no código; aceito (provado à mão no parecer anterior).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Duas junções limpas após a conferida cumprem e gravam o head | JuncaoLimpa.test_caso_real_duas_juncoes_limpas_cumprem_e_gravam, test_uma_juncao_limpa_cumpre | 1 e 2 merges | passou |
| Merge sem âncora selada segue pendente | test_juncao_sem_ancora_segue_pendente | sem âncora | passou |
| Conflito resolvido à mão, ou arquivo da develop descartado à mão, segue pendente | test_conflito_resolvido_a_mao_segue_pendente, test_merge_que_descarta_a_mudanca_da_develop_segue_pendente | árvore do merge ≠ mescla automática | passou |
| Conferida fora da forma não cobre o primeiro pai | test_conferida_fora_da_forma_nao_cobre_o_primeiro_pai | forma da linha | passou |
| Intervalo vazio, commit comum, sem base, sem âncora recusam | test_intervalo_vazio_commit_comum_ou_sem_base_recusam | vazio, commit comum | passou |
| Âncoras da conferida também no `ponto_da_integracao` (sem regressão) | MergeDaBaseDepoisDoBrief.test_conferida_trazida_pela_develop_nao_e_desde | Desde = Base-sha | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_selo_e_entrega.JuncaoLimpa tests.test_selo_e_entrega.MergeDaBaseDepoisDoBrief`: 15 testes, OK (114 s).
- Vermelho antes do verde (`bin/forge-testes --vermelho d4b5dac669e1929ee9671c62a45b458a5ac0b82d --modulos test_selo_e_entrega`), rc 0:
  `contagem: não prova (passa na base)=109; prova (API ausente)=1; prova (asserção)=2`. Os 3 que provam são os de comportamento novo; os demais são guardas ou herdados.
- Mutação (`bin/forge-mutante --processos 3 tests/mutantes/v047-conferencia-juncao-limpa.json`), rc 0: J1 a J5 morreram, nenhum sobrevivente da lista do autor.
- Cobertura (`forge-mutante --cobertura --base d4b5dac6`): 2475, 2478, 2481, 2842 e 9174 têm mutante declarado (declarado, não provado). A lista não tem mutante por condição dentro das linhas 2478 e 2481 (AR-1).
- Mutantes extras meus (spec temporária, não commitada): Q1 (tirar `len(pais) != 2`) morreu por erro do teste, aceito (commit comum dá IndexError; um 3º pai só entra se a árvore bater com a mescla de dois pais); Q2 e Q3 sobreviveram (A1, A2).
- Análise de afrouxamento (R-PROVA): a isenção exige merge de 2 pais, 2º pai na base e na âncora selada, árvore igual à da mescla automática e a conferida da ferramenta no primeiro pai. Sem caminho novo além do achado A1.
- Suíte inteira: check-run `bateria` do CI do PR (sem PR neste pedido).
- Remoto: `origin/melhoria/v047-conferencia-juncao-limpa` = d093ee81 no fetch; nada a mesclar.

## Revalidação por delta (head 1477a480, base do delta d093ee81)
`forge-check parecer delta` listou no domínio: bin/forge-check, tests/mutantes/v047-conferencia-juncao-limpa.json, tests/test_selo_e_entrega.py. Cobre também o `--attr-source` vazio no merge-tree (segurança A1).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 2º pai ancorado mas fora da base recusa (A1 QA) | JuncaoLimpa.test_segundo_pai_ancorado_mas_fora_da_base_recusa | base_ref ≠ âncora | passou |
| `.gitattributes` `merge=union` da árvore de trabalho não limpa conflito | JuncaoLimpa.test_gitattributes_da_arvore_de_trabalho_nao_resolve_conflito | atributos da árvore vazia | passou |
- `python3 -m unittest tests.test_selo_e_entrega.JuncaoLimpa`: 9 testes, OK.
- Mutação `forge-mutante spec --base d093ee81` (`base=d093ee81... rev=1477a480...`): J1 a J7 morreram; `equivalente: Q3`. Sobrevivente: nenhum.
- Vermelho: `forge-testes --vermelho` ficou na fila do R-TETO; feito à mão em cópia (bin/forge-check do d093ee81 + testes do head): `test_gitattributes...` FALHA (prova); `test_segundo_pai...` passa (a guarda já existia; prova por mutação J6, que morre).
- Suíte inteira: check-run `bateria` do CI do PR (sem PR neste pedido).
