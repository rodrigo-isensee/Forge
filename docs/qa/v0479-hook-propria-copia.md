---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: 4ee59dfcdf2b82cb10a3c49f8ed6fefdc92113dd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: HOOK-AGENTE-FORA-DA-PROPRIA-COPIA (E88.5)

## Achados
- A1 (recomendado) hooks/copia.py:63 · `cd -` vira o caminho literal `<pasta>/-`: `cd /raiz && git log; cd - && git commit` recusa o agente na própria cópia (falso positivo). Tratar `-` como pasta incerta (None).
- A2 (recomendado) hooks/copia.py:23 · O token `);` (e `&>`, `>&` com arquivo) não está em SEPARADORES/REDIRECOES: `(true); git -C <raiz> add f` e `echo x &> <raiz>/f` passam sem leitura (falso negativo, fora dos limites de docs/hooks.md).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Recusa fora da cópia (Write, redireção, git -C, cd+git, outra worktree/clone) | 9 fixtures `recusa-*` | alvo na raiz, em outra cópia, fora de tudo | passou |
| Fluxo real livre: Jarvis (sem agent_id), pasta de controle, temporária e /dev, write na cópia, commit na cópia, clone próprio em wt/, leitura de git fora | fixtures `libera-*` (8) | falso positivo | passou |
| Sem registro ou erro interno libera e anota | `libera-sem-registro-avisa`, `erro-interno`, `sem-forge-versao` | falta de dado não trava | passou |
| Leitura dos alvos, `copias`, `branches_do_agente` | `tests/test_copia.py` (11 testes) | cd, -C, heredoc, aspa sem par | passou |

## Cenários e resultado real
- Só `test_copia` e `-k test_hooks_json`: `Ran 11 tests ... OK` e `Ran 1 test ... OK`. Sem suíte local.
- Sem `skip`/`expectedFailure` em tests/test_copia.py nem em tests/hooks/copia (grep vazio). A guarda de suíte vazia existe (>= 18 fixtures, >= 8 de recusa).
- Vermelho antes do verde (`bin/forge-testes --vermelho ad3b3b6fb674376de0c2783be9a4bb694757f3b0 --modulos test_copia`): `vermelho: base=ad3b3b6fb674 head=4ee59dfcdf2b módulos=test_copia (restrito por --modulos)`; revertidos à base: hooks/copia.py, hooks/hooks.json e outros; `contagem: prova (API ausente)=11` (H=ok, B=erro nos 11). O vermelho vem de o módulo `copia` não existir na base, não de asserção; as 18 fixtures só rodam dentro de `test_fixtures`.
- Mutantes (`bin/forge-mutante --processos 4` nas 4 specs): 30 de 30 `morreu` (CP1 a CP30, copia.py:47 a 154 e hooks.json:54), rc 0; CP11 morreu por erro do teste declarado sob o mutante (aceito pela regra).
- Falso positivo, `alvos_do_bash` com as formas reais: `git commit/push`, `git -C <raiz> log/status/fetch` (leitura), `git stash list`, `git tag -l`, `git -c k=v commit`, `git commit -C HEAD`, `git worktree add`, `> /dev/null`, `2>&1 | tee ../x`, clone próprio em wt/ seguido de `cd` e commit: nenhum alvo fora da cópia. Exceção: A1.
