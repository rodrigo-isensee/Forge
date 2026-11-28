---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 87575570ef9ac5b24f09ab56e9f7354dab3a2987
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (qa-testing sob demanda, PR #958)

- ci: 87575570ef9ac5b24f09ab56e9f7354dab3a2987 verde

Mudança só de texto: `skills/qa-testing/SKILL.md` encurtada, texto movido para `skills/qa-testing/referencia.md`, mais um fragmento de changelog. O diff não toca `hooks/`, `bin/`, `.githooks/` nem `tests/catraca.py`; por isso não há mutante a declarar nem vermelho-antes-do-verde (nenhum teste novo, nenhuma regra de código mudada).

## Achados
- A1 (recomendado) skills/qa-testing/referencia.md:46 · o trecho do `--cobertura` não é idêntico ao original: "lista a condição ... (\"declarado, não provado\"; ...)" virou "sai \"declarado, não provado\"; ..." (some "lista", entra "sai"). Sentido igual; o brief pede o texto movido sem mudar palavra.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nenhuma regra com ID saiu da SKILL.md | comparação dos IDs (R-, EXT-, G3-, AR-) de develop x head: conjunto perdido vazio | n/a | passou |
| Invariantes de `tests/config.json` presentes | `re.search` dos 12 padrões da SKILL.md e dos 8 de `agents/qa-engineer.md` no head: nenhum ausente | n/a | passou |
| Texto movido idêntico | blocos markdown (plano e bug) presentes byte a byte em referencia.md; "Onde e como", "Review" e "equivalente" idênticos após normalizar espaço | texto removido da SKILL.md | passou, exceto A1 |
| SKILL.md diz quando ler cada seção | linhas 22, 35 e 81 trazem o gatilho ("ao abrir o plano", "ao escrever o oráculo", "ao abrir o relatório"); linhas 70 e 73 (equivalente e `--cobertura`) só apontam `referencia.md`, e o gatilho de leitura está na própria referência ("Leia ao declarar um mutante equivalente ou ao ler a saída do `--cobertura`") | 5 de 5 seções com ponteiro, 3 com gatilho na SKILL.md | passou |
| Orçamento do qa-engineer (teto 21480) | `python3 -m unittest tests.test_orcamento_instrucao`: 8 testes, OK | teto de 21480 caracteres | passou |
| Catraca e teste de custo (ordem do dono 28/11) | diff sem hook, bin/ nem arquivo protegido; check-runs `catraca` e `catraca (conferência)` pass; suíte 5/5 pass (inclui os testes de custo) | n/a | passou |

## Cenários e resultado real
CI do head: `gh run view 46142076201` tem `headSha` igual ao Revisar-sha; todos os check-runs concluídos e verdes (bateria, pareceres, passos, python 3.14, verificações longas, instalação, suíte 1/5 a 5/5, teto de pulados, árvore já provada, catraca, catraca (conferência)). Não rerrodei a suíte. `forge-check docs --base develop`: `docs: ok`, rc=0.
