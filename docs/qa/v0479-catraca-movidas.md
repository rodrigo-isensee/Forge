---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-catraca-movidas
commit: 6c1f86913acbbd8185b4dba9c1b7985c5f457f5b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (catraca: guarda movida, E28.1)

Escopo: `tests/catraca.py` (`regra_guardas_dos_hooks` passa as saídas por `fm.movidas`, como `forge-mutante --cobertura`), 3 testes novos em `GuardasDosHooks` e `tests/mutantes/v0479-catraca-movidas.json`. Sem suíte local: só os testes tocados, com TMPDIR; a suíte inteira é do check-run `bateria` do CI.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guarda movida de arquivo com mutante no destino passa (R-QA) | `test_guarda_movida_de_arquivo_com_mutante_no_destino_passa` | condição some em x.py e reaparece em y.py do mesmo diff | passou; vermelho na base (falha) |
| Movida sem mutante no destino barra os dois lados | `test_guarda_movida_sem_mutante_no_destino_barra` | `sem mutante` em y.py e `apagada` em x.py | passou (guarda de regressão; passa na base, esperado); morre no mutante M2 |
| Apagada de verdade segue acusada, mesmo com mutante de outra condição ao lado | `test_guarda_apagada_de_verdade_barra_com_mutante_de_outra_condicao_ao_lado` | movida não engole apagada | passou (guarda de regressão; passa na base) |

## Provas
- Classe `GuardasDosHooks` (TMPDIR, `python3 -I -m unittest discover -s tests -p test_catraca.py -k GuardasDosHooks`): `Ran 15 tests`, `OK`.
- Vermelho (cópia em TMPDIR com `tests/catraca.py` da base 2904a68a e os testes do head): `FAIL: test_guarda_movida_de_arquivo_com_mutante_no_destino_passa`; os outros dois passam na base. `bin/forge-testes --vermelho 2904a68a --modulos tests.test_catraca` (saída 0, demorou além de 5 min): `vermelho: base=2904a68ae6d3 head=6c1f86913acb`, `...test_guarda_movida_de_arquivo_com_mutante_no_destino_passa · H=ok · B=falha · prova (asserção)`, `contagem: não prova (passa na base)=368; prova (asserção)=1`.
- `bin/forge-mutante tests/mutantes/v0479-catraca-movidas.json` (rev=6c1f86913acb, saída 0): `M1 · morreu · tests/catraca.py:871`, `M2 · morreu · tests/catraca.py:873`.
- `bin/forge-mutante --cobertura --base 2904a68a`: sem condição sem mutante (só a linha `base=`/`rev=`).

## Cenários e resultado real
Diff lido contra a lista de guardas: as duas linhas novas de decisão (`fm.movidas` e a devolução por arquivo) têm um mutante cada. Nenhum bug aberto.
