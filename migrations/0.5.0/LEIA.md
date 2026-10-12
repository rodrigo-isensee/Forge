# Migração 0.5.0

Para projetos criados antes do `.forge/` (ADR 0005). Cria `.forge/versao` e `.forge/config.json` (padrões) e a linha `.forge/run/` no `.gitignore`. Não sobrescreve nada que exista; rodar de novo não muda nada.
