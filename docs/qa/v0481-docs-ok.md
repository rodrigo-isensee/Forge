---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 9fa5f83278cfea50921a8fbd156766067450d354
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-docs-ok (E14.20)

Clone de revisão em `/root/.forge-contrib/wt/v0481-docs-ok-qa`, no head `9fa5f832`. O `forge-copia` do plugin instalado (0.47.15) ainda não tem `--revisao`: criei o clone pelo `bin/forge-copia` da própria branch e levei a branch ao head remoto por `git fetch` e `reset`.

## Achados
- A1 (bloqueante) bin/forge-check:11241 · `gravar =not` perdeu o espaço de `gravar = not`: a spec `tests/mutantes/v046-pr-hook-prazo-2.json` M12 deixa de conferir com a fonte e `ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` (AR-12) falha no CI do head. Restaure a linha.
- A2 (bloqueante) bin/forge-check:9735 · o `if` virou `elif` com `and etapa ...`: a spec `tests/mutantes/v0478-clone-nome-unico.json` M6 perde o `de` e o mesmo teste (AR-12) falha. Alinhe o `de` da spec no mesmo commit que muda a linha.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `docs` sem violação imprime `docs: ok` e rc 0 | `test_forge.ForgeCheck.test_docs_validos_e_ignorados`, `DocsPareceresPedidoECaminho.test_linha_de_comando_com_arquivo`, `test_volta_por_delta` (saídas `(0, "docs: ok\n")`) | o único caso em que o ok sai: lista de violações vazia | passou; vermelho na base, mutantes M1 morto |
| `docs` com violação não imprime `docs: ok` e mantém o rc | `test_forge.ForgeCheck.test_docs_invalidos` (`assertNotIn`) | reprovação: nada de ok, rc inalterado | passou; M2 morto |
| Brief de review, QA e segurança manda `forge-copia clone ... --revisao` | `test_forge_copia.BriefSugereACopia.test_brief_de_parecer_cria_o_clone_de_revisao` | as três etapas de parecer; etapa `codigo` sem `--revisao` | passou; vermelho na base; M3 e M4 mortos |
| Skill `checagem-do-brief/por-tema.md` diz o mesmo | leitura do diff (uma frase acrescentada) | n/a | conferido |
| Nenhum chamador do docs que lê a saída quebra | busca em `bin/`, `hooks/`, `.githooks/`, `scripts/`, `tests/catraca.py`, `.github/` | n/a | nenhum consome o stdout do `docs`; o hook `conformidade` só cita o comando na lista de permitidos |
| Nada que barra deixa de barrar | o `print` vem antes de `gravar` e não muda `violacoes` nem o rc | rc 0 sem violação, 1 com | passou |
| A suíte inteira no CI (`R-QA`) | check-run `bateria` do sha `9fa5f832` (run 45563155477) | n/a | **falhou**: ver A1 e A2 |

## Cenários e resultado real
- `forge-testes --vermelho 220ba3fa... --modulos tests.test_forge_copia,tests.test_volta_por_delta`: `vermelho: base=220ba3fa27fe head=9fa5f83278cf`; 6 provam (asserção), 194 passam na base, 0 caem no head; rc 0.
- `forge-testes --vermelho 220ba3fa... --modulos tests.test_forge --prazo 1500`: 5 provam, 640 passam na base; 2 falham no head e na base (`ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`: `gh pr view` sem acesso no sandbox; `PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso`, que passa quando rodado solto). Os dois são do ambiente local e não tocam o diff; o CI é a autoridade e não os apontou.
- `forge-testes --vermelho 220ba3fa... --modulos tests.test_forge_mutante`: `ConferirTodas.test_toda_spec_do_forge_confere...` falha no head. Local a base também cai (sem veredito limpo no sandbox), mas o CI do head acusa exatamente `v046-pr-hook-prazo-2.json: M12` e `v0478-clone-nome-unico.json: M6`, as duas specs cujo `de` o diff alterou (A1 e A2). A causa é do diff.
- `forge-mutante --cobertura --base 220ba3fa...`: `coberta · bin/forge-check:9731` e `:11239`, declarado, não provado; rc 0.
- `forge-mutante tests/mutantes/v0481-docs-ok.json`: `pedido=v0481-docs-ok rev=9fa5f83278cf`; M1 a M4 morreram; rc 0.

Falta: A1 e A2 (bug alto: bateria do CI vermelha por spec de mutante desalinhada). Corrigindo, o delta para reteste é só `tests/mutantes/*.json` e a linha de `bin/forge-check` (`forge-check parecer delta docs/qa/v0481-docs-ok.md`).
