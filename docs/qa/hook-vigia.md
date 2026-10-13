---
tipo: qa
contrato: 1
pedido: hook-vigia
branch: melhoria/hook-vigia
commit: e74b287
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---
# QA: hook `vigia` (ADR 0009, seção 8)

Ambiente: worktree da branch no commit e7df31b; Python 3 da estação, sem sessão do `claude` (nada que custe uso de IA). Os cenários rodaram `hooks/vigia.py` com JSON no stdin em projetos temporários criados com `git init` (config só neles), cada um com `.forge/versao`, `.claude/settings.json` e `.forge/config.json` versionados; os projetos foram removidos ao fim. Tempos medidos de ponta a ponta (processo Python, incluindo a partida).

Parecer: **aprovado**. Todos os cenários pedidos passam; BUG-01 (falso positivo, N1 do review) corrigido em e74b287 e revalidado (seção "Revalidação (e74b287)"). Nenhum bug aberto.

## Suíte e verificações do CI
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 168 testes, OK (45 s) |
| `shellcheck` (lista do job do CI) | sem avisos, código 0 |
| `claude plugin validate . --strict` | passou |
| `bash tests/e2e-instalacao.sh` | ok (plugin instalado, 8 agentes, 9 skills, projeto inicializado; 3,8 s) |
| `python3 tests/catraca.py --base origin/develop` | código 0, sem violações |

## Cenários
| ID | Cenário | Resultado real | Status |
|---|---|---|---|
| CT-01 | `SessionStart` (`startup`) silencioso | stdout vazio, código 0, stderr vazio (35 ms) | passou |
| CT-02 | Sem mudança, `Stop` sem saída | stdout vazio, código 0, `violacoes.jsonl` não criado (38 ms) | passou |
| CT-03 | `.claude/settings.json` alterado entre `SessionStart` e `Stop` | `systemMessage` de 1 linha: `Forge: 1 mudança(s) — em-vigor: .claude/settings.json alterado (.forge/run/violacoes.jsonl)`; 1 linha em `violacoes.jsonl` (evento `Stop`, gravidade `mudança(s)`, tipo `em-vigor`) | passou |
| CT-04 | Mesma mudança no `Stop` seguinte | sem saída, `violacoes.jsonl` continua com 1 linha | passou |
| CT-05 | Segunda mudança real no mesmo arquivo | avisa de novo; 2 linhas no registro | passou |
| CT-06 | Linha nova em `.forge/run/erros.log` (hook `conformidade`) | `Forge: 1 aviso(s) — erro-hook: ...`; linha de `vigia` no `erros.log` não gera aviso | passou |
| CT-07 | Transcrição: `Write` em `.claude/settings.json` barrado por `R-CONFORMIDADE`, depois `Bash` com `>` no mesmo arquivo, aceito | `Forge: 1 violação(ões) — contorno: Bash em .claude/settings.json depois de Write barrado no mesmo alvo` | passou |
| CT-08 | `git push --no-verify` barrado (`R-VERIFY`), depois `git push` sem a flag | nada (correção esperada, e `R-VERIFY` fora das regras de contorno) | passou |
| CT-09 | `git -c core.hooksPath=... push` barrado (`R-CONFORMIDADE`), depois `git push` simples | nada | passou |
| CT-10 | Projeto sem `.forge/versao`: `SessionStart` e `Stop` com arquivo em vigor alterado | stdout vazio, código 0, `.forge/run/` sem `vigia.json` nem `violacoes.jsonl` | passou |
| CT-11 | 5000 arquivos em `.claude/worktrees/` (50 pastas com `node_modules`) | `Stop`: 41, 41, 42, 45, 41, 43, 41 ms (mediana 41 ms; meta 300 ms) | passou |
| CT-12 | `SessionStart` com `source: compact` e com `resume` depois de uma mudança | saída vazia; o `Stop` seguinte ainda avisa a mudança (base preservada). Controle: `source: startup` reinicia a base, e a mudança só aparece pelo `git status` (`git: M .claude/settings.json`) | passou |
| CT-13 | Erro interno: `vigia.json` corrompido | código 0, stdout vazio, linha `vigia JSONDecodeError` em `erros.log` | passou |
| CT-14 | `vigia.json` com tipo errado (lista) | código 0; a base é recriada e o aviso sai pelo `git status` | passou |
| CT-15 | stdin que não é JSON | código 0, sem saída | passou |
| CT-16 | Reincidência de contorno: o mesmo `Stop` repetido não reavisa; novo contorno (`tee`, outro id de chamada) avisa | confirmado | passou |
| CT-17 | `SubagentStop` com `agent_type` | aviso emitido; registro traz `evento: SubagentStop` e `agente: forge:qa-engineer` | passou |
| CT-18 | `R-MAIN`: `git push origin main` barrado e depois `git push origin HEAD:main` aceito | `contorno` avisado | passou |
| CT-19 | `R-MAIN`: `git push origin main` barrado e depois `git log --oneline main` | nada | passou |
| CT-20 | `R-MAIN`: `git merge x main` barrado e depois `git merge main` na branch de trabalho | **avisa contorno (falso positivo)** | falhou, ver BUG-01 |

## Bugs

### BUG-01 - falso positivo de contorno em `git merge main` depois de bloqueio `R-MAIN` (corrigido em e74b287)
- Severidade: baixa (aviso só ao usuário, sem bloqueio; o review já o registrou como N1 recomendado)
- Responsável sugerido: node-backend
- Ambiente: e7df31b, `hooks/vigia.py` (`perfil_da_chamada` e `eh_contorno`)

Passos para reproduzir:
1. Criar projeto com `.forge/versao`, rodar `SessionStart`.
2. Acrescentar à transcrição um `Bash` com `git merge x main`, resultado com erro e texto `R-MAIN: proibido`.
3. Acrescentar um `Bash` com `git merge main` (trazer a `main` para a branch de trabalho) e resultado aceito.
4. Rodar `Stop`.

Esperado: nada, pois é outra operação, legítima (a prática manda trazer a `main` para a branch).
Obtido: `{"systemMessage": "Forge: 1 violação(ões) — contorno: Bash em main depois de Bash barrado no mesmo alvo ..."}` e registro de `contorno`. Causa: o alvo de `git`/`gh` é a última palavra e o subcomando `merge` coincide; falta comparar a sequência completa de referências.

## Observações (não são bugs)
- Com `vigia.json` corrompido, a mudança daquele turno não é avisada (falha aberto, só registro em `erros.log`); o turno seguinte recria a base. Coerente com a ADR 0003.
- `SessionStart` com `source: startup` numa sessão nova reinicia a base por desenho; mudança anterior só aparece pelo `git status` (arquivo versionado).
- Pendências já declaradas e não testáveis aqui: fixture de transcrição real com bloqueio do `conformidade` (R6), hook ausente (R7), hash só quando `(tamanho, mtime)` mudar.

## Revalidação (e74b287)
Escopo incremental: `git diff fd27ded..e74b287` (3 arquivos): `hooks/vigia.py` (`perfil_da_chamada` ganha `args`, os argumentos depois do subcomando de escrita; `eh_contorno` passa a exigir os mesmos argumentos para merge, rebase e `gh pr merge`, e mantém o `push` como antes), `tests/hooks/vigia/merge-main-na-branch-de-trabalho.json` (fixture novo) e entrada no `CHANGELOG.md`. Ambiente: worktree `/home/rodrigoisensee/Forge-vigia`, branch `melhoria/hook-vigia`, commit e74b287; `hooks/vigia.py` rodado com JSON no stdin em projetos temporários (`git init`, removidos ao fim).

Parecer da revalidação: **aprovado**. BUG-01 corrigido; sem regressão nos cenários de `R-MAIN` e de contorno revalidados; nenhum bug aberto.

| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 168 testes, OK (41 s); inclui o `test_fixtures` com todos os fixtures do vigia |
| `python3 tests/catraca.py --base origin/develop` | código 0, sem violações |
| Fixture `merge-main-na-branch-de-trabalho` (à mão) | passou: `git merge x main` barrado (`R-MAIN`) e depois `git merge main` aceito; stdout vazio, código 0, sem `violacoes.jsonl` |
| Fixture `contorno-repetido` (à mão) | passou: `git push origin main` barrado e depois `git -C . push origin HEAD:main` aceito; aviso em cada um dos dois `Stop` (um por turno), `violacoes.jsonl` com 2 linhas, tipo `contorno` |

Sondagens extras (à mão, com a transcrição anexada depois do `SessionStart`):

| Cenário | Esperado | Resultado |
|---|---|---|
| `git merge x main` barrado e depois `git merge x main` aceito (mesmos argumentos) | aviso de contorno | passou: aviso `contorno: Bash em main depois de Bash barrado no mesmo alvo` |
| `gh pr merge 5 --squash` barrado e depois `gh pr merge 5 --squash` aceito | aviso de contorno | passou: aviso `contorno: Bash em 5 depois de Bash barrado no mesmo alvo` |
| `gh pr merge 5 --squash` barrado e depois `gh pr merge 5 --merge` aceito | nada (a expectativa inicial desta revalidação) | **aviso** `contorno: Bash em 5 ...`: ver observação abaixo |

Observação sobre a última sondagem (não é bug aberto): as flags de `gh` não entram em `args` (`resto` filtra o que começa com `-`), então `--squash` e `--merge` têm os mesmos argumentos (`5`). A mesma PR 5 continua sendo mesclada na `main`, por outro método, depois de um bloqueio `R-MAIN`; o aviso é coerente com a regra de contorno. Se o dono preferir distinguir o método, é mudança de desenho, não correção. Não abre bug.

Os fixtures do vigia (incluindo `contorno-entre-turnos`, `contorno-na-transcricao`, `leitura-depois-de-r-main-nao-conta` e `repetir-a-mesma-ferramenta-nao-conta`) passam no `test_fixtures`, então o `push` (CT-18 e CT-19 deste plano) segue como antes.
