---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.3
branch: melhoria/v047-release-0473
commit: eb9b4295bd8cafbbd70977f9c9170275b7932982
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: release-0.47.3

Escopo: a leva desde a marca da 0.47.2 (4068c807) até eb9b4295: #610 (docs/práticas), #606 (`tmpdir_da_prova` no `bin/forge-check`) e o commit de versão. Parecer completo (não havia parecer anterior desta release); o #606 tem o parecer próprio `docs/security/v047-prova-tmpdir.md` (aprovado, commit ed99ab1e), relido aqui contra o código final.

Gatilhos: execução de comando e ambiente passado a subprocesso (`tmpdir_da_prova` / `rodar_prova`); o resto da leva é documentação e versão.

## Achados

## Sondas

## Detalhe dos achados
Sem achados. Conferido:
- `bin/forge-check:9030-9051` (`tmpdir_da_prova`): só aceita TMPDIR absoluto, resolvido por `realpath` (symlink não escapa), pasta, do próprio usuário, com escrita e fora da worktree e do clone comum do `.git`. Qualquer falha devolve `None` e a prova roda sem a variável. Sem caminho de ataque realista: o TMPDIR é do ambiente do operador, não da branch revisada.
- `bin/forge-check:9053-9060` (`rodar_prova`): o ambiente continua listado (PATH, LC_ALL, PYTHONDONTWRITEBYTECODE, HOME) e ganha só o TMPDIR validado; sem shell, `stdin` fechado, tempo limitado. Nenhuma outra variável herdada.
- Guardas cobertas por `tests/test_forge_run.py` (classe `TmpdirDaProva`) e pelos 8 mutantes de `tests/mutantes/v047-prova-tmpdir.json`.
- #610: só `docs/engineering/praticas.md` e o teste `PraticasDoForge` (leitura de arquivo do repositório); sem execução nova.
- Versão e changelog: `plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.3, entrada no `CHANGELOG.md`; sem mudança de permissão, workflow ou dependência.
- Segredos: nenhum literal no diff da leva (leitura do diff).

## Riscos aceitos e ferramentas
Sem riscos aceitos. Testes rodados: `python3 -m unittest tests.test_forge_run tests.test_modelos_projeto` (OK); a suíte inteira fica para o CI (R-SEGURANCA). Lacuna: `gitleaks` não está no PATH, então a varredura de segredos foi só por leitura do diff; `shellcheck` presente, sem arquivo de shell na leva.
