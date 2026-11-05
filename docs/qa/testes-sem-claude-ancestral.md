---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/testes-sem-claude-ancestral
commit: 9a08b1c860fc0c24f47467429018020680ba5811
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: TESTES-SEM-CLAUDE-ANCESTRAL (versao-034, item E1a)

Head da branch: cd8fb561753d36aeb7221fd08977c33e60878f45 (só pareceres acima do commit testado; o diff de código é `4f53bde..9a08b1c`).

## Achados
- A1 (recomendado) tests/test_atualizar.py:706 · Reproduzido: se a guarda não recusa (lançador com defeito), o timeout=60 mata só o sh; o pty.spawn pai e o lançador ficam órfãos (ppid 1) esperando a pergunta. Sugestão: start_new_session e matar o grupo no timeout (E1.3b).
- A2 (recomendado) tests/sem_claude_ancestral.py:27 · Lançador no plugin aceita --ate arbitrário; mesmo ponto do review A1 e da segurança A1. Sem nova capacidade provada; sem ação neste pedido.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Testes de sugerir/atualizar/voltar-versao passam sob o `claude` ancestral | tests.test_sugerir (37), tests.test_atualizar (80), de dentro desta sessão (CLAUDECODE=1) | `claude` acima do teste não conta | passou, rc=0 nos dois |
| Vermelho antes do verde | tests.test_sugerir na base 4f53bde, numa worktree descartável | base sem lançador | 9 falhas na base, 0 no head |
| `claude` entre o teste e o script segue recusando | Dentro.test_o_lancador_dos_testes_nao_esconde_um_claude_abaixo_do_teste | só o que está acima do teste é ignorado | passou; com mutante (cortar todos os ancestrais) falha (1 falha, 1 erro, 61 s) |
| Guarda de produção intacta | diff não toca `bin/`, `hooks/` | n/a | passou (conferido no diff) |
| Suíte inteira | `.githooks/pre-push --suite` | n/a | OK, 2559 testes, 30 skips herdados, rc=0 |

## Cenários e resultado real
- Vermelho: `forge-testes --vermelho` não tem mapa para o arquivo novo e roda a suíte completa; foi interrompido pelo reinício da sessão e não deu veredito. Valeu a prova manual acima (base: 9 falhas em test_sugerir).
- Suíte inteira dentro da sessão do Claude: processo 1 rc 0 (972 testes), processo 2 rc 0 (1587), 2117,9 s. Nenhuma falha de ambiente do pid namespace apareceu; não há falha a comparar com a origin/develop. Log: /tmp/qa-testes-sem-claude-suite.log.
- Órfãos (E1a): reproduzido só com a guarda falhando (mutante do lançador numa cópia): após o teste, `pty.spawn` pai e `sem_claude_ancestral.py --ate <pid>` vivos com ppid 1. No head sem defeito, nenhum processo restou após os testes e a suíte. A causa provável dos quatro de 16 h é a guarda não recusar (ancestrais ilegíveis, como no sandbox) e o teste novo cair no timeout; vira A1. Processos da reprodução mortos.
- Mutantes declarados: o pedido não toca guarda de `bin/`, `hooks/` nem `.githooks/`; `forge-mutante` não se aplica. O mutante manual do lançador acima morreu.

## Parecer
Aprovado: o conserto cumpre o objetivo, suíte verde, nenhum bug aberto. A1 e A2 são recomendações.
