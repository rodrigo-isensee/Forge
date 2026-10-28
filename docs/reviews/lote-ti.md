---
tipo: review
contrato: 1
pedido: lote-ti
branch: melhoria/lote-ti
commit: 98991ed1ae89eb2e94612acaad29201582aec83e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: lote-ti

## Achados

## Parecer
Aprovado. Revisado ed7fbd8...98991ed, um commit por item, contra o escopo do LOTE-TI e a DECISÃO TÉCNICA de 09:57.

- Tamanho: 102 linhas de código e teste (teto M14 de 400); `hooks/` e `tests/config.json` intactos; fragmento `changelog.d/lote-ti.md` presente. PA-7 (`achados-recorrentes.md`) está vazio: nada a conferir.
- E1 (645f6b8): só o teste de pré-condição do apoio `apoio_pathlib_312`; a mensagem do commit registra a causa (Python 3.14 engole o ENAMETOOLONG) e as 10 execuções verdes. Nenhuma asserção alterada.
- E2 (03c32ed): prazo do bash do T9b de 10 para 60 s e `TimeoutExpired` convertido em falha do arnês com a causa; teste novo com prazo de 0,5 s sobre `while :`. Asserções do G1 e da divisão intactas.
- E3 (d4a24cd): deslocamento da amostra por semente (`random.Random`), sem semente igual à amostra fixa de antes; a semente sai na falha (`add_note`, Python 3.11+; o CI usa 3.12 e 3.14). Medi o tamanho da amostra com 9 sementes: 17936 a 18048 formas, acima do mínimo de 10 000. Teste novo cobre determinismo, faixa e subconjunto.
- E4 (83cb294): a `Guarda` passa a medir `process_time`; o teto K usa limites de 15 ms (máximo) e 10 ms (média), cerca de 2x o p95 medido no sandbox (6,9 e 4,9 ms). A propriedade fica nos 120 s (já era o valor da decisão de 19:13, como diz a DECISÃO TÉCNICA); a docstring registra o p95 de 42,3 s. Nenhuma asserção ficou mais fraca; as de tempo mudaram de relógio para CPU conforme a D3.
- Rodei só os testes do item (7 testes, OK em 5 s, Python 3.14.4).

Riscos (sem bloquear): o p95 da D3 foi medido no sandbox, não no runner do CI; a medida no runner fica para o QA e o PR. O teste `test_guarda_mede_cpu_e_nao_relogio` confere o texto do driver, não o comportamento; é suficiente porque o teto K exerce o caminho.
