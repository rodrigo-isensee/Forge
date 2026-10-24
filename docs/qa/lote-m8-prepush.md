---
tipo: qa
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: e025ed8a210a7c97796adc5075854066bc0e0b9a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-m8-prepush

Escopo: EST-M8 (o pre-push de `melhoria/*` roda só os testes afetados, com recuo à suíte inteira), REVERSAO-MAPA e FORGE-TESTES-CAMINHOS. Revalidação 2 sobre o head e025ed8 (o parecer anterior era sobre a15a569, reprovado por A1 e A2). Plano antecipado não houve (pedido de controle sem especificação `CA-n`; as obrigações são os itens E1 a E3 do pedido e a decisão do dono, "A"). Diff conferido contra o escopo: só `.githooks/pre-push`, `bin/forge-testes`, testes, spec de mutantes e changelog; escopo igual ao anterior.

## Achados

## Revalidação dos achados anteriores
- A1 (guarda de árvore limpa com arquivo mapeado sujo): resolvido. `test_arvore_suja_com_arquivo_mapeado_nao_vira_envio_dirigido` mata o mutante M1 da spec.
- A2 (spec de mutantes): resolvido. `tests/mutantes/lote-m8-prepush.json` existe, com 8 mutantes.
- A3 (`! -L bin/forge-testes`): resolvido (M2 morreu, `test_ferramenta_que_e_link_roda_a_suite_inteira`). A4 (recomendado): guarda `origin/develop` redundante, mantida como recomendação.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 só o módulo afetado roda, sem anotar árvore verde | `PrePushAfetados.test_so_o_modulo_afetado_roda_e_nao_anota_a_arvore_verde` | caminho mapeado | passou |
| E1 falha em módulo afetado barra, em não afetado não | `test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra` | limite do afetado | passou |
| E1 recuo à suíte inteira (sem mapa, sem base, sem ferramenta, link, árvore suja, HEAD diferente, várias refs, ref não branch) | testes `test_*_roda_a_suite_inteira` e `test_arvore_suja_com_arquivo_mapeado_...` | falha fechada | passou |
| E1 diff que toca filtro, mapa ou hook roda a suíte inteira (seg A1/A2) | `test_diff_que_toca_o_filtro_o_mapa_ou_o_hook_roda_a_suite_inteira` | auto-julgamento | passou |
| E1 base é a ref remota, não branch local homônima | `test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome` | ref ambígua | passou |
| E1 bloqueios de conteúdo antes do filtro | `test_bloqueios_de_conteudo_valem_antes_do_filtro` | main, force, fluxo | passou |
| E2 mapa de `conferir-reversao.py` e scripts de aviso | `MapaCobreOQueOsTestesLeem`, `NaoEPortao` | script fora da suíte completa | passou |
| E3 caminhos, fora do repositório, `--completa`/`--vermelho`, manifesto de dev | testes de `Execucao`, `test_manifesto_do_plugin_de_dev_...` | limite do repositório, vazio | passou |
| Seg A1 mapa cobre os testes que executam `hooks/` e `bin/forge-changelog` | `test_a_familia_dos_testes_que_executam_hooks_e_bin_roda_no_envio_dirigido` | mapa estreito | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados -q`: 92 testes, OK.
- Vermelho/verde (`bin/forge-testes --vermelho 3c66b88 --modulos test_pre_push_afetados,test_testes_tocados`, rc=0): `vermelho: base=3c66b881af31 head=e025ed8a210a`; `revertidos à base: .githooks/pre-push, bin/forge-testes, changelog.d/lote-m8-prepush.md, docs/qa/..., docs/reviews/..., docs/security/...`; `contagem: não prova (passa na base)=75; prova (asserção)=17`. Os que passam na base guardam o recuo à suíte inteira (a base sempre rodava tudo).
- Mutantes declarados (`bin/forge-mutante tests/mutantes/lote-m8-prepush.json`, saída 0): M1 `.githooks/pre-push:253` morreu; M2 `:253` morreu; M3 `:253` morreu; M4 `:263` morreu; M5 `:263` morreu; M6 `:257` morreu; M7 `:305` morreu; M8 `bin/forge-testes:96` morreu.
- Conferência da lista contra o diff (spec limitada a 8): linhas de guarda de `dirigido()` sem mutante na spec rodei eu, à mão, em cópia descartável (`$TMPDIR`), com `tests.test_pre_push_afetados`: sem `n_refs` -eq 1: morreu; sem `refs/heads/*`: morreu; sem `.githooks/` no diff conferido: morreu; sem `bin/forge-testes` no diff conferido: morreu; plano sempre aceito: morreu. Sobreviveram, por equivalência: sem o filtro de hex e sem o de sha zero (a guarda `HEAD = enviado` já os recusa e a exclusão de ref remota por sha zero sai antes, no hook), `-f bin/forge-testes` (plano falha fechado sem a ferramenta) e `[ -n "$ancora" ]` (merge-base vazio com rc 0 não ocorre). Nenhum comportamento a provar; fica como recomendação, não bloqueia.
- À mão, clone de brinquedo (`$TMPDIR/qa-engineer-lote-m8-prepush/toy2`, hook e `forge-testes` reais): push que muda só `tests/test_a.py`: `pre-push: rodando só os testes afetados`, `forge-testes: dirigido (test_a)`, rc=0, marca `rodou-a`. Push que muda `.githooks/pre-push`: suíte inteira, rc=0, marcas `rodou-a rodou-b`.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando). Achados recorrentes (PA-7): a lista está vazia, nada a conferir.
- Teto M14 (500 de 400 linhas) é decisão de review, não de QA.
