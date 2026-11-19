---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 9a20739e0d4ff607033690eaa238e6c0342e6d74
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
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
