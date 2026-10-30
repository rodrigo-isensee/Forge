---
tipo: qa
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 9001a894b1b08fd016ce3ef4c5539e1bd2c1f1ab
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: PN7-DOLAR-INTERROG, volta 3 (H1-1 da P-N7, `R-QA`)

Código testado: `9001a89` (worktree desanexada, base `31257c1`), delta `4514fdd..9001a89` sobre o meu parecer anterior (sobre `3b412fa`). Sem `CA-n` de UX; as obrigações são o escopo do pedido e a decisão técnica de 2026-10-30 02:08: fora de aspas, o `$?` só vale se o texto do comando não tiver `$(`, `$((`, crase, `<(` ou `>(`; `simples_da_gramatica` recusa o `$?` solto com a palavra K3 no resto; entre aspas duplas segue valendo; as regras de posição da volta 2 não mudam.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Com substituição de comando em qualquer ponto, o `$?` fora de aspas recusa; entre aspas duplas passa | `CodigoDeSaida.test_substituicao_de_comando_recusa_o_codigo_fora_de_aspas` (6 prefixos × `$?main`/`"$?"main`; K3 em `simples_da_gramatica`) | `git push origin $(true) echo x$?main`, `$((0))`, `<(…)`, `>(…)`, crase via K3, `IFS=0` antes | passou |
| Propriedade `$?` × posição × aspas × `IFS` × lugar, agora com `$(true) echo {}` e `$((0)) echo {}` | `CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs` (mínimo 5000) | `x$?main`, `printf -v`, `read`, `source`, pipe, redireção, `$(...)` | passou |
| Fixtures novas: substituição e aritmética antes do código recusam (rc 2) | `Hooks.test_fixtures` (`pn7-dolar-interrog-substituicao-antes-do-codigo-bloqueia`, `...-aritmetica-antes-do-codigo-bloqueia`) | push na `main` por `$?` depois de `$(…)` ou `$((…))` | passou |
| `echo rc=$?` e `git push origin x; echo rc=$?` (sem substituição) seguem passando | mesmo teste novo (`assertIsNone`, `simples_da_gramatica` retorna lista) | uso legítimo do `$?` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.CodigoDeSaida tests.test_hooks.Hooks.test_fixtures tests.test_hooks_volta_corpus` sobre `9001a89`: 20 testes, OK, rc=0 (carga de 1 min em 0,72 no disparo).
- Vermelho (`bin/forge-testes --vermelho 4514fdd3d822f512887ca2a8f9c3b2a20999fa70 --modulos test_hooks`, rc=0):
```
vermelho: base=4514fdd3d822 head=9001a894b1b0 módulos=test_hooks (restrito por --modulos)
revertidos à base: changelog.d/pn7-dolar-interrog.md, docs/adr/0011-analisador-de-comandos-gramatica-positiva.md, docs/hooks.md, hooks/_comum.py
tests.test_hooks.CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs · H=ok · B=falha · prova (asserção)
tests.test_hooks.CodigoDeSaida.test_substituicao_de_comando_recusa_o_codigo_fora_de_aspas · H=ok · B=falha · prova (asserção)
tests.test_hooks.Hooks.test_fixtures · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=52; prova (asserção)=3
```
- Mutantes (`bin/forge-mutante tests/mutantes/pn7-dolar-interrog.json`, rc=0): D1, D2, D4, D5, D6, D7, D8, D9, D10, D11, D12, D14, D15, D16, D17 e D19 (16) todos `morreu` (_comum.py:1481, 1482, 1530, 1551, 1432, 1434, 1434, 1444, 1444, 1617, 1603, 1447, 1622, 1637, 1548, 1603).
- Cobertura (`bin/forge-mutante --cobertura --base 31257c14c8d245d66e7806edb7cd65e22b3aeb04`, rc=0): as 13 condições Python mudadas saem `coberta` (_comum.py:1432, 1434, 1444, 1447, 1481, 1482, 1530, 1548, 1551, 1603, 1617, 1622, 1637), nenhuma `sem mutante`. Novas da volta 3: 1548 (D17) e 1603 (D19). A linha removida `limites.append(i + 1)` não é condição.
- Sonda minha, fora do teste do autor (`construcao_nao_modelada` sobre `9001a89`): com `IFS=0;` antes, `&&`, `||`, `&`, `|&`, `;` sem espaço, subshell `(…)`, quebra de linha, `!` e `echo x$?; git push origin x$?main` recusam o `$?` solto no `git`; `{ …; }` e `\`+quebra recusam por outra construção; `echo $? <(true)` recusa por substituição. Só `echo "a" git push origin x$?main` passa, e é argumento de `echo` (inofensivo).
- `scripts/verificar-contribuicao.sh origin/develop`: `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.` rc=0.
- PA-7 (`docs/engineering/achados-recorrentes.md`), itens de QA: AR-1 (lista de mutantes incompleta) conferido contra o diff, sem ocorrência; AR-2 (ramo de falha sem teste de comportamento) sem ocorrência: o ramo novo de recusa tem casos rc 2 no teste novo, na propriedade e nas fixtures.
- A recusa da volta 3 é mais estrita que a da volta 2 (aperta, não afrouxa): o `$?` solto em `echo` com substituição no mesmo texto passa a recusar; aceito pela decisão técnica de 02:08.
- Acessibilidade e E2E de UI: não se aplicam (hooks de linha de comando). Sem `skip`, sem teste instável.
- Os pareceres de review e segurança do mesmo head são de outras delegações e não foram lidos.
