# Contribuir com o Forge

Qualquer pessoa ou agente, em qualquer projeto, pode propor uma melhoria de fábrica (agentes, skills, fluxo, modelos, hooks, testes, CI). Decisão: `docs/adr/0006-contribuicao-de-qualquer-projeto.md`. O passo a passo completo está na skill `skills/contribuir-com-o-forge/SKILL.md`.

## Como
1. Use um clone próprio (`~/.forge-contrib/<projeto>`), nunca uma worktree de outro clone nem o cache do plugin.
2. Com acesso de escrita: branch `melhoria/<assunto>` a partir da `develop` atualizada (`git switch --no-track -c`; envio com `git push origin <branch>`, sem `-u`; worktrees com `git worktree add --no-track`: em `~/.forge-contrib/wt/` na sessão do Forge, em `~/.forge-contrib/<projeto>-wt/` na de outro projeto). Sem acesso: fork (`gh repo fork`) e a mesma branch no fork.
3. Uma melhoria por PR, com o PR **para a `develop`**. Nunca envie para `develop`, `homolog` ou `main`; a `main` só muda por PR mesclado pelo usuário.

## Checagens antes do PR
```bash
python3 -m unittest discover -s tests -v
scripts/validar-plugin.sh                  # cópia limpa em $TMPDIR (o sandbox suja a raiz; o CI usa claude plugin validate . --strict)
scripts/verificar-contribuicao.sh
```
- Acrescente uma linha em `## [Não publicado]` do `CHANGELOG.md`. **Não** suba a versão: ela é decidida na release.
- Neutralidade: nada de nome, regra de negócio, dado pessoal ou trecho de código do projeto de origem.
- Não afrouxe `invariantes` nem `termos_proibidos_hash` de `tests/config.json` sem destacar no título do PR e explicar o motivo.
- Nada que custe dinheiro entra sem autorização expressa do usuário.

## CI local (`ci-local`)
```bash
scripts/ci-local <número do PR>              # roda a bateria e imprime uma linha por job
scripts/ci-local <número do PR> --publicar   # grava o resultado como commit status `ci-local` no PR
```
- Roda os mesmos `run:` de `.github/workflows/ci.yml` e `catraca.yml` do PR, numa worktree temporária no sha exato da cabeça do PR, com `nice -n 10`. Custo zero (`R-CUSTO`).
- Enquanto o GitHub Actions estiver sem cota, o status `ci-local` vale como portão local (decisão do dono, opção A, 2026-10-14): o `tech-lead` só mescla com ele verde.
- Obrigatórios: todos os jobs, menos `workflows` (actionlint e zizmor só rodam se já estiverem no PATH). Job "pulado" porque não se aplica ao PR (`if:` do workflow) não reprova; pulado por ferramenta ausente (`claude`, `shellcheck`) num job obrigatório reprova (`failure`).
- Limite conhecido: a catraca libera violações pelo rótulo `afrouxa-regra` só com execução do Actions registrada para o sha; sem Actions, o job `catraca` de PR com rótulo falha localmente, e a decisão fica com o dono.

## Texto do PR
Siga `.github/pull_request_template.md`: projeto de origem, situação observada, o que muda e como medir o efeito. Descreva a situação sem dados do projeto, porque o PR pode ser público.
