---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-teste-carga
commit: 3da64e122b71a831b97c1f33987950f353a0e5e7
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 · E5.2 (testes de tempo pela carga)

Branch: melhoria/v047-teste-carga. Head revisado: 3da64e12. Sem PR e sem check-run `bateria` ainda (máquina com carga 12 a 17 em 12 CPUs); rodei só os testes afetados e leves.

## Achados
- A1 (bloqueante) tests/test_hooks.py:636 · mutante manual `os.getloadavg()[0]` -> `[2]` (carga de 15 min) sobreviveu: nenhum teste lê a carga real, só passam `carga` explícita. Um teste com `os.getloadavg` mockado em `(6.0, 0.0, 0.0)` e 4 núcleos esperando 1.5 o mata (verifiquei).
- A2 (bloqueante) tests/test_hooks.py:639 · mutante manual `nucleos or nucleos_do_processo() or 1` -> `nucleos or 1` sobreviveu: o caminho sem `nucleos`, o que os dois testes de tempo usam, nunca roda. Mockar `nucleos_do_processo` em 4 e chamar `fator_de_carga(6, None)` esperando 1.5 o mata (verifiquei).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fator = min(2, max(1, carga/núcleos)) | `test_fator_segue_a_carga_por_nucleo_entre_1_e_2` (0.2, 4, 6/4, 8/4 e 400/4) | piso 1, teto 2, carga igual a núcleos | passou; mortos M-piso, M-teto, M-por-núcleo, M-min/max |
| Leitura da carga que falha dá 1 | `test_carga_ilegivel_deixa_o_limite_de_sempre` | OSError | passou; morto M-retorno e M-exceção |
| Limite do corpus escala, teto 2x ainda pega regressão | `test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha` | 0.5, 12/8, 999/8 | passou; 4 mutantes do spec mortos |
| Prazo do gh pendurado escala e o defeito (`sleep 30`) continua barrado | `Hooks.test_rotulo_so_dono_gh_pendurado_...` | teto 9 s x 2 = 18 s < 30 s | passou em 5,9 s; mutante `* 0` morto |
| Leitura de 1 min e núcleos padrão | nenhum | n/a | SEM TESTE (A1, A2) |

Teto de 2x: o corpus tem limite de 90 s por trabalhador, o máximo é 180 s; o gh vai a 18 s contra os 30 s do `sleep 30`. Regressão acima do dobro falha em qualquer carga. Ressalva: o fio `limite_de_cpu_do_corpus_sob_carga()` em `test_corpus_nos_dois_hooks` não tem teste próprio (o corpus leva uns 270 s); lido por revisão, correto.

## Vermelho antes do verde
```
vermelho: base=9b2c6474cc1e head=ddc19d86616b módulos=test_medida_cpu (restrito por --modulos)
revertidos à base: changelog.d/v047-teste-carga.md, tests/apoio_volta_unica.py
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_carga_ilegivel_deixa_o_limite_de_sempre · H=ok · B=erro · prova (API ausente)
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_fator_segue_a_carga_por_nucleo_entre_1_e_2 · H=ok · B=erro · prova (API ausente)
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha · H=ok · B=erro · prova (API ausente)
contagem: não prova (herdada da base)=5; prova (API ausente)=3
```
O head desse comando é ddc19d86 (3da64e12 mais o meu commit de spec, que só acrescenta `tests/mutantes/v047-teste-carga.json`). A execução sem `--modulos` estourou 500 s sob carga e não vale como vermelho.

## Mutantes da fórmula
`bin/forge-mutante` recusa mutar arquivo de teste (`arquivo de teste não se muta`), e `fator_de_carga` mora em `tests/test_hooks.py`. A spec `tests/mutantes/v047-teste-carga.json` traz só os 4 mutantes do `limite_de_cpu_do_corpus_sob_carga` (em `tests/apoio_volta_unica.py`):
```
forge-mutante: pedido=v047-teste-carga rev=ddc19d86616b
M1 · morreu · tests/apoio_volta_unica.py:55
M2 · morreu · tests/apoio_volta_unica.py:55
M3 · morreu · tests/apoio_volta_unica.py:55
M4 · morreu · tests/apoio_volta_unica.py:55
```
Os mutantes de `fator_de_carga` fiz à mão numa cópia, rodando `tests.test_medida_cpu` (árvore restaurada em seguida):

| Mutante | Resultado |
|---|---|
| TETO 2 -> 3 | morto (2 falhas) |
| `max(1.0, ...)` -> `max(0.5, ...)` | morto (2) |
| `carga / nucleos` -> `carga` | morto (3) |
| `except OSError: return 1.0` -> `return 2.0` | morto (1) |
| `min(` -> `max(` | morto (5) |
| `except OSError` -> `except ValueError` | morto (1) |
| `getloadavg()[0]` -> `[2]` | SOBREVIVEU (A1) |
| `nucleos or nucleos_do_processo() or 1` -> `nucleos or 1` | SOBREVIVEU (A2) |

## Cenários e resultado real
- `python3 -m unittest tests.test_medida_cpu`: 8 testes, OK.
- Teste do gh pendurado: OK em 5,9 s.
- Não rodei o corpus nem a suíte: sem PR e com a máquina sob carga; o CI do PR cobre.
