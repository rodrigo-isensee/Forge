---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-reserva-retomada
commit: 768c27efebe14607a881fd4f60b3395fc7444bf5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-h2-reserva-retomada (E87.4)

Escopo: H2-RESERVA-DA-RETOMADA-PRAZO em `hooks/agentes.py` (`prazo_do_registro`, `escrita_do_autor`, `iniciar` com `autores`), 2 fixtures `autor-retomado-inicio-tardio-*`, 3 testes em `tests/test_hooks_agentes_autor.py`, specs de mutantes. Sem suíte local; rodados só o módulo do autor e as fixtures da pasta `agentes`.

## Achados
- A1 (recomendado) tests/hooks/agentes/autor-retomado-inicio-tardio-libera-no-fim.json:1 · passa também na base (guarda do lado oposto: a reserva refeita cai no SubagentStop), não prova o vermelho; quem prova é a `reserva-de-novo`. Vira cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Retomado que inicia após RESERVA_S reserva de novo as branches | fixture `autor-retomado-inicio-tardio-reserva-de-novo` (via `PeloHook.test_fixtures_do_pedido`) | início tardio | passou; vermelho na base (`0 != 2`) |
| A reserva refeita cai no SubagentStop | fixture `autor-retomado-inicio-tardio-libera-no-fim` | fim do autor | passou; na base também passa (A1) |
| Prazo único por registro (sem início, RETOMADA, iniciado; expira menor que RESERVA_S) | `Autores.test_prazo_unico_por_registro` | prazo curto x longo | passou; vermelho na base (API ausente) |
| Hora da recusa usa o prazo do registro | `Autores.test_hora_da_recusa_da_retomada_usa_o_prazo_curto` | RETOMADA com expira longo | passou; vermelho na base (asserção) |
| Id fora de `autores` não ganha branch | `Autores.test_inicio_sem_autor_nao_reserva_branch` | id sem autor | passou; na base erro de assinatura (`iniciar` sem `autores`): sem veredito do `forge-testes` |

## Vermelho antes do verde
`bin/forge-testes --vermelho ad3b3b6f --modulos tests.test_hooks_agentes_autor` (rc 2 só pelo item sem veredito acima):
```
vermelho: base=ad3b3b6fb674 head=610ba4ce1568 módulos=test_hooks_agentes_autor (restrito por --modulos)
revertidos à base: changelog.d/v0479-h2-reserva-retomada.md, docs/hooks-fixtures.md, docs/hooks.md, hooks/agentes.py
Autores.test_hora_da_recusa_da_retomada_usa_o_prazo_curto · H=ok · B=falha · prova (asserção)
Autores.test_inicio_sem_autor_nao_reserva_branch · H=ok · B=erro · sem veredito
Autores.test_prazo_unico_por_registro · H=ok · B=erro · prova (API ausente)
PeloHook.test_fixtures_do_pedido · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=9; prova (API ausente)=1; prova (asserção)=2; sem veredito=1
```
Fixtures isoladas na base (cópia de `git archive ad3b3b6f`): com as duas, `FAIL ... fixture='agentes/autor-retomado-inicio-tardio-reserva-de-novo'` (`0 != 2`); só com `libera-no-fim`, OK (A1).

## Mutantes
- `bin/forge-mutante tests/mutantes/v0479-h2-reserva-retomada.json`: M1 a M4 morreu, rc 0.
- `bin/forge-mutante tests/mutantes/v047-h2-autor-fica-3.json`: M17 a M25 morreu (M17 com `(erro)`, já existente), rc 0. M22 e M23 alinhados ao novo texto e com teste novo.
- `bin/forge-mutante --ids I55 tests/mutantes/v0432-integracao-4.json`: I55 morreu (só o id editado; a spec inteira não foi rerrodada).
- `--cobertura --base ad3b3b6f`: 4 condições `coberta` (366, 371, 746, 1302), 2 `apagada` (base), nenhuma sem mutante; `--conferir --base ad3b3b6f`: trecho de cada spec no lugar.

## Skip
`grep -iE "skip|expectedFailure"` em `tests/test_hooks_agentes_autor.py`, nas duas fixtures novas e nas linhas adicionadas do diff: vazio.

## Revalidação (E87.8, head 768c27ef)
Delta: só o bloco `isentas` em `tests/mutantes/v0479-h2-reserva-retomada.json` (duas guardas apagadas: `hooks/agentes.py:982(base)` e `:745(base)`).
- `bin/forge-mutante --cobertura --base origin/develop`: rc=0, `base=dcf8486f… rev=768c27ef…`; 366, 371, 746 e 1302 cobertas; as duas `isenta` com motivo que confere (366 e 746 têm M23/I55/M22); nenhuma guarda sem mutante.
- `bin/forge-mutante tests/mutantes/v0479-h2-reserva-retomada.json`: rc=0; M1, M2, M3 e M4 `morreu`.
Parecer segue aprovado.

## Execução
`python3 -I -m unittest discover -s tests -p test_hooks_agentes_autor.py`: 13 testes, OK (inclui as fixtures `autor-*` da pasta `agentes`). Suíte completa: check-run `bateria` do CI do PR, não rodada aqui.
