---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: a318e97d9cc5012c3481e0027063c4646c559b40
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-trilha-forge-check (E91.4)

Escopo: BRIEF-PORTAO-REBASE, FC-DOCS-CAMINHO e MODELO-PEDIDO-E-BRIEF (K-166, K-252, K-156) no `bin/forge-check`; módulo novo `tests/test_trilha_forge_check.py`. Só os testes dos arquivos tocados, com TMPDIR; sem suíte local (o check-run `bateria` do mesmo sha é do CI do PR).

## Achados
- A1 (bloqueante) tests/test_trilha_forge_check.py:46 · `forge-testes --vermelho 15936278 --modulos test_trilha_forge_check` sai rc=2: test_portao_manda_rebase_e_traz_o_id_do_pedido dá erro na base (sem veredito). Sem vermelho conclusivo, o autor ajusta o teste (falha por asserção) e repete.
- A2 (bloqueante) tests/mutantes/v0479-trilha-forge-check-2.json:6 · os ids M1..M6 repetem os da spec sem sufixo; `forge-mutante` das duas specs juntas sai rc=2 (id repetido). A rodada única dos 12 não roda; renumere a -2 (M7..M12).
- A3 (recomendado) tests/mutantes/v0479-trilha-forge-check-2.json:6 · `--cobertura` lista bin/forge-check:466 (`base or 'develop'`) sem mutante: o M1 não casa ("a troca sai do nó da condição"). Ajuste o `de`/`para` ao nó.

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
