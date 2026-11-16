---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-frontmatter-agentes
commit: 58822e8d07d7943af1475f73df344b9704f51bb6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (frontmatter dos agentes, E2.164; revalidado em E2.296)

Revalidação por delta (E2.296) no head `58822e8d`: `forge-check parecer delta` em `b1fa63a8..58822e8d`, sem o que veio da develop, traz só `agents/devops-engineer.md:3`, a `description` encurtada (“do time” e “escrita por” saem). O valor continua entre aspas simples, sem aspa simples interna; `tools`, `model` e `skills` não mudam. `python3 -m unittest tests.test_frontmatter_agentes`: 3 testes, OK. Sem achado novo; A1 e A2 seguem recomendados (o teste não mudou).

Escopo: `bf475209..b1fa63a8` (3 arquivos): aspas na `description` de `agents/devops-engineer.md`, fragmento `changelog.d/v047-frontmatter-agentes.md` e o teste novo `tests/test_frontmatter_agentes.py`. Parecer completo (não havia parecer anterior desta branch).

## Gatilhos
`R-SEGURANCA`: a mudança toca a definição de um agente (ferramentas e modelo concedidos, menor privilégio). Sem segredo, sem workflow, sem hook.

## Achados
- A1 (recomendado) tests/test_frontmatter_agentes.py:33 · aspas duplas só conferem o último caractere: `description: "a "b" c"` passa sem erro e não é YAML válido; conferir aspa dupla interna não escapada, como já é feito para a simples.
- A2 (recomendado) tests/test_frontmatter_agentes.py:41 · `tools:` e `model:` vazios ou ausentes passam; hoje os 12 agentes declaram os dois, e exigi-los não vazios barraria o alargamento silencioso de ferramentas que motivou este item.

## Sondas

## Detalhe dos achados
**Pergunta da etapa: o devops-engineer rodava com permissões padrão?** Em parte. Antes de `b1fa63a8`, a `description` era escalar simples com `": "` no meio (`"como entrega e roda": pipeline`), o que não é YAML válido; o defeito existe desde a criação do agente (`5df7b684`, #109) e está na 0.47.1 instalada (`~/.claude/plugins/cache/forge/forge/0.47.1/agents/devops-engineer.md:3`). Com o frontmatter descartado, `tools`, `model` e `skills` deixam de valer: o agente herda todas as ferramentas da sessão (inclusive as de rede, a de criar subagente e as MCP) e o modelo de quem o chama, e não pré-carrega `ci-cd` nem `cyber-security`. O que **não** muda: as permissões da sessão, o sandbox do Bash e o hook `conformidade`, que decide o papel pelo `agent_type` do lançamento, não pelo `tools:` do frontmatter. Como o agente já tinha `Bash`, `Write` e `Edit`, o ganho real foi de ferramentas de rede (sob o proxy filtrado) e de delegação; não houve ganho de escrita além do que o papel já tinha. Severidade: baixa (perda de menor privilégio, sem caminho de ataque externo: exige instrução maliciosa já dentro do contexto do agente). Não reproduzido no carregador real (a rede da Anthropic é negada neste ambiente); a conclusão vem da semântica YAML e da descrição do autor no fragmento do changelog.

**A correção** (`agents/devops-engineer.md:3`): aspa simples envolvendo o valor; o texto não tem aspa simples interna, então o escalar fecha certo. Conferido que os 12 agentes (`agents/*.md`, `stacks/*/agents/*.md`) declaram `tools:` e `model:`.

**O teste** (`tests/test_frontmatter_agentes.py`): biblioteca padrão, sem ambiente nem rede, cobre `agents/` e `stacks/*/agents/`, detecta o caso original (sonda: `description: Dono do "como entrega e roda": pipeline` gera erro). Linha que não é `chave: valor` (continuação multilinha) vira erro, o que é conservador. Lacunas: A1 e A2, ambos sem arquivo atual que as explore; esforço P; dono: autor da branch (`tech-lead` ou quem implementou E2.151). Sobre AR-3 (lista negativa): o teste usa padrões proibidos, mas é uma checagem estrutural de autoria, não trava de ambiente; A2 é o complemento positivo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `unittest` do teste novo (3 testes, OK) e sondas diretas da função `erros_do_frontmatter`; a suíte completa roda no CI do PR (não há PR nesta etapa). Sem leitor YAML de terceiros no ambiente (lacuna; o teste foi desenhado para não precisar dele). Varredura de segredos não se aplica (diff sem credencial).
