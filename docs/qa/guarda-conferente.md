---
tipo: qa
contrato: 1
pedido: guarda-conferente
branch: melhoria/guarda-conferente
commit: 2aebf36855edc5a089aa9f14c7ca96289c422376
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: guarda do conferente (M6, R-BRIEF)

Ambiente: worktree no HEAD 6df34a7 (só parecer de review acima do commit de código 2aebf36); sondas em cópia limpa (`git archive`) em `$TMPDIR`, chamando `hooks/agentes.py` com o JSON de PreToolUse (Agent), projeto com `.forge/versao`, sem rede.

## Suíte
| Verificação | Resultado |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` | 1210 testes, OK |
| `scripts/validar-plugin.sh` | Validation passed |

## Critério (decisão M6) → teste → resultado
| ID | Cenário | Esperado | Obtido | Fronteira protegida |
|---|---|---|---|---|
| CT-01 | conferente sem `modo:` | recusa (R-BRIEF) | rc=2, mensagem com a falta | modo ausente |
| CT-02 | sem `Arquivo:` | recusa | rc=2 | arquivo ausente |
| CT-03 | `Arquivo:` fora de docs/briefs/ | recusa | rc=2 | caminho fora da pasta |
| CT-04 | `Brief-sha256` com 3 hex | recusa | rc=2 | hash curto |
| CT-05 | `Brief-sha256` com 65 hex | recusa | rc=2 | logo acima do limite (64) |
| CT-06 | três linhas corretas | passa | rc=0 | caso feliz |
| CT-07 | `Arquivo:` absoluto com espaço | passa | rc=0 | espaço no caminho |
| CT-08 | vários blocos `<<<BRIEF`/`<<<ENTREGA` | passa | rc=0 | vários blocos |
| CT-09 | outro agente (`forge:tech-lead`) | não muda | rc=0 | outro tipo |

Os testes automatizados do autor (`tests/test_guarda_conferente.py`) rodaram dentro da suíte; vermelho antes do verde não refeito aqui (a recusa só existe no código novo; CT-01 a CT-05 provam a recusa).

## Observação (não bloqueante)
`subagent_type` sem o prefixo (`conferente`) passa sem a guarda (rc=0); é o R2 do parecer de segurança, só perde a economia, o conferente ainda confere o cabeçalho.

## Achados
