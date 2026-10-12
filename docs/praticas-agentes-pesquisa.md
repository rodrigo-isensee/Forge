# Práticas atuais para desenvolvimento com agentes de código

Pesquisa feita em 2026-10-11. Legenda: [DOC] documentação oficial (lida nesta pesquisa), [ART] artigo ou relato, [INF] inferência minha.
Fontes principais (lidas): B = https://code.claude.com/docs/en/best-practices ; S = https://code.claude.com/docs/en/sub-agents ;
C = https://code.claude.com/docs/en/costs ; X = https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents ;
SEC = https://code.claude.com/docs/en/security

## 1. Premissa central
- O contexto é o recurso mais escasso; o desempenho cai conforme ele enche. Quase toda boa prática deriva disso. [DOC: B]
- Buscar "o menor conjunto de tokens de alto sinal"; carregar sob demanda (just-in-time), compactar, anotar fora do contexto, delegar a subagentes. [ART: X]

## 2. CLAUDE.md e definições de agentes
1. CLAUDE.md é carregado em toda sessão: só o que vale sempre (comandos que Claude não adivinha, estilo fora do padrão, etiqueta de repositório, decisões de arquitetura, pegadinhas). [DOC: B]
2. Teste por linha: "remover isso causaria erro?" Se não, cortar. CLAUDE.md inchado faz o agente ignorar regras reais. [DOC: B]
3. Não incluir: o que se deduz lendo o código, estrutura de pastas arquivo a arquivo, documentação de API longa, informação volátil. [DOC: B]
4. Meta: menos de 200 linhas; instruções de fluxo específico (revisão de PR, migração) vão para skills, que carregam sob demanda. [DOC: C]
5. Regra ignorada repetidamente: encurtar o arquivo, ou converter em hook (determinístico). Ênfase ("IMPORTANT") só em uma ou duas linhas. [DOC: B]
6. `/doctor` propõe cortes do que é derivável do código; `/context` mostra o que foi carregado. [DOC: B]
7. Subagentes carregam o CLAUDE.md (exceto Explore/Plan) mas não herdam histórico nem auto memory; logo CLAUDE.md grande é custo multiplicado por agente. [DOC: S] + [INF]
8. `description` de agente deve ser curta (aviso de startup acima de ~15 mil tokens somados); detalhe vai no prompt de sistema, que só carrega quando o agente roda. [DOC: S]
9. Skills: `description` diz quando usar; `disable-model-invocation: true` para fluxos com efeito colateral. Skills com corpo grande: separar referências em arquivos. [DOC: B]
10. Instruções de compactação podem ir no CLAUDE.md ("ao compactar, preserve lista de arquivos modificados e comandos de teste"). [DOC: B, C]

## 3. Design de subagentes
1. Um papel claro por agente; `description` com "use proactively" quando a delegação deve ser automática. [DOC: S]
2. Ferramentas mínimas: `tools` é allowlist (omitir = herda tudo); `disallowedTools` é denylist. Revisor: Read, Grep, Glob (+Bash se rodar testes). [DOC: S, B]
3. Modelo por tarefa: `model: haiku/sonnet/opus/inherit`; `effort` por agente. Sonnet para a maioria, Opus só para arquitetura/raciocínio complexo, Haiku para tarefas simples. [DOC: S, C]
4. Subagente retorna só um resumo ao principal: use para pesquisa, logs, testes verbosos. Não serve para tarefas com muito vai-e-vem ou contexto compartilhado entre fases. [DOC: S, C]
5. Prompt de delegação específico: arquivos, restrições, padrão a seguir, critério de pronto e formato de retorno curto. Prompts vagos geram varredura ampla. [DOC: B, C]
6. Subagentes não conversam entre si nem com o usuário (AskUserQuestion removido); aninhamento até 3 níveis por padrão, limite de 20 simultâneos (configuráveis). [DOC: S]
7. `memory: project` dá ao agente um diretório persistente (primeiras 200 linhas/25 KB de MEMORY.md entram no prompt). Útil para lições do agente; vigiar o tamanho. [DOC: S]
8. Agent teams: experimental, desligado por padrão, ~7x mais tokens que sessão comum. Preferir subagentes + worktrees. [DOC: C]

## 4. Contexto e custo de tokens
1. `/clear` entre tarefas não relacionadas; após 2 correções falhas na mesma questão, limpar e reescrever o prompt. [DOC: B, C]
2. Prompt cache automático: reduz custo de prefixo repetido. Pausa maior que o TTL (1 h assinatura; 5 min por API key) perde o cache; mudar definições de ferramentas ou CLAUDE.md no meio da sessão também invalida. Ver linha "Prompt cache" em `/usage`. [DOC: C]
3. Compactar de forma dirigida (`/compact <foco>`); compactar contexto grande é uma requisição grande, `/clear` é grátis. [DOC: B, C]
4. Prompts específicos ("validação no login em auth.ts") reduzem leituras; evitar "investigue" sem escopo. [DOC: B, C]
5. Preferir CLI (`gh`) a MCP; servidores MCP têm definições adiadas (tool search), ainda assim desligar os não usados. [DOC: C]
6. Hooks podem pré-processar saída (filtrar só falhas de teste) antes de chegar ao modelo. [DOC: C]
7. Thinking: reduzir `/effort` em tarefas simples; em modelos 5.5 não dá para desligar thinking. [DOC: C]
8. Plano só quando incerto ou multi-arquivo; se o diff cabe em uma frase, pular. [DOC: B]
9. Subagentes somam requisições próprias ao consumo; o breakdown de `/usage` atribui custo a skills, subagentes, plugins e MCP. [DOC: C]
10. Não reler: pedir ao agente que escreva notas/estado em arquivo (KANBAN.md, spec) e retome daí. [ART: X] + [INF]

## 5. Paralelismo seguro
1. Worktrees: sessões CLI em checkouts git isolados; subagente com `isolation: worktree` (removido sozinho se não houve mudança; Bash confinado ao worktree). [DOC: B, S]
2. `/batch` e `claude -p` em loop para fan-out; testar em 2-3 itens antes de rodar tudo; `--permission-mode dontAsk` + `--allowedTools` em execução sem supervisão. [DOC: B]
3. Escopos de arquivo disjuntos por agente (back em `server/`, front em `web/`) e um único dono por arquivo compartilhado. [INF]
4. Commits explícitos por caminho (`git add <arquivos>`), nunca `git add -A` em árvore compartilhada; um commit por responsabilidade. [INF] (consistente com a regra de checkpoints: Bash fora do rastreio, git é a rede de segurança [DOC: B])
5. Checkpoints (`/rewind`) cobrem só edições por ferramenta de arquivo, não Bash; não substituem git. [DOC: B]
6. Reviewer em contexto novo (padrão Writer/Reviewer) evita viés do autor. [DOC: B]

## 6. Verificação
1. Dar ao agente uma checagem executável (testes, build, lint, screenshot): é a prática de maior alavanca; sem ela o humano vira o loop de verificação. [DOC: B]
2. Pedir evidência (saída do teste, comando e retorno), não afirmação de sucesso. [DOC: B]
3. Portão determinístico: hook Stop roda a checagem e bloqueia o fim do turno até passar; `/goal` mantém o agente trabalhando até a condição valer. [DOC: B]
4. Hooks (PreToolUse/PostToolUse) para o que deve acontecer sempre (lint, bloquear escrita em migrations): instruções em CLAUDE.md são consultivas, hooks garantem. [DOC: B]
5. Revisão adversarial em subagente de contexto novo; instruir a reportar só lacunas que afetam correção ou requisitos, senão gera supercorreção e over-engineering. [DOC: B]
6. Testes primeiro: pedir teste que reproduz falha, depois a correção; um agente escreve testes, outro o código. [DOC: B]
7. `/code-review` e `/verify` (exercitar o fluxo real) antes de commitar mudança não trivial. [DOC: B]
8. Cobertura de 100% como meta é prática de equipe, não recomendação oficial; mitigar o risco de testes vazios com mutation testing ou revisão independente. [INF]

## 7. Spec-driven development
1. Para features maiores: o agente entrevista (AskUserQuestion), escreve SPEC.md; executar em sessão nova com contexto limpo. [DOC: B]
2. Boa spec nomeia arquivos e interfaces, declara o fora de escopo e termina com verificação ponta a ponta. [DOC: B]
3. Fluxo explorar -> planejar -> implementar -> commitar; revisar o plano antes (Ctrl+G edita). [DOC: B]
4. Rastreabilidade spec -> teste (um verificador de especificação no CI) é do mesmo espírito. [INF]

## 8. Segurança
1. Permissões: allowlist do que é seguro, `permissions.deny` para o que nunca (ex.: `Bash(git push * main)`, leitura de `.env`); regra deny casa o comando como escrito, então combinar com sandbox. [DOC: SEC]
2. Sandbox (`/sandbox`) dá isolamento de arquivos e rede no nível do SO; auto mode usa classificador contra escalada de escopo e ações induzidas por conteúdo hostil. [DOC: B, SEC]
3. Conteúdo não confiável (web, issues, saída de MCP, retorno de subagente) pode conter injeção: o relatório de subagente é varrido por texto que imita tags de sistema, mas sem remover nem autorizar; ações disparadas passam pelas permissões normais. [DOC: S, SEC]
4. Segredos só em `.env` fora do git; negar leitura via deny; revisar `.mcp.json` e plugins (MCP de claude.ai/plugins não aparecem no repo). [DOC: SEC] + [INF]
5. Hooks `ConfigChange` auditam/bloqueiam mudança de configuração na sessão; managed settings impõem padrão organizacional. [DOC: SEC]
6. Hooks de agente em frontmatter de projeto exigem confiança na pasta: revisar `.claude/` de PRs externos como código executável. [DOC: S]
7. Proteger a main com branch protection no GitHub (hook local não basta, pode ser contornado). [INF]

## 9. Observabilidade e custo
1. `/usage` (sessão, cache, atribuição), status line com contexto e custo, `/insights` (atritos), `/context`. [DOC: C, B]
2. OpenTelemetry para métricas por usuário/tarefa em qualquer provedor; `--max-budget-usd` em execuções `-p`; `--output-format json` traz custo. [DOC: C] (flag: [DOC: C, citada])
3. Medir por demanda: tokens por cartão e retrabalho (bugs voltando) no KANBAN. [INF]

## 10. Armadilhas comuns
- Sessão "pia de cozinha", correção em loop, CLAUDE.md inflado, confiar sem verificar, exploração infinita. [DOC: B]
- Agente cai por erro de API/limite: persistir estado em arquivo (cartão, spec) para retomar; `claude --continue/--resume`; esperar reset do limite em vez de relançar. [DOC: C] + [INF]
- Relançar duplicado: antes de relançar, checar worktree/branch/commit do agente anterior; idempotência por cartão com dono único. [INF]
- Estado compartilhado: dois agentes na mesma árvore de trabalho; usar worktree por agente escritor. [DOC: S] + [INF]
- Retornos de subagente longos reinflam o contexto principal; exigir resumo curto no prompt. [DOC: S]
- Revisor pedido para "achar problemas" sempre acha: delimitar por correção/requisito. [DOC: B]

## 11. Não consegui verificar (declarado)
- Páginas oficiais de worktrees, hooks, memória/auto memory, prompt caching, MCP e Agent SDK não foram abertas em detalhe; usei só o que as páginas B, S, C citam. Reabrir antes de decidir.
- Artigos de engenharia "Building effective agents" e "How we built our multi-agent research system": conhecidos de treinamento, não relidos agora; não citei números deles.
- Evidência empírica de que "100% de cobertura" melhora qualidade com agentes: não encontrei fonte; tratar como [INF].
- Percentuais de economia por prática: não há dados oficiais além dos custos médios (US$13/dev/dia) e do 7x de agent teams.
