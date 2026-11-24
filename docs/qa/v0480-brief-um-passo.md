---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-brief-um-passo
commit: 91958d3ec525ada0a983241d372d89f980b084ed
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 E130.4 (PR #816, receita do envio de parecer)

Mudança só de texto de agentes e skills (classe C, E130.1). Sem código executável e sem regra de código mudada: mutação e vermelho antes do verde não se aplicam (nenhum teste novo). A suíte inteira fica no CI do PR; aqui rodaram só os testes dos arquivos tocados.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orçamento de instrução dos agentes tocados (qa-engineer, security-engineer, tech-lead) | `tests.test_orcamento_instrucao` | máximo de tamanho | passou |
| Métricas de texto | `tests.test_metricas_texto` | máximo | passou |
| Núcleo do Jarvis intacto | `tests.test_jarvis_nucleo` | n/a | passou |
| Regras citadas pelo ID | `tests.test_citacao`, `tests.test_citacao_p2` | `R-QA`, `R-REVIEW`, `R-NEUTRO` mantidos | passou |
| Clareza do texto | `tests.test_clareza` | n/a | passou |
| Frontmatter dos agentes | `tests.test_frontmatter_agentes` | n/a | passou |
| A lista de pastas de controle saiu do qa-engineer e está na skill | leitura do diff e `git grep` | `bin/`, `hooks/`, `.githooks/`, `tests/catraca.py` | passou |

Comando, da raiz e sem `-I`: `python3 -m unittest tests.test_orcamento_instrucao tests.test_metricas_texto tests.test_jarvis_nucleo tests.test_citacao tests.test_citacao_p2 tests.test_clareza tests.test_frontmatter_agentes`. Saída: `Ran 99 tests in 23.876s`, `OK`.

## Cenários e resultado real
- Pastas de controle: o diff de `agents/qa-engineer.md` tira `(bin/, hooks/, .githooks/, tests/catraca.py)` da linha do pedido de controle. A skill `skills/qa-testing/SKILL.md` (seção "Mutantes declarados nos pedidos de controle") traz a lista inteira, `bin/`, `hooks/`, `.githooks/`, `tests/catraca.py`. O `git grep` dessa lista em `agents/qa-engineer.md` no head não acha nada: a lista tem uma só fonte.
- Receita nova (`skills/briefs-e-conferencia/envio-de-parecer.md`): um passo por chamada, Write ou Edit, `git pull --rebase origin <branch>`, sem ID curto de mutante. Coerente com os três ponteiros (tech-lead, qa-engineer, security-engineer) e com `SKILL.md` de briefs, que a cita. Perdeu-se a menção "com `git add <caminho>` explícito" nos três agentes, mas a receita mantém a regra (caminho explícito, nada de `git add .` nem `-A`).
- Fragmento `changelog.d/v0480-brief-um-passo.md` presente.
- Cabeçalho: o `Revisar-sha:` do brief é e3eb537e; o head é 91958d3e, que soma só o parecer de review. O campo `commit:` segue o pedido do brief (91958d3e). O diff de código entre os dois é vazio.
- Remoto em 91958d3e no início da rodada: sem rebase necessário.
