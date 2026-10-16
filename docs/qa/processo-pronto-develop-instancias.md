---
tipo: qa
contrato: 1
pedido: processo-pronto-develop-instancias
branch: melhoria/processo-pronto-develop-instancias
commit: 694edc7a2d1a2d5574a541cfc06f3941b88bec30
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA: processo (pronto, develop antes do review, instâncias por worktree)

Links: pedido `~/.forge-contrib/docs/pedidos/k2-e-processo.md` (E2), `docs/reviews/processo-pronto-develop-instancias.md` (aprovado em b8916bb), `docs/security/processo-pronto-develop-instancias.md` (aprovado). Sem UX nem API.

HEAD da branch: b8916bb; o código testado é o de 694edc7 (b8916bb só acrescenta o parecer de review). Diff próprio da E2: `git diff 930d6bb...HEAD` (14 arquivos). Obrigações: `R-WIP` (instâncias por worktree), `R-TETO` (teto de 3 instâncias; suíte do Forge é pesada), `R-FLUXO` (develop uma vez, antes do review), `R-REVIEW`, definição de pronto, S-11 (brief único).

## Suíte e validação (na worktree)
- `python3 -m unittest discover -s tests -q`: `Ran 657 tests in 244.641s` / `OK`.
- `scripts/validar-plugin.sh`: `Validation passed`.
- `forge-check pr processo-pronto-develop-instancias --ref HEAD --base origin/develop`: só duas pendências, `qa: sem parecer` e `revisao-seguranca: sem parecer`, que este commit resolve (o review não aparece como pendência).

## Critério → teste → resultado
Método: cópias descartáveis em `$TMPDIR` (projeto com `.git`, `.forge/versao`, `.forge/config.json`; KANBAN com a seção `Em andamento (WIP 1 por agente)`), `bin/forge-check` e `hooks/*.py` reais da worktree, ambiente sem `FORGE_*`. O `KANBAN.md` real não foi tocado.

| ID | Obrigação | Cenário | Fronteira protegida | Esperado | Obtido | Resultado |
|---|---|---|---|---|---|---|
| a | R-WIP | 2 cartões do mesmo agente, `worktree: principal` e `wt-b` | 2 instâncias, nomes distintos | rc 0 | CLI rc 0; hook rc 0 | passou |
| a2 | R-WIP/R-TETO | 3 cartões, worktrees `p`, `b`, `c` | máximo (3) | rc 0 | rc 0 | passou |
| b | R-WIP | 2 cartões sem o campo | campo ausente | barra com (R-WIP) | CLI rc 1; hook rc 2: `forge:tech-lead com 2 cartões, limite 1 por agente; instância extra exige worktree: <nome> distinto na Obs. ... (R-WIP)` | passou |
| b2 | R-WIP | 2 cartões com a mesma worktree | nome repetido | barra | rc 1, mesma mensagem | passou |
| c | R-TETO | 4 cartões, 4 worktrees distintas | logo acima de 3 | barra | rc 1: `limite 3 instâncias por agente (R-WIP, R-TETO)` | passou |
| c2 | R-TETO | `teto_maximo: 2` em `.forge/config.json`, 3 cartões distintos | teto menor da config | barra | rc 1: `limite 2 instâncias` | passou |
| a3 | R-WIP | 3 cartões, 2 agentes diferentes, 1 a 2 por agente | contagem por agente | rc 0 | rc 0 | passou |
| d | R-TETO | clone do Forge (`.git` + manifesto `forge`, sem `.forge/config.json`): `python3 -m unittest discover -s tests -q` | suíte completa | cria trava `.forge/run/pesado.json` | criada | passou |
| d2 | R-TETO | mesmo clone: `ls -la`, `python3 -m unittest tests.test_forge`, `echo python3 -m unittest discover` | comando comum, suíte parcial, citação | sem trava | nenhuma criada | passou |
| d3 | R-TETO | trava de outra sessão viva, depois a suíte | pesado concorrente | rc 2 | rc 2: `R-TETO: tarefa pesada de outra sessão ou agente...`; `ls` na mesma situação rc 0 | passou |
| e | definição de pronto, develop antes do review | leitura dos textos | n/a | presentes e neutros | `agents/jarvis.md:60` (comando de pronto da raiz, documentação atualizada), `skills/engineering-practices/SKILL.md:30`, `docs/regras/R-FLUXO.md:25`, `agents/tech-lead.md:24` ("uma vez, antes do review") | passou |
| f | hook do quadro aplica a regra | `hooks/quadro.py` PostToolUse/Write sobre os casos a e b | n/a | a passa, b barra | a rc 0; b rc 2 `R-WIP: ...` | passou |
| g | S-11 | leitura | n/a | brief único | `agents/jarvis.md:37` ("brief único") e `skills/kanban-scrum/SKILL.md:93` ("uma devolução só ... brief único") | passou |

## Vermelho antes do verde
Cópia de `HEAD` com `bin/forge-check` e `hooks/pesado.py` trocados pelos de 930d6bb (sem a E2), rodando `python3 -m unittest tests.test_forge tests.test_hooks -q`: `FAILED (failures=5, errors=1)`. Falham `test_instancias_worktrees_distintas_passam`, `test_cartoes_sem_worktree_barram` (3 subcasos), `test_instancias_acima_do_teto_barram` e `test_suite_do_forge_e_pesada` (erro: `pesados_da_raiz` não existe). Com a implementação, a suíte inteira passa. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Observações (sem bug)
- A checagem confia no que o cartão declara (nome da worktree e responsável), como já registrado em B3 e B4 do parecer de segurança (baixos, fora desta entrega, com texto proibindo o contorno em `R-WIP`).
- Três instâncias é o máximo com a config padrão; a leitura de carga real continua com o hook `agentes` (`R-TETO`).

## Bugs
Nenhum aberto.

## Veredito
Aprovado em 694edc7 (conteúdo igual em b8916bb). Suíte de 657 testes e validação do plugin verdes; casos exploratórios a a g passaram; zero bugs.
