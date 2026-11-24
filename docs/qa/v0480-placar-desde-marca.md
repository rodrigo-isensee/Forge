---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-desde-marca
commit: 19c1c2a6063d1600c19ef8a88aee1979cda4b15b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 (E138.3, placar desde a marca anterior na develop), revalidação por delta

Delta 752cf974..19c1c2a6: só `tests/mutantes/v046-mutacao-bench-2.json` (M10), `tests/mutantes/v047-placar-mutacao.json` (M7) e `tests/mutantes/v0480-placar-desde-marca.json` (isenta). Sem mudança de código de produção. Suíte inteira: check-run `bateria` do PR no mesmo sha (não rodada local).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--desde` na marca não avisa | PlacarDaRelease.test_marca_anterior_na_develop_vale_como_a_tag_sem_aviso | marca vs. commit comum | passou |
| Sem tag na marca, sugere o commit | ReleaseAvisaMedidasDaVersao.test_sem_tag_na_marca_sugere_o_commit_da_marca | tag ausente | passou |
| Sem marca, pede a mão | ReleaseAvisaMedidasDaVersao.test_sem_marca_pede_a_marca_anterior_a_mao | histórico vazio | passou |
| Tag fora da develop cede à marca | ReleaseAvisaMedidasDaVersao.test_tag_fora_da_develop_cede_a_marca_anterior_na_develop | tag ancestral antiga | passou |
| Tag na marca vence o commit | test_no_forge_imprime_o_placar_desde_a_tag_anterior_e_o_bench | tag e marca no mesmo commit | passou |
| Specs de mutante conferem com a fonte (A1) | ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes | `de` fora da fonte | passou (resolvido) |

## Execução (head 19c1c2a6)
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: Ran 4 tests, OK.
- `python3 -m unittest tests.test_changelog tests.test_forge_mutante.PlacarDaRelease`: Ran 98 tests, OK.
- Mutação, uma chamada por spec, `--base 752cf974`, todas rc 0, nenhum sobrevivente: v047-placar-mutacao M1 a M7 `morreu` (M7 em scripts/placar-mutacao.py:95); v046-mutacao-bench-2 M9 a M15 `morreu` (M10 em bin/forge-changelog:285); v0480-placar-desde-marca PDM1, PDM2, PDM6 (scripts/placar-mutacao.py:61, :61, :95) e PDM3, PDM4, PDM5 (bin/forge-changelog:284, :285, :285) `morreu`. Cabeçalho: `base=752cf974ae69 mb=752cf974ae69 rev=19c1c2a6063d`.
- `forge-mutante --cobertura --base 0e59c446`, rc 0: linhas 284, 285 (changelog) e 61, 95 (placar) cobertas; a linha 282 da base sai `isenta` com motivo (guarda trocada por `if tags or marca`, coberta por PDM4 e M10), sem `isenta velha`.
- Vermelho: sem teste novo no delta; o vermelho do head anterior segue válido (4 testes provam contra a base 0e59c446, parecer anterior).
- Remoto: `origin/melhoria/v0480-placar-desde-marca` = 19c1c2a6 no fetch.
