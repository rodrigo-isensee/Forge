---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v0479-vermelho-evals
commit: 05ee66764cc0008dfd77dd7481e9bec525ae0a19
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 E13.41 (VERMELHO-TESTS-EVALS, retomada E13.32), delta do merge da develop 9479650b

## Achados
- A1 (bloqueante) tests/mutantes/forge-testes-modulos-nome.json:1 · M1 e M2 têm o `de` na linha antiga de `modulos_pedidos` (bin/forge-testes:1287 mudou); test_toda_spec_do_forge_confere_com_a_fonte falha no CI (parte 4/5) e local. Alinhe a spec no mesmo commit.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Merge não perde o lado da branch | diff de `bin/forge-testes` e `tests/test_testes_tocados.py`: delta do merge contra o 1.º pai igual ao da develop (004ce869..9479650b), 392 e 474 linhas | n/a | passou, idênticos |
| Merge não perde o lado da develop (#960) | diff do merge contra 9479650b em `bin/forge-testes`: só as 23 linhas do patch | n/a | passou |
| Módulo de pacote, caminho e prefixo `tests.` no `--vermelho` | testes do E48.4 em `tests/test_testes_tocados.py` (5 provas por asserção) | pacote aninhado, grafia torta | passou; ver M1-M11 |
| Specs de mutantes conferem com a fonte | `test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` | linha de guarda movida | FALHOU (A1) |

## Cenários e resultado real
- `bin/forge-mutante tests/mutantes/vermelho-tests-evals.json` no head: `rev=05ee66764cc0`; M1 a M11 todos `morreu` (M1/M2 :144, M3 :1287, M4 :942, M5 :142, M6/M10 :940, M7 :872, M8 :903, M9 :900, M11 :942); sem sobrevivente.
- `forge-testes --vermelho 004ce869d641 --modulos evals.test_placar` (módulo de pacote real, rc=0): `vermelho: base=004ce869d641 head=05ee66764cc0 módulos=evals.test_placar (restrito por --modulos)`; `tests.evals.test_placar.CiPrimeira.test_cancelada_nao_conta_como_verde_nem_vermelha · H=ok · B=falha · prova (asserção)` e demais da classe iguais.
- `--modulos evals.test_regressao_forma`: roda 31 testes nas duas cópias; `não prova (passa na base)=31`, rc=1 (esperado: módulo não mudado no diff).
- Comportamento igual ao aprovado em 20/11: o delta do merge não altera a lógica do patch.
- A1 reproduzido local: `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k test_toda_spec_do_forge_confere` dá `FAILED (failures=1)`, listando `forge-testes-modulos-nome.json: M1` e `M2`.
- O teste que cai já existia; o patch muda a linha que a spec antiga (v0432) cita e a spec não foi alinhada.

## CI
- ci: 05ee66764cc0008dfd77dd7481e9bec525ae0a19 NÃO verde. PR #970, `gh pr checks`: `suíte (python 3.12, parte 4/5)` fail e `bateria` fail (consequência); partes 1, 2, 3 e 5, `bateria (pareceres)`, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `catraca`, `catraca (conferência)` e instalação passam.
