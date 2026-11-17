---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-g4-medida-idioma
commit: bdbb45cd5235d601649e3bbdd889bb8b4aaae4cb
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 (SIEG-G4, medida de idioma da mensagem ao dono em `hooks/meta.py`, E2.700)

Escopo `5b1aacd5...675cf7a1`: `hooks/meta.py`, `tests/test_meta.py` (classe `IdiomaDoDono`), `tests/mutantes/v047-g4-medida-idioma.json`, fragmento de changelog. Sem parecer anterior: completo. O pedido não traz `CA-n`; as obrigações são as da E2.683 (a medida grava `idioma`, `idioma_do_dono` e `outro_idioma`; só mede, nunca bloqueia) e `R-QA`. Sem PR nem check-run `bateria` para o sha: a prova é a execução local dos cenários.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem configuração, o dono fala pt; inglês e espanhol são acusados | `test_sem_configuracao_o_dono_fala_portugues_e_ingles_e_acusado` | raiz nula, sem arquivo, sem chave, config que não é objeto | passou |
| O idioma do dono vem do `.forge/config.json` | `test_idioma_vem_da_configuracao_do_projeto` | pt acusado quando o dono é en | passou |
| Código sem lista ou valor que não é texto: sem medida, sem acusação | `test_idioma_sem_lista_nao_mede_nem_acusa` | `fr`, lista no lugar do texto | passou |
| Mensagem curta, mista ou só em código/citação: sem idioma, sem acusação | `test_mensagem_curta_mista_ou_em_codigo_fica_sem_idioma_e_nao_e_acusada` | abaixo do mínimo (2 de 3), empate, bloco e citação | passou |
| Listas de palavras disjuntas | `test_listas_de_palavras_sao_disjuntas` | 3 listas ao menos | passou |
| A medida recebe a raiz e o Stop segue (S6 só mede) | `Jargao.test_stop_bloqueado_ainda_mede_e_sai_com_2`, `test_medida_que_falha_nao_troca_o_stop` | rc 2 preservado | passou |

## Execução
- `TMPDIR=... python3 -m unittest tests.test_meta` no clone: `Ran 20 tests in 7.116s`, OK.

## Vermelho antes do verde
`forge-testes --vermelho 5b1aacd5... --modulos tests.test_meta`: `vermelho: base=5b1aacd5068f head=675cf7a1f906`; revertidos à base `changelog.d/...md` e `hooks/meta.py`. Contagem: `prova (API ausente)=2; prova (asserção)=1; sem veredito=4; não prova (passa na base)=13`, saída 2. Os 4 "sem veredito" são os testes de `IdiomaDoDono` que erram na base (`medir_mensagem` sem o parâmetro `raiz`, o campo `idioma` não existe) e a ferramenta não os classifica; os 3 com veredito provam (`test_listas_de_palavras_sao_disjuntas`, `test_stop_bloqueado_ainda_mede_e_sai_com_2`, `test_medida_que_falha_nao_troca_o_stop`) e nenhum cai no HEAD (H=ok em todos). Os 13 que passam na base são testes antigos de jargão, não deste item. O vermelho dos 4 sem veredito: o `erro` na base é a ausência da API nova, não problema de preparação.

## Mutação (`forge-mutante`)
Lista conferida contra o diff com `forge-mutante --cobertura --base 5b1aacd5...`: toda condição Python mudada tem mutante (`meta.py:198,200,208,209,210,212,231`). Rodada, `--processos 2`:

```
forge-mutante: pedido=v047-g4-medida-idioma rev=675cf7a1f906 spec=c6e4bf08...
M1 a M8 · morreu (8 de 8)
```

Nenhum sobrevivente nem equivalente.

## Revalidação (delta 675cf7a1..bdbb45cd)
`forge-check parecer delta` lista só `tests/mutantes/v047-jargao-medida-4.json`: o `de` do M27 passou de `medir_mensagem(hook)` a `medir_mensagem(hook, raiz)`, para casar com o código. Reteste:

```
$ bin/forge-mutante tests/mutantes/v047-jargao-medida-4.json
forge-mutante: pedido=v047-jargao-medida rev=bdbb45cd5235 spec=b1e0fdf6...
M25 · morreu · hooks/meta.py:229
M26 · morreu · hooks/meta.py:243
M27 · morreu · hooks/meta.py:246
M28 · morreu · hooks/meta.py:227
$ python3 -m unittest tests.test_forge_mutante.ConferirTodas
Ran 4 tests in 11.947s  OK
```

M27 morre; sem sobrevivente. Resto do parecer anterior segue valendo (nenhum arquivo de produção mudou no delta). Parecer aprovado.

## Bugs
Nenhum aberto (crítico 0, alto 0, médio 0, baixo 0).
