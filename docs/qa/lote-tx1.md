---
tipo: qa
contrato: 1
pedido: lote-tx1
branch: melhoria/lote-tx1
commit: 426bbd46d4f3e1a34c4fe6da2306f54510e7ee6c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-tx1

Lote de texto (seis cartões, E3.1). Sem mudança em `bin/`, `hooks/`, `.githooks/`, `tests/catraca.py` nem `tests/`: sem mutantes declarados e sem teste novo, então não há vermelho a provar.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 item 12 no checklist de review | leitura do diff: `skills/engineering-practices/SKILL.md:51`, a skill que o `tech-lead` lê (`agents/tech-lead.md:6,15`) | n/a | passou |
| E2 correção que cita lista reproduz o conteúdo | `skills/cyber-security/SKILL.md` (item 4) e `agents/jarvis.md:65` (brief de volta) | n/a | passou |
| E3 logs e sondas em `$TMPDIR` levam o pedido no nome | `agents/jarvis.md:65` (autoconferência fixa do brief; chega ao agente pelo brief) | n/a | passou |
| E4 retomada confere `git branch --show-current` ou traz `HEAD:refs/heads/<branch>` | `agents/jarvis.md:65` | n/a | passou |
| E5 review e QA gravam a linha AR-n na recorrência | `skills/engineering-practices/SKILL.md:53` e `skills/qa-testing/SKILL.md:91` | n/a | passou (ver nota 1) |
| E6 README diz repositório público | `README.md:22` | n/a | passou |
| Nenhum invariante tocado | `git diff base...HEAD --stat -- tests/config.json` vazio | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge`: `Ran 432 tests in 90.859s`, `OK` (log em `$TMPDIR/qa-engineer-lote-tx1/tf-lote-tx1.log`).
- Diff: 6 arquivos (README, jarvis, 3 skills, fragmento `changelog.d/lote-tx1.md`); nenhum fora do escopo; `agents/conferente.md` e `bin/` intactos.
- Nota 1 (recomendado, não devolve): `docs/engineering/achados-recorrentes.md` diz que só entra achado de review ou de segurança, que quem escreve é `tech-lead` e `security-engineer`, e o formato só aceita `review|seguranca`. O texto novo do `qa-testing` manda o `qa-engineer` gravar a linha, sem categoria `qa` no formato. Vale alinhar o arquivo (categoria e quem escreve) num lote seguinte; não é defeito de comportamento provado.
- Nota 2 (recomendado): E3 está só na autoconferência do brief do Jarvis; o agente que cria sonda sem brief explícito não lê esse trecho. Cobre o caso do cartão (brief manda o nome).
