---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 9b075525eaa2a3cadf408e77bafbe5e1817884ab
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
