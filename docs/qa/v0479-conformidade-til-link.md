---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 9451e78c19bbbe44b640c04ff1f6a135e0b41767
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

## Revalidação no head 9451e78c (E80.8, delta 481d2855..9451e78c)
Vermelho antes do verde (forma de projeto, cópia do head com `hooks/conformidade.py` de 481d2855, `test_hooks -k test_fixtures_do_til_em_substituicao -k test_fixtures_do_link_por_copia`): `Ran 2 tests · FAILED (failures=36)` · `rc=1`; no head `Ran 2 tests · OK` · `rc=0`. As fixtures novas do delta são 44 (o brief diz 47; `git diff --name-status` dá 44 `A`, nenhuma mudada): 36 `bloqueia` caem na base, uma por uma; as 8 `libera` (`cp-longa-comum`, `python-sem-controle`, `unzip-lista-sem-controle`, `for-sem-vigor`, `home-vizinho`, `interpretador-sem-vigor`, `reatribuicao-outra-pasta`, `script-com-vigor`) passam na base de propósito: guardam o lado livre.
Verde no head: `test_conformidade_verde` OK (`rc=0`); `test_hooks_volta_corpus` `Ran 33 tests in 165.269s · OK` (`rc=0`).
Mutantes, 63 de 63 mortos, nenhum equivalente, `rc=0` em cada chamada (uma por pedido): `tests/mutantes/v0479-conformidade-til-link.json`, `-2`, `-3`, `-4` (32 mortos); `tests/mutantes/v047-conformidade-cf1.json`, `v047-destino-opaco-10.json`, `v047-destino-opaco-13.json` (24 mortos); `tests/mutantes/v0479-conformidade-trilha-13.json` (7 mortos).
Realinhamento das specs cf1, destino-opaco-10 e -13 e trilha-13: só o trecho `de` acompanhou o código novo e o `para` mantém o efeito (desligar o ramo); os `testes` que devem cair são os mesmos; os mutantes mataram, sem enfraquecimento.
Sem `skip` novo: o delta dos testes não acrescenta `skip`, `skipIf` nem `expectedFailure`; os `skipTest` existentes são de ambiente (bash ausente, namespace de pid, root) e anteriores.
Falso positivo, sondagem direta do hook com cerca de 50 linhas de fluxo real (fixture base `linkcopia-unzip-lista-sem-controle-libera`, `TMPDIR` próprio), todas liberam (rc 0): `cat`/`sed`/`bash -n .githooks/pre-push`, `7z l`, `tar -tf`/`-tzf`/`-czf`, `unzip -l`/`-p`, `tar -xf -C $TMPDIR`, `7z x -o$TMPDIR`, `python3 -c` sem citar controle e `python3 -I -m unittest`, `perl -e`, `node -e`, `cp -a/-r/-p` e `rsync -avz` para `$TMPDIR`, `git diff/log/show` de `docs/pedidos`, `for` e `while read` sem `.claude`, e o jarvis gravando por `echo >`, `cp`, `cp -a`, `tar -x`, `unzip` e `cat <<` na pasta de controle. Só recusa o que é para recusar (`ln -s` do jarvis em brief, regra anterior). Falha fechado, por desenho, o `python3 -c` de quem não é o jarvis que cita a pasta de controle por caminho absoluto ou `docs/qa/` (A1, recomendado).

## Achados
- A1 (recomendado) hooks/conformidade.py:1 · `python3 -c "print(open('docs/qa/v1.md').read())"` (qa-engineer) e a leitura de `/root/.forge-contrib/docs/briefs/b1.md` (tech-lead) recusam: leitura pura cai no fechado. Raro e com contorno (`cat`); vira cartão.
