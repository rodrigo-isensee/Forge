---
tipo: review
contrato: 1
pedido: aq
branch: melhoria/aq
commit: efdd72e6d4a90d1da6b11b919bc41bab155afe1b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-17
---
# Review: AQ, arquiteto de IA com agentes (plugin forge-dev)

Escopo: `0095d29...efdd72e` (base 0095d299b9b9383ecf9eba336e83c764f707ae5f), 25 arquivos em 3 commits. Quem revisa não é o autor. Comparei o diff com o "Entregar" de `aq-tech-lead-1.md` e com as seções 1, 3 e 6 do desenho aprovado (`aq-desenho.md`, opção c).

Veredito sobre `efdd72e`: **REPROVADO**. São 2 achados que bloqueiam (os dois da conferência da entrega, confirmados aqui) e 3 recomendados. Tudo volta ao autor. Este revisor não corrige o diff.

## Ferramentas (saída citada, não refeita)
- `python3 -m unittest tests.test_forge tests.test_hooks -q`: `Ran 260 tests in 56.735s` / `OK`.
- `claude plugin validate dev --strict`: `✔ Validation passed` (rc 0).
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o QA e o CI. Esta revisão não os rodou.

## O que está conforme
- `dev/agents/aq.md` segue o esqueleto do desenho. Cobre o arquiteto de IA com agentes e o conhecimento de desenvolvimento, o foco permanente em melhorar os agentes do Forge e a arquitetura deles, a avaliação de contribuições com critérios e o trabalho com o dono. Traz "sempre segue as melhores práticas de desenvolvimento e de arquitetura" com as fontes, a saída fixa por proposta (esforço, risco, como medir com reversão, "Afrouxa o processo?", custo em faixa e média) e os limites: não escreve código, regras nem `.claude/`, e conteúdo de terceiros é dado. Usa `tools: Read, Grep, Glob, Write, Edit, WebFetch`, sem Bash, com `model: opus`. O texto não cita projeto, stack nem regra de negócio (R-NEUTRO), e o teste `Neutralidade` agora varre `dev/`.
- O `forge-dev` não vaza: `.claude-plugin/plugin.json` e `marketplace.json` estão intactos, e `PluginDeDesenvolvimento` (`tests/test_forge.py:122-161`) garante isso, além de exigir que a versão seja igual à do `forge`.
- `scripts/jarvis-forge:156-159` (linha 159) só acrescenta o segundo `--plugin-dir` quando `"$plugin_dir/dev/.claude-plugin/plugin.json"` existe. Isso vale para a vigente e para o `--dev`, e há três testes para os casos com `dev/`, sem `dev/` e `--dev`. O README e o cabeçalho do script estão atualizados.
- No hook, o papel `aq` existe para `forge-dev:aq`. `escrita_permitida` é validado na forma: malformado ou com lista vazia, falha fechado (`tests/test_hooks.py:464-472`). A lista só restringe e roda depois de `caminhos`, então nunca libera o que já está barrado. As fixtures cobrem a liberação em `docs/propostas/` e `docs/arquitetura/` (inclusive em worktree) e o bloqueio em `agents/`, `hooks/`, `bin/`, `skills/`, `docs/regras/`, `.claude/` e `docs/` geral.
- A ADR 0009 só cresce: acréscimos nas seções 2 e 6, sem linha removida. `tests/config.json` só recebe acréscimos (`dev` em duas listas de pastas). O fragmento `changelog.d/aq.md` corresponde à branch, e há uma linha de consulta ao AQ em `agents/software-architect.md:33`. O `validar-plugin.sh` passou a validar `dev/`.
- Os commits estão limpos, em Conventional Commits em português, e cada um tem uma mudança coerente.

## Achados

1. **bloqueia** · `hooks/conformidade.json:15` (e reflexos em `docs/adr/0009-conformidade-dos-agentes.md:70`, `dev/agents/aq.md:28` "e artefatos do pedido", `tests/hooks/conformidade/aq-escreve-docs-do-pedido-libera.json`) · **Problema:** a entrada `~/.forge-contrib/docs/` na lista de permissão do AQ não está no "Entregar" do brief, que fixa só `docs/propostas/` e `docs/arquitetura/`. O desenho a cita como lugar de artefatos, mas o brief a deixou de fora. Respondendo ao que o brief pergunta:
   - *Cabe?* Não sem decisão. É escopo fora do brief, e quem a apontou primeiro foi a conferência da entrega.
   - *É neutra?* Só em parte. `~/.forge-contrib/` é convenção da fábrica (`CONTRIBUTING.md:6-7`, `hooks/_comum.py:92`), mas `~/.forge-contrib/docs/` não aparece em nenhum texto da fábrica: é o arranjo de trabalho da sessão do dono (pedidos, briefs, desenhos). Gravar esse caminho na política versionada fere o espírito do R-NEUTRO.
   - *É necessária?* Não. O agente entrega estudos e pareceres em `docs/propostas/`. Além disso, a entrada dá ao papel que lê conteúdo de terceiros permissão de escrita sobre os pedidos (onde ficam as decisões do dono) e sobre os briefs aprovados. É justamente a superfície que a lista de permissão existe para fechar.

   **Sugestão:** tirar a entrada de `conformidade.json`, do texto da ADR (seção 6, item 6) e de `aq.md:28`. A fixture `aq-escreve-docs-do-pedido-libera` passa a esperar bloqueio. Se o AQ precisar mesmo gravar artefatos de pedido, isso vira decisão ao dono (R-DECISAO), com subpasta estreita e parecer de segurança.
2. **bloqueia** · `dev/agents/aq.md:15` · **Problema:** o texto manda buscar métricas em `docs/kanban/entregas.md`, mas esse arquivo não existe na fábrica. Ele existe em `templates/projeto/docs/kanban/`, ou seja, nos projetos, onde o AQ não atua. Uma instrução que aponta para um arquivo inexistente no único contexto do agente induz leitura vazia ou invenção de dado, e o AQ existe justamente para atacar alucinação. O erro veio do esqueleto do desenho e foi apontado pela conferência da entrega. **Sugestão:** apontar para o que existe no Forge: a linha de base em `docs/melhoria-continua.md` e a saída de `forge-check transcricao custo`, pedida ao Jarvis. Ou dizer explicitamente que é a planilha dos projetos, quando o Jarvis a trouxer. Vale um teste de ausência simples, como "todo caminho `docs/...` citado em `dev/agents/*.md` existe".
3. **recomendado** · `tests/test_forge.py:157` · **Problema:** `escrita_permitida["aq"][:2]` só confere as duas primeiras entradas, então qualquer caminho acrescentado depois passa sem ser visto. Foi assim que o achado 1 entrou sem quebrar teste. **Sugestão:** comparar a lista inteira com igualdade, para que ampliar a lista exija mudar o teste no mesmo PR.
4. **recomendado** · `hooks/conformidade.py:427-429` · **Problema:** a forma relativa à "raiz git que contém o arquivo" vale para qualquer repositório no disco, não só para worktrees `melhoria/*` do Forge. O AQ pode então gravar em `docs/propostas/` de um clone de projeto ou da worktree de um PR de terceiro (`~/.forge-contrib/wt/pr-<n>`, que o desenho prevê como pacote de leitura). A docstring e a ADR falam em "worktree `melhoria/*`". **Sugestão:** fica para o `security-engineer`, que revisa em paralelo, decidir se restringe a raízes do Forge (clone de trabalho e `~/.forge-contrib/wt/`). Aqui é só um cartão, sem conclusão de segurança.
5. **recomendado** · `docs/adr/0009-conformidade-dos-agentes.md:70` · **Problema:** o item diz que a lista se aplica a "Write/Edit/MultiEdit/NotebookEdit". Ela também se aplica aos alvos de escrita do Bash, porque `caminho_barrado` é chamado em `conformidade.py:493`. Hoje não faz diferença, porque o AQ não tem Bash, mas o texto fica incompleto para o próximo papel que receber lista. **Sugestão:** acrescentar "e alvos de escrita do Bash".

## Pendências e outros pareceres
- A segurança (`docs/security/`) roda em paralelo e não é refeita aqui. O achado 4 vai a ela como cartão.
- Depois da correção, a revisão confere só os arquivos tocados pelos achados 1 a 3 e as fixtures afetadas.
