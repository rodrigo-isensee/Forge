---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pos-merge-587
commit: 58dfa2ab016fbc10c730b369995b0f1e75b000d6
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (depois do merge do #587, E2.414)

Escopo: o que o #587 (`3b1b9e3f`, frontmatter dos agentes) levou à develop, lido contra a develop em `58dfa2ab`: `agents/devops-engineer.md`, `bin/forge-testes`, `tests/test_frontmatter_agentes.py` e `docs/qa/bugs/v047-1-devops-teto-orcamento.md`. O parecer anterior (`docs/security/v047-frontmatter-agentes.md`, aprovado em `58822e8d`) não viu o último commit da branch, a entrada do teste no mapa de `bin/forge-testes`, revisado aqui. Nenhum dos quatro arquivos mudou depois de `3b1b9e3f`; quem mudou foi o vizinho, `agents/jarvis.md` (#584, `e2e32879`, mesclado 6 min depois).

## Gatilhos
Gatilhos: definição de agente (ferramentas e modelo concedidos, menor privilégio; `R-SEGURANCA`)

## Achados
- A1 (bloqueante) agents/jarvis.md:3 · a description voltou a ser escalar simples com ': ' ("da sessão: entende", vindo do #584): o frontmatter do Jarvis não lê como YAML e tools e model caem; o teste do #587 falha na develop (S1). Correção: aspas simples no valor ou trocar ': ' por ' - '.
- A2 (recomendado) tests/test_frontmatter_agentes.py:33 · segue o A1 do parecer anterior: aspas duplas só conferem o último caractere; "a "b" c" passa sem erro (S2) e não é YAML válido.
- A3 (recomendado) tests/test_frontmatter_agentes.py:41 · segue o A2 do parecer anterior: tools e model vazios ou ausentes passam; exigi-los não vazios barra o alargamento silencioso de ferramentas.
- A4 (recomendado) tests/test_frontmatter_agentes.py:37 · valor que começa com crase, @ ou % é pulado como válido, e '- x' e '? x' passam (S3); pelo YAML esses indicadores não abrem escalar simples e o carregador descarta o frontmatter.

## Sondas
- S1 · cd tests && python3 -m unittest test_frontmatter_agentes (develop 58dfa2ab) · espera: OK · obtido: FAILED (failures=1), agents/jarvis.md linha 3 'description' tem ': ' ou ' #' sem aspas
- S2 · erros_do_frontmatter com description: "a "b" c" · espera: erro · obtido: []
- S3 · erros_do_frontmatter com description: `x` y, @x, %x, - x e ? x · espera: erro em cada · obtido: [] em todos

## Detalhe dos achados
**A1.** Evidência: `agents/jarvis.md:3` na develop `58dfa2ab`; no `3b1b9e3f` a mesma linha usava ` - ` ("É o agente principal da sessão - entende"), e o #584 trocou por `: `. Os dois PRs passaram cada um no próprio CI: o do #584 rodou sem o teste novo na base, e o do #587 sem o texto novo do Jarvis; o defeito nasce do merge dos dois (conflito semântico, sem conflito de texto). Efeito: escalar simples com `: ` no meio não é YAML válido, o carregador descarta o frontmatter e o Jarvis perde `tools` (a lista fechada: as de arquivo, `Bash`, `Agent`, `TodoWrite` e duas MCP de mensagem) e `model: opus`; passa a herdar todas as ferramentas da sessão. É a mesma classe do defeito do devops-engineer que o #587 corrigiu, agora no agente principal da sessão. Caminho de ataque: não há atacante externo; o ganho é de ferramentas (rede sob o proxy, MCP de terceiros) para uma instrução maliciosa que já esteja no contexto do Jarvis. O hook `conformidade`, as permissões e o sandbox não mudam. Severidade: baixa no risco, mas defeito provado com gatilho e develop vermelha no teste do próprio #587, por isso bloqueante (`R-REVIEW`, `R-SEGURANCA`). Correção mínima: `agents/jarvis.md:3` com o valor entre aspas simples (o texto não tem aspa simples interna) ou `: ` de volta a ` - `; depois, `test_frontmatter_agentes` verde. Esforço P. Dono: autor da correção que o Jarvis abrir na develop (texto do Jarvis; `tech-lead` revisa). Não reproduzido no carregador real (rede da Anthropic negada aqui); a conclusão vem da semântica YAML, a mesma do parecer anterior.

**A2, A3.** Estado: abertos, o teste não mudou desde o parecer anterior; nenhum arquivo atual os explora. Esforço P; dono: quem mantém `tests/test_frontmatter_agentes.py`.

**A4.** Evidência: `tests/test_frontmatter_agentes.py:37-38` pula valor que começa com `[ { | > & * ! % @` e crase sem conferir nada; `@`, crase e `%` são indicadores que não abrem escalar simples, e `- ` e `? ` também não passam por nenhuma conferência. Nenhum agente atual começa assim. Correção mínima: tratar `@`, crase, `%`, `- ` e `? ` no início como erro (exigir aspas) e, para `[`, `{`, `|`, `>`, `&`, `*`, `!`, dar erro também, já que nenhum agente usa forma de bloco, fluxo, âncora ou etiqueta. Esforço P; dono: o mesmo de A2. Isto vira dimensão nova da matriz do teste (indicador no primeiro caractere), não correção pontual.

**O resto do #587 na develop.** `agents/devops-engineer.md:3` segue entre aspas simples, sem aspa interna, com `tools`, `model` e `skills` intactos. `bin/forge-testes:125`: o teste entra em `LEITORES_DE_TEXTO`, logo em `CONTEUDO`, que as regras `stacks/.*` e `(agents|skills|docs)/.*` do `MAPA` levam; mudança em `agents/*.md` ou `stacks/*/agents/*.md` roda o teste no envio com testes afetados. O próprio `bin/forge-testes` está em `ALTERA_O_MAPA` (suíte completa). Sem gatilho novo. `docs/qa/bugs/v047-1-devops-teto-orcamento.md`: só registro, sem segredo nem dado pessoal. O teto do devops-engineer (`test_orcamento_instrucao`, `test_nenhum_agente_passa_do_teto`) também falha na develop (22669 caracteres para teto 21991; 44 marcadores para 42); está com o E2.412 no PR da develop-verde-576 e não é achado deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática de `git show 3b1b9e3f` e da develop em `58dfa2ab`, `unittest` de `test_frontmatter_agentes` e `test_orcamento_instrucao` e sondas diretas de `erros_do_frontmatter`, com `python3 -I`. A suíte inteira roda no CI; não há PR nesta etapa. Sem leitor YAML de terceiros no ambiente (lacuna; o teste foi feito para não precisar dele). Varredura de segredos não se aplica (diff sem credencial).
