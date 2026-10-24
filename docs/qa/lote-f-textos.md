---
tipo: qa
contrato: 1
pedido: LOTE-F-TEXTOS
branch: melhoria/lote-f-textos
commit: 11eae9c7fca437d23f823fb0427c55621b0f9a94
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: LOTE-F-TEXTOS

Diff só de texto (7 arquivos `.md`): agentes `node-backend` e `react-frontend`, skills `kanban-scrum` e `novo-projeto`, `docs/melhoria-continua.md`, fragmento de changelog e o parecer de review. Cada F foi lido como o agente ou o dono que o usa. Sem código de produção, não há vermelho antes do verde nem mutação aplicáveis.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (F3) pronto completo uma vez, até 2 execuções | CT-01 leitura dos dois agentes | n/a | passou |
| E2 (F9) "Pronto: não reproduz" com prova no lugar do merge | CT-02 leitura de `kanban-scrum` contra a tabela de colunas e `R-MAIN` | bug sem código; prova ausente | passou |
| E3 (F11) quem faz cada coisa no ambiente novo | CT-03 leitura do passo 4 de `novo-projeto` | papel errado (hook barra) | passou |
| E4 (F12) Docker antes do Claude Code ou shell novo | CT-04 leitura do passo 4 | grupo `docker` só vale em sessão nova | passou |
| Regressão dos textos lidos por teste | CT-05 `bin/forge-testes --base origin/develop` | n/a | passou |

## Cenários e resultado real
- CT-01 (F3, os dois agentes): o passo 5 é idêntico nos dois, seguível: durante o desenvolvimento só testes e checagem de tipos do pacote alterado; pronto completo (`CLAUDE.md`, campo "Pronto" do modelo, que existe em `templates/projeto/CLAUDE.md:20`) uma vez antes do commit final; meta até 2 (a folga cobre uma repetição após falha). Reporte do resultado real preservado.
- CT-02 (F9): a coluna "Aguardando sua validação" existe (linha 30), o texto não contradiz "Pronto só com o merge do usuário" (a exceção é só para bug sem código e exige a prova listada: passos, ambiente e versão, saída copiada). Seguível.
- CT-03 e CT-04 (F11 e F12, passo 4): papéis claros (dono: `sudo` e segredos; `tech-lead`: dependências; `devops-engineer`: banco), instrução de Docker com os dois ramos e o motivo. Seguível. A renumeração (antigo 4 virou 5) não é citada por nenhum arquivo.
- CT-05: `bin/forge-testes --base origin/develop` na worktree do head: 640 testes, OK (1 skipped, preexistente), módulos test_changelog, test_doutor, test_forge, test_hooks, test_modelos_citados, test_novo_projeto, test_sobreposicao_quadro, 369 s. A suíte completa e a validação do plugin são dos portões da PR e não foram refeitas aqui.

## Recomendados (não bloqueiam)
- F3: "pacote alterado" pressupõe projeto com pacotes; em projeto de pacote único o agente precisa inferir que é o projeto todo. Aceitável.
- F9: o texto não diz quem move o cartão para "Pronto" com a prova (o usuário valida a prova; o mover fica implícito). Aceitável.
- `docs/melhoria-continua.md:20`: já apontado no review (linha fora do escopo declarada no PR; fonte `forge-check transcricao` imprecisa). Não reaberto aqui.
- F12: o `forge novo-projeto` já abre a sessão do Claude Code, então na prática vale o segundo ramo (reabrir em shell novo); o texto cobre os dois.
