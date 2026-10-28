---
tipo: qa
contrato: 1
pedido: catraca-pr-mesclado
branch: melhoria/catraca-pr-mesclado
commit: 676dd62a3ae429574c961e3eebf0fb3a1b64ebc8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: catraca-pr-mesclado

Base `e833d3c57fe97a717db0636c1d194dbe85cdd8de`, head `676dd62a3ae429574c961e3eebf0fb3a1b64ebc8`. Diff: `tests/catraca.py` (`ponta_promovida`, `sem`, motivos em `prova_do_squash`, `sha_rotulado_do_mesclado`, `liberado_por_pr_mesclado`, `liberado_por_pr_mesclado_ou_none`), `tests/test_catraca.py`, fragmento do changelog.

## Achados
- A1 (recomendado) tests/mutantes/catraca-pr-mesclado.json:1 · o diff muda guardas de tests/catraca.py e o autor não declarou a spec de mutantes; o QA escreveu 7 (abaixo) e todos morreram; vale versionar a spec

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Promoções #310 e #317 (head no merge de teste, dois PRs squash rotulados, arquivos idênticos) liberam | `RotuloDePrSquash.test_promocoes_310_e_317_com_head_no_merge_de_teste_passam` (CLI ponta a ponta em repositório temporário) | head = merge de teste (2 pais, 1º = base) | passou (vermelho na base) |
| M fora da cadeia de primeiro pai da develop segue pedindo o rótulo, mesmo com head no merge de teste | `test_merge_de_teste_com_merge_fora_da_cadeia_de_primeiro_pai_da_develop_pede`, `test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede` | M fora da cadeia (não libera mais do que a regra já libera) | passou |
| Head que não é merge de teste continua valendo o próprio head | `test_b1_squash_rotulado_busca_o_head_e_passa`, `test_b1_head_com_varios_commits_no_pr_passa` | 1 pai / vários commits | passou |
| Motivo impresso por PR e por arquivo pendente quando não libera (rótulo intruso, não mesclado, sem execução, arquivo mudado depois) | `test_promocao_que_nao_libera_diz_o_motivo_de_cada_pr` | uma só linha `catraca: a conferência do PR mesclado não liberou (...)` terminada em `vale como sem rótulo.` | passou (vermelho na base) |
| Motivo para merge fora da cadeia, sem PR citado e violação sem arquivo | `test_merge_fora_da_cadeia_diz_o_motivo`, `test_sem_pr_citado_e_violacao_sem_arquivo_dizem_o_motivo` | `None in arquivos` agora depois do teste de promoção | passou (vermelho na base) |
| Fora de promoção, sem ruído | `test_fora_da_promocao_nao_fala_da_conferencia` | não-promoção | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_catraca`: Ran 261, OK, 0 falhas.
- Vermelho antes do verde: `bin/forge-testes --vermelho e833d3c57fe9 --modulos test_catraca` saiu 0; `vermelho: base=e833d3c57fe9 head=676dd62a3ae4`, revertidos à base `changelog.d/catraca-pr-mesclado.md` e `tests/catraca.py`; os 4 testes novos, `test_merge_fora_da_cadeia_diz_o_motivo`, `test_promocao_que_nao_libera_diz_o_motivo_de_cada_pr`, `test_promocoes_310_e_317_com_head_no_merge_de_teste_passam` e `test_sem_pr_citado_e_violacao_sem_arquivo_dizem_o_motivo`, `H=ok · B=falha · prova (asserção)`; nenhum cai no head (257 não provam, são herdados).
- Mutação, spec do QA (7 mutantes, um por guarda mudada: segundo pai, primeiro pai = base, exatos 2 pais, cadeia da ponta, M na cadeia, `None in arquivos` reposicionado, impressão do motivo), `bin/forge-mutante`: rc 0, M1 a M7 todos `morreu`. Na primeira rodada M2 sobreviveu só porque declarei o teste errado; com o teste certo (`test_b1_squash_rotulado_busca_o_head_e_passa`, e a mutação derruba 6 testes da classe) morreu; não é teste ausente.
- Não liberou mais do que a regra libera: o 1º pai da ponta continua exigindo base e M continua exigindo a cadeia de primeiro pai da ponta; `test_b8` e o equivalente com merge de teste seguem pedindo o rótulo.
- Não rodei a suíte completa (fora do escopo do lote; roda no pre-push).
