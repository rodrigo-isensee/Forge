---
tipo: qa
contrato: 1
pedido: pendencias-0.7.0
branch: melhoria/pendencias-hooks-0.7
commit: 4a35848
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-12
---
# QA - pendências dos hooks e migração 0.7.0

## Escopo
Itens de `[Não publicado]` do CHANGELOG: migração 0.7.0, lista de pesados na stack, `git checkout <ref> <arquivo>` no hook `parecer`, mensagens do hook `agentes` e "Limites conhecidos" de `docs/hooks.md`. Tudo executado em projetos temporários (removidos ao fim); nenhuma sessão `claude` foi aberta.

Escopo desta revalidação (`escopo: incremental`): só o que mudou entre 4d4d7fb e 4a35848 (correção do `git checkout <ref> --` no hook `parecer`, lista `pesados` da stack sem `pytest -m integration`, CHANGELOG). O restante foi verificado no parecer completo de 4d4d7fb e não foi reexecutado.

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 88 testes, OK (rodado em 4a35848) |
| shellcheck, `claude plugin validate`, `e2e-instalacao.sh` | não reexecutados nesta revalidação (ver parecer de 4d4d7fb) |

## Cenários e resultado real
| ID | Cenário | Resultado |
|---|---|---|
| MIG-01 a MIG-07, AGE-01 a AGE-06, DOC-01 | migração, teto de agentes, documentação | não reexecutados; mudanças desde 4d4d7fb não os tocam |
| INI-01 | `forge-init --stack node-react` | a lista da stack agora tem 2 itens (`playwright`, `docker compose up`), não 3; a contagem anterior está desatualizada. A consistência com o arquivo é coberta por `tests/test_hooks.py` (`PESADOS_DA_STACK`), que passou |
| INI-02, PAR-02, PAR-03 | forge-init em projeto existente; merge sem parecer | não reexecutados; cobertos pela suíte unitária, que passou |
| PAR-01 | branch de trabalho: `git checkout develop app.js && git merge feature/x` | liberado (código 0), como antes; reexecutado (ver Revalidação) |

## Observações (não são defeitos)
- `forge-init --forcar` em projeto existente regrava `.forge/config.json` e substitui a lista `pesados` própria pela da stack. É o que `--forcar` documenta (sobrescrever); sem ele a lista é mantida.
- A migração só trata o inteiro `3`; `3.0` e `true` não são cobertos de propósito (`type(valor) is int`).

## Bugs
Nenhum.

## Revalidação (4a35848)
Motivo: o parecer de 4d4d7fb não pegou que `git checkout develop -- && git merge feature/x` (troca de branch com `--` sem caminho) era tratado como restauração de arquivo e liberava o merge na integração sem parecer. A correção está em 4a35848; esta revalidação confirma o comportamento e registra o defeito que o parecer anterior deixou passar (falha de QA minha, não do produto). Não há bug aberto: foi corrigido antes do merge.

| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` na worktree `Forge-pend` (4a35848) | 88 testes, OK |
| Cenário 1: repositório temporário com `.forge/versao`, `develop` e `feature/y` (de trabalho) com `feature/x` (código alterado, sem parecer). Hook `hooks/parecer.py`, JSON no stdin, `git checkout develop -- && git merge feature/x` | código 2, `R-REVIEW: nenhum parecer ... com branch: feature/x` (esperado: bloqueado) |
| Cenário 2: mesmo repositório, na branch de trabalho `feature/y`, `git checkout develop -- app.js && git merge feature/x` | código 0, sem saída (esperado: liberado) |
| Controle: mesmo cenário 1 com `hooks/parecer.py` de 4d4d7fb | código 0 (liberava indevidamente; o teste de regressão da correção cobre isso) |
| Sanidade: `git checkout develop && git merge feature/x` sem parecer | código 2, bloqueado |

O repositório temporário foi removido ao fim. Nenhum defeito novo. Parecer mantido: aprovado.

## Resultado da execução
2026-10-12, WSL, commit 4a35848 (revalidação incremental sobre 4d4d7fb, que teve todos os cenários aprovados com zero bugs). Parecer: aprovado.
