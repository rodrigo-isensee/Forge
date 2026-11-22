---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: bf57b17e42a1c6019ac7f4c721f9f4900c51cc4e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---

## Revalidação 2ª volta (head bf57b17e)
Delta de `forge-check parecer delta` (14696864..bf57b17e): `hooks/conformidade.py`, 26 fixtures `tests/hooks/conformidade/a5-*` e S22, `docs/hooks-fixtures.md`, spec `-6`. A3 (subshell só leva a troca se ela é o 1º comando), A4 (`cd` no subshell não vaza) e A5 (`cp -r` para variável de fora recusa) cobertos; nenhum achado novo.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3 | test_s22_troca_so_sai_do_subshell_se_e_o_primeiro_comando | troca em 2º comando do subshell | passou |
| A4 | test_s22_cd_dentro_do_subshell_fica_nele | `cd` dentro de `( )` | passou |
| A5 | test_a5_copia_recursiva_para_opaco_sem_resto_recusa | `-r`/`-a`/`-t`/`--recursive`, `.` de origem; libera arquivo, mktemp, variável da própria linha | passou |

Provas:
- `python3 -I -m unittest discover -s tests -p test_conformidade_seg_v0480.py`: 11 testes, OK.
- `bin/forge-mutante --base 14696864b679 tests/mutantes/v0480-seg-conformidade-6.json` (rev bf57b17e42a1): S22p, S22c, A5c, A5r, A5v, todos `morreu`.
- `bin/forge-mutante` nas specs 1 a 5 (rev bf57b17e42a1): 35 `morreu`, nenhum sobrevivente. Specs 1-6 juntas não rodam: ids S22c e S22p repetidos entre -5 e -6 (só nomes, sem efeito no veredito).
- `tests/test_indice_fixtures.py`: 7 testes, OK. Corpus completo `test_hooks.py` fica para o check-run `bateria` do CI do PR (não terminou local no prazo).

# QA: v0478 (E113.10) S22, A20, RESTO-SOBE, negação, RESTO-ANULA e += no hooks/conformidade.py

Revalidação no head 14696864 (delta de `forge-check parecer delta`: `hooks/conformidade.py` e as fixtures). A1 (negação `!`) e A2 (`+=`) do parecer anterior estão corrigidos. Passada anterior (a4266c77) preservada abaixo.

Passada única, head a4266c77, base b0895f6cc. Só os testes afetados, as specs de mutante e as sondas do QA; a suíte inteira fica para o CI do PR (`R-QA`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S22: troca de branch só vale com `&&` que garante | test_s22_... (7 fixtures: 5 recusam, 2 liberam) | `\|\|`, `\|`, `;`, quebra de linha, `&&` simples | passou; lacuna na `!` (A1) |
| A20: resto com barra depois do opaco no `.git` recusa | test_a20_... (8 fixtures: 6 recusam, 2 liberam) | `$d/.`, `$(echo .git)/.`, `"$@"/c`; variável fora do `.git` libera | passou; lacuna `+=` (A2) |
| RESTO-SOBE: `..` depois do opaco vale resolvido | test_resto_sobe_... (6 fixtures: 5 recusam, 1 libera) | sobe e desce, sobe duas vezes, `TMPDIR` exportado, nome livre | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_conformidade_seg_v0480.py`: 3 testes, OK, três rodadas seguidas (8 s, 8 s, 5 s).
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-seg-conformidade.json tests/mutantes/v0480-seg-conformidade-2.json`, 13 de 13 `morreu` (S22a-f, A20a-d, RS1-RS3), nenhum sobrevivente, sem equivalentes. Rev a4266c778966.
- `forge-mutante --cobertura --base b0895f6cc`: toda condição mudada de `hooks/conformidade.py` aparece `coberta` (linhas 840, 842, 1768, 1776, 1778, 1847, 2228, 2230, 2612, 2613); `apagada` só `chave in ramos` (2568 da base, trocada pela forma nova). `não coberto: tests/pesos-d4.json` é dado, não guarda.
- Vermelho: o `forge-testes --vermelho` não rodou, porque a trava de tarefa pesada estava com outra sessão (R-TETO; duas tentativas bloqueadas pelo hook; a primeira, sem `--modulos`, ia para a suíte completa e foi cancelada). Substituto equivalente: o teste e as 21 fixtures novas sobre o `hooks/conformidade.py` da base (`git archive b0895f6cc` em cópia descartável): 3 testes, `FAILED (failures=16)`; as 16 fixtures que recusam caem (A20: 6, RESTO-SOBE: 5, S22: 5) e as 5 que liberam passam. O autor ainda deve colar o `--vermelho` oficial.
- Sondas do QA (29 comandos, esperado recusa): 27 recusados; liberaram `! git switch -c x && git push origin` (A1) e a do `+=` (A2); ambas liberam igual na base, são lacunas e não regressão. Recusadas, entre outras: `git switch -c x || push`, `x & push`, `x |& cat && push`, `x && echo a || push`, `if ! git switch ...; then push; fi`, `$X/.git/../hooks`, `$X/a/../.git`, `$X/a/../../.git`, `$d//c`, `$d/./c`, `for d in .git`, `read d <<< .git`, `$(printf .git)/c`, `TMPDIR=.git/a` com `../..`. Controle `{ git switch -c x; } && git push` libera, como deve.

## Fixture pesado/mesma-sessao-libera
Não é instável. Ela não está no diff (última mudança em #747) e roda em série, por depender de PID e da trava global. Sozinha: 10 de 10 aprovadas, 0,20 a 0,30 s cada. O estouro do autor é prazo sob carga (suíte paralela e outras sessões na mesma máquina), não resultado que oscila. Nenhum `skip`; sem cartão.

## Resultado
Reprovado por A1 (alta, segurança com gatilho: push na main liberado). Devolver ao autor com fixture `S22: ! git switch ... && git push` e mutante para a guarda nova; depois `forge-check parecer delta docs/qa/v0480-seg-conformidade.md`.


## Revalidação E113.10 (head 14696864)
- A1 corrigido: sondas (`!`, `!` sem espaço, `! !`, `( ! ... )`, `{ ! ...; }`, `true && ! ...`, `! x; push`, `! x || push`) na main: todas rc 2. Controles livres: `git switch -c x && git push` e `( git switch -c x ) && git push` rc 0; `! git switch ... && push` em `feature/x` rc 0. Fixtures `s22-negado-*` e `s22-subshell-negado-*` guardam.
- A2 corrigido: `d=.gi; d+=t`, `d=.; d+=git`, `d+=` vazio, `${d}`, `d+=.git` solto, `d=x; d+=.git`, três `+=`, `d+="t"`, `export d=.gi`, `"$d/."`: todas rc 2; `d=ok; d+=y` e `d=docs; d+=/x` rc 0.
- `{ git switch -c x; } && git push origin` na main: rc 2, igual ao head anterior (as chaves não são modeladas; fixture `s22-chaves-...` o declara); falso positivo conservador, não é achado.
- Testes: `python3 -I -m unittest discover -s tests -p test_conformidade_seg_v0480.py`: 8 testes, OK (36 s). Vermelho: mesmo teste e fixtures sobre a base bfed8033b (`git archive` em cópia descartável): 8 testes, `FAILED (failures=61)`.
- Mutantes: `bin/forge-mutante --processos 2` nas 5 specs: `rev=14696864b679`, 37 de 37 `morreu`, nenhum sobrevivente, sem equivalentes, rc 0 (log em `$TMPDIR/q/mut.log`).
- Specs antigas editadas pelo diff, uma por pedido: `impl-furo-hook-a-a3` 16/16 `morreu`, `v0435-hooks-n5` 13/13, `v047-destino-opaco` 8/8; rc 0, `rev=14696864b679`, sem sobrevivente.
- `forge-mutante --cobertura --base bfed8033b`: toda condição mudada `coberta`; só `tests/pesos-d4.json` (dado) `não coberto`; rc 0.

## Resultado
Aprovado. Sem achado aberto. A suíte inteira fica no check-run `bateria` do PR.
