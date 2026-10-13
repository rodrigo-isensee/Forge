# 0001 - Núcleo neutro e pacotes de stack

Estado: vigente. Data: 2026-10-12.
Propósito: separar o que vale para qualquer projeto do que depende da stack. Público: quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
Hoje o Forge mistura no mesmo nível o processo da fábrica (Jarvis, review, QA, Kanban, discovery) e uma stack fixa (Node + React, com os agentes `node-backend` e `react-frontend` e as skills de mesmo nome). Um projeto com outra stack herda convenções que não se aplicam a ele, e a regra de neutralidade (`.claude/CLAUDE.md`, "Neutralidade") fica difícil de cumprir: "stack fixa" é justamente o que ela proíbe no núcleo.

Restrições do mecanismo de plugins do Claude Code (manifesto `plugin.json`), a confirmar na implementação:
- `agents` aceita só arquivos `.md`, não pastas, e **substitui** a varredura padrão de `agents/`; subpastas de `agents/` entram no nome do agente.
- `skills` aceita pastas e **soma** à varredura padrão de `skills/`.
- O nome do agente vem do `name` do frontmatter, com o prefixo do plugin (`forge:`).

## Decisão
1. **Núcleo neutro** (fica onde está): `agents/` com `jarvis`, `tech-lead`, `software-architect`, `ux-designer`, `qa-engineer` e `agile-coach`; `skills/` com as skills de processo (`kanban-scrum`, `engineering-practices`, `software-architecture`, `ux-design`, `qa-testing`, `cyber-security`, `iniciar-projeto`); `hooks/` (ADR 0003) e `docs/regras/` (ADR 0002). Nada no núcleo cita linguagem, framework ou banco como obrigatório.
2. **Pacote de stack** em `stacks/<nome>/`, sempre com a mesma forma:
   - `agents/<papel>.md`: os agentes de desenvolvimento da stack;
   - `skills/<nome>/SKILL.md`: convenções da stack;
   - `seguranca.md`: checklist de segurança da stack, que a skill `cyber-security` do núcleo manda aplicar;
   - `pronto.md`: o comando "pronto" sugerido para o `forge-init` e o que ele precisa verificar;
   - `pesados.json` (opcional): lista JSON dos comandos pesados padrão (hook `pesado`), que o `forge-init` grava em `.forge/config.json`.
3. **`stacks/node-react`** recebe o conteúdo atual: agentes `node-backend` e `react-frontend`, skills de mesmo nome e os checklists de API Node, front React e banco que hoje estão na skill `cyber-security`.
4. **Registro no manifesto:** `plugin.json` lista explicitamente cada agente (núcleo e stacks) em `agents` e cada pasta de skills de stack em `skills`. Um teste estrutural confere que todo `.md` de `agents/` e de `stacks/*/agents/` está listado e vice-versa.
5. **Compatibilidade:** os agentes de stack mantêm o `name` atual; `forge:node-backend` e `forge:react-frontend` continuam existindo. Como todas as stacks vivem no mesmo plugin, o nome de um agente de stack leva a tecnologia (ex.: `node-backend`, nunca `backend`) para não colidir com o de outra stack.
6. **O projeto declara a stack** no `CLAUDE.md` (seção "Stack": `node-react`). O `forge-init` ganha `--stack` (padrão `node-react`), preenche a seção e sugere o comando "pronto". O Jarvis lê a stack declarada e só delega aos agentes daquele pacote. Projeto sem a seção é tratado como `node-react` (comportamento atual).

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| Um plugin por stack no mesmo marketplace (`forge-node-react@forge`) | Projeto carrega só a stack que usa; menos tokens de descrição de agentes | O prefixo muda para `forge-node-react:node-backend`, quebrando os projetos (major); dois plugins para instalar e versionar juntos |
| Manter tudo em `agents/` e `skills/` com prefixo no nome | Nenhuma mudança de manifesto | Não separa núcleo de stack; a neutralidade continua sem fronteira verificável |
| Subpastas `agents/stacks/node-react/` | Sem listar arquivos no manifesto | A subpasta entra no nome do agente e quebra `forge:node-backend` |

## Consequências
- Mais fácil: adicionar uma stack é criar uma pasta com forma conhecida; o teste de neutralidade vale com rigor total para o núcleo e ignora só `stacks/`.
- Mais difícil: `plugin.json` passa a listar agentes um a um (o teste do item 4 evita esquecer um); `tests/config.json` (`agentes_obrigatorios`) e o teste do time do Jarvis precisam conhecer `stacks/`.
- Risco: todas as stacks carregam em todo projeto, e as descrições dos agentes ocupam contexto. Aceito enquanto houver até 3 stacks; acima disso, reavaliar um plugin por stack (exigiria versão major).
- Mover arquivos de lugar não muda nada para os projetos (nomes iguais); entra como minor.
