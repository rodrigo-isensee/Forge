---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: d2358465fafc56c42b396ef7e1efe2c4d0e6e854
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-conformidade-sessao-forge (E51.9, revalidação)

Revalidação no head d2358465 (antes: fe8607df). Delta: `hooks/conformidade.py` (marca `trava=` no `barrar`, `toca_uma_trava`, listas positivas do git e do gh), 16 fixtures `e51-*` novas, 2 specs de mutantes novas, `tests/test_hooks.py` (piso 11 para 27). O remoto avançou só com pareceres de review e segurança (código segue em d2358465); trazido por merge. Suíte inteira: só no CI do PR, não rodada aqui.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Na sessão do Forge as travas valem para todo papel: R-MAIN, R-VERIFY, push para integração, tag v* | `HookSessaoDoForge.test_travas_do_conformidade` (27 fixtures) | papel sem lista, wt/* e clone; piso 27 | passou |
| O resto da linha segue livre (ADR 0009, seção 6) | mesmo teste (`-libera`: escrita, branch de trabalho, `tag -l`, `git log $B`, `gh pr view $N`, atribuição opaca) | leitura e branch de trabalho com variável | passou |
| Alvo opaco com ação crítica (variável, eval, bash -c, heredoc, substituição, teto) recusa | mesmo teste, `-bloqueia` do E51.6 | `B=develop; git push origin $B`, `F=--force; git push $F ...` | passou (A1 e A2 do parecer anterior fechados) |
| O `vigia` grava `violacoes.jsonl` | `HookSessaoDoForge.test_vigia_registra` | piso 2 | passou; erra na base |
| Here-string com push direto (`bash <<< 'git push origin develop'`) | sonda do QA, sem teste no branch | `<<<` em wt/* | FALHA: saída 0, esperado 2 (A1) |
| O que passava na base segue passando | `test_hooks` inteiro, vermelho e verde | 5 testes de `Hooks` | FALHA: 5 regressões (A2) |

## Provas
Classe no head: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`: 2 testes, OK.

Mutantes: `bin/forge-mutante` sobre as 3 specs (`tests/mutantes/v0479-conformidade-sessao-forge.json`, `-2`, `-3`), saída 0, 24 de 24 `morreu` (M1 a M24; M7 morreu por erro com controle verde). Cobertura (`--cobertura --base 0f6034ea`): todas as linhas de decisão mudadas (3778, 3801 a 3805, 3816 a 3828) têm mutante declarado; `fix-037-uniao-seg.json` sai `isenta fora do diff`. Os mutantes não cobrem o here-string nem as 5 regressões.

Vermelho (`bin/forge-testes --vermelho 0f6034ea5aaaab5f0aab8acb593523497cdc3b6f --modulos test_hooks --prazo 3000`, rc=2, H 2218 s, B 2212 s):
```
vermelho: base=0f6034ea5aaa head=d2358465fafc módulos=test_hooks (restrito por --modulos)
tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade · H=ok · B=falha · prova (asserção)
tests.test_hooks.HookSessaoDoForge.test_vigia_registra · H=ok · B=erro · sem veredito
tests.test_hooks.Hooks.test_fixtures_da_trilha_034 · H=falha · B=ok · regressão
tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a · H=falha · B=ok · regressão
tests.test_hooks.Hooks.test_fixtures_do_rverify_falso_positivo · H=falha · B=ok · regressão
tests.test_hooks.Hooks.test_rotulo_so_dono_formas_alternativas · H=falha · B=ok · regressão
tests.test_hooks.Hooks.test_rotulo_so_dono_volta_2_crase_escapada_comentario_clone_e_remocao · H=falha · B=ok · regressão
tests.test_hooks.Hooks.test_fixtures · H=falha · B=erro · falha da entrega (regressão ou sem veredito)
contagem: falha da entrega (regressão ou sem veredito)=1; não prova (passa na base)=139; prova (asserção)=1; pulado=11; regressão=5; sem veredito=1
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
```
Os 5 casos de regressão, rodados um a um no head (`-k <teste>`), falham: `2 != 0 : R-CONFORMIDADE: $R com ação crítica: o hook não modela` (`conformidade/rotulo-variavel-outro-argumento-libera`) e `'R-VERIFY: ...' not found in 'R-CONFORMIDADE: crase com ação crítica...'` (`rverify-fp-verdadeiro-linha-ilegivel-heredoc-na-crase-bloqueia`). O `test_vigia_registra` erra na base (hook sem o clone como projeto), o esperado. Vermelho manual da classe (cópia do head com `conformidade.py` e `vigia.py` da base): `FAILED (failures=19, errors=2)`; os `-libera` passam.

Abuso (cópia do head, fixtures extras, como `forge:dev` em `wt/x`): `B=develop; git push origin $B` com `export` e aspas, `git push origin HEAD:refs/heads/develop`, `$G push` com `G=git`, `--force-with-lease`, `for b in develop; do git push origin $b; done`, `gh pr merge 5 --admin`, `git commit --no-verify` (direto e por variável) saem 2; `git push origin melhoria/x`, `git log $B`, `echo $B > x` e `R=$(git rev-parse HEAD); git push origin melhoria/x` saem 0. `bash <<< 'git push origin develop'` sai 0 em wt/* e 2 no projeto. `cmd=push; git $cmd origin develop` e `git push origin $(echo develop)` saem 0 também no projeto (sem diferença entre as sessões; fora desta trava).

## Achados
- A1 (bloqueante) hooks/conformidade.py:3808 · `bash <<< 'git push origin develop'` sai 0 em wt/* (no projeto recusa: heredoc com ação crítica): `toca_uma_trava` não lê o corpo do here-string. Somar fixture `e51-*` e mutante.
- A2 (bloqueante) hooks/conformidade.py:3801 · a trava opaca recusa na sessão do Forge o que a base liberava: 5 testes de `Hooks` regridem (`$R`, crase, `${`, `$PWD`; R-VERIFY virou R-CONFORMIDADE). Ajustar a lista positiva (`gh pr edit`) ou as fixtures, com o motivo.
- A3 (recomendado) bin/forge-testes:1 · `--vermelho` do `test_hooks` leva 2200 s por cópia e não aceita `-k` nem classe; `test_vigia_registra` fica sem veredito por erro da base. Cartão: veredito por classe.
