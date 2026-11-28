---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: 06ab19882f2550d175dbd077d85d02f0d2d1d16c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-trilha-forge-check (E91.4)

Escopo: BRIEF-PORTAO-REBASE, FC-DOCS-CAMINHO e MODELO-PEDIDO-E-BRIEF (K-166, K-252, K-156) no `bin/forge-check`; módulo novo `tests/test_trilha_forge_check.py`. Só os testes dos arquivos tocados, com TMPDIR; sem suíte local (o check-run `bateria` do mesmo sha é do CI do PR).


## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| BRIEF-PORTAO-REBASE: linha de envio com `pull --rebase` e `pedido:` | EnvioDoParecer (3 testes) | branch ausente ou fora da forma (G-5) | passou (10 do módulo ok no HEAD) |
| FC-DOCS-CAMINHO: `docs --base` só no diff, estrito; diff ilegível reprova | DocsNoFluxoDeEntrega, DocsEstritoNoDelta (5 ok) | base fora do fluxo; `main` sem ref | passou |
| K-166, K-252, K-156 no `brief gerar` | ModeloDePedidoNoGerar (5) | etapa conferida; base `a..b` | passou |
| Specs realinhadas z075 e aq1 | forge-mutante | n/a | z075: 8/8 mortos; aq1 (3 specs, 20 mutantes) mortos; a aq1 não está no diff, só confere |
| Sem skip | grep no diff e nos módulos | n/a | passou (nenhum skip, skipIf ou expectedFailure) |

## Cenários e resultado real
- Vermelho antes do verde: `vermelho: base=159362786f6f head=a318e97d9cc5 módulos=test_trilha_forge_check (restrito por --modulos)`; prova=5 (3 asserção, 2 API ausente), não prova (passa na base)=5 (testes de borda negativa), sem veredito=1; saída 2.
- Mutantes, cada spec sozinha: v0479-trilha-forge-check.json M1..M6 mortos, rc=0; -2.json M1..M6 mortos, rc=0. Juntas: rc=2 (A2).
- Prova de ponta a ponta, raiz descartável com `mktemp`: o `brief gerar` de portão traz a linha `- envio: ... com pedido: pxx ... git push origin melhoria/pxx; ... git pull --rebase ... nunca merge nem --force`; os PQ `forge-check docs --base develop` e `forge-check pr pxx --previo --base develop`. Com um review velho fora do formato na base e um parecer novo na branch, `docs` sem `--base` acusa os dois (rc=1); `docs --base develop` acusa só o do diff (rc=1). `pr --previo` roda rc=0.

## Revalidação (head 95994eec, delta de a318e97d)
- A1 resolvido: `forge-testes --vermelho 159362786f --modulos test_trilha_forge_check` sai 0 (`vermelho: base=159362786f6f head=95994eec3b87`): prova=6 (4 asserção, 2 API ausente), nenhum cai no HEAD.
- A2 resolvido: as três specs `tests/mutantes/v0479-trilha-forge-check*.json` numa chamada, rc=0, M1..M15 mortos (ids únicos).
- A3 resolvido: M7..M11 cobrem bin/forge-check:466-469. `--cobertura --base 159362786f` lista só `não coberto: tests/pesos-d4.json` (dado, sem guarda).
- `de_outra_branch` (K-156): `test_sha_ilegivel_de_outra_branch_nao_conta_e_o_da_branch_sim` (tests/test_revisor_wt.py) cobre 5 casos, com a fronteira slug `x` vs `x-2` e linha sem parecer citado (falha fechada); M13..M15 o matam. `test_revisor_wt.py`: 40 testes, OK.
- Sem skip, skipIf ou expectedFailure nos dois módulos.

## Revalidação (head d2f79996, delta de 95994eec; E91.12)
- Vermelho antes do verde, `forge-testes --vermelho 95994eec --modulos test_revisor_wt`: `vermelho: base=95994eec3b87 head=d2f79996cc41`; `PrLeParecerConferido.test_sha_ilegivel_de_outra_branch_nao_conta_e_o_da_branch_sim · H=ok · B=falha · prova (asserção)`; contagem: prova=1, não prova (passa na base)=39 (herdados); nenhum cai no HEAD.
- Mutantes, `--base 95994eec`: v0479-trilha-forge-check-3.json M13..M20 mortos; revisor-wt-e6a-4.json M1..M4 mortos (M3 realinhado, bin/forge-check:3372); revisor-wt-e6a-1.json M1, M3..M8 mortos (M6 realinhado, :2423), mas M2 `inválido` (trecho aparece 2 vezes) e a spec sai 2 (A1; já era assim no 95994eec, fora do delta do M6).
- Sem skip, skipIf ou expectedFailure em tests/test_revisor_wt.py (grep: 0).

## Revalidação (head 06ab1988, delta de d2f79996; E91.17)
- Mudou no domínio só `tests/mutantes/v0479-trilha-forge-check-2.json` (`para` do M7 virou `f"origin/{'develop'}"`); o merge da develop 27169ed1 (ce5b60de) fica fora do delta.
- `bin/forge-mutante --ids M7` (3 specs): `M7 · morreu · bin/forge-check:466`, rc=0.
- `bin/forge-mutante --base d2f79996cc41129fab309d802639e83228d981c8 tests/mutantes/v0479-trilha-forge-check-2.json`: M7..M12 mortos, rc=0.
- `bin/forge-mutante --cobertura --base 27169ed1dc3e02ea82bc90bdcee5576ae3e6192f`: `coberta · bin/forge-check:466 · …-2.json:M7 · declarado, não provado`; 467, 469 e demais linhas do diff do pedido cobertas; só `não coberto: tests/pesos-d4.json` (dado, sem guarda).

## Achados
- A1 (recomendado) tests/mutantes/revisor-wt-e6a-1.json:1 · M2 `inválido` (o trecho `de` aparece 2 vezes em bin/forge-check, linhas 2018 e 2470): a spec sai 2 e a guarda do filtro por branch fica sem mutante rodando; desambiguar o trecho (cartão).
