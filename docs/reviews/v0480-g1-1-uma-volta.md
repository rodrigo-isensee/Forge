---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 45d1fc2728a489d04950a6a304369f6f4f6e8fa5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 · G1.1 (no máximo 1 volta por item), etapas E100.2, E100.6, E100.10, E100.15 e E100.20

Revisão única (ORDEM DO DONO 21/11 22:13): a revalidação (E100.6) leu só o delta `forge-check parecer delta` de 57c0cbff..8522e8fe (no domínio: `agents/jarvis.md`, `bin/forge-check`, `changelog.d/v0480-g1-1-uma-volta.md`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, `tests/mutantes/v0480-g1-1-uma-volta{,-2,-3}.json`, `tests/test_volta_por_delta.py`). Desenho: `docs/propostas/g1-g3-fluxo-rapido.md`, seções 2 e 5.

## Revalidação (E100.6, head 8522e8fe)
- A1 (bloqueante, 57c0cbff) resolvido: `voltas_da_branch` conta as voltas pelo item (briefs com `Volta-de:` da mesma `Branch:` do anterior) e recusa o anterior que já tem sucessor, em `gerar_volta` (bin/forge-check:4307) e em `conferir_volta` (bin/forge-check:4441); o brief com `(volta N)` sem `Volta-de:` também é recusado (bin/forge-check:8731). A sonda S1 da rodada anterior virou `test_volta_conta_o_item_e_nao_a_cadeia`: o 2.º `--volta` do original sai rc 1 com "já tem volta", e a conferência da mesma volta escrita de novo é recusada.
- A2 (recomendado) resolvido: só a forma canônica logo depois do prefixo da decisão autoriza, e as linhas contam como conjunto. Sondas refeitas: "nenhuma volta a mais para melhoria/x" dá 1 (antes 2); linha repetida em duas fontes vale uma (`test_so_a_forma_canonica_autoriza_e_uma_linha_vale_uma_volta`). Resta a cauda livre depois da branch (A4).
- A3 (recomendado) resolvido: `agents/jarvis.md:31` diz "máx. 1 volta por item", coerente com o R-QA novo e com `autor-ate-o-merge.md`.

## Revalidação (E100.10, head 4d2c5333, volta 2 autorizada pelo dono em 22/11)
Delta lido: `forge-check parecer delta` de 8522e8fe..4d2c5333 (no domínio: `bin/forge-check`, `changelog.d/v0480-g1-1-uma-volta.md`, `tests/fixtures/brief/volta-anterior.md`, `tests/mutantes/v0480-g1-1-uma-volta-{3,4}.json`, `tests/test_conferencia_base_dono.py`, `tests/test_etapa_do_brief.py`, `tests/test_volta_por_delta.py`).
- A4 (recomendado, 8522e8fe) resolvido: `VOLTA_NA_DECISAO` ancora em `\.?\s*$` (bin/forge-check:4247); "mais uma volta para melhoria/x foi negada" e a cauda `→ "não"` dão 1 volta no teste, e o espaço final ainda autoriza. M23 (volta à âncora antiga) morre.
- S7 e S8 (segurança A2): `branch_do_anterior_diferente` (bin/forge-check:4278) recusa o anterior sem `Branch:` ou com outra que a do brief novo, nos dois caminhos: `gerar_volta` (bin/forge-check:4317, contra o `--branch`) e `conferir_volta` (bin/forge-check:4453, contra a `Branch:` do brief novo; sem ela, "<branch>"). A contagem segue pela `Branch:` do anterior. Nomes passam por `nome_seguro(sem_controle(...))`.
- Testes: `test_s7_*`, `test_s8_*` e `test_conferencia_recusa_a_volta_sem_branch_no_brief_novo` provam o ramo de falha por comportamento (rc 1 e a mensagem), sem ler a fonte. Os testes que usavam `etapa-outro-papel.md` (sem `Branch:`) passam a usar a fixture `volta-anterior.md`, coerente com a recusa nova; o ajuste em `test_etapa_do_brief.py:984` mantém o caso da branch fora da forma.
- Verificação: os 39 testes afetados (`BriefDeVolta`, `VoltaComABaseDoDono`, `PqDoExecutor.test_volta_com_branch_fora_da_forma_nao_gera`) verdes no head 4d2c5333 com `env -i`. `bin/forge-mutante` M23 a M28 morreram, 1 processo. `--cobertura --base 8522e8fe`: guardas 4281, 4283, 4284, 4317 e 4453 cobertas (M24 a M28). Suíte inteira: CI do PR (sem PR aberto; nada a citar). Tamanho (H1): cerca de 15 linhas de código no delta, dentro do teto.

## Revalidação (E100.15, head e103b9a6, volta 3 autorizada pelo dono em 22/11 06:07)
Delta lido: `forge-check parecer delta` de 4d2c5333..e103b9a6 (no domínio: `bin/forge-check`, `tests/mutantes/v0480-g1-1-uma-volta-{2,3}.json`).
- `bool(branch) and` saiu de `voltas_da_branch` (bin/forge-check:4273): era morto. Com `do_item` vazio, `gerar_volta` já sai em `branch_do_anterior_diferente` (bin/forge-check:4317) antes da contagem, e `conferir_volta` já grava a recusa (bin/forge-check:4453), então contar os briefs sem `Branch:` não muda o veredito.
- M17 saiu com o trecho que ele mutava. M16 passou a mutar a linha nova inteira (`voltas += True`) e morre em `test_volta_de_outro_item_nao_conta`.
- M9 ficou único: o `de` (`recusada para {nome_seguro(sem_controle(branch or '<branch>'))}`) ocorre 1 vez, e o antigo ocorria 2 (bin/forge-check:4284 e 4293). M11 saiu: o trecho `\.?(?=\s|$)` não existe desde a A4, e a âncora segue guardada pelo M23.
- Verificação: `bin/forge-mutante --processos 1 --ids M9,M16`: M9 morreu (4293), M16 morreu (4273). `--cobertura --base 4d2c5333`: 4273 coberta (M16). `--conferir --base 4d2c5333`: o trecho de cada spec do diff está no lugar. Suíte inteira: CI do PR (sem PR aberto; nada a citar). Tamanho (H1): 1 linha de código no delta.

## Revalidação (E100.20, head 45d1fc27, volta autorizada pelo dono, só testes)
Delta lido: `forge-check parecer delta` de e103b9a6..45d1fc27 (no domínio: `bin/forge-check`, `tests/test_forge.py`, `tests/test_revisor_wt.py`, `tests/test_volta_por_delta.py`). `bin/forge-check` e `tests/test_volta_por_delta.py` chegam pelo merge 027af0c6 da `develop` (bfed8033), sem resolução manual (`git show --cc 027af0c6` vazio); o código do item é o já aprovado.
- 45d1fc27 só toca testes (4 linhas acrescentadas, 1 trocada); nenhuma asserção removida nem mudada:
  - `tests/test_forge.py:5999` (setUp de `VoltaComRecomendacao`): o brief anterior ganha `Branch: melhoria/x   Base: develop`, coerente com a recusa S7 (anterior sem `Branch:` é recusado). Não afrouxa: o teste volta a exercer o caminho que ele afirma, em vez de cair na recusa.
  - `tests/test_forge.py:6123` e `tests/test_revisor_wt.py:415`: apagam o `-2.md` que o próprio teste gerou antes de gerar de novo; sem isso, o 2.º `gerar` cai em "já tem volta" (G1.1, comportamento aprovado). O `unlink` sem `missing_ok` falha se o arquivo não existir, o que prova a geração anterior. As asserções seguintes são as mesmas.
- Verificação: `VoltaComRecomendacao` e `VoltaLeParecerConferido`, 19 testes, verdes no head 45d1fc27 com `env -i`. Sem guarda nova, sem mutante a declarar. Suíte inteira: CI do PR (sem PR; nada a citar). Tamanho (H1): 0 linha de código.

## Verificação
- Testes afetados: `tests.test_volta_por_delta.BriefDeVolta`, 29 testes, verdes no head 8522e8fe, com ambiente limpo (`env -i`) e `python3 -I`. Suíte inteira: com o CI do PR (sem PR aberto agora; nada a citar).
- Mutantes: `bin/forge-mutante` nas três specs, M1 a M22 morreram (M1 por erro sob `None`, como antes). `bin/forge-mutante --cobertura --base 57c0cbff`: toda guarda do delta coberta (4261, 4269, 4272 a 4274, 4307, 4311, 4441, 4443, 8731); a guarda apagada em 4421(base) foi substituída pela 4443.
- Tamanho (H1): o delta soma cerca de 20 linhas líquidas de código em `bin/forge-check`; o item segue dentro do teto de 150.
- Regras de leitura alcançadas pelo delta: R-QA coerente entre `agents/jarvis.md`, `autor-ate-o-merge.md` e a mensagem de recusa; fragmento do `changelog.d/` atualizado com a branch.

## Parecer
Aprovado no head 45d1fc27 (E100.20): o delta só ajusta a preparação de dois testes ao G1.1, sem afrouxar asserção, e o merge da `develop` não muda o patch do item. Aprovado no head e103b9a6 (E100.15): o delta tira código morto e acerta as specs de mutante, M9 e M16 mortos, sem achado novo. Na rodada anterior (head 4d2c5333): A4 está resolvido, e S7 e S8 (segurança A2) estão recusados no gerar e na conferência, com teste do ramo de falha e mutante por guarda, todos mortos. Sem achado novo no delta.
