---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-anexar
commit: f7f7f28fa5c798f7714b270a4d948ec8bd41b54c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 · E1.256 (forge-changelog release --anexar)

Head revisado: f7f7f28f (base develop c5c3a449; classe C, sensível da catraca). Melhoria sem especificação de UX: as obrigações vêm do pedido (E1.256) e do fragmento. O `--anexar` junta os fragmentos à entrada já existente, por tipo; cria a seção que falta na ordem Adicionado, Alterado, Corrigido; apaga os fragmentos; não toca nos manifestos. Recusa versão ausente, versão fora de X.Y.Z, chamada sem fragmento, fragmento malformado, `CHANGELOG.md` link simbólico e uso misto com `<data>`. Sem plano antecipado (sem especificação nova). Instância que não fez a entrega.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Junta por tipo, cria a seção que falta, apaga fragmentos, manifesto intacto | `ReleaseAnexar.test_junta_na_secao_de_cada_tipo_cria_a_que_falta_e_apaga` | seção ausente no meio; manifesto byte a byte | passou |
| Tipo mais tardio entra no fim da entrada | `test_tipo_que_vem_depois_de_todos_entra_no_fim_da_entrada` | última seção | passou |
| Linha em branco entre seções continua depois da anexada | `test_linha_em_branco_entre_secoes_fica_depois_da_linha_anexada` | separador | passou |
| Cabeçalho com espaço no fim e tipo fora da lista | `test_cabecalho_com_espaco_no_fim_e_tipo_fora_da_lista_sao_respeitados` | caractere especial | passou |
| Entrada vazia e entrada mais antiga | `test_entrada_vazia_recebe_a_secao`, `test_entrada_mais_antiga_tambem_recebe` | vazio; última entrada do arquivo | passou |
| Versão ausente, prefixo de outra (`0.2`), sem fragmento, fragmento malformado: recusa sem alterar | `test_versao_que_nao_existe_e_recusada_sem_mexer`, `test_versao_prefixo_de_outra_e_recusada`, `test_sem_fragmento_e_recusado_sem_mexer`, `test_fragmento_malformado_falha_sem_apagar` | entrada inválida; arquivo e fragmentos intactos | passou |
| `CHANGELOG.md` link simbólico recusado | `test_changelog_link_simbolico_e_recusado` | alvo fora do repositório intacto | passou |
| `--anexar` com `<data>` e `release` sem data recusados | `test_anexar_com_versao_ou_data_posicional_e_recusado`, `test_release_sem_data_e_recusada` | uso misto | passou |
| Release comum não regride | 74 testes anteriores de `tests.test_changelog` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog`: `Ran 87 tests ... OK` (13 novos).
- Vermelho antes do verde, `forge-testes --vermelho c5c3a449 --modulos test_changelog` (rc=0): `vermelho: base=c5c3a449d7c3 head=f7f7f28fa5c7`; revertidos à base `bin/forge-changelog` e o fragmento; fecha com `contagem: não prova (passa na base)=74; prova (asserção)=13`. Os 13 testes de `ReleaseAnexar` saem `H=ok · B=falha`, nada cai no HEAD.
- Mutação, `bin/forge-mutante --processos 4` nas 3 specs (`v047-changelog-anexar.json`, `-2`, `-3`), rc=0: M1 a M17 todos `morreu` (`bin/forge-changelog` linhas 181 a 265). `forge-mutante --cobertura --base c5c3a449` lista as condições Python mudadas como cobertas, sem `não coberto` nem `só equivalente`.
- Exploração à mão em repositório temporário: CHANGELOG sem quebra de linha final recebe a seção e termina com uma; `--anexar 0.2.0 2026-01-01` sai rc=1 com a mensagem de uso; anexar numa seção existente mantém a ordem. Sem defeito.
- Prova de CI: sem PR aberto (pedido sem PR), não há check-run `bateria` para o sha; a suíte inteira fica para o CI do PR. Rodei o módulo afetado e a mutação, não a suíte inteira.
- O remoto avançou com os pareceres de review e segurança; trouxe por merge, sem rebase. O código testado continua o `f7f7f28f` (o merge só soma `docs/reviews` e `docs/security`).
- Limite: o `--anexar` não foi exercitado contra o `CHANGELOG.md` real do Forge, só contra fixtures e repositório temporário.
- Parecer: aprovado, sem achados.
