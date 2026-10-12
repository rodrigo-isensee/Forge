# Migração 0.5.0

Para projetos criados antes do `.forge/` (ADR 0005). Cria `.forge/versao` e `.forge/config.json` (padrões), acrescenta a linha `.forge/run/` ao `.gitignore` e marca como anteriores ao contrato (`contrato: 0`, ADR 0004) os documentos de `docs/reviews/`, `docs/qa/` e `docs/architecture/features/` sem frontmatter (exceto `README.md` e `_*.md`). Não sobrescreve nada que exista, só acrescenta; rodar de novo não muda nada.
