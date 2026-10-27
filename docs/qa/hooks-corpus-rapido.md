---
tipo: qa
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 2c14a56245b9dc4060903073c5e4e8227aecd6b3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: hooks-corpus-rapido

Escopo: revalidação 2 do pedido HOOKS-CORPUS-RAPIDO (CorpusHeredocVoltaUnica em 3 módulos, decisão em lote com teste de equivalência, teto de 225 s por módulo, mapa do `bin/forge-testes`). Base 363ceee; delta desde 978d2d6 (e 1364bc0, o parecer anterior): `bin/forge-testes`, `tests/mutantes/hooks-corpus-rapido.json`, `tests/test_hooks_volta_corpus.py`, `tests/test_testes_tocados.py`. Roda junto com review e segurança (ACELERA-RODADA "A", item 4).

## Achados

## Revalidação dos achados anteriores
- A1 (mapa sem teste, bloqueante): resolvido. `tests/mutantes/hooks-corpus-rapido.json` declara M1 a M6; `forge-mutante` mata os seis (saída abaixo). O teste `test_modulos_da_volta_unica_rodam_onde_o_test_hooks_roda` guarda as 5 regras do mapa. Conferência da lista contra o diff do `bin/forge-testes`: linhas `+ VOLTA_UNICA` (hooks/doutor.py, hooks/, stacks/, .claude-plugin/, FORGE_CHECK) = M1 a M5; a entrada nova `test_doutor_relogio` em FORGE_CHECK não estava na lista, e eu a mutei à mão (X1: tirar a entrada) e ela morre em `MapaDoForgeCheck`. Linha de guarda sem mutante: nenhuma.
- A2 (tempo): critério trocado pela DECISÃO TÉCNICA 13:13 (cada módulo <= 225 s); cumprido (tempos abaixo).

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 mesmo conjunto de textos | `DECIDIDOS` do apoio, comparado com 363ceee | 6 testes, 79 a 7152 textos | passou (idênticos) |
| E1 decisão em lote = hook real | `test_decisao_em_lote_igual_ao_subprocesso_do_hook` | códigos 0 e 2 | passou |
| E1 driver do lote igual ao `__main__` dos hooks | `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` | CRITICO, argumentos, pasta do hook | passou; M6 morre |
| E2 classe em 3 módulos | `test_hooks_volta_corpus/_lancador/_propriedades` | n/a | passou |
| E3 teto por módulo 225 s | `test_pesos_teto` (2 testes) | 225 e 225,1 s | passou |
| Mapa do `bin/forge-testes` | `test_testes_tocados` (81 testes) | 5 regras + FORGE_CHECK (25 módulos) | passou; M1 a M5 e X1 morrem |

## Execução (CI=true, </dev/null, worktree em 2c14a56)
- test_hooks_volta_corpus: 15 testes, OK, 52 s
- test_hooks_volta_lancador: 20 testes, OK, 59 s
- test_hooks_volta_propriedades: 8 testes, OK, 46 s
- test_hooks: 51 testes, OK, 92 s
- test_pesos_teto: 2 testes, OK, 0 s
- test_testes_tocados: 81 testes, OK, 14 s
- Todos abaixo de 225 s. Os três módulos juntos, numa só execução: 43 testes, OK, 130 s.

## Mutação (saída de `CI=true bin/forge-mutante tests/mutantes/hooks-corpus-rapido.json`, rc=0)
```
forge-mutante: pedido=hooks-corpus-rapido rev=2c14a56245b9 spec=bab279f96f5ad87521a2d3346e6e8719c0dd35f70b21414502b8035264200b76
M1 · morreu · bin/forge-testes:97
M2 · morreu · bin/forge-testes:101
M3 · morreu · bin/forge-testes:106
M4 · morreu · bin/forge-testes:107
M5 · morreu · bin/forge-testes:74
M6 · morreu · tests/apoio_volta_unica.py:343
```
X1 (QA, spec em `$TMPDIR`): `X1 · morreu · bin/forge-testes:70`.

## Textos decididos (corpus não encolheu)
`apoio_volta_unica.BaseVoltaUnica.DECIDIDOS` no head, mesmos números medidos em 363ceee (parecer anterior, por conteúdo): test_lancador_fora_da_tabela_com_efeito_real 79; test_propriedade_da_reavaliacao_com_marcador 7152; test_propriedade_do_alfabeto_de_escapes_com_marcador 936; test_propriedade_do_alfabeto_de_opcoes_do_lancador 1782; test_propriedade_do_lancador_que_divide_texto_com_marcador 2268; test_t9b_oraculo_do_gatilho 3576. O apoio e os módulos lançador e propriedades não mudaram desde 978d2d6; o delta do corpus só soma um teste.

## Vermelho antes do verde
O teste novo do delta (driver do lote) tem o vermelho na mutação M6; os do mapa, em M1 a M5. `forge-testes --vermelho` não foi pedido.

## PA-7
`docs/engineering/achados-recorrentes.md` sem achado registrado: nada a conferir.

## Notas
Fora do escopo e ambiental: o `test_forge` falha 4 testes em cópia sem `.git` e sem rede, iguais com e sem o diff (parecer anterior).
