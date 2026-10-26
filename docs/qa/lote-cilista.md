---
tipo: qa
contrato: 1
pedido: lote-cilista
branch: melhoria/lote-cilista
commit: 79fb8162cbaafc7d34f5b1eab672a2383e3c39d0
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-cilista

Revalidação de QA da volta 1 (head 79fb816; diff `b6eb84f...79fb816`: `tests/test_ci_local.py`, `changelog.d/lote-cilista.md` e os pareceres de review e segurança; nenhum código de produção muda). Substitui o parecer b01d744 (009668b), que ficou só local. Rodado em paralelo ao review e à segurança (ACELERA-RODADA "A", item 4): só os testes do item, a suíte completa fica no pre-push.

## Achados
- A1 (bloqueante) tests/test_ci_local.py:36 · o env dos passos e do job não é conferido: env inline com BASH_ENV, chave com aspas, PATH, GIT_EXTERNAL_DIFF e LD_PRELOAD no gate passam e rodam código da branch antes do lint (ver Detalhe)
- A2 (recomendado) tests/test_ci_local.py:72 · passo com SO_SEM_LINT depois do gate aceita qualquer `run`; vale por desenho (no caminho `pesada != 'true'` o lint nem roda), por isso não devolve; se quiser fechar, exigir `run` esperado como no gate

## Detalhe dos achados
**A1** · a volta fechou BASH_ENV/ENV/defaults só na forma de bloco (`^\s*BASH_ENV:`) e o `env` do passo nunca é lido (`passos_da_bateria` guarda só `uses` e `id`). Sondas à mão sobre uma cópia do `ci.yml` real, chamando `passos_antes_do_lint_fora_da_lista` (saída `PASSA` = lista vazia = teste verde):
- `env: {BASH_ENV: scripts/x.sh}` no download: PASSA; no actionlint: PASSA; no zizmor: PASSA; no gate (inline): PASSA.
- `"BASH_ENV": scripts/x.sh` com aspas no env do gate: PASSA.
- `PATH: scripts` no env do gate: PASSA; `GIT_EXTERNAL_DIFF: scripts/x.sh` no gate (que roda `git diff`): PASSA; `LD_PRELOAD: scripts/x.so` no gate: PASSA; `PATH: scripts` no `env` do job: PASSA.
O gate e o download passam pelo hash do `run`, mas o ambiente em que o `run` roda não entra no hash. Correção mínima (esforço P): lista positiva de chaves de `env` por passo (o gate: GH_TOKEN, EVENTO, ACAO, ANTES, HEAD_SHA, REPO, BASE_REF; download, actionlint e zizmor: nenhuma) e, no job, só ACTIONLINT_VERSAO/SHA256 e ZIZMOR_VERSAO/SHA256, lendo `env` com o mesmo laço que lê `uses` e `id`; somar os subcasos inline, aspas, PATH, GIT_EXTERNAL_DIFF e LD_PRELOAD à tabela `variantes`. Dono: `devops-engineer`.

**A2** · `tests/test_ci_local.py:71-72` devolve `n > n_gate` sem olhar o `run`. Sonda: passo `python3 scripts/arbitrario.py` com SO_SEM_LINT logo antes do setup-python (depois do gate): PASSA; idem `echo scripts >> $GITHUB_PATH`. Como `pesada != 'true'` e `pesada == 'true'` são excludentes, o lint não roda onde esse passo roda; não fura a ordem. Recomendado.

## Critério → teste → resultado
Obrigação: E1 do pedido (CI-LINT-LISTA-ABERTA) e a volta 1 (decisão técnica de 18:11: A1 e A2 da segurança, A3 e A4 da segurança, A1 a A3 do review).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (ci.yml real respeita a lista) | `test_bateria_lint_e_ferramentas_antes_de_qualquer_codigo_da_branch` | download < actionlint < zizmor; lista vazia no arquivo real | passou |
| E1 (passo fora da lista reprova) | `test_passo_novo_antes_do_lint_reprova`, 7 subcasos `novos` | passo novo com e sem nome, ação de terceiros, setup sem SHA, gate copiado, download sem checksum, condição alterada; contraprova depois do zizmor | passou |
| Segurança A1 (SO_SEM_LINT antes do gate) | subcaso `SO_SEM_LINT antes do gate roda antes do lint` | posição do passo condicional | passou |
| Segurança A2 (run disfarçado, shell) | subcasos `|-`, `shell: python`, `shell: ./scripts` do gate, `shell` do download, `>-` do download | corpo do `run` não lido; shell próprio | passou |
| Segurança A3, A4; review A1 a A3 | subcasos perl, `. .github/x`, docs/x (gate e download), run e condição do actionlint e do zizmor | classe de comando não listada; condição fora da esperada | passou |
| BASH_ENV, ENV, defaults proibidos | subcasos `BASH_ENV`/`ENV` no env do gate, `defaults`, `BASH_ENV` no env do job | forma de bloco | passou na forma de bloco; furo nas formas inline, aspas, PATH, GIT_EXTERNAL_DIFF, LD_PRELOAD (A1) |

## Cenários e resultado real
- `python3 -m unittest tests.test_ci_local`: Ran 53 tests, OK (no head 79fb816).
- Vermelho: `bin/forge-testes --vermelho b6eb84fed86e3b5289f3950b33d43a86f34343c2 --modulos test_ci_local` saiu rc=1, "contagem: não prova (passa na base)=53; nenhum teste prova a mudança". Igual ao parecer b01d744: o `ci.yml` é o mesmo na base e o teste só troca o leitor sintético; a prova vem das sondas e dos mutantes abaixo (a falha pré-correção, 16 subcasos, é do autor e do pedido, não reproduzida pelo forge-testes). Registrado, não bloqueia.
- Mutação no diff, em cópia descartável (`tests/` copiado para `$TMPDIR/qa-engineer-lote-cilista/cop`, worktree intocada), rodando `LeituraDosWorkflowsTest`; cada mutante precisa derrubar o teste (todos morreram):
  - `return n_gate is not None and n > n_gate` -> `return True`: FAILED (failures=1)
  - gate: `_run_igual(...)` removido do retorno: FAILED (failures=4)
  - download: `_run_igual(...)` -> `True`: FAILED (failures=4)
  - `if passo["shell"]:` -> `if False:`: FAILED (failures=3)
  - `if ENV_QUE_EXECUTA.search(texto):` -> `if False:`: FAILED (failures=4)
  - `passos[n]["run"] != run or` -> `False or`: FAILED (failures=2)
  - `passos[n]["se"] != SO_COM_LINT or` -> `False or`: FAILED (failures=2)
  Teste original restaurado na cópia: OK.
- Sondas à mão sobre o `ci.yml` real (script `$TMPDIR/qa-engineer-lote-cilista/sonda_lote_cilista_qa2.py`; a base real devolve `[]`). Reprovam, como devem: S1 (SO_SEM_LINT antes do gate), S2b (gate `run: |-`), S3b (gate `shell: python {0}`), S4 e S4z (run do actionlint e do zizmor com comando extra), S6b (`docs/x` no gate), perl no gate, `. .github/x` no gate, BASH_ENV em bloco no gate, condição do actionlint `always()`. Passam (não reprovam): as duas da conferência, SO_SEM_LINT depois do gate com `run` arbitrário (A2, recomendado) e `env` inline com BASH_ENV (A1, bloqueante), além das variantes de A1 acima.
- Acessibilidade e E2E: não se aplicam (mudança só de teste de estrutura do CI).

## Riscos
Quem edita o `ci.yml` e também o teste burla a trava de qualquer forma (fica com o review); o que se cobra aqui é que a trava não tenha furo nos casos que ela mesma declara cobrir (BASH_ENV proibido). A severidade do A1 é média (fura CI-ORDEM-LINT); os contadores do frontmatter ficam em 0 porque o defeito está no teste de estrutura, não em código de produção, e volta pelo bloco `## Achados`.
