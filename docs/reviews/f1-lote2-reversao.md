---
tipo: review
contrato: 1
pedido: f1-lote2-reversao
branch: melhoria/f1-lote2-reversao
commit: de1e3af
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: lote 2 da fonte F1 (critério de reversão e mecanismo novo)

Escopo: modelo de ADR (`docs/adr/_modelo.md` e `templates/projeto/docs/architecture/adr/_modelo.md`), formato de experimento (`docs/melhoria-continua.md` e `melhorias.md` do modelo), linhas no arquiteto, no `tech-lead`, no checklist de review e na skill de contribuição, invariantes e CHANGELOG. ADRs antigas intactas; `R-NEUTRO`: fonte só como F1.

Verificação: testes (310) e `scripts/validar-plugin.sh` verdes.

Pendência: campo "o que já existe e por que não basta" em `.github/pull_request_template.md` (`.github/` é protegido; registrada no CHANGELOG).

Parecer de autor, sujeito a review independente (`R-REVIEW`).

## Review independente

Escopo: `origin/develop...de1e3af` (HEAD revisado, com o parecer de autor acima). Revisor: `forge:tech-lead`.

Verificação:
- `python3 -m unittest discover -s tests` numa worktree destacada em `de1e3af`: **310 testes, OK**.
- `scripts/validar-plugin.sh`: **validação passou**. Os bloqueios de rede do sandbox (telemetria) não afetaram o resultado.
- `bin/forge-check docs`: sem saída de erro.

Achados:
1. **bloqueia** · `skills/software-architecture/SKILL.md:22-38` · a skill que define o formato da ADR (carregada pelo arquiteto) não tem "Critério de reversão", "Leituras" nem "Por que o existente não basta", e usa `Status: proposta | aceita`, enquanto o `_modelo.md` usa `Estado:` (padrão de documentação). O arquiteto recebe duas instruções: o princípio novo exige critério de reversão, e a skill que ele segue não pede. Sugestão: alinhar a skill ao `_modelo.md` (seções e linha `Estado:`), apontando para o modelo em vez de copiar o texto. Falta a exigência "nas skills" do pedido.
2. **recomendado** · `tests/config.json`, bloco `invariantes` · o modelo de ADR do projeto (`templates/projeto/docs/architecture/adr/_modelo.md`) não tem invariante; o do Forge tem. Remover as seções do modelo do projeto não quebra teste algum. Sugestão: incluir o mesmo trio de trechos para esse caminho. Vale também para o cabeçalho novo de `templates/projeto/docs/kanban/melhorias.md`.
3. **recomendado** · `docs/adr/README.md:3` · `Revisão: 2026-10-12` não foi atualizada, embora o conteúdo mudou (`docs/padrao-de-documentacao.md`, linha 15: "Atualize a data de revisão sempre que o conteúdo mudar"). Sugestão: `Revisão: 2026-10-13`.

Verificado sem achado:
- Nome real da fonte: ausente do diff e dos arquivos novos; só aparece o código F1.
- Citações por ID: as linhas novas apontam para `_modelo.md` e não repetem texto de regra (ADR 0002).
- Colisão com o `forge-init`: copia `templates/projeto` sem sobrescrever; o único arquivo novo, `docs/architecture/adr/_modelo.md`, não colide com nada copiado. O padrão de ADR é `NNNN-titulo.md`, que não casa com `_modelo.md`.
- Invariantes: os trechos protegidos (`docs/adr/_modelo.md`, `skills/engineering-practices/SKILL.md`, `docs/melhoria-continua.md`, `agents/tech-lead.md`, `agents/software-architect.md`) existem no texto e estão nos lugares certos.
- Concisão: as linhas novas são curtas e sem repetição de texto entre arquivos, exceto a exigência, que aparece em quatro lugares (aceitável como ponteiro, mas a skill de ADR precisa dela, achado 1).

Parecer: **reprovado** por ajustes necessários. Bloqueia o achado 1; os achados 2 e 3 são recomendados. A correção vai para o autor (`melhoria/f1-lote2-reversao`); depois, novo review sobre o HEAD novo.
