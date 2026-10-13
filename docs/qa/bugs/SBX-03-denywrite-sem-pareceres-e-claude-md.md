# SBX-03 - `denyWrite` do Forge não cobre `docs/reviews/`, `docs/qa/` nem `CLAUDE.md`; a matriz do ADR 0009 promete
- Status: aberto (achado na revalidação 6e0ff68)
- Severidade: média (integridade de processo: o parecer pode ser gravado por Bash sem passar pelo hook de autoria; não é perda de dados nem vazamento)
- Responsável sugerido: dono do Forge (`.claude/settings.json` é protegido, R-DECISAO), com `software-architect` para alinhar o ADR 0009 e o README ao que for decidido
- Ambiente: branch `melhoria/sandbox-bash-r1`, commit 6e0ff68, Linux/WSL2, bubblewrap; sessão com a configuração ativa (anterior à branch)

## Passos para reproduzir
1. Na raiz do Forge (ou na worktree), com o sandbox ativo: `printf 'probe\n' > docs/qa/.sonda-qa && rm docs/qa/.sonda-qa`
2. Repetir com `docs/reviews/.sonda-qa`.
3. Conferir `.claude/settings.json` da branch: `sandbox.filesystem.denyWrite` não contém `docs/reviews/`, `docs/qa/` nem `CLAUDE.md`.

## Resultado esperado
Escrita por Bash bloqueada em `docs/reviews/`, `docs/qa/` e `CLAUDE.md`. O ADR 0009, seção 3 (matriz), marca "Escrever parecer em `docs/reviews/` / `docs/qa/`" como "Bash: `denyWrite` no sandbox [I]", e a seção 5 lista esses caminhos em `denyWrite` do `.claude/settings.json` do Forge.

## Resultado obtido
- Probe em `docs/qa/` com a configuração ativa: escrita concluída (rc 0), arquivo removido, árvore limpa.
- Probe em `docs/reviews/`: escrita concluída.
- `denyWrite` da branch: `.forge/`, `.githooks/`, `.claude-plugin/`, `.github/`, `tests/config.json`, `tests/catraca.py`, `tests/neutralidade.py`, `hooks/conformidade.json`. Sem `docs/reviews/`, `docs/qa/` nem `CLAUDE.md`.
- O README (seção "Sandbox do Bash", item Escrita) também não lista esses caminhos; a lacuna está entre o ADR 0009 e a implementação, não só no arquivo.

## Evidência
Saída dos probes acima (rc 0 nos dois) e a leitura de `.claude/settings.json` e `docs/adr/0009-conformidade-dos-agentes.md` (linhas da seção 3, "Escrever parecer", e da seção 5, "denyWrite para ..."). O ADR também diz, na seção 4, que o "Andamento" da etapa 1 cobre só os arquivos em vigor; se o dono decidir que `docs/reviews/` e `docs/qa/` ficam para outra etapa, a ação correta é registrar isso no ADR e no README como limite, e não manter a linha "[I]" da matriz.
Risco: um agente pode gravar o parecer por Bash (`printf ... > docs/qa/...`) e o hook de autoria (`PostToolUse` só em Write/Edit) não registra a autoria.
