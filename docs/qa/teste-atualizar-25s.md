---
tipo: qa
contrato: 1
pedido: teste-atualizar-25s
branch: melhoria/teste-atualizar-25s
commit: 4057d257490c53589ba2858cf4e06415773713f7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: teste-atualizar-25s

Sem UX nem API. Diff `bd204b8..4057d25` (só `tests/test_atualizar.py` e o fragmento de changelog). Não escrevi o diff. HEAD da branch `c7d2e2b` só acrescenta o parecer de review sobre o mesmo código.

## Achados

## Critério → teste → resultado
| Critério (pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: processo lento termina sem marcar travou | `EsperaDoTerminal.test_processo_lento_depois_da_ultima_linha_termina_sem_marcar_travou`; mais cenário meu de 30 s com saída a cada 1,5 s | tempo total acima do intervalo ocioso | passou |
| E1: pergunta sem resposta continua "[TRAVOU esperando resposta]" | `EsperaDoTerminal.test_pergunta_sem_resposta_continua_marcada_como_travou` | processo vivo sem saída por `ocioso` | passou |
| E2: passa sob carga | módulo `tests.test_atualizar` com 4 laços de CPU e 2 execuções paralelas do mesmo módulo | máquina lenta | passou (57 testes, 31,8 s) |
| E3: fragmento de changelog | `changelog.d/teste-atualizar-25s.md` presente; suíte estrutural verde | n/a | passou |

## Execução real
- `python3 -m unittest discover -s tests -q`: Ran 878 tests in 203,1 s, OK.
- `scripts/validar-plugin.sh`: Validation passed (as duas validações).
- Vermelho antes do verde: cópia do HEAD em `$TMPDIR` com o `rodar` de `bd204b8` (kwargs aceitos e ignorados) e script lento (20 passos de 1,5 s, saída contínua, 30 s): `python3 -m unittest tests.test_lento` falhou em 25,2 s com `[TRAVOU esperando resposta]` (FAILED failures=1). Com o `rodar` novo, o mesmo script: OK em 30,2 s. Observação: os dois testes novos rodando contra o `rodar` antigo sem adaptar dão TypeError (kwarg `ocioso`), então a prova de vermelho vem do cenário lento acima.
- Instáveis: nenhum teste falhou e passou de novo sem mudança nas execuções (suíte, carga, vermelho/verde).

## Riscos
- `ocioso=20` fixo: processo real com pausa maior de 20 s sem saída ainda seria morto (recomendação do review; ligada ao FLAKY-1, fora do escopo).
- O push anterior foi barrado por `errors=1` sem nome (FLAKY-1); não reproduzi nesta rodada.
