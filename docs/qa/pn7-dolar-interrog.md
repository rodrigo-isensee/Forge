---
tipo: qa
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 3b412fa65d473b33ddd8bc61504db97046cdf510
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: PN7-DOLAR-INTERROG, volta 2 (H1-1 da P-N7, `R-QA`)

Código testado: `3b412fa` (worktree desanexada, base `31257c1`), delta `c6eb028..3b412fa` sobre o meu parecer anterior (c6eb028, sobre 312ecf0). Pedidos: PN7-DOLAR-INTERROG e PN7-DOLAR-INTERROG-REV. Sem `CA-n` de UX; as obrigações são o escopo do pedido e as decisões técnicas de 2026-10-30 01:04 e 01:45: `$?` entre aspas duplas sempre passa; fora de aspas só como argumento de `echo` ou de `printf` sem opção, sem redireção nem pipe; a guarda textual do `IFS` saiu; `heredocs_simples` voltou à regra da base.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `$?` entre aspas duplas passa; fora de aspas só em `echo`/`printf` sem opção, sem redireção nem pipe, com `IFS` posto de 9 jeitos | `CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs` (10 tokens × 4 posições × 3 aspas × 9 `IFS` × 12 lugares, mínimo 5000) | `I"FS"=0`, `printf -v`, `read`, `source`, `$(printf I)FS`; `x$?main`, `git$?push`, `printf -v`, `printf $?`, `x=$?`, pipe, redireção, `$(...)` | passou |
| Todo outro `$`, crase, chaves, `<<'$'` seguem recusados (rc 2); os casos legítimos passam | fixtures `pn7-dolar-interrog-*` via `Hooks.test_fixtures` (inclui os novos `ifs-por-*` e `codigo-fora-de-echo-com-heredoc`) | push na main, parecer ausente, heredoc que cita a palavra do merge | passou |
| `heredocs_simples` na regra da base (nenhum `$` nas linhas de comando) | mesmo teste de propriedade (`assertFalse` em todo `$?`) | `$?` após heredoc | passou |
| Motivo da regra: `IFS` com dígito divide a palavra | `CodigoDeSaida.test_ifs_com_digito_divide_o_codigo_fora_de_aspas` | `x$?main` com `IFS=1` | passou (premissa, passa na base de propósito) |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.CodigoDeSaida tests.test_hooks.Hooks.test_fixtures tests.test_hooks_volta_corpus` sobre `3b412fa`: 19 testes, OK, rc=0 (carga de 1 min em 0,72 no disparo).
- Vermelho (`bin/forge-testes --vermelho c6eb0288395cbb8b32b6b921cda6eea5287fd864 --modulos test_hooks`, rc=0):
```
vermelho: base=c6eb0288395c head=3b412fa65d47 módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/pn7-dolar-interrog.md, docs/adr/0011-analisador-de-comandos-gramatica-positiva.md, docs/hooks.md, hooks/_comum.py, hooks/parecer.py
tests.test_hooks.CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs · H=ok · B=falha · prova (asserção)
tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=52; prova (asserção)=2
```
- Mutantes (`bin/forge-mutante tests/mutantes/pn7-dolar-interrog.json`, rc=0): D1 a D16 todos `morreu` (_comum.py:1478, 1479, 1488, 1528, 1547, 1432, 1434, 1434, 1441, 1441, 1612, 1598, 1621, 1444, 1617, 1632).
- Cobertura (`bin/forge-mutante --cobertura --base 31257c14c8d245d66e7806edb7cd65e22b3aeb04`, rc=0): as 12 condições Python mudadas saem `coberta` (_comum.py:1432, 1434, 1441, 1444, 1478, 1479, 1528, 1547, 1598, 1612, 1617, 1632), nenhuma `sem mutante`. Conferência à mão contra o diff: `limites.append(fim - 1)` (heredoc) e o `except ValueError` não são condição; o ramo do heredoc é exercido pelo fixture `codigo-fora-de-echo-com-heredoc-bloqueia`. `parecer.py` só voltou à base: sem guarda mudada. O meu A1 anterior (mutante de `"IFS" in texto`, parecer.py:109) ficou sem objeto: o trecho saiu.
- `scripts/verificar-contribuicao.sh origin/develop`: `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.` rc=0.
- PA-7 (`docs/engineering/achados-recorrentes.md`), itens de QA: AR-1 (lista de mutantes incompleta) conferido, sem ocorrência; AR-2 (ramo de falha sem teste de comportamento) sem ocorrência: todo ramo de recusa tem caso rc 2 no teste de propriedade ou fixture.
- Os dois bloqueantes da volta 1 (nome do `IFS` montado com aspas, barra, `printf -v`, `read`, `source`, substituição) estão na coluna `IFS` do teste de propriedade e nos fixtures `ifs-por-*`, e passam sobre `3b412fa`.
- Acessibilidade e E2E de UI: não se aplicam (hooks de linha de comando). Sem `skip`, sem teste instável.
- Os pareceres de review e segurança do mesmo head são de outras delegações e não foram lidos.
