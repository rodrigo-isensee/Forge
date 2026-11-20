---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-agentes-caiu-em-finito
commit: c838a467219922cc11c89680dc0aed730bebc0ef
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-agentes-caiu-em-finito (E53.1)

Código testado: `hooks/agentes.py` (`lapides_vigentes`, `autores_vigentes`) e `tests/test_agentes_interrompidos.py`. Pareceres de review e segurança trazidos por merge (head local df9b0d01, só docs além do 81408618). Sem suíte local; o check-run `bateria` do mesmo sha é do CI do PR, não citado aqui.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E53.1: `desde` não finito (10**400, -10**400, inf, -inf, nan) em lápide e autor deixa o estado ilegível | `test_lapide_e_autor_com_numero_nao_finito_deixam_o_estado_ilegivel` | máximo, infinito, nan | passou; vermelho na base (falha por asserção) |
| Valores finitos seguem o prazo; item que não é registro ou sem id válido é ignorado | `test_lapide_e_autor_finitos_seguem_o_prazo` | prazo vencido, item inválido | passou; não prova na base (comportamento preservado, esperado) |
| O disparo recusa e não regrava o estado | `test_disparo_com_lapide_ou_autor_enorme_e_recusado_sem_regravar_o_estado` | estado intacto | passou; vermelho na base (falha por asserção, após c838a467) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_agentes_interrompidos.py`: Ran 29 tests, OK (head c838a467).
- Revalidação no head c838a467 (delta: só `tests/test_agentes_interrompidos.py`, o disparo agora captura OverflowError e falha por asserção). Vermelho (`bin/forge-testes --vermelho 5ccac0bf --modulos test_agentes_interrompidos`): `contagem: não prova (passa na base)=27; prova (asserção)=2`, rc=0; os dois testes de lápide/autor e de disparo provam. A1 resolvido.
- Mutação, uma spec por pedido (`bin/forge-mutante`): `v0479-agentes-caiu-em-finito.json` M1 a M6 morreram (reexecutada no head c838a467) (M5 e M6 por erro do teste declarado, que passa sem o mutante), rc=0; `trava-agente-morto-3.json` M17 a M24 morreram, rc=0; `v047-h2-autor-fica.json` M1 a M8 morreram, rc=0.
- `forge-mutante --cobertura --base 5ccac0bf`: as linhas de guarda mudadas (568, 570, 573, 681, 684, 687) saem `coberta`, sem condição sem mutante.
- Nenhum bug de produto: a correção de código se comporta conforme o pedido. Sem bloqueio aberto.
