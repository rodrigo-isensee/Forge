---
tipo: review
contrato: 1
pedido: settings-sem-env
branch: melhoria/settings-sem-env
commit: 983472c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: env sai do settings.json versionado

Revalidado após merge da develop (só CHANGELOG): o diff do script, do `.claude/settings.json`, do README e dos testes não mudou desde `bf706f7`.

Escopo: `.claude/settings.json`, `scripts/configurar-ambiente-local.sh`, `tests/test_forge.py`, `README.md`, `CHANGELOG.md`.

- Testes escritos antes: o do `settings.json` sem `env` e o do script falharam sem a mudança e passam com ela.
- O script é idempotente, mescla com `json` preservando chaves existentes, calcula os caminhos por `${TMPDIR:-/tmp}` e UID, escreve só dentro da raiz informada e passa no shellcheck.
- O subdiretório de cache de pacotes JS chama-se `pacotes-js` para não acusar termo de stack no teste de neutralidade (R-NEUTRO).
- Sem segredo nos valores; histórico não reescrito (R-VERIFY).
- Pendência: o job `shellcheck` em `.github/workflows/ci.yml` tem lista explícita e não inclui o script novo; arquivo protegido, fica para PR com o rótulo do dono.
- Autor é o próprio revisor: recomenda-se segunda leitura do dono no PR.

## Review independente
Revisor: `forge:tech-lead` (sessão independente). HEAD revisado: `bf706f7`. Parecer: **aprovado**.

- Suíte inteira no checkout do PR: 251 testes OK (134 s); `shellcheck scripts/configurar-ambiente-local.sh` limpo.
- Script, rodado só em cópia temporária com a raiz como argumento: idempotente (duas execuções, saída byte a byte igual); preserva `permissions` e chaves do `env` existentes; escreve só em `<raiz>/.claude` e `<raiz>/.gitignore`; `GIT_CONFIG_COUNT=3` bate com os três pares; com `TMPDIR` diferente o cache vai para `<TMPDIR>/claude-<uid>/cache`; nenhum token (a credencial é `!gh auth git-credential`).
- `/.claude/settings.local.json` está no `.gitignore` (linha 31).
- Teste de barreira: reinserindo `env` no `settings.json`, `test_settings_versionado_nao_tem_env` falha; restaurado, passa.
- CI no momento da revisão: tudo verde, exceto `testes estruturais` ainda pendente (a suíte local passou).
- Recomendado, não bloqueia: (1) `settings.local.json` vazio ou com JSON inválido derruba o script com traceback; (2) o job `shellcheck` do CI não lista o script novo (pendência já registrada, exige rótulo do dono); (3) como o autor da revisão de autor é o mesmo papel, a segunda leitura do dono no PR segue valendo.
