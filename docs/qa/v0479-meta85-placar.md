---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 6f6aab30715d2ae7cd6136c37cc35ed10bb59f81
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E36.4), forge-placar `fases`: meta de 42 min, mediana, p75, corte por hora e horas paradas

Escopo: só o que a branch acrescenta à `melhoria/v0479-placar-fases` (42c2a906, aprovada): `bin/forge-placar`, `tests/evals/test_placar.py`, mutantes `tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json` e os três `v0479-placar-fases-{2,3,4}.json` reescritos, texto de `docs/melhoria-continua.md` e o fragmento de changelog. Sem suíte local (é do CI do PR, `R-QA`).

## Critério → teste → resultado
Obrigações lidas do cabeçalho de `bin/forge-placar`, do fragmento de changelog e da ordem do dono (19/11 14:52, meta 42 min).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Meta 42 min no json e no texto | `test_fases_e_primeira_rodada...`, `test_texto_traz_a_meta...` | n/a | passou |
| Média, mediana e p75 inclusivo | `test_media_mediana_e_p75` | dia sem item (None), um item só, três itens | passou |
| PR e hora do merge no `--json` | `test_pr_e_hora_do_merge_no_json` | merge sem PR (None) e squash | passou |
| Corte `[desde, ate)` por hora do merge, fuso opcional | `test_corte_por_hora_do_merge` | limite exclusivo, só `--desde`, só `--ate`, sem fuso (TZ) | passou |
| Corte inválido sai 2 | `test_corte_invalido_sai_com_2` | ate igual e antes de desde, data inexistente | passou |
| Parada de sessão e promoção pelo histórico, união sem dupla contagem, recorte na janela | `test_horas_paradas_de_sessao_e_promocao_pelo_historico` | sobreposição, intervalo contido, virada de dia | passou |
| Parada sem fonte sai `-` | `test_sem_historico_ou_sem_linha_do_tipo_as_paradas_saem_tracinho` | sem `docs/pedidos` | passou |
| Parada sem fonte sai `-` (histórico sem linha PARADA) | `test_sem_historico_ou_sem_linha_do_tipo_as_paradas_saem_tracinho` | histórico sem o tipo; tipo com linha noutro dia dá 0 | passou (A1 fechado) |
| Data impossível em PARADA não derruba o fases | `test_parada_com_data_impossivel_cita_o_arquivo_e_segue` | mês 13, 30/02, só linhas ruins dá `-` | passou |
| Develop vermelha pelo CI | `test_horas_paradas_da_develop_vermelha_pelo_ci`, `test_develop_ainda_vermelha_conta_ate_agora` | cancelado, em andamento, sem updatedAt, vermelha em curso | passou |
| `--ci` ilegível ou ausente sai 2 | `test_ci_ilegivel_sai_com_2` | quatro formatos ruins e arquivo ausente | passou |

## Cenários e resultado real
- `PYTHONPATH=. python3 -m unittest tests.evals.test_placar` no head: `Ran 47 tests ... OK`.
- Sonda: raiz com `docs/pedidos/p.md` cujo histórico só tem "Sessão caiu" e `fases --dia 2025-03-18 --raiz <raiz>`: `horas paradas, sessão: 0 h 00 min` (esperado `-`). Mesmo resultado do review (S1).

## Vermelho antes do verde
`forge-testes --vermelho 42c2a906 --modulos test_placar` sai 2 (`módulo sem arquivo em tests/: test_placar`; o teste mora em `tests/evals/`, e `evals.test_placar` não passa no padrão de `--modulos`); sem `--modulos` ele escolheu a suíte inteira e não devolveu veredito. Prova manual, em cópia em `$TMPDIR`: HEAD com só `bin/forge-placar` da base 42c2a906.
```
PYTHONPATH=. python3 -m unittest tests.evals.test_placar   (base)
ERROR: test_horas_paradas_da_develop_vermelha_pelo_ci, test_horas_paradas_de_sessao_e_promocao_pelo_historico,
       test_media_mediana_e_p75, test_pr_e_hora_do_merge_no_json, test_sem_historico_as_paradas_saem_tracinho_e_data_invalida_sai_com_2
FAIL:  test_ci_ilegivel_sai_com_2, test_corte_invalido_sai_com_2, test_corte_por_hora_do_merge,
       test_develop_ainda_vermelha_conta_ate_agora, test_fases_e_primeira_rodada_por_item_e_total_do_dia, test_texto_traz_a_meta_e_a_primeira_rodada
Ran 47 tests ... FAILED (failures=6, errors=5)      (HEAD: Ran 47 tests ... OK)
```
Onze testes caem na base e nenhum cai no HEAD.

## Mutação
`bin/forge-mutante --processos 2 tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json` (rev 87aff761c47a): rc=0, M1 a M28 todos `morreu`, nenhum sobrevivente. As specs reescritas `bin/forge-mutante --processos 2 tests/mutantes/v0479-placar-fases{,-2,-3,-4}.json`: rc=0, 31 `morreu`. `bin/forge-mutante --cobertura --base 42c2a906`: toda condição nova de `bin/forge-placar` com mutante `coberta ... declarado, não provado`; as três linhas `sem mutante` são de `tests/evals/test_placar.py`, não de guarda. Falta o mutante do ramo de A1.

## Revalidação no head 97ef4fd1 (delta de 87aff761)
Delta lido por `forge-check parecer delta`: `bin/forge-placar`, `tests/evals/test_placar.py`, mutantes `-2` e `-4`.
- A1 fechado: sem linha do tipo, `paradas_do_historico` devolve None (`-`); o teste cobre histórico sem o tipo e tipo noutro dia (0).
- Vermelho à mão (o forge-testes não aceita o subpacote evals): `python3 -m unittest` dos dois testes novos com `bin/forge-placar` da base 87aff761: `FAIL` nos dois (`failures=2`); no HEAD `Ran 2 tests ... OK`. Árvore restaurada e limpa.
- `PYTHONPATH=. python3 -m unittest tests.evals.test_placar` no head: `Ran 48 tests ... OK`.
- `bin/forge-mutante --processos 2 --base 87aff761 tests/mutantes/v0479-meta85-placar-2.json tests/mutantes/v0479-meta85-placar-4.json`: rc=0, M9 a M16, M25 a M31 todos `morreu` (M29, M30, M31 são os do ramo de A1 e da data impossível), nenhum sobrevivente.

## Parecer
Aprovado no head 97ef4fd1. Sem achado aberto. Sem suíte local (é do CI do PR, `R-QA`).

## Revalidação (delta 97ef4fd1..f74d6dd7, E36.12)
Delta lido por `forge-check parecer delta`: `bin/forge-placar` (`fundo_demais`, `TETO_ANINHAMENTO = 64`, JSON mais fundo sai 2), `tests/evals/test_placar.py`, specs `v0479-meta85-placar-4.json` e `v0479-placar-fases-6.json` e o fragmento de changelog. O aviso do merge de 5d6d87a (fora da origin/develop local) só diz que o que veio da base conta inteiro; nada fora do domínio foi relido.

- `python3 -m unittest discover -s tests/evals -p test_placar.py -t .`: `Ran 50 tests ... OK`.
- `forge-mutante tests/mutantes/v0479-meta85-placar*.json`: 31 morreram, nenhum sobrevivente, rc 0 (uma chamada por pedido; as duas famílias rodam em separado).
- `forge-mutante tests/mutantes/v0479-placar-fases*.json`: 49 morreram, nenhum sobrevivente, rc 0.
- `forge-mutante --cobertura --base 5ae868eb`: rc 1 só por `apagada · bin/forge-placar:641(base) · itens` (mais `spec editada` nas fases-2/3/4, que não é falta).
- Linha 641 da base: `"media_min": round(sum(...)/len(itens)) if itens else None`, dentro de `dados` do `fases`. No head a média saiu dali e a guarda `if not totais: return {... None}` vive em `estatisticas()` (`bin/forge-placar:671`). Ela tem mutante, `v0479-placar-fases-3.json` M19 (dia sem item tem media None, teste `test_dia_sem_item`), que morreu nesta rodada. A linha apagada não perdeu guarda; a cobertura aponta a linha antiga porque ela deixou de existir. Julgada coberta, sem bloqueio.

Parecer mantido: aprovado, sem achados.

## Revalidação (delta f74d6dd7..d340b213, E36.16)
Delta lido por `forge-check parecer delta`: `bin/forge-placar` (guarda `fundo_demais` em `paradas_do_ci`, linha 712), `tests/evals/test_placar.py` (caso novo em `test_ci_ilegivel_sai_com_2`: 100000 colchetes abertos, rc 2, mensagem "aninhado acima de", sem Traceback, sem eco) e o mutante M32 na spec `v0479-meta85-placar-4.json`. Nada fora do domínio foi relido.

- Vermelho à mão, em cópia do HEAD com `if fundo_demais(texto):` trocado por `if False:` (o mutante M32): `python3 -I tests/evals/test_placar.py Fases.test_ci_ilegivel_sai_com_2` cai em `test_placar.py:609`, `'aninhado acima de' not found in 'forge-placar: --ci ... não é uma lista de runs legível'`. Com a guarda, o mesmo comando passa (`OK`). A guarda é o que o caso novo protege.
- `python3 -I tests/evals/test_placar.py`: `Ran 50 tests ... OK`.
- `bin/forge-mutante tests/mutantes/v0479-meta85-placar-4.json`: M25 a M32 morreram (M32 em `bin/forge-placar:712`), nenhum sobrevivente.
- Uma linha de guarda mudada no diff (712) e um mutante (M32): cobertura declarada.

Parecer mantido: aprovado, sem achados. Sem suíte local (é do CI do PR, `R-QA`).

## Revalidação (delta d340b213..89936fa3, E36.21)
Delta lido por `forge-check parecer delta` (intervalo 57a66ff4..89936fa3 no código): `bin/forge-placar` (guarda `if itens` de volta em `cmd_fases`, `estatisticas` sem a guarda `if not totais`, docstrings e cortes de linha) e o mutante M19 de `v0479-placar-fases-3.json`.

- `python3 -I tests/evals/test_placar.py`: `Ran 50 tests ... OK`.
- `bin/forge-mutante --processos 2 tests/mutantes/v0479-meta85-placar*.json`: rev=89936fa3db57, rc=0, M1 a M32 todos `morreu`, nenhum sobrevivente.
- `bin/forge-mutante --processos 2 tests/mutantes/v0479-placar-fases*.json`: rev=89936fa3db57, rc=2. 48 `morreu` (M19 em `bin/forge-placar:744` morreu no `test_dia_sem_item`, com o `de` novo `for i in itens]) if itens else dict.fromkeys(`; M20 morreu por erro do teste sob o mutante, como antes) e M34 `inválido`: `o trecho aparece 2 vezes no arquivo (precisa de exatamente uma)`. Sem veredito de M34.
- M34 (`v0479-placar-fases-6.json`, vindo da develop no #700) mira `    if fundo_demais(texto):\n        raise SystemExit(`. Desde a guarda do `--ci` (`bin/forge-placar:706`, E36.16) o trecho existe duas vezes (linhas 237 e 706); a rodada de E36.16 só rodou as specs `-4` e não pegou. Fora do delta de E36.21, mas a família `v0479-placar-fases*` pedida não fecha rc 0.
- Prova de que a guarda da linha 237 continua protegida: em cópia em `$TMPDIR`, `237: if fundo_demais(texto):` trocada por `if False:`, `python3 -I tests/evals/test_placar.py SemTeste.test_arquivo_ausente_ou_invalido_sai_com_2` cai (`FAILED (failures=1)`). O teste mata; falta só a spec apontar uma linha única.
- `bin/forge-mutante --cobertura --base 57a66ff4`: `spec editada · v0479-placar-fases-3.json`; `coberta · bin/forge-placar:744 · fases-3.json:M19 · declarado, não provado`; `apagada · bin/forge-placar:671(base) · not totais` (a guarda `if not totais` saiu de `estatisticas` e voltou como `if itens` em `cmd_fases:744`, que tem o M19; julgada coberta). Nenhuma condição sem mutante.
- Catraca local: `python3 -I tests/catraca.py` rc=0, sem violação.

## Parecer da revalidação
Reprovado no head 89936fa3 por A1 (a spec M34 não dá veredito); o código e o M19 estão aprovados. Sem suíte local (é do CI do PR, `R-QA`).

## Revalidação (delta 89936fa3..7e20ac8b, E36.24)
Delta lido por `forge-check parecer delta` (intervalo 89936fa3..7e20ac8b): só `tests/mutantes/v0479-placar-fases-6.json`, M34 com `de` único (`raise SystemExit(f"forge-placar: --prs {arq} não é JSON`, aponta `bin/forge-placar:237`). Resolve o A1.

- `bin/forge-mutante` nas 6 specs `tests/mutantes/v0479-placar-fases-*.json` (uma chamada, caminhos completos): rev=7e20ac8b8b61, rc=0, M9 a M49 todos `morreu` (M20 por erro do teste sob o mutante, como antes), M34 `morreu · bin/forge-placar:237`.
- `bin/forge-mutante` nas 3 specs `tests/mutantes/v0479-meta85-placar-*.json`: rev=7e20ac8b8b61, rc=0, M9 a M32 todos `morreu`, nenhum sobrevivente.
- Código de produção sem mudança no delta; sem suíte local (é do CI do PR, `R-QA`).

## Parecer da revalidação
Aprovado no head 7e20ac8b: A1 resolvido, nenhum achado aberto.

## Revalidação (delta 7e20ac8b..6f6aab30, E36.28)
Delta lido por `forge-check parecer delta`: `bin/forge-placar` (`hora_numerica`: o `merge` do `--json` sempre com `+00:00`), `tests/evals/test_placar.py` (teste com git falso que escreve `Z`) e a spec `v0479-meta85-placar-5.json` (M50).

- Vermelho, em cópia em `$TMPDIR` com `"merge": hora_numerica(hora)` trocado por `"merge": hora`: `python3 -I tests/evals/test_placar.py Fases.test_merge_em_utc_sai_com_deslocamento_numerico_mesmo_com_git_que_escreve_z` dá `FAILED (failures=1)`. No head: `Ran 1 test ... OK`.
- `python3 -I tests/evals/test_placar.py`: `Ran 51 tests in 17.517s`, `OK`.
- `bin/forge-mutante --processos 4 tests/mutantes/v0479-meta85-placar*.json`: rev=6f6aab30715d, rc=0, 33 `morreu`, nenhum sobrevivente.
- `bin/forge-mutante --processos 4 tests/mutantes/v0479-placar-fases*.json`: rev=6f6aab30715d, rc=0, 49 `morreu`, nenhum sobrevivente.
- Delta do M50: `base=7e20ac8b8b61245135cd495a06aaa8795bfee4d4 mb=7e20ac8b8b61245135cd495a06aaa8795bfee4d4 rev=6f6aab30715d2ae7cd6136c37cc35ed10bb59f81`, `M50 · morreu · bin/forge-placar:625`.
- Uma linha de guarda mudada (625) e um mutante (M50). Sem suíte local (é do CI do PR, `R-QA`).

## Parecer da revalidação
Aprovado no head 6f6aab30: nenhum achado aberto.
