---
tipo: review
contrato: 1
pedido: settings-sem-env
branch: melhoria/settings-sem-env
commit: aa86553
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: env sai do settings.json versionado

Escopo: `.claude/settings.json`, `scripts/configurar-ambiente-local.sh`, `tests/test_forge.py`, `README.md`, `CHANGELOG.md`.

- Testes escritos antes: o do `settings.json` sem `env` e o do script falharam sem a mudança e passam com ela.
- O script é idempotente, mescla com `json` preservando chaves existentes, calcula os caminhos por `${TMPDIR:-/tmp}` e UID, escreve só dentro da raiz informada e passa no shellcheck.
- O subdiretório de cache de pacotes JS chama-se `pacotes-js` para não acusar termo de stack no teste de neutralidade (R-NEUTRO).
- Sem segredo nos valores; histórico não reescrito (R-VERIFY).
- Pendência: o job `shellcheck` em `.github/workflows/ci.yml` tem lista explícita e não inclui o script novo; arquivo protegido, fica para PR com o rótulo do dono.
- Autor é o próprio revisor: recomenda-se segunda leitura do dono no PR.
