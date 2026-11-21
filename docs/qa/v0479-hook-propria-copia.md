---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: bde062d7d009f4d2670967a03f5d05fb507fbc43
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: HOOK-AGENTE-FORA-DA-PROPRIA-COPIA (E88.5, revalidado em E88.9)

## Achados
- A3 (recomendado) hooks/copia.py:222 · Cópia com o HEAD fora da reserva (agente fez `git switch -c outra`): o `git switch <reserva>` e o `git commit` na própria cópia recusam; só a sessão principal destrava (desenho documentado em docs/hooks.md). Agente preso até o Jarvis agir; considerar liberar `switch` para a branch da reserva.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Recusa fora da cópia (Write, redireção, git -C, cd+git, outra worktree/clone, raiz com HEAD na reserva, GIT_DIR, symbolic-ref, timeout git) | 14 fixtures `recusa-*` | alvo na raiz, em outra cópia, fora de tudo | passou |
| Fluxo real livre: Jarvis (sem agent_id), pasta de controle, temporária, write e commit na cópia, clone próprio em wt/ e em .forge/wt/, leitura de git na raiz | fixtures `libera-*` | falso positivo | passou |
| Sem registro ou erro interno libera e anota | `libera-sem-registro-avisa`, `erro-interno`, `sem-forge-versao` | falta de dado não trava | passou |
| Leitura dos alvos, `copias`, `branches_do_agente` | `tests/test_copia.py` (16 testes) | cd -, `);`, `&>`, heredoc | passou |

## Revalidação no head bde062d7 (E88.9)
- A1 (`cd -`) e A2 (`);`, `&>`, `>&`) tratados: `test_copia.py:68,114` cobrem. `python3 -I -m unittest discover -s tests -p test_copia.py`: `Ran 16 tests ... OK`. Sem `skip` nem `expectedFailure` em `tests/test_copia.py`.
- Fixtures de `tests/hooks/copia/`: 27 (9 novas), todas passam em `test_fixtures`.
- Vermelho: `forge-testes --vermelho 4ee59dfcdf2b82cb10a3c49f8ed6fefdc92113dd --modulos test_copia` abriu com `vermelho: base=4ee59dfcdf2b head=bde062d7d009 módulos=test_copia`; `prova (asserção)=7`, `prova (API ausente)=3`, `não prova (passa na base)=6` (herdados da base); `FixturesDaCopia.test_fixtures`: H=ok, B=falha.
- Mutantes: `bin/forge-mutante --processos 4 tests/mutantes/v0478-e88-copia.json tests/mutantes/v0478-e88-copia-{2,3,4,5,6,7}.json`, rc 0, 55 linhas `morreu`, nenhum sobrevivente (7 specs: 8+8+8+8+8+8+7).
- Falso positivo (sondas por fixture efêmera no hook real, agente com reserva): liberam `cd <cópia> && git commit`, `git -C <cópia> commit`, `add && commit && push`, `pull --rebase`, `fetch && merge`, `git switch -c` na cópia; na raiz, `git tag -l`, `stash list`, `branch -a`, `worktree list`, `status/log/diff/show/fetch`, `rev-parse`, `ls-remote`, `remote -v`, `config --get`. Recusam na raiz `git tag v1`, `checkout`, `stash`, `pull --rebase`. `cd -` libera (pasta incerta, por desenho). Cópia com HEAD trocado: `switch` de volta e `commit` recusam (A3).
