---
id: R-COPIA
titulo: Não copiar agentes e skills para o projeto
verificada_por: revisão (skill iniciar-projeto avisa sobre cópias)
---
# R-COPIA: Não copiar agentes e skills para o projeto

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- Nunca copie agentes ou skills do Forge para `.claude/agents/` ou `.claude/skills/` do projeto para "consertar rápido": a cópia tem prioridade sobre o plugin e vira uma versão paralela que diverge da fábrica.
- Nunca edite o cache do plugin em `~/.claude/plugins/`.
- Projeto que já tem cópias dos agentes do time: avise o usuário e proponha removê-las, para o projeto usar a fábrica.
- O conserto vai ao Forge por PR (skill `contribuir-com-o-forge`) e chega ao projeto pela atualização do plugin.
