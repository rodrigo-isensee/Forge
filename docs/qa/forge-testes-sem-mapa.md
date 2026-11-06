---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-sem-mapa
commit: aec509298678b0987cc2b3943ca07d9c6a97a584
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: forge-testes-sem-mapa (cartão 15)

Escopo: `bin/forge-testes` com CAMINHO de módulo de teste existente sem entrada no MAPA (FORGE-TESTES-SEM-MAPA). Base b45e40a. Suíte completa fica com o CI/pre-push (D-5); aqui rodou só tests/test_testes_tocados.py.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| FORGE-TESTES-SEM-MAPA | CT-01 `--listar tests/test_changelog.py` | módulo existente sem mapa | passou: modo dirigido, só test_changelog, aviso "sem mapa" |
| FORGE-TESTES-SEM-MAPA | CT-02 `--listar tests/nao_existe.py` | caminho inexistente | passou: falha fechado, suíte completa |
| FORGE-TESTES-SEM-MAPA | CT-03 módulo + bin/forge-changelog | pedido misto | passou: suíte completa, sem aviso de "sem mapa" |
| regressão | CT-04 tests/test_testes_tocados.py | n/a | passou: 88 testes, OK |

## Cenários e resultado real
`python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em aec5092: Ran 88 tests, OK. Cenários CT-01 a CT-03 rodados à mão na worktree da branch (rc 0 nos três, saídas acima). Sem mutante declarado neste pedido (sem spec em tests/mutantes/). Vermelho antes do verde: a rodada de `--vermelho` não concluiu neste ambiente (processo encerrado, rc 144), então não conta; a ausência do aviso na base foi conferida por comparação direta (b45e40a não tem `modulos_sem_mapa`).

Parecer: aprovado sobre aec5092.
