---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: ba6f6a0366ed1d0c1280bc9f43e402d25d830e57
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

## Revalidação (head ba6f6a03, delta)
`forge-check parecer delta` listou `changelog.d/v0479-quarentena-s1.md` e `tests/test_hooks.py` (a junção com a develop, que trouxe o #701, ficou fora do domínio). Parecer segue aprovado; o A1 anterior está atendido e sai do bloco de achados.
- Pulado com motivo, cartão e prazo: `python3 -I -m unittest discover -s tests -p test_hooks.py -k sonda_s1 -v` deu `skipped 'quarentena (OK do dono 19/11 18:12) ... cartão TESTE-SONDA-S1-RELOGIO; prazo 2026-11-26'`, `OK (skipped=1)`. O prazo em data atende o A1.
- Corpo igual ao da develop: `git diff origin/develop -- tests/` (develop ef186de8) mostra só as 3 linhas do `@unittest.skip` antes do `def`; o corpo não muda.
- Volta a rodar sem o skip: numa cópia em TMPDIR, com o decorador removido, o mesmo comando deu `... ok`, `Ran 1 test in 8.739s`, `OK`, e o diff da cópia contra a develop em `tests/test_hooks.py` ficou vazio.
- Teto: `teto_pulados` é 1 no head e na develop (T3 só deixa cair); a quarentena ocupa a vaga, sem subir o teto. Suíte inteira: só o CI do PR (`R-QA`).
