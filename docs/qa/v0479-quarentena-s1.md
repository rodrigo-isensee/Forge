---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: 1c0c1e9e81d306e5745a9a6c54ed92946a53b2dd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
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

## Revalidação (head 0f7e405b, delta)
`forge-check parecer delta docs/qa/v0479-quarentena-s1.md` (intervalo `ba6f6a03..0f7e405b`) listou só `tests/mutantes/v0478-develop-relogio.json`: o M1 de `tests/prova_de_carga.py:70` (`>= APROVEITAMENTO_MINIMO` para `>= 0`) ganhou o teste `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`. Parecer segue aprovado; sem achado novo.
- Mutante: `bin/forge-mutante tests/mutantes/v0478-develop-relogio.json` (rev `0f7e405b960f`), saída `M1 · morreu · tests/prova_de_carga.py:70`, rc 0. M1 morre.
- Quem mata: o teste novo. A outra entrada da lista (`test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`) está pulada pela quarentena e não pode matar. Prova por cópia do HEAD com o mesmo `para` aplicado: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada -v` deu `FAILED (failures=2)`, `AssertionError: True is not false`, rc 1.
- Sem o mutante, no HEAD: o mesmo teste dá `ok`, `OK (skipped=1)` com o outro pulado, rc 0.
- Os demais itens do domínio (`changelog.d/`, `tests/test_hooks.py`, `tests/config.json`) não mudam neste delta; os critérios da tabela acima seguem valendo.

## Revalidação (head 04e7293b, delta)
`forge-check parecer delta docs/qa/v0479-quarentena-s1.md` (intervalo `0f7e405b..04e7293b`) listou `changelog.d/v0479-quarentena-s1.md`, `tests/config.json` (`teto_pulados` 1 para 2), `tests/mutantes/v0479-quarentena-s1.json`, `tests/quarentenas.py` e `tests/test_catraca.py`. Parecer segue aprovado; sem achado novo. Obrigação: E37.15 (teto 1 mais as quarentenas abertas; o mesmo PR que tira a quarentena devolve o teto a 1).
- Verde no HEAD: `python3 -I -m unittest discover -s tests -p test_catraca.py -k TetoDaQuarentena`, `Ran 4 tests`, `OK`.
- Vermelho: cópia do HEAD em `$TMPDIR` (`git archive`) com `teto_pulados` 2 e sem nenhuma quarentena (as 3 linhas do `@unittest.skip` da S1 apagadas), mesmo comando: `FAIL: test_o_forge_nao_passa_do_teto_da_quarentena`, `AssertionError: True is not false : teto_pulados=2 > 1 + 0 quarentena(s) aberta(s): devolva o teto no PR que tira a quarentena`, `FAILED (failures=1)`. O teto volta a ser exigido quando a quarentena sai.
- Mutantes: `bin/forge-mutante tests/mutantes/v0479-quarentena-s1.json` (rev `04e7293b3c89`), rc 0: M1 morreu (`quarentenas.py:28`), M2 (`:15`), M3 (`:15`), M4 (`:16`), M5 (`:17`), M6 (`:22`) morreram. M4 e M5 morrem por erro do teste sob o mutante, que passa sem ele (a ferramenta marca `(erro)`): valem como mortos.
- Fronteira protegida: teto acima de 1 mais as quarentenas abertas (teto 2 sem quarentena reprova; teto 2 com uma passa; teto 3 reprova). Suíte inteira: só o CI do PR (`R-QA`).

## Revalidação (head 968bc3ff, delta)
`forge-check parecer delta docs/qa/v0479-quarentena-s1.md` (intervalo `04e7293b..968bc3ff`) listou `tests/quarentenas.py`, `tests/test_catraca.py` e as três specs de mutantes (`v0479-quarentena-s1.json`, `-2.json`, `-3.json`). A contagem passa a aceitar só skip vivo (`test_*` de TestCase; sem função aninhada, `if False` ou classe que não é TestCase) e exige prazo AAAA-MM-DD e "OK do dono" no motivo. Parecer segue aprovado; sem achado novo.
- Verde no HEAD: `python3 -I -m unittest discover -s tests -p test_catraca.py -k TetoDaQuarentena`, `Ran 8 tests`, `OK`; `-k TetoDePulados`, `Ran 4 tests`, `OK`.
- Vermelho: cópia do HEAD em `$TMPDIR` (`git archive`) com `tests/quarentenas.py` da base `04e7293b` (função antiga), mesmo comando: `Ran 8 tests`, `FAILED (failures=12)`. Caem `test_conta_skiptest_vivo_e_subpasta`, `test_skip_morto_da_sonda_s1_nao_conta` e 10 subcasos de `test_quarentena_sem_prazo_ou_sem_ok_do_dono_e_recusada` (sem prazo, sem OK, prazo `26/11`, `2026`, `ok do dono` em minúscula, em decorador e em `skipTest`). Os testes novos provam a mudança.
- Mutantes: `bin/forge-mutante` nas três specs (`--processos 3`), rev `968bc3ff91e4`, rc 0: M1 e M4 a M22 morreram (20 de 20; nenhum sobrevivente nem sem veredito). M4, M5, M6, M7, M14, M15, M19 e M21 morrem por erro do teste sob o mutante, que passa sem ele (`(erro)`): valem como mortos.
- Cobertura: `bin/forge-mutante --cobertura --base 04e7293b3c89` lista todas as condições mudadas de `tests/quarentenas.py` (linhas 15, 20, 26, 28, 30, 38, 41, 44, 50, 61) como `coberta`; nenhuma sem mutante. "Declarado, não provado" é lido junto da rodada acima, que provou.
- Fronteira protegida: skip morto não conta; quarentena sem prazo em data ou sem "OK do dono" é recusada (ValueError); `teto_pulados` segue limitado a 1 mais as quarentenas vivas. Suíte inteira: só o CI do PR (`R-QA`).

## Revalidação (head 1c0c1e9e, delta)
`forge-check parecer delta docs/qa/v0479-quarentena-s1.md` (intervalo `968bc3ff..1c0c1e9e`) listou `tests/quarentenas.py`, `tests/test_catraca.py` e as cinco specs `tests/mutantes/v0479-quarentena-s1*.json`. A contagem passa a usar o carregador do unittest e prazo vencido é recusado. Parecer segue aprovado; sem achado novo.
- Verde no HEAD: `python3 -I -m unittest discover -s tests -p test_catraca.py -k TetoDaQuarentena`, `Ran 15 tests`, `OK`; `-k TetoDePulados`, `Ran 4 tests`, `OK`.
- Vermelho contra `1277477e`: `forge-testes --vermelho 1277477e` passou dos 550 s que dei e foi morto (rc 143), sem veredito; não vale como prova. Prova por cópia (`git archive HEAD` em `$TMPDIR`, com `tests/quarentenas.py` de `1277477e`), `-k TetoDaQuarentena`: `Ran 15 tests`, `FAILED (failures=1, errors=24)`. Caem 25 casos: 24 por erro de API ausente na versão anterior, incluindo `test_quarentena_vencida_e_recusada_e_a_do_dia_passa`, `test_pasta_que_o_unittest_nao_carrega_e_recusada`, `test_subpasta_conta_so_se_o_unittest_a_descobre` e os 10 subcasos de prazo/OK do dono, e 1 por asserção (`test_sem_data_dada_o_prazo_e_comparado_com_hoje`). O vermelho por erro (e não por asserção) vale pela mudança de interface; a asserção de prazo vencido só se prova pelo mutante.
- Mutantes: `bin/forge-mutante --processos 3` nas cinco specs, rev `1c0c1e9e81d3`, rc 0: 33 mutantes (M1, M4 a M7, M9 a M12, M16 a M19, M21, M23 a M41), todos `morreu`; nenhum sobrevivente nem sem veredito. Os marcados `(erro)` (M4, M5, M6, M7, M19, M21, M23, M24, M26, M27, M32, M33, M34, M38) morrem por erro do teste sob o mutante, que passa sem ele: valem como mortos.
- Fronteira protegida: skip morto não conta; subpasta só conta se o unittest a descobre; quarentena sem prazo, sem "OK do dono" ou com prazo vencido é recusada; o dia do prazo passa. Suíte inteira: só o CI do PR (`R-QA`).
