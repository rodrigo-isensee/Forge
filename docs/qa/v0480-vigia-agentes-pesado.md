---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: 25c60be778696f894a488b8a266d5874db63ef9b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: VIGIA-AGENTES-PESADO (v0478 E172.24, PR #859, obrigação E172.3)

## Critério → teste → resultado
| Obrigação (E172.3) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `agentes` e `pesado` recusam com R-TETO o disparo/tarefa cujo prazo vence no PreToolUse, no projeto e no clone do Forge | `test_fixtures_do_vigia_agentes_pesado` (6 fixtures `vigia-prazo-*`) | projeto × clone | passou |
| Fora do PreToolUse (SubagentStop, PostToolUseFailure) só registra no `erros.log` | fixtures `vigia-prazo-fim-libera`, `vigia-prazo-falha-libera`; `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera` | evento | passou |
| Prazo do hook (8 s / 290 s) vale no lugar dos 3 s; passo logo abaixo libera, no prazo recusa; saída desarma | `test_prazo_do_hook_pelo_relogio_falso` | prazo-0,1 s e prazo exato | passou |
| Prazo abaixo do `timeout` do hooks.json com folga de 2 s e acima do piso | `test_prazo_de_cada_hook_abaixo_do_timeout_do_hooks_json` | timeout−2 | passou |
| Índice de fixtures em dia | `indice-fixtures.py --conferir` | contagem | passou (rc 0) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks_volta_propriedades.py`: 12 testes, OK. `test_hooks.py -k test_vigia_prazo_trava`: 1 teste, OK. Suíte inteira não rodada (CI do PR).
- Sem `skip`/`expectedFailure` novos no diff (o único `skipTest` do módulo, linha 101, é anterior).
- Conferência do diff: o escopo bate (3 hooks, 6 fixtures, 2 módulos de teste, spec de mutantes, índice, fragmento). Observação sem defeito: nos eventos Post, o prazo de 290 s do `pesado` passa do timeout de 10 s, então o vigia nunca dispara ali; o efeito é nulo.

## Vermelho antes do verde
```
forge-testes --vermelho f82c7cc558ae --modulos test_hooks_volta_propriedades --prazo 500
revertidos à base: changelog.d/…, docs/hooks-fixtures.md, hooks/_comum.py, hooks/agentes.py, hooks/pesado.py
VigiaAgentesPesado.test_fixtures_do_vigia_agentes_pesado · H=ok · B=falha · prova (asserção)
VigiaAgentesPesado.test_prazo_de_cada_hook_abaixo_do_timeout_do_hooks_json · H=ok · B=erro · prova (API ausente)
VigiaAgentesPesado.test_prazo_do_hook_pelo_relogio_falso · H=ok · B=erro · prova (API ausente)
contagem: não prova (passa na base)=9 (testes antigos do módulo); prova (API ausente)=2; prova (asserção)=1
```
O teste alterado de `test_hooks.py` não entrou nessa rodada (módulo fora de `--modulos`); a mudança dele é a recusa sem marcador no PreToolUse, coberta também pelas fixtures acima (vermelhas na base).

## Mutantes
```
forge-mutante: pedido=v0480-vigia-agentes-pesado rev=e54654c90628 spec=aedbda05...
M1 morreu · hooks/_comum.py:2861
M2 morreu · hooks/_comum.py:2863
M3 morreu · hooks/_comum.py:2900
M6 morreu · hooks/_comum.py:2900
M4 morreu · hooks/agentes.py:1426
M5 morreu · hooks/pesado.py:466
```
6 de 6 mortos. `forge-mutante --cobertura --base f82c7cc558ae`: as 4 condições de `_comum.py` mudadas têm mutante declarado e morto; a linha `apagada · _comum.py:2894(base)` é a condição removida (`and critico is not None`), coberta pelo M3. Nas linhas de `agentes.py`/`pesado.py` as trocas são M4/M5.

## Revalidação por delta (v0478 E172.36, head 25c60be7)
`forge-check parecer delta` lista no domínio: `tests/mutantes/v0455-prazo.json`, `tests/mutantes/v0480-vigia-trava-critica.json`, `tests/test_hooks_volta_propriedades.py` (e54654c9..25c60be7). Só teste e spec de mutantes mudaram; o código de produção do delta é nulo.
- Os trechos `de`/`para` de P11 (v0455-prazo) e M1 (trava-crítica) acompanham as linhas atuais de `hooks/_comum.py` (a guarda do vigia sem o marcador); o teste do `git init` passou a usar `sem_manutencao` (ponto único), sem mudar o que o teste prova.
- `test_hooks_volta_propriedades.py`: 12 testes, OK. `test_hooks.py -k test_vigia_prazo_trava -k test_prazo_do_merge`: 3 testes, OK (uma execução simultânea à rodada de mutantes deu 1 falha por carga; repetida sozinha, verde; sem reprodução, não vira achado).
- Suíte inteira não rodada (CI do PR).
```
base=e54654c906288892ddc3462ee4503c55f848692f rev=25c60be77869
v0455-prazo: P1..P13 morreu (13 de 13)
v0480-vigia-trava-critica: M1..M5 morreu (5 de 5; M2 e M4 por erro do teste declarado, com controle verde)
v0480-vigia-agentes-pesado: M1..M6 morreu (6 de 6)
```
Sem sobrevivente, sem achado, sem bug novo. Parecer anterior (aprovado) mantido.
