---
tipo: qa
contrato: 1
pedido: ci-postinstall-cli
branch: melhoria/ci-postinstall-cli
commit: d346475762edfb6a1f3dc1227cabfc4173f73521
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# Parecer de QA: ci-postinstall-cli

Entrega testada: conserto do passo de instalação do Claude Code no CI (versão fixa 2.1.296) e fragmento de changelog. HEAD da branch no teste: 02ba544b99c42cc48228ec9969437ca7110833d8 (acima do commit testado só há pareceres de review, segurança e devops). Sem especificação de UX nem contrato de API: o pedido não tem tela nem endpoint, então não há plano antecipado; a obrigação é a E1 do pedido.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: o passo de instalação instala o binário nativo (só o script desse pacote fixo roda) | Execução 39532870066 (PR #251): o passo "Claude Code CLI" terminou com "added 2 packages" (a execução falha anterior terminou com 1 pacote e sem o binário); o passo seguinte, a validação do plugin em modo estrito, respondeu "Validation passed" | só o pacote fixo tem script liberado; a diff do workflow é uma linha | aprovado |
| E1: nenhum passo da bateria pulado ou condicional novo | Comparação dos passos da execução com a diff contra a base 0f480c8: só o passo de instalação mudou; os dois passos "skipped" (testes que leem pareceres em commit só de parecer; release exige versão nova) já tinham a condição antes e não se aplicam a este PR | n/a | aprovado |
| E1: a bateria inteira passa | Execução 39532870066, job bateria: success em 5m34s; suíte 1105 testes OK; análises do workflow, validação do plugin, instalação de ponta a ponta, fragmento, "Nada pula degrau", segredos e pareceres: todos success | n/a | aprovado |
| E2: fragmento de changelog | Passo "mudança na fábrica exige fragmento em changelog.d": success | fragmento presente | aprovado |

## Execução
- PR #251 (rascunho): execução 39532870066, job bateria success (5m34s); job "checagem rápida (push na develop)" skipping, como esperado em PR; Catraca (execução 39533064764) success (8s).
- Suíte local na worktree (HEAD 02ba544): 1082 testes, OK (275s). O CI contou 1105; a diferença de 23 não foi investigada (nenhum teste falhou nos dois lados).
- Validação do plugin local (`scripts/validar-plugin.sh`): Validation passed (o aviso de ícone ausente não muda o resultado).
- Rodadas sem suíte concorrente: confirmado antes com `.githooks/pre-push --status` (rc=1).

## Vermelho antes do verde
Não há teste novo: a prova é a própria bateria. O vermelho está registrado no pedido: a execução 39518179092 (PR #249) falhou neste passo com o binário ausente; a execução 39532870066 passou com a mudança de uma linha.

## Observação
O gerenciador de pacotes na execução verde foi o mesmo da falha (11.19.0), logo a correção não depende de a versão flutuante do ambiente voltar atrás; a liberação explícita do script do pacote fixo basta.

## Achados
