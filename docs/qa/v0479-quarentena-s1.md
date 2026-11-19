---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: a2cc7fb24092f8f51378775a42efec62e21998d2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (E37.6), quarentena da sonda S1

Escopo: `tests/test_hooks.py` (`@unittest.skip` em `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`) e `changelog.d/v0479-quarentena-s1.md`. Diff contra a base `aa16e1a7`: 2 arquivos, 4 linhas a mais, nenhuma removida. Sem suíte local (a suíte inteira é do CI do PR, `R-QA`).

## Achados
- A1 (recomendado) tests/test_hooks.py:1315 · O skip e o fragmento só dão condição de volta (PR #701 com 10 rodadas verdes), sem data; o cartão TESTE-SONDA-S1-RELOGIO deve registrar o prazo, senão a quarentena fica aberta sem limite.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aparece pulado, com motivo e cartão | `unittest discover -s tests -p test_hooks.py -k test_liberar_ou_provar_a_carga_recusa_a_sonda_s1 -v` | n/a | passou: `skipped 'quarentena (OK do dono 19/11 18:12) ... cartão TESTE-SONDA-S1-RELOGIO'`, `OK (skipped=1)`; prazo em data: não há (A1) |
| Corpo igual ao da develop | `diff` do trecho `def test_liberar...` até o próximo `def test_` entre `aa16e1a7` e HEAD | corpo inteiro | passou: "corpo igual"; a única linha nova é o decorador |
| Segue no arquivo e volta a rodar sem o skip | cópia em `$TMPDIR/semskip` (`git archive HEAD`, decorador de duas linhas apagado), mesmo comando | skip removido | passou: `Ran 1 test in 9.015s`, `ok` (o teste roda de verdade, 9 s) |
| `teto_pulados` não subiu | `git diff aa16e1a7 HEAD -- tests/config.json` vazio; `teto_pulados` = 1 nos dois | n/a | passou |

## Pulados da suíte e o teto
- Pulos incondicionais (`@unittest.skip`) em `tests/`: base = 0, HEAD = 1 (este). `expectedFailure` (4, em `tests/evals/test_erros_por_papel.py`) não entra: o `suite-paralela` conta só `result.skipped`.
- Pulos condicionais (`skipTest`, `skipUnless`, cerca de 39 pontos): dependem de ambiente (root, bash, env GNU, shellcheck, `/proc` de outro namespace, `sys.monitoring`). O CI roda sem root, com as ferramentas e em Python 3.12 e 3.14, e `tests/apoio_sandbox.py` diz que no CI nada pula; nenhum deve disparar.
- Soma estimada no CI: 0 + 1 = 1, igual ao teto 1, sem passar. Não há folga: qualquer outro pulo no CI reprova o `teto de pulados`.
- Limite da prova: tentei ler o resultado do `teto de pulados` de runs recentes da develop (artefato `pulados-rapida-doze-*` e log do job), mas o download vai para `*.blob.core.windows.net`, fora da rede liberada do sandbox; o acesso foi negado. A soma acima é por contagem estática, não pela saída do CI. O job `teto de pulados` (só em push na develop) confirma depois do merge.

## Cenários e resultado real
Vermelho antes do verde e mutação: não se aplicam (nenhum teste ou regra nova; o teste é o mesmo, só pulado). Prova de reversão: cópia sem o skip, teste verde em 9 s.
