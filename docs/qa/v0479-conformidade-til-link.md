---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 481d2855dbf0acc7c9fc9ec09d35ad8bf5d87e24
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: CONFORMIDADE-TIL-E-LINK (E80.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Til e variável em `$(…)`/crase como alvo (`CONFORMIDADE-TIL-EM-SUBSTITUICAO`) | `test_hooks.Hooks.test_fixtures_do_til_em_substituicao` (tilsubst-*: 7 bloqueiam, 4 liberam) | pasta protegida × vizinho × valor que o hook não sabe (`pwd`, ambiente) | passou no head; 7 de 7 `bloqueia` caem na base |
| Link criado por cópia na linha (`CONFORMIDADE-LINK-POR-COPIA`) | `test_hooks.Hooks.test_fixtures_do_link_por_copia` (linkcopia-*: 9 bloqueiam, 2 liberam) | `cp` sem `-a` e `tar -t` seguem livres | passou no head; 9 de 9 `bloqueia` caem na base |
| `tar -x` com estado na linha agora recusa | `test_conformidade_verde.EstadoDoAgentesNoClone.test_tar_x_na_linha_que_cita_o_estado_recusa` | os 2 casos tirados de "libera" mudaram de lado de propósito | passou no head, falha na base |
| Corpus dentro do teto | `test_hooks_volta_corpus.test_corpus_nos_dois_hooks` | contagem de trabalho, não cronômetro | passou (OK, 102 s) |

## Cenários e resultado real
Vermelho antes do verde. `forge-testes --vermelho adc52def… --modulos test_hooks,test_conformidade_verde --prazo 1500`:
- `test_conformidade_verde`: o único teste novo (`test_tar_x_na_linha_que_cita_o_estado_recusa`) sai `H=ok · B=falha · prova (asserção)`; os demais, `não prova (passa na base)`.
- `test_hooks`: `sem veredito (prazo, sinal ou executor sem registro em B)`, com `H 1012.6 s, B 1500.1 s`. Pelo `forge-testes`, esse módulo não dá vermelho; o veredito saiu da forma de projeto, numa cópia do HEAD com `hooks/conformidade.py` da base:
  `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_til_em_substituicao -k test_fixtures_do_link_por_copia` → `Ran 2 tests in 7.105s · FAILED (failures=16)`: os 16 casos `bloqueia` (7 tilsubst, 9 linkcopia) com `AssertionError: 0 != 2`; nenhum caso `libera` cai. No head, o mesmo comando dá `Ran 2 tests in 8.218s · OK`.

Mutantes (`bin/forge-mutante tests/mutantes/v0479-conformidade-til-link.json tests/mutantes/v0479-conformidade-til-link-2.json --processos 3`), rc=0, 11 de 11 mortos:
`T1 T2 (1692) T3 (1695) T5 (1694) T4 (4340)` e `L1 (3835) L2 L3 (3836) L4 L5 (3837) L6 (3838)`, todos `morreu`, nenhum equivalente.
`forge-mutante --cobertura --base adc52def…`: as 4 condições Python mudadas (1692, 1694, 1695, 4341) saem `coberta · declarado, não provado`; essas mesmas 11 rodadas provam. As alternativas da regex `CAMINHO_TROCADO_NA_LINHA` são o que L1 a L6 mutam, uma por ramo (`cp`, `rsync`, `tar x`, `tar` com `-x`/`--extract`/`--get`, `symlink(`).
`spec editada · tests/mutantes/v0479-conformidade-trilha-13.json` (4 linhas): só a linha de referência deslocou; fora do recorte.

Falso bloqueio: `linkcopia-cp-preserva-libera` (`cp -p`) e `linkcopia-tar-lista-libera` (`tar -t`) liberam no head; na leitura da regex, `cp -v/-f/-n/-u/--preserve`, `tar -tvf`, `tar -cf` e `--exclude` não casam. O que passou a recusar são os dois `tar -x` que o `test_conformidade_verde` moveu de "libera" para "recusa" (mudança declarada no pedido).

Limites do QA: suíte inteira não rodada (só os módulos do recorte, `R-TETO`). O módulo `test_hooks` inteiro não deu veredito local no prazo; as duas funções novas foram rodadas isoladas, e o resto do módulo fica para a prova do check-run `bateria` do mesmo sha no CI do PR.
