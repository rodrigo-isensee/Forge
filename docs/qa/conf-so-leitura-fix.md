---
tipo: qa
contrato: 1
pedido: conf-so-leitura-fix
branch: melhoria/conf-so-leitura-fix
commit: f3d68cb9933219014b82279d730c2dd525393eed
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: conf-so-leitura-fix

Parecer sobre f3d68cb (código); o HEAD da branch é 6d509dc, que só acrescenta os pareceres de review e de segurança. Pedido sem especificação de UX: as obrigações são E1, E2 e E3 do pedido.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (conferente só leitura na sessão do Forge) | CT-01 sonda do hook real, sessão do Forge | permissão: python3, sh, bash -c e redirecionamento recusados (rc=2) | passou |
| E1 (leitura segue livre) | CT-02 sonda do hook real, sessão do Forge e projeto | permissão: git log, diff, show, grep, cat, forge-check, gh pr view liberados (rc=0) | passou |
| E2 (fixtures python3, redirecionamento, git log) | CT-03 suíte completa (`test_fixtures`) | mínimo de 460 fixtures (hoje 822) | passou |
| E1 (vermelho antes do verde) | CT-04 sonda com `hooks/conformidade.json` da base 0f480c8 | sem a linha do conferente, tudo rc=0 | falhou como esperado, verde com a correção |
| E3 (fragmento) | CT-05 suíte completa (testes de changelog) | n/a | passou |
| Plugin válido | CT-06 `scripts/validar-plugin.sh` | n/a | passou |

## Cenários e resultado real
- Pré-suíte: `.githooks/pre-push --status` deu rc=0 (suíte alheia rodando); esperei até rc=1 ("nenhuma suíte do Forge rodando"). `__pycache__` não versionados apagados.
- CT-03/CT-05: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na raiz da worktree: `Ran 1082 tests in 278.031s`, `OK`.
- CT-06: `scripts/validar-plugin.sh`: `Validation passed`, rc=0.
- CT-01/CT-02: cópia `git archive` em `$TMPDIR`, hook `hooks/conformidade.py` chamado com JSON no stdin (`agent_type: forge:conferente`, `hook_event_name: PreToolUse`). Sessão do Forge: cwd fora de projeto, `CLAUDE_PROJECT_DIR` com `.claude-plugin/plugin.json` do Forge. Projeto: repositório com `.forge/versao`.

| Comando | Sessão do Forge | Projeto |
|---|---|---|
| `git log -1` | rc=0, sem saída | rc=0, sem saída |
| `git diff` | rc=0 | rc=0 |
| `git show HEAD` | rc=0 | rc=0 |
| `grep -rn foo .` | rc=0 | rc=0 |
| `cat README.md` | rc=0 | rc=0 |
| `forge-check brief gerar --ajuda` | rc=0 | rc=0 |
| `forge-check entrega` | rc=0 | rc=0 |
| `gh pr view 1` | rc=0 | rc=0 |
| `python3 -c 'print(1)'` | rc=2, "`python3` fora da lista do papel só de leitura (conferente)" | rc=2, mesma mensagem |
| `sh -c 'ls'` | rc=2, "`sh` fora da lista ..." | rc=2, mesma mensagem |
| `bash -c 'ls'` | rc=2, "`bash` fora da lista ..." | rc=2, mesma mensagem |
| `echo x > f.txt` | rc=2, "`>` fora da gramática do papel só de leitura (conferente)" | rc=2, mesma mensagem |
| `cat a > b` | rc=2, "`>` fora da gramática ..." | rc=2, mesma mensagem |

- CT-04 (vermelho): na mesma cópia, com `hooks/conformidade.json` de 0f480c8, a sessão do Forge liberou (rc=0) python3, sh, bash -c e os dois redirecionamentos; o projeto não mudou. Prova que a linha do conferente é o que fecha o furo, só na sessão do Forge.
- Mutação: já feita no review e na segurança (sem a linha, as duas fixtures de recusa falham); não repeti.

## Riscos
Nenhum bug aberto. Fora do escopo, com cartão próprio: a frase em `agents/conferente.md` e o R1 do grep (opções que executam).
