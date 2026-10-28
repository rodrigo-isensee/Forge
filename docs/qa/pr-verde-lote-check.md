---
tipo: qa
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 26d2260eecbc01712927cfdaa67003df6b0ec107
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: pr-verde-lote-check

Pedido de controle do Forge (`bin/forge-check`): E1 (G1), E2 (G2), E3 (G6) e E4 (D4), head `26d2260`, base `1f7bd7f`. Nenhum defeito de comportamento encontrado: os 4 itens funcionam nos casos antes/depois. O parecer reprova porque a lista de mutantes declarada (M1 a M8) não cobre todas as linhas de guarda mudadas, e a prova de mutação de QA (`R-QA`, skill `qa-testing`) deixou 5 mutantes de guarda sobreviverem.

## Achados
- A1 (bloqueante) bin/forge-check:4222 · guarda sem teste nem mutante: `(?:REV|PR)` em decisoes_cobradas; trocar por `(?:REV)` (o -PR deixa de cobrar a decisão do pedido de origem, requisito E1) sobrevive; falta teste do -PR e mutante.
- A2 (bloqueante) bin/forge-check:4013 · guarda sem teste nem mutante: a etapa do Cobre só reprova se o papel dela é o do destino; remover `nome_do_papel(...) == papel_destino` sobrevive (reprovaria etapa de outro papel cortada legitimamente).
- A3 (bloqueante) bin/forge-check:912 · guarda sem teste nem mutante: em reescrito_por_portao, a igualdade da `Branch:` do brief do -REV com a da entrega pode virar `True` sem teste cair; brief de outra branch isentaria a remoção no parecer.
- A4 (bloqueante) bin/forge-check:659 · guarda sem teste nem mutante: em pedido_do_pr, `Pedido:` do brief igual ao id pedido pode ser removida sem teste cair (o glob `<id>-*` pega brief de outro pedido de prefixo igual e troca o slug).
- A5 (bloqueante) bin/forge-check:455 · guarda sem teste nem mutante: em commit_vale, passar `livres` a arquivos_divergentes (D4 com `--base`, o caso do CI) pode voltar a `LIVRES` sem teste cair; o comportamento está certo (provado à mão abaixo), falta o teste e o mutante.

## Classe dos achados
Classe única dos 5: guarda mudada no diff sem mutante na lista declarada e sem teste que a prenda (a saída 0 de `forge-mutante` só vale para o que a lista cobre). Correção: um teste e um mutante por guarda (A1 a A5; a spec divide em `-1`/`-2` por passar de 8). Mutante X1 (`return nomes if integrou else None` -> `return nomes`) também sobreviveu e é equivalente: sem merge da base a união dos diffs por commit contém o diff do intervalo, então o filtro `arquivos` não muda; aceito como equivalente.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 Cobre cortado sem marca reprova | `LoteDoBriefG1.test_a_etapa_do_cobre_no_fora_do_escopo_sem_marca_reprova` (M1) | etapa do Cobre vs. outra | passou (guarda do papel: A2) |
| E1 caminho de PQ inexistente reprova | `LoteDoBriefG1.test_caminho_do_pq_que_nao_existe_nem_e_criado_reprova` (M2) | criado pelo Entregar, `refs/heads/x`, `origin/develop` | passou |
| E1 -REV sem decisão da origem reprova | `LoteDoBriefG1.test_no_rev_falta_a_decisao_do_pedido_de_origem_reprova` (M3) | com e sem a decisão | passou; -PR sem teste (A1) |
| E2 escopo pelo primeiro pai, com commits de parecer | `IntegracaoNaBranch.test_com_commits_de_parecer_depois_do_merge_...` (M4) | merge da base + parecer | passou |
| E2 merge de outra branch conta tudo | `IntegracaoNaBranch.test_merge_de_outra_branch_conta_tudo` (M5) | falha fechada | passou |
| E2 `pr` aceita o id do pedido | `RecusaDoIdDoPedido.test_id_com_brief_da_branch_vira_o_slug_da_linha_branch` (M6) | 0, 1 e 2 slugs | passou; filtro `Pedido:` sem teste (A4) |
| E3 parecer reescrito pelo portão do -REV | `EntregasParalelas.test_parecer_reescrito_pelo_portao_do_rev_casa_pelo_commit_e_pelo_papel` (M7); `test_uniao_aceita_o_brief_do_rev_da_mesma_branch` | papel, commit, outro pedido | passou; `Branch:` sem teste (A3) |
| E4 só o fragmento do changelog não desatualiza | `PortaoDiffProprio.test_d4_so_o_fragmento_do_changelog_da_branch_...` (M8) | fragmento da branch vs. de outra | passou; com `--base`: A5 |

## Cenários e resultado real
- Testes do item: `bin/forge-testes --listar bin/forge-check` (26 módulos) + `tests.test_testes_tocados`: `Ran 1335 tests ... OK`, rc=0. A suíte completa não foi rodada pelo QA (corte 1 da decisão de 2026-10-24; o pre-push a roda).
- Vermelho antes do verde (cópia em `$TMPDIR` com `bin/forge-check` e `agents/conferente.md` da base `1f7bd7f`, testes novos do HEAD): 15 testes, 10 falharam (os 3 de `LoteDoBriefG1`, `RecusaDoIdDoPedido...slug`, 3 de `IntegracaoNaBranch`, 2 de `EntregasParalelas` e o D4); `test_merge_de_outra_branch_conta_tudo` passa na base de propósito (guarda de falha fechada, morta pelo M5). O `forge-testes --vermelho 1f7bd7f` rodou a suíte inteira e passou do prazo de 580 s do QA (rc=124, sem veredito); o vermelho acima vale como prova por teste.
- `bin/forge-mutante tests/mutantes/pr-verde-lote-check.json`, rc=0:
  `M1 morreu 4014; M2 morreu 4390; M3 morreu 4222; M4 morreu 987; M5 morreu 985; M6 morreu 661; M7 morreu 899; M8 morreu 702`.
- Mutantes extras do QA (spec em `$TMPDIR`, mesmos arquivos, testes dos módulos do item), rc=1: `X1 sobreviveu 989 (equivalente); X2 sobreviveu 912 (A3); X3 morreu 914; X4 morreu 937; X5 sobreviveu 659 (A4); X6 sobreviveu 455 (A5); X7 sobreviveu 4222 (A1); X8 sobreviveu 4013 (A2)`.
- Provas à mão (antes = `bin/forge-check` da base, depois = HEAD):
  - brief `-REV` sem a decisão que só o pedido de origem tem: antes `resultado: aprovado`; depois `decisões: falta "DECISÃO DO DONO 2026-10-27 20:26: ... " (docs/pedidos/PR-VERDE-LOTE-CHECK.md:30)`, `reprovado`.
  - brief com PQ cmd citando `bin/nao-existe-xyz`: antes `aprovado`; depois `pq: PQ-4 cita "bin/nao-existe-xyz", que não existe nem é criado pelo Entregar (R-PROVA)`, `reprovado`. O brief real deste QA passa (`aprovado`, sem falso positivo nos caminhos com `~` e `docs/qa/`).
  - brief com a E3.1 do Cobre movida ao Fora do escopo sem marca: antes `aprovado`; depois `corte: sem marca "E3.1" (etapa do próprio papel cortada ...)`, `reprovado`.
  - parecer reescrito do -REV, entrega com merge da develop e commits de parecer, id do pedido no `pr`: os testes da tabela acima, vermelhos na base e verdes no HEAD (cenário de repositório git descartável por teste).
  - fragmento mudado depois do parecer, com merge da develop no meio e `--base develop`: `commit_vale` com o fragmento em `livres` devolve `None`; sem ele, `desatualizado: changelog.d/ramo.md mudou depois do parecer`. Fragmento de outra branch continua desatualizando (teste D4).
- Nota: o item E2 "`brief gerar` escreve o Base-sha como merge-base" já existia na base (`base_sha_real`); o diff não o muda e não há defeito.
- Recomendação não bloqueante: `startswith` com o prefixo `changelog.d/<slug>.md` também casa `changelog.d/<slug>.md.x`; inofensivo, mas um `==` seria mais estreito.

## Dados de teste
Repositórios git descartáveis por teste (tempfile), briefs e pedidos reais do `~/.forge-contrib` para as sondas de CLI, cópia da base em `$TMPDIR/qa-engineer-pr-verde-lote-check/`.
