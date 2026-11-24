---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp12-dado-real
commit: 0fedb7b6886125f54f600c9d1f569005621f4a1a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · dado real antes de painel simulado (BP12, E144.4, PR #832)

Head 82277931. Mudança só de texto (skill `ux-design`, constituição do modelo, fragmento). Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha; aqui, só os testes dos arquivos tocados. Sem teste novo, então vermelho antes do verde e mutação não se aplicam (nenhuma regra de código mudou).

| Obrigação | Teste ou conferência | Fronteira protegida | Resultado |
|---|---|---|---|
| E144.1: o discovery pede prova de dado real ou amostra anonimizada antes de painel simulado | leitura do diff: `01-empatia.md` na skill e portão novo na constituição | só a parte do discovery; a parte do QA do BP12 ficou fora, como o brief manda | passou |
| O sentido do texto do ux-designer se manteve nos trechos enxutos | leitura do diff linha a linha contra a base | Validar, Especificar e "Trabalho técnico" mantêm a regra; "Correções e tarefas técnicas" virou "Trabalho técnico" (correção é trabalho técnico) | passou |
| Orçamento de instrução e tetos de métricas | `test_orcamento_instrucao` (8), `test_metricas_texto` (2), `test_metricas_portoes` (5) | teto de métricas da skill não sobe | passou |
| Modelos de projeto | `test_modelos_projeto` (25), `test_modelos_citados` (3), `test_textos_034` (9) | constituição do modelo segue válida | passou |
| Neutralidade (R-NEUTRO) | `tests.test_forge.Neutralidade` (3) | nenhum termo de projeto no texto novo | passou |
| Critérios de reversão do Como medir (corpo do PR) | leitura do corpo do PR | meta: toda demanda com painel traz a prova e 0 escapes altos nas 3 retros seguintes; reversão: nenhuma demanda registra a prova em 30 dias | passou: mensuráveis e com prazo |

Comandos: `python3 -I -m unittest discover -s tests -p <arquivo>` para cada módulo acima (todos `OK`); `python3 -m unittest tests.test_forge.Neutralidade`: `Ran 3 tests ... OK`.

Observação sem bloqueio: "dados de exemplo realistas" na linha Prototipar segue valendo e não contradiz o portão novo (o protótipo continua com dado de exemplo; o portão exige a prova antes da validação).

## Delta da volta (E144.8, head 0fedb7b6)

Intervalo 82277931..0fedb7b6 no domínio do QA: só skills/ux-design/SKILL.md, texto (A1 da segurança: "ou amostra anonimizada" na prova do discovery; enxugamento de palavras em Idear, Prototipar, Regras e Necessidades de dados). Sentido preservado; a regra de dado real do 01-empatia.md ganhou a alternativa da amostra anonimizada, coerente com E144.1.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Teto de instrução da skill | test_orcamento_instrucao (8) | skill não passa do orçamento | passou |
| Teto de métricas | test_metricas_texto (2) | métricas de texto | passou |
| R-NEUTRO | tests.test_forge.Neutralidade (3) | sem termo de projeto | passou |

Sem teste novo: vermelho antes do verde e mutação não se aplicam. A bateria inteira é o check-run bateria do CI do mesmo sha.
