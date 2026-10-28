---
tipo: qa
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 044ef1d4ae7ce8f7136ef07fd4c0b810e8d91616
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: pr-verde-lote-check (volta 1)

Pedido de controle do Forge (`bin/forge-check`): E1 (G1), E2 (G2), E3 (G6), E4 (D4), head `044ef1d`, base `1f7bd7f`; delta da volta `26d2260...044ef1d`. Os 5 achados A1 a A5 do parecer anterior estão resolvidos (M9 a M13 mortos, com teste). Nenhum defeito de comportamento. O parecer reprova porque a volta mudou duas guardas (`livre()` em `arquivos_divergentes` para conflitos e em `cmd_delta`) que nenhum teste nem mutante prende (mesma regra do parecer anterior).

## Achados
- A1 (bloqueante) bin/forge-check:423 · guarda mudada sem teste nem mutante: `if livre(nome, ignorar): continue` dos conflitos do merge simulado; trocar por `if False:` sobrevive; falta teste com conflito em arquivo livre (docs/qa/x.md) e mutante.
- A2 (bloqueante) bin/forge-check:1151 · guarda mudada sem teste nem mutante: cmd_delta com `not livre(n, LIVRES)`; voltar para `startswith` sobrevive; falta teste do delta com `KANBAN.md.x` e mutante.

## Classe dos achados
Classe única: linha de guarda mudada no diff (troca de `startswith` por `livre()`, segurança A2 da rodada 1) sem mutante na lista declarada e sem teste que a prenda; a saída 0 de `forge-mutante` só vale para o que a lista cobre. Correção: um teste e um mutante por uso (A1 e A2), numa terceira spec `-3` ou na `-2` (limite de 8 por spec). Recomendação não bloqueante (não devolve): `bin/forge-check:993` (`... if not cod and mb else da_base`) tem o recuo para `da_base` (falha do `merge-base`, fechada para um escopo maior) que o mutante `if False else da_base` não derruba; só alcançável com falha do git ou histórias sem ancestral comum; o autor pode justificar em vez de testar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 Cobre cortado sem marca, só do papel do destino | `LoteDoBriefG1.test_a_etapa_do_cobre_no_fora_do_escopo_sem_marca_reprova` (M1); `..._de_outro_papel_cortada_nao_reprova` (M10) | papel do destino vs. outro | passou |
| E1 caminho de PQ inexistente reprova; com curinga não | `..._caminho_do_pq_que_nao_existe_nem_e_criado_reprova` (M2); `..._com_curinga_nao_e_cobrado` (M16) | criado pelo Entregar, glob | passou |
| E1 -REV e -PR sem a decisão da origem reprova | `..._no_rev_falta_a_decisao...` (M3); `..._no_pr_falta_a_decisao...` (M9) | REV, PR, com e sem a decisão | passou |
| E2 escopo pelo primeiro pai, com parecer depois do merge | `IntegracaoNaBranch.test_com_commits_de_parecer_depois_do_merge_...` (M4); `test_merge_de_outra_branch_conta_tudo` (M5); `test_merge_que_descarta_a_base_mostra_o_que_ela_desfez` (M14) | merge da base, -s ours, outra branch | passou |
| E2 `pr` aceita o id do pedido | `RecusaDoIdDoPedido.test_id_com_brief_da_branch_vira_o_slug_da_linha_branch` (M6, M12) | 0, 1 e 2 slugs, prefixo igual | passou |
| E3 parecer reescrito pelo portão do -REV | `EntregasParalelas.test_parecer_reescrito_pelo_portao_do_rev_casa_pelo_commit_e_pelo_papel` (M7, M11) | papel, commit, Branch | passou |
| E4 só o fragmento exato sai do hash | `PortaoDiffProprio.test_d4_so_o_fragmento_...` (M8); `..._so_o_caminho_exato_do_fragmento_sai_do_hash` (M15); `..._com_base_o_merge_simulado_tambem_ignora_o_fragmento` (M13) | `.md.md`, `.mdx/`, `.md~`, `--base` | passou; conflito em arquivo livre e delta: A1, A2 |

## Cenários e resultado real
- Testes do item: módulos de `bin/forge-testes --listar bin/forge-check` (26) com `python3 -m unittest tests.<módulo>...`: `Ran 1260 tests in 410.129s ... OK`, rc=0 (a suíte completa fica com o pre-push, corte 1 da decisão de 2026-10-24). `tests.test_testes_tocados` está entre eles.
- Vermelho antes do verde dos 6 testes novos da volta (cópia do HEAD em `$TMPDIR/qa-engineer-pr-verde-lote-check/v` com o `bin/forge-check` de `26d2260`): 3 caem (curinga; exato do fragmento, 3 subcasos; descarte da base, 3 subcasos: `FAILED (failures=7)`); os outros 3 (`no_pr`, `outro_papel`, `com_base`) guardam código que já existia em `26d2260` e são presos pelos mutantes M9, M10 e M13, todos mortos. O `forge-testes --vermelho` roda a suíte inteira e estoura o prazo do QA; por isso a prova é por teste.
- `bin/forge-mutante tests/mutantes/pr-verde-lote-check.json tests/mutantes/pr-verde-lote-check-2.json`, rc=0:
  `M1 morreu 4021; M2 morreu 4397; M3 morreu 4229; M4 morreu 994; M5 morreu 989; M6 morreu 665; M7 morreu 903; M8 morreu 706; M9 morreu 4229; M10 morreu 4020; M11 morreu 916; M12 morreu 663; M13 morreu 459; M14 morreu 994; M15 morreu 390; M16 morreu 4384`.
- Conferência das guardas do diff `26d2260...044ef1d` contra a lista: `livre()` (M15), `commit_vale` (M13 e X4), `divergem` (X3), `escopo_pelo_primeiro_pai` (M4, M14), `CAMINHO_NO_PQ` (M16): cobertos. Mutantes extras do QA (spec em `$TMPDIR`): `X1 sobreviveu 1151; X2 sobreviveu 423; X3 morreu 421; X4 morreu 456; X5 sobreviveu 993; X6 morreu 390`; X1 e X2 são os A2 e A1; X5 é a recomendação.
- Resolução dos achados do parecer anterior: A1 (M9), A2 (M10), A3 (M11), A4 (M12), A5 (M13) resolvidos; o `startswith` do changelog virou exato (M15).
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem item a conferir.
