---
tipo: review
contrato: 1
pedido: aq
branch: melhoria/aq
commit: 03789a2e9656b85648d3701c02ba72c9b3f99f10
parecer: aprovado
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

## Revalidação após a volta única
Escopo: `6060bec..679aaf1` (commits `e812309` e `679aaf1`), 10 arquivos. Conferi cada achado acima contra esse diff e reli só os arquivos tocados. Veredito sobre `679aaf17dcd55fc74183c95476621e50df534ddc`: **APROVADO**.

### Ferramentas (saída citada)
- `python3 -m unittest tests.test_forge tests.test_hooks -q`: `Ran 263 tests in 53.840s` / `OK`. O teste novo de falha fechada rodou de fato, sem skip.
- `claude plugin validate dev --strict`: `✔ Validation passed` (rc 0).
- `git diff 0095d29...679aaf1 -- tests/config.json docs/adr/0009-conformidade-dos-agentes.md | grep -cE '^-[^-]'`: `0`. Nada anterior ao PR foi removido. A linha da seção 6 trocada no `679aaf1` é a que o próprio PR tinha acrescentado.
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o QA e o CI.

### Achados do parecer anterior
1. **Resolvido.** `~/.forge-contrib/docs/` saiu de `hooks/conformidade.json:15`, da ADR 0009 (seção 6, item 6) e de `dev/agents/aq.md:28`. A fixture foi renomeada para `aq-escreve-docs-do-pedido-bloqueia.json` e espera saída 2 em `~/.forge-contrib/docs/pedidos/`. `grep` por `forge-contrib/docs` em `dev/`, na política e na ADR não acha nada.
2. **Resolvido.** `dev/agents/aq.md:15` agora aponta para a linha de base de `docs/melhoria-continua.md`, que existe. O teste de ausência sugerido entrou: `test_caminhos_citados_pelos_agentes_de_dev_existem` exige que todo `docs/...md` citado em `dev/agents/*.md` exista, com mínimo de itens (`minimo`).
3. **Resolvido.** `tests/test_forge.py:157` compara o mapa `escrita_permitida` inteiro por igualdade, então ampliar a lista ou dar lista a outro papel exige mudar o teste.
4. **Resolvido** (a decisão foi da segurança). Em `hooks/conformidade.py:429-430`, a forma relativa à raiz git só vale se essa raiz for cópia do Forge (`e_clone_do_forge`) e estiver em `~/.forge-contrib/` ou for a raiz do projeto. A nova fixture `aq-arquitetura-em-outro-repositorio-bloqueia.json` cobre outro repositório, e as fixtures de worktree ganharam o manifesto do Forge.
5. **Resolvido.** O item 6 da ADR cita os "alvos de escrita do Bash".

### Pontos trazidos pela volta, todos conformes
- `WebFetch` saiu das ferramentas do AQ, conforme a decisão técnica do pedido. A instrução diz que pesquisa externa chega a ele como dado, pelo Jarvis ou pelo `software-architect`. O teste do manifesto barra `Bash` e `WebFetch`.
- Falha fechada em erro interno (`conformidade.py:1285-1293`): só a chamada a `decidir` fica no `try`. `bloquear` encerra com `SystemExit`, que não é `Exception`, então as decisões normais passam intactas. Papel sem lista e `PostToolUse` relançam e seguem a regra geral da seção 7. O teste cobre os dois lados (`aq` barra, `dev` libera).
- `test_dev_so_tem_manifesto_e_agentes` limita `dev/` ao manifesto e a `agents/*.md`, com mínimo de itens.
- Os commits estão limpos, em Conventional Commits em português, um por grupo de achados e sem `--amend`. O `changelog.d/aq.md` continua correto e não precisou mudar.

### Observação (não bloqueia)
- `politica()` e a construção de `Guarda` ficam fora do `try` (`conformidade.py:1281-1284`). Hoje isso está coberto: a política malformada já falha fechado, e o papel ainda não é conhecido antes da `Guarda`. Fica só o registro, para quem mexer ali depois.

### Outros pareceres
- A revalidação da segurança (`docs/security/aq.md`) roda em paralelo e não é refeita aqui. Quem decide o achado 4 do ponto de vista de segurança é ela.


## Revalidação após a segunda volta
Escopo: `4fcaf22..c8acc52` (commits `96a21aa` e `c8acc52`), 8 arquivos: `hooks/conformidade.py`, cinco fixtures `aq-sessao-forge-*`, a ADR 0009 e `changelog.d/aq.md`. Conferi o achado 8 da segurança e a observação acima contra esse diff e reli só os trechos tocados (`principal`, `Guarda` na linha 430, `identificar_sessao`, `politica`). Veredito sobre `c8acc52ededd96fb9c0159d19308feca63b95237`: **APROVADO**.

### Ferramentas (saída citada)
- `python3 -m unittest tests.test_forge tests.test_hooks -q`: `Ran 263 tests in 52.987s` / `OK`. As fixtures novas rodam como subTest do laço de fixtures (`tests/test_hooks.py:230-236`), por isso o total não muda.
- `claude plugin validate dev --strict`: `✔ Validation passed` (rc 0).
- A suíte completa e o `scripts/validar-plugin.sh` ficam com o QA e o CI.

### Achado 8 da segurança: resolvido
- `principal` (`conformidade.py:1278-1288`): quando `identificar_sessao` devolve `False`, o papel com `escrita_permitida` segue avaliado se a raiz declarada for clone do Forge e o evento não for `PostToolUse`. A raiz da sessão vira `hook.raiz` e `externo` fica `None`. Os outros papéis continuam saindo sem guarda, como antes.
- `Guarda` (`conformidade.py:430`): a raiz extra usa `raiz_declarada()` quando `hook.raiz` vem `None`. Se as duas faltarem, o `realpath(None)` levanta erro, e para o `aq` isso cai na falha fechada.
- As fixtures cobrem o que o brief pede, todas com `CLAUDE_PROJECT_DIR` num clone do Forge e a pasta corrente em `~`. O `aq` é barrado em `agents/` do Forge, em `agents/` de uma worktree `melhoria/*` e em `~/.forge-contrib/docs/pedidos/`. É liberado em `docs/propostas/`. O `forge:dev` grava em `agents/` sem guarda, como hoje.
- A ADR 0009 muda só na linha 70, que este PR acrescentou. O texto ganha a frase sobre a sessão do Forge e nada anterior ao PR sai. O `changelog.d/aq.md` acompanha a mudança.

### Observação sobre `conformidade.py:1281-1284`: resolvida, com justificativa
- A construção da `Guarda` e a marcação da sessão entraram no `try`. O `politica()` ficou fora, com comentário: o papel só se conhece depois dela, e política malformada já falha fechado por conta própria. O motivo procede.

### Ponto novo trazido pela volta (recomendado, não bloqueia)
- `conformidade.py:1279`: o `politica()` passou para antes do `return` de `externo is False`. Em qualquer sessão fora de projeto, o arquivo agora é lido e validado em toda chamada de ferramenta, para todos os papéis. Com política malformada, essas chamadas passam a ser barradas, quando antes o hook ficava calado. Isso só acontece com defeito no `conformidade.json` versionado, que a suíte já pega, e falhar fechado nesse caso é coerente com a seção 7. Fica registrado para o QA conferir e para quem mexer ali depois. **Sugestão:** se a leitura extra pesar, carregar a política só quando houver raiz do Forge.

### Outros pareceres
- A revalidação da segurança (`docs/security/aq.md`) roda em paralelo na mesma worktree e não é refeita aqui.

## Revalidação após a terceira volta (03789a2)
- A volta tocou só a fixture `aq-arquitetura-em-outro-repositorio-bloqueia.json`: o caminho fictício `home/proj-x` virou `outro-repo/proj-x` (arquivo, `HOME` e chave de `repos`), para a bateria não apontar caminho pessoal. Nada mais mudou.
- O teste prova o mesmo: o `forge-dev:aq` escrevendo em `docs/arquitetura/` de outro repositório git é barrado ("o papel aq escreve só em").
- `python3 -m unittest tests.test_hooks -q`: `Ran 16 tests` / `OK`.
- Parecer mantido: **aprovado**.
