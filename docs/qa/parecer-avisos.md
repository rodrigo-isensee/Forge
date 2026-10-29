---
tipo: qa
contrato: 1
pedido: parecer-avisos
branch: melhoria/parecer-avisos
commit: 937ea10781ffc8d6fabc97df7a745fb094565b92
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: parecer-avisos

Só texto, sem UX nem API, sem gatilho de segurança. Diff `a83de9e...937ea10` (6 arquivos), lido depois de conferir o escopo do pedido (E1 a E3). Não escrevi o diff.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 aviso nos modelos de parecer (reviews, qa, security do template e `docs/security/_modelo.md`) | `grep -c 'Avisos (o pre-push'` nos quatro arquivos (1 cada); o aviso traz o teto de 300 e o ID da regra | modelo de segurança do Forge idêntico ao do template | passou |
| E2 aviso no brief de parecer em `agents/jarvis.md` | `grep` da frase "Brief que manda escrever parecer" (1 ocorrência, na seção de conferências) | uma só ocorrência, sem duplicar | passou |
| E3 fragmento de changelog e testes estruturais | `tests.test_forge` `AntiDuplicacao`, `Neutralidade`, `NeutralidadeDoNucleo`, `RegrasInviolaveis`, `Agentes`: 14 testes, OK | aviso não copia frase de regra (o teste AntiDuplicacao varre `docs/qa/` e `templates/`) | passou |
| Exemplo que segue o modelo | este parecer, `forge-check docs` | bloco `## Achados` vazio com `aprovado` | passou |
| PA-7 | `docs/engineering/achados-recorrentes.md` conferido: sem linha AR | n/a | passou |

## Execução
Testes só dos arquivos tocados (a suíte completa roda no pre-push). Sem código de comportamento no diff: vermelho antes do verde e mutação não se aplicam (texto de modelo); lacuna declarada.

## Observação
O aviso repete o teto de 300 caracteres que o parágrafo de formato já traz no modelo de QA e de review; é redundância, não defeito.
