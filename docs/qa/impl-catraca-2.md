---
tipo: qa
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c3
commit: a69bdf7ddb907b2bde43f73272aa77328eb137f5
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-catraca-2 (branch c3, item CATRACA-ISENCAO-AMBIENTE)

## Achados
- A1 (recomendado) tests/test_ambiente_git.py:279 · o `forge-testes --vermelho` não prova estes testes, porque a "implementação" é a constante EXCECOES, no próprio arquivo de teste; a prova de vermelho foi por mutação manual (abaixo).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Motivo da isenção da catraca cita o `fetch` e o `merge-tree --write-tree`, sem "só lê" | test_motivo_da_excecao_cita_o_que_o_arquivo_escreve | texto antigo do motivo | passou |
| Todo `fetch` da catraca leva as duas chaves de manutenção desligada na própria chamada | test_todo_fetch_da_catraca_leva_a_manutencao_desligada_na_propria_chamada | uma chave só; piso de 1 fetch achado | passou |
| Nada mais do módulo regride | `python3 -m unittest tests.test_ambiente_git` | n/a | 17 testes, OK |

## Cenários e resultado real
- Escopo: diff `234dbe0..a69bdf7` = um teste alterado (tests/test_ambiente_git.py), fragmento de changelog e dois pareceres. Nenhum arquivo de produção, hooks ou `tests/catraca.py` muda, então não há spec de `forge-mutante` a rodar.
- `forge-testes --vermelho 234dbe0...`: saída 0 com "nenhum teste prova a mudança" (811 "passa na base"). Esperado: o código sob teste (catraca.py) já estava correto na base e a mudança é o motivo dentro do teste. Não vale como prova; vale a mutação manual.
- Mutação manual em cópia descartável (os três mutantes morreram):
  - M1: motivo antigo de EXCECOES de volta → o teste do motivo falha (`'fetch' not found in 'controle protegido ... só lê ...'`).
  - M2: tirado `gc.auto=0` do fetch (catraca.py:912) → o teste da guarda falha.
  - M3: tirado `maintenance.auto=false` do mesmo fetch → o teste da guarda falha.
- Fronteira de piso: a guarda exige ao menos um `fetch` achado, então renomear a função não a esvazia.
- Lado revelado pelo código: a guarda lê só chamadas com a constante "fetch" nos argumentos; fetch montado por variável escapa. Aceito, pois o fonte tem uma chamada só e a recomendação C3-3 (lista positiva) ficou com a segurança.
- Acessibilidade e E2E: não se aplicam (sem interface).
- M14 (`agents/tech-lead.md:19`): cumprida. 28 linhas contáveis (26+2 em tests/test_ambiente_git.py), abaixo de 150; um comportamento só; não toca `hooks/` nem `PROTEGIDOS`.
- Suíte completa fica com o CI do PR; aqui rodei o módulo tocado.
