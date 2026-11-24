---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-receita-alcance
commit: f56597cbefd9f17b22078b21773cacbbdddc735c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA · receita do envio de parecer nos quatro portões (E146.3, PR #835)

Head f56597cb. Mudança só de texto: quatro agentes (`devops-engineer`, `qa-engineer`, `security-engineer`, `tech-lead`), a receita `skills/briefs-e-conferencia/envio-de-parecer.md` e um fragmento de changelog. Sem código de produção, hook nem `bin/`: não é pedido de controle, sem mutante e sem teste novo, logo sem vermelho antes do verde. Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha; aqui, só os testes dos arquivos tocados.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orçamento de instrução dos agentes não estoura (`R-TETO` de texto) | `tests.test_orcamento_instrucao` | teto por agente, sem subir teto | passou |
| Métricas de texto e dos portões | `tests.test_metricas_texto`, `tests.test_metricas_portoes` | tamanho dos agentes | passou |
| Modelos citados existem | `tests.test_modelos_citados` | modelo removido do agente continua citado na receita | passou |
| Citação de regra por ID | `tests.test_citacao`, `tests.test_citacao_p2` | ID de regra | passou |
| Clareza do texto | `tests.test_clareza` | frase longa, ambiguidade | passou |
| Frontmatter dos agentes | `tests.test_frontmatter_agentes`, `Agentes` | campos obrigatórios | passou |
| Caminho `${CLAUDE_PLUGIN_ROOT}/...` citado existe | `Referencias.test_caminhos_do_plugin_existem` e `test_todo_caminho_citado_em_agentes_skills_e_regras_existe` (mínimo de 120 caminhos afirmado) | caminho renomeado derruba | passou |
| Receita citada nos 4 agentes | conferência manual: `grep -c` do caminho completo, 1 ocorrência em cada um; arquivo existe | n/a | passou |
| Envio pela receita: um passo por chamada, Write, `git pull --rebase origin <branch>` | leitura da receita (passos 1 a 3) e dos 4 agentes; `tests.test_pre_push_parecer_curto` | atrás do remoto sem upstream | passou |
| Neutralidade, anti-duplicação, regras com ID | `Neutralidade`, `AntiDuplicacao`, `RegrasComId`, `Orcamento`, `Skills` | termo proibido, texto duplicado | passou |

Execução (raiz do clone, sem -I):
- `python3 -m unittest tests.test_orcamento_instrucao tests.test_metricas_texto tests.test_modelos_citados tests.test_citacao tests.test_citacao_p2 tests.test_clareza tests.test_frontmatter_agentes` : `Ran 73 tests ... OK`
- `python3 -m unittest tests.test_forge.Agentes tests.test_forge.Referencias tests.test_forge.Neutralidade tests.test_forge.AntiDuplicacao tests.test_forge.RegrasComId tests.test_forge.Orcamento tests.test_forge.Skills tests.test_metricas_portoes tests.test_pre_push_parecer_curto` : `Ran 39 tests ... OK`

## Conferência do diff contra a receita
- A receita passou a cobrir qualquer pasta de portão (`git add docs/<pasta do portão>/<pedido>.md`, `docs(<portão>)` com os quatro valores) e absorveu modelo, `forge-check docs` e validade presa ao domínio; os quatro agentes citam o caminho e a condição "atrás do remoto" volta ao `git pull --rebase origin <branch>`.
- Sem o limite de 300 caracteres no texto dos agentes: segue na receita (passo 1) e no modelo; sem perda de obrigação.
- Parecer de segurança do `security-engineer` mantém a restrição de `docs/security/aceites/`.
