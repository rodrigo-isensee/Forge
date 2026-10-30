---
tipo: qa
contrato: 1
pedido: impl-d5a-pa6
branch: melhoria/impl-d5a-pa6
commit: ad3c5a5bef6aef0a7d6e1ae0065f9a12077938a9
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: impl-d5a-pa6

Entrega testada: ad3c5a5 (depois dela só entraram os pareceres de segurança e review; HEAD 2ee2bbc). Base 234dbe0. Diff: 8 arquivos, 66 inserções e 14 remoções, só texto de regra, skill, modelo, invariantes e 3 testes.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 complemento em R-DECISAO (os pontos e a invariante) | leitura do diff + 6 invariantes novas de R-DECISAO em tests/config.json, via RegrasInviolaveis | texto da regra não some | passou |
| E2 R-WIP: vaga na coluna de origem | leitura do diff + 3 invariantes novas de R-WIP | `origem:` nunca coluna de validação | passou |
| E3 skill kanban-scrum: coluna e fronteira com Bloqueado | leitura do diff + 3 invariantes novas da skill | decisão ou ação do usuário vs Bloqueado | passou |
| E4 modelo com a seção no topo | test_kanban_painel_do_dono_no_topo; test_kanban_painel_com_cartao_valido; test_kanban_painel_barra_pipe_no_comando_e_id_repetido; `forge-check kanban` no modelo (rc 0) | posição, painel vazio, 7 colunas, ID repetido, pipe no comando | passou |
| E5 frase em agents/jarvis.md citando a regra | leitura do diff + invariante nova de agents/jarvis.md | citação pelo ID | passou |

## Cenários e resultado real
Cópia limpa em $TMPDIR (git archive do HEAD):
- Os 3 testes novos: 3 testes, OK. `RegrasInviolaveis` e `Neutralidade`: 6 testes, OK. `forge-check --raiz templates/projeto kanban`: rc 0.
- Mutantes (cópia descartável), todos mortos:
  - M1 painel movido para depois do Upstream: test_kanban_painel_do_dono_no_topo FALHA.
  - M2 cartão de exemplo no painel do modelo: o mesmo teste FALHA.
  - M3 cabeçalho do painel com 5 colunas: `forge-check kanban` no modelo rc 1 (colunas diferentes do modelo), o que derruba o teste existente do modelo.
  - M4 troca da contagem de colunas em bin/forge-check:343: test_kanban_painel_barra_pipe_no_comando_e_id_repetido FALHA.
  - M5 checagem de ID repetido desligada em bin/forge-check:348: o mesmo teste FALHA.
- Código intacto: verdes. A suíte completa roda no pre-push desta entrega.
- O pedido não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`: sem spec de forge-mutante; os mutantes acima são sondas de QA.
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; os mutantes fazem o papel por teste, no sentido inverso.

## Recomendações (fora do bloco)
- Segurança, R1: invariantes para as frases de C-3, C-4 e do aceite sem comando em R-DECISAO; segue como cartão do tech-lead.
- Review: redação repetida na frase da evidência, "topo" duas vezes na skill e o terceiro teste que junta pipe e ID repetido; sem custo à cobertura.
- O pedido fala em "seis pontos"; o complemento traz sete tópicos, todos conferidos com o texto; sem efeito sobre o aceite.
