---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-heredoc-palavra
commit: 55418634d158dda4f8693915d16162d03ebfe256
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 (E2.8, HOOK-HEREDOC-PALAVRA-FP)

Head 730261a5 (`corpos_de_dado` em `hooks/parecer.py`, 10 fixtures `heredoc-dado-*`, teste `test_corpus_heredoc_dado_libera_e_bloqueia`, 9 mutantes, índice). Passada única, parecer completo. Sem PR (instrução do brief); a suíte inteira roda no CI do PR, que ainda não existe.

## Achados
- A1 (recomendado) hooks/parecer.py:274 · resolvido em 7185b64c: crase no alvo agora recusa (Q1-Q3 rc 2); bug v0474-01 fechado.
- A2 (recomendado) tests/mutantes/v047-hook-heredoc-palavra-2.json:1 · resolvido: M9, M10 e M11 cobrem as guardas novas; 5 fixtures `heredoc-dado-*-bloqueia` somadas.

## Critério → teste → resultado
O pedido não tem `CA-n` de UX; as obrigações são a regra HOOK-HEREDOC-PALAVRA-FP e o `R-REVIEW` (marca da chamada), lidas do diff e das descrições das fixtures.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Corpo que nenhum programa roda é dado e libera (cat+ls, mkdir/cat/wc/head, python3 - arq) | fixtures `heredoc-dado-*-libera` (3) | lista PROGRAMAS_DE_DADO; argumento depois do `-` | passou |
| sh/python que roda o arquivo ou o corpo segue recusado | `cat-e-sh-roda-o-arquivo`, `python-com-argumento-e-subprocess` | programa fora da lista | passou |
| Atribuição na chamada, `<<$'FIM'`, `git merge` fora do corpo recusam | `atribuicao-antes-do-ls`, `delimitador-ansi-c`, `git-merge-fora-do-corpo` | forma não simples, atribuição | passou |
| Arquivo gravado com nome de programa da chamada recusa (literal e curinga) | `grava-programa-da-chamada`, `alvo-com-curinga` | nome literal e `*?[` | passou |
| Alvo gravado por substituição de crase recusa | sonda Q1-Q3 (sem fixture no head) | alvo sem valor literal | FALHOU (rc 0, esperado 2) |
| Quatro fixtures revistas (libera) mantêm o lado bloqueia | `heredoc-parecer-*-bloqueia`, `texto-barra-heredoc-lido-e-ls` | renomeio sem perda do lado recusa | passou |
| Corpus tem os dois lados e mínimo de 10 | `test_corpus_heredoc_dado_libera_e_bloqueia` (3 libera, 7 bloqueia) | guarda de suíte vazia (10) | passou |

## Cenários e resultado real
Ambiente: clone `/root/.forge-contrib/wt/v047-hook-heredoc-palavra-E28`, Python 3.12, `TMPDIR` do sandbox, máquina com carga 13 a 27 (vários agentes em paralelo).

Mutantes (`bin/forge-mutante` nas duas specs, 9 mutantes, 1m14s): todos morreram.
```
forge-mutante: pedido=v047-hook-heredoc-palavra rev=730261a5406e spec=f049fdf8... spec=cb7f9417...
M1 · morreu · hooks/parecer.py:217
M2 · morreu · hooks/parecer.py:218
M3 · morreu · hooks/parecer.py:247
M4 · morreu · hooks/parecer.py:268
M5 · morreu · hooks/parecer.py:270
M6 · morreu · hooks/parecer.py:277
M7 · morreu · hooks/parecer.py:277
M8 · morreu · hooks/parecer.py:1053
M9 · morreu · hooks/parecer.py:275
```
Cobertura (`forge-mutante --cobertura --base 5b1aacd5`): cada condição mudada tem mutante declarado (linhas 217, 218, 247, 268, 270, 275, 277, 1053; "declarado, não provado"). A lista cobre o diff; a guarda que falta (crase) não existe no código, é o A1.

Vermelho antes do verde (`forge-testes --vermelho 5b1aacd5 --modulos test_hooks_parecer_pasta`, 5m51s):
```
vermelho: base=5b1aacd5068f head=730261a5406e módulos=test_hooks_parecer_pasta (restrito por --modulos)
revertidos à base: changelog.d/v047-hook-heredoc-palavra.md, docs/hooks-fixtures.md, hooks/parecer.py
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_dado_libera_e_bloqueia · H=ok · B=falha · prova (asserção)
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_texto_passa_e_barra · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=3; prova (asserção)=2
```
(`texto_passa_e_barra` cai na base porque as fixtures revistas mudaram de veredito.)

Índice: `python3 -I scripts/indice-fixtures.py --conferir` → `docs/hooks-fixtures.md: em dia`.

Teste do módulo: `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py` → `Ran 5 tests in 43.844s · OK`.

Corpus completo dos hooks (inclui `pesado/mesma-sessao-libera` e `pesado/sem-lista-nada-e-pesado`): `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures` → `Ran 24 tests in 1130.044s · OK (skipped=4)` (4 puladas com motivo declarado pelo próprio teste: fixtures de PID/sessão sem ns de pid legível). Os pesados passaram no head. Sobre o estouro de tempo visto pelo autor: não reproduzi falha; o corpus levou 18m50s com carga 13 a 27 na máquina compartilhada, e o hook `pesado` está fora do diff (`git diff --stat` só toca `hooks/parecer.py` em `hooks/`), então a causa é do ambiente (carga e prazo por fixture), não desta mudança. Um segundo `forge-testes --vermelho` sem `--modulos` (suíte inteira) e uma execução em segundo plano com `nohup` não terminaram ou foram mortos pelo sandbox ("fatal library error, lookup self"), por isso restrito a módulo.

Sondas de abuso (22 variantes, fixtures montadas em `$TMPDIR` com `tests/test_hooks.Fixture`), todas como esperado: recusam `. ./a.sh`, `source`, `| sh`, `cat >bin/ls`, `1>`, `&>`, `>>`, alvo antes ou depois do heredoc, `/usr/local/bin/ls`, `bin/$N`, `'bin/ls'`, `bin/$(echo ls)`, `/bin/ls` depois de `cat > bin/ls`, `| xargs sh`, `grep | sh` (R-CONTRIB), crase e `$( )` nos argumentos, `ls <(git merge y)`, `head | sh`; liberam dado legítimo (`<<'F1'` e `ls <<'F2'`, `cat <<'FIM' > a.md` + `wc`, `<<FIM` sem aspas gravando arquivo).

Falha (Q1-Q3, mesma fixture-base, `cat > ALVO <<'FIM'` com corpo `#!/bin/sh` e `git merge melhoria/x`, depois `ls`), esperado rc 2 `R-REVIEW`, obtido rc 0:
```
Q1  cat > `echo bin/ls`        AssertionError: 0 != 2
Q2  cat > bin/`echo l`s        AssertionError: 0 != 2
Q3  cat > `cat n`              AssertionError: 0 != 2
```
Confirma o A1 do review (E2.6) e da segurança (E2.7) de forma independente. Bug v0474-01 (alta; sem arquivo separado, o brief limita o commit ao parecer). Corrige: autor da branch (`tech-lead` revisa); correção mínima já indicada pela segurança: `corpos_de_dado` devolve False com crase na linha fora dos corpos ou alvo sem valor literal.

Revalidação: `forge-check parecer delta docs/qa/v047-hook-heredoc-palavra.md`; rodar `bin/forge-mutante --base <head aprovado>` com o mutante novo da guarda.

## Revalidação (E2.16, head 7185b64c)
Delta lido com `forge-check parecer delta` (hooks/parecer.py, 5 fixtures novas, 2 specs de mutantes, ADR, changelog, índice). Reteste:
- Sondas Q1 (cat > `echo bin/ls`), Q2 (bin/`echo l`s), Q3 (cat > `cat n`), mesma fixture-base: as 3 recusam com rc 2 (`Ran 1 test · OK`).
- `bin/forge-mutante tests/mutantes/v047-hook-heredoc-palavra.json tests/mutantes/v047-hook-heredoc-palavra-2.json` → rc 0: M1 a M11 morreram (M5 parecer.py:271, M9 :281, M10 :273, M11 :278).
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py` → `Ran 5 tests in 89.812s · OK`.
- `python3 -I scripts/indice-fixtures.py --conferir` → `docs/hooks-fixtures.md: em dia`.
- `forge-testes --vermelho 5b1aacd5068fdf0ad78cb0404444ba33cdbf594a --modulos test_hooks_parecer_pasta` → rc 0; `vermelho: base=5b1aacd5068f head=7185b64c5783`; `test_corpus_heredoc_dado_libera_e_bloqueia` e `test_corpus_texto_passa_e_barra` provam (falham na base); contagem: não prova (passa na base)=3; prova (asserção)=2.
## Revalidação (E2.39, head 76b50dc7)
Delta lido com `forge-check parecer delta` (7185b64c..76b50dc7: `hooks/parecer.py:281` filtro `*?[{`, 3 fixtures `heredoc-dado-alvo-com-chave-*-bloqueia`, spec `-2` com M12 e M9 realinhado, ADR, índice). Reteste:
- `bin/forge-mutante tests/mutantes/v047-hook-heredoc-palavra.json tests/mutantes/v047-hook-heredoc-palavra-2.json` → rc 0, `rev=76b50dc775c3`: M1 a M12 morreram (M9 e M12 em parecer.py:281).
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py` → `Ran 5 tests in 144.821s · OK`.
- `python3 -I scripts/indice-fixtures.py --conferir` → `docs/hooks-fixtures.md: em dia`.
- `forge-testes --vermelho 5b1aacd5068fdf0ad78cb0404444ba33cdbf594a --modulos test_hooks_parecer_pasta` → rc 0; `vermelho: base=5b1aacd5068f head=76b50dc775c3`; `test_corpus_heredoc_dado_libera_e_bloqueia` e `test_corpus_texto_passa_e_barra` provam (asserção); 3 não provam (passam na base).
Parecer: aprovado; nenhum bug aberto.

## Revalidação E2.51 no head 228d0083 (escopo incremental)
Delta desde 76b50dc7: junção da develop; no domínio do QA só o índice gerado `docs/hooks-fixtures.md` (conflito regerado pelo script). `python3 -I scripts/indice-fixtures.py --conferir`: "docs/hooks-fixtures.md: em dia". `python3 -m unittest tests.test_hooks_parecer_pasta`: 5 testes, OK (96 s). Nenhum bug novo; parecer segue aprovado.

## Revalidação E2.57 no head 55418634 (escopo incremental)
Delta desde 228d0083 (`forge-check parecer delta`): junção da develop (#637) e M2/M14 das specs do #623 (`v047-hook-heredoc-fp.json`, `-fp-2.json`) alinhados. Reteste:
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_hooks_parecer_pasta` (sem -I): `Ran 9 tests in 73.896s · OK`.
- `bin/forge-mutante` nas duas specs do #623 (`rev=55418634d158`, rc 0): M1 a M4, M6 a M16 morreram (M5 não declarado na spec).
- `bin/forge-mutante` nas duas desta branch (`rev=55418634d158`, rc 0): M1 a M12 morreram.
Nenhum bug novo; parecer segue aprovado.
