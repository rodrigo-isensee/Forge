---
tipo: qa
contrato: 1
pedido: pre-push-ff
branch: melhoria/pre-push-ff
commit: e60fa6e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA - pre-push recusa envio não fast-forward (ADR 0009, R-VERIFY)

Links: revisão de código `docs/reviews/pre-push-ff.md`; ADR `docs/adr/0009-conformidade-dos-agentes.md`; hook da fábrica `.githooks/pre-push`; hook do modelo `templates/projeto/.githooks/pre-push`.

## Escopo
Coberto:
- Hook do modelo (`templates/projeto/.githooks/pre-push`) em repositório temporário com remoto bare, copiado para fora da árvore do Forge e ativado com `core.hooksPath` (removido ao fim).
- Os nove cenários pedidos: fast-forward, amend + `--force`, `+refspec`, branch nova, apagar branch, tag nova, apagar tag, remoto com commit ausente localmente (sem fetch), push direto para `main`.
- Testes unitários do Forge (`python3 -m unittest discover -s tests`, inclui a classe `HookPrePush`).
- Shellcheck nos dois hooks.

Não coberto nesta rodada:
- Mover tag existente para outro commit (`git push -f` de tag): só verificado pela leitura do código e pela revisão.
- Apagar `main`, criar `main` nova, e envio simultâneo de várias refs numa mesma chamada.
- Hook `pre-push.local` do projeto (só roda quando o envio é aceito; não exercitado).
- Acessibilidade e E2E: não se aplicam, o pedido é de hook de git.

## Cenários
| ID | Cenário | Tipo | Prioridade | Automatizado | Esperado | Resultado real |
|---|---|---|---|---|---|---|
| CT-01 | Fast-forward em branch existente | Hook (script) | Alta | não (script manual) | Passa | Passou (rc 0); remoto `feat` avançou de `422abc6` para `81178f2` |
| CT-02 | Amend + `--force` em branch existente | Hook (script) | Alta | não (script manual) | Recusa com R-VERIFY | Recusou (rc 1): "R-VERIFY: envio não fast-forward para feat (histórico reescrito) bloqueado; faça rebase..." Remoto inalterado (`81178f2`) |
| CT-03 | `+refspec` (`+HEAD:refs/heads/feat`) não fast-forward | Hook (script) | Alta | não (script manual) | Recusa com R-VERIFY | Recusou (rc 1), mesma mensagem R-VERIFY. Remoto inalterado |
| CT-04 | Branch nova | Hook (script) | Média | não (script manual) | Passa | Passou (rc 0): `[new branch] HEAD -> nova` |
| CT-05 | Apagar branch | Hook (script) | Média | não (script manual) | Passa | Passou (rc 0): `[deleted] nova` |
| CT-06 | Tag nova (leve) | Hook (script) | Média | não (script manual) | Passa | Passou (rc 0): `[new tag] v0.1.0` |
| CT-07 | Apagar tag | Hook (script) | Média | não (script manual) | Passa | Passou (rc 0): `[deleted] v0.1.0` |
| CT-08 | Remoto com commit que o local não tem (sem fetch) | Hook (script) | Alta | não (script manual) | Recusa pedindo `git fetch` | Recusou (rc 1): "o commit atual de feat no remoto não existe aqui, ... rode 'git fetch' e tente de novo." Remoto inalterado (`325c82f`); objeto ausente confirmado localmente |
| CT-09 | Push direto para `main` (fast-forward) | Hook (script) | Alta | não (script manual) | Recusa (regra antiga) | Recusou (rc 1): "envio para a main bloqueado. Abra um pull request..." Remoto `main` inalterado |
| CT-10 | Testes unitários do Forge | Unitário | Alta | sim | Verde | 193 testes, OK (`python3 -m unittest discover -s tests`) |
| CT-11 | Shellcheck nos dois hooks | Estático | Alta | sim | Sem avisos | `.githooks/pre-push` e `templates/projeto/.githooks/pre-push`: rc 0, sem avisos |
| CT-12 | Mensagem de tag movida fora do histórico | Hook (script) | Média | não | Recusa com texto neutro (tag) | Não executado nesta rodada (ver Escopo). Texto verificado na leitura: "mover a tag ... (histórico reescrito) bloqueado" |

Notas de execução:
- Todos os envios recusados deixaram o remoto no mesmo SHA (verificado por `git ls-remote` após cada caso).
- CT-08: a checagem `git cat-file -e` antes do `merge-base` já está no hook de `HEAD` (`e60fa6e`), com a mensagem de `git fetch` recomendada em `docs/reviews/pre-push-ff.md`. Por isso a mensagem é correta. A revisão foi escrita sobre `2910e1e`, antes dessa correção.
- O texto de CT-12 também saiu neutro (sem "branch/rebase"), como a revisão recomendou; continua sem execução.

## Dados de teste
- Repositório temporário: remoto bare `remote.git`, cópias de trabalho `work` e `other`, branches `main` (commit inicial) e `feat`.
- Hook do modelo copiado para diretório próprio fora da árvore do Forge; `core.hooksPath` configurado com `git -C <tmp> config` (repositório temporário, sem `--worktree`).
- Sem usuários, permissões ou fixtures de aplicação; o pedido não envolve esses dados.

## Defeitos
Nenhum defeito encontrado. Nenhum arquivo em `docs/qa/bugs/` foi criado.

## Resultado da execução
- Data: 2026-10-13. Ambiente: worktree `melhoria/pre-push-ff`, commit `e60fa6e`, Linux (WSL2), git local, bash.
- Aprovados: CT-01 a CT-11. Falhos: nenhum. Não executado: CT-12 (escopo acima).
- Parecer: aprovado, sem bugs abertos.
