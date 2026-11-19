---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: deaf35704182bc20c1bcc2e630f044480e1ddb06
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (guardas do hook `parecer`, E3.23, revalidação)

Escopo: delta `014f3e53..9b075525` (`forge-check parecer delta` lista a partir de `b989773a`): `hooks/parecer.py` (regras por classe D1 a D5), gerador `tests/test_hooks_parecer_matriz.py` (237 linhas cruzadas), mutantes M42 a M57 (specs -8 e -9), M28 realinhado (spec -5), módulo em `bin/forge-testes` e `tests/pesos-d4.json`, `docs/hooks.md`. O remoto avançou depois de `9b075525` só com pareceres de review e segurança (sem código). Sem PR nem CI deste head: rodei só os módulos tocados e os mutantes, sem `tests.test_hooks` inteiro (brief).

Obrigação: GH-REMOTO-NA-LINHA (A5 a A7 da segurança, A3 do review): GH_REPO e remotos do gh não mudam na mesma linha sem o hook ver.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Matriz: cada dimensão x posição x gh recusa e o legítimo passa | `MatrizDaCopiaAlheia.test_cada_dimensao_posicao_e_gh_recusa_e_o_legitimo_passa` | legítimo libera; PATH fora (declarado no changelog) | passou |
| D1 opções depois de `builtin`/`command` | `RegrasPorClasse.test_d1_opcoes_depois_de_builtin_e_command` | `--`, `-p` | passou |
| D2 nome por expansão e caminho de variável | `RegrasPorClasse.test_d2_nome_por_expansao_e_caminho_de_variavel` | `$c env.sh`, `$(cat)` | passou |
| D4 classe do config do git (`GIT_*`, HOME, XDG) | `RegrasPorClasse.test_d4_classe_do_config_do_git` | todo `GIT_*` | passou |
| D5 programas que mantêm remotos | `RegrasPorClasse.test_d5_programas_que_mantem_os_remotos` | programa fora da lista que só lê recusa | passou |
| Módulo no mapa e peso | `test_testes_tocados.py` (162 testes) | módulo novo listado | passou (1 skip herdado, não é teste meu) |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_matriz.py` (TMPDIR próprio): `Ran 5 tests in 10.277s ... OK`; `test_hooks_parecer_repo.py`: `Ran 5 ... OK`; `test_testes_tocados.py`: `Ran 162 ... OK (skipped=1)`.
- Vermelho antes do verde: `bin/forge-testes --vermelho b989773a2ae7276692081441ff72c05d26d0f8da --modulos tests.test_hooks_parecer_matriz` → `vermelho: base=b989773a2ae7 head=0da1a32bcda6`, `hooks/parecer.py` revertido à base; 5 testes `H=ok · B=falha/erro`; `contagem: prova (API ausente)=2; prova (asserção)=3`, rc 0.
- Mutação: `bin/forge-mutante` specs -5, -8, -9 `--processos 3 --base b989773a2ae7276692081441ff72c05d26d0f8da` → `base=b989773a2ae7276692081441ff72c05d26d0f8da mb=b989773a2ae7276692081441ff72c05d26d0f8da rev=0da1a32bcda6`; M27 a M34 (M28 realinhado em :640) e M42 a M57 todos `morreu`. Nenhum sobrevivente, nenhum equivalente.
- Cobertura: `forge-mutante --cobertura --base b989773a...` → rc 0; condições novas (449, 638 a 671, 1002 a 1006, 1033, 1034, 1248) todas `coberta`; só `não coberto: tests/pesos-d4.json` (dado, sem condição).
- Árvore limpa após as rodadas (cópias em `$TMPDIR`).

## Revalidação E3.26 (head 9a20739e, código em 415eaa82)
Escopo: delta `9b075525..9a20739e` (`forge-check parecer delta`): `hooks/parecer.py` (`mexidas_por_expansao`, `EXPANSAO_QUE_ATRIBUI`, chamada em `principal`), `docs/hooks.md` D4, matriz (`EXPANSOES`, sondas S28 e S29), `test_d4_atribuicao_por_expansao`, spec de mutantes `-10` (M58 a M62). Obrigação: A5 do review da E3.21 (`${N:=v}` e `${N=v}` contam como variável mexida).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `${N:=v}`, `${N=v}`, `${N[i]:=v}`, `${!n:=v}` recusam na cópia alheia | `MatrizDaCopiaAlheia.test_cada_dimensao_posicao_e_gh_recusa_e_o_legitimo_passa` | `${N:-v}`, `${N:+v}`, `${N:?}`, `${PAGER:=less}` liberam | passou |
| Regra da classe | `RegrasPorClasse.test_d4_atribuicao_por_expansao` | vazio, `${#HOME}`, `$GH_REPO=x` | passou |

- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_matriz.py` (TMPDIR próprio): `Ran 6 tests in 15.137s ... OK`.
- Vermelho: `bin/forge-testes --vermelho 9b075525... --modulos tests.test_hooks_parecer_matriz` → `vermelho: base=9b075525eaa2 head=9a20739e0d4f`; matriz `H=ok · B=falha · prova (asserção)`; `test_d4_atribuicao_por_expansao` `H=ok · B=erro · prova (API ausente)`; os outros 4 não provam (já existiam, não são novos).
- Mutação: `forge-mutante tests/mutantes/v0478-guardas-parecer-10.json --processos 3 --base 9b075525...` → `base=9b075525eaa2... rev=9a20739e0d4f`; M58 a M62 todos `morreu`. Sem sobrevivente nem equivalente.
- Cobertura `--cobertura --base 9b075525...`: condições novas (657, 660) `coberta`.
- Sem CI deste head, sem suíte inteira (brief). Parecer final: sem bug aberto.

## Revalidação E3.31 (head 460a8a00)
Escopo: delta `9a20739e..460a8a00` (`forge-check parecer delta`): `hooks/parecer.py` (`ATRIBUICAO_ARITMETICA`, `ABRE_ARITMETICA`, `mexidas_por_aritmetica`, `mexidas_do_texto`, chamada em `principal`), `docs/hooks.md` D4 e D7, matriz (A9 na chave, A10 aritmética, S30 a S34), `test_d4_atribuicao_aritmetica`, `test_d4_cada_forma_que_o_shell_le`, specs de mutantes `-10` (M62 a M65), `-11` (M66 a M71) e `-12` (M72 a M75). Obrigação: A9 e A10 da segurança da E3.27 (GH-REMOTO-NA-LINHA).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `${GH_\⏎REPO:=v}` e aritmética (`$((N=0))`, `$[N=0]`, `((N++))`, `let`, `${A[N=0]}`, `${P:N=0:0}`) recusam na cópia alheia | `MatrizDaCopiaAlheia.test_cada_dimensao_posicao_e_gh_recusa_e_o_legitimo_passa` (S30 a S34) | `$((HOME == 0))`, `$((PAGER = 1))`, `"$HOME=x"` liberam | passou |
| Regra da classe aritmética | `RegrasPorClasse.test_d4_atribuicao_aritmetica` | `==`, `!=`, `<=`, `>=`, `$HOME=x`, `HOMEX`, `XHOME`, `--title` fora; `=` simples só com contexto | passou |
| Cada forma que o shell lê | `RegrasPorClasse.test_d4_cada_forma_que_o_shell_le` | barra+quebra dentro da chave e do nome | passou |

- Local (TMPDIR próprio): `python3 -I -m unittest discover -s tests -p test_hooks_parecer_matriz.py` → `Ran 8 tests ... OK`.
- Vermelho: `forge-testes --vermelho 9a20739e... --modulos tests.test_hooks_parecer_matriz --prazo 500` → `vermelho: base=9a20739e0d4f head=460a8a002d27`; matriz `H=ok · B=falha · prova (asserção)`; `test_d4_atribuicao_aritmetica` e `test_d4_cada_forma_que_o_shell_le` `H=ok · B=erro · prova (API ausente)`; os outros 5 já existiam (não provam, não são novos).
- Mutação: `forge-mutante -10 -11 -12 --processos 3 --base 9a20739e...` → `base=9a20739e... rev=460a8a002d27`, rc 0; M58 a M75 todos `morreu`, sem sobrevivente nem equivalente. `--cobertura --base`: condições novas (677, 678) `coberta`; a spec `-10` sai `spec editada` (M62 acompanha a nova chamada, M63 a M65 novos).
- Sondas minhas, fora do corpus: `$(( HOME = 0 ))`, `$((GIT_DIR=1,2))`, `(( HOME<TAB>=0 ))`, `$((x?HOME=1:2))`, `let "HOME=0"`, `$(( HO""ME=0 ))` contam todas como `HOME`/`GIT_DIR`.
- D7 (`PATH`) é limite declarado por decisão do dono (docs/hooks.md); o `n=HOME; $(($n=0))` e o valor avaliado são abertos declarados (trava do sandbox, E29). Sem CI deste head, sem suíte inteira (brief). Parecer: aprovado, sem bug aberto.

## Revalidação E3.36 (head deaf3570)
Escopo: delta `460a8a00..deaf3570` (`forge-check parecer delta`): `hooks/parecer.py` (`pasta_do_gh`: sessão em cópia alheia com `cd` não resolvido recusa), `docs/hooks.md` D6, `changelog.d`, `SessaoNaCopiaAlheia`, spec `-12` (M76). Obrigação: A12 da segurança da E3.32 (GH-REMOTO-NA-LINHA).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `export HOME`, `: ${HOME:=/x}`, `HOME=…`, `declare HOME` seguidos de `cd ~/proj && gh` recusam (R-REVIEW) | `SessaoNaCopiaAlheia.test_cd_sem_resolver_recusa_e_o_resolvido_segue` | `cd ~/proj` resolvido confere o parecer (rc 2); gh sem `cd` na cópia alheia libera (rc 0, stderr vazio) | passou |

- Vermelho: `forge-testes --vermelho 460a8a00... --modulos tests.test_hooks_parecer_matriz` → `vermelho: base=460a8a002d27 head=deaf35704182`; `SessaoNaCopiaAlheia.test_cd_sem_resolver_recusa_e_o_resolvido_segue` `H=ok · B=falha · prova (asserção)`; os outros 8 já existiam (não provam, não são novos).
- Mutação: `forge-mutante tests/mutantes/v0478-guardas-parecer-12.json --processos 3 --base 460a8a00...` → `rev=deaf35704182`; M72 a M76 `morreu` (M76 em `hooks/parecer.py:1065`), sem sobrevivente nem equivalente. `--cobertura --base 460a8a00...`: `coberta · hooks/parecer.py:1065 · M76`.
- Sem CI deste head, sem suíte inteira (brief). Parecer: aprovado, sem bug aberto.
