---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 46000ed50e0089fb2818c440c2c5355a6d38dd10
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (melhoria/v0481-voltas-alinhada, #902, E14.60)

1ª rodada completa (G1), diff `34ab6714..46000ed5` (merge-base com a `develop`): `bin/forge-check` (+44 de código), `bin/forge-testes` (1 linha, ESCOPO+ E14.59), R-QA, `agents/jarvis.md`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, fragmento do changelog, 2 specs novas e 2 ajustadas, `tests/test_volta_alinhada.py` (novo), `tests/test_volta_por_delta.py`. H1 dentro do teto.

## Achados
- A1 (bloqueante) bin/forge-check:4437 · Teto de 3 voltas e recusa da 4ª sem decisão do dono (recusa_da_volta, :4502) divergem da DECISÃO DO DONO 25/11 17:07 (resolver, não cortar: quantas voltas forem precisas; da 4ª, tech-lead e o revisor que reprovou juntos). A 4ª do #875 já corre; com o merge, o brief gerar --volta a recusa (S1).
- A2 (bloqueante) docs/regras/R-QA.md:17 · Texto segue a ordem substituída: "Até 3 voltas por item sem o dono" aqui, "recusa a 4.ª" e decisão ao dono com "cortar o item" em autor-ate-o-merge.md:10, "até 3 voltas" em agents/jarvis.md:31 e changelog.d/v0481-voltas-alinhada.md:2. Alinhar à ordem de 17:07.
- A3 (recomendado) tests/test_volta_por_delta.py:1189 · VA-M7 morre por erro (AttributeError com a catraca None), não por asserção (forge-mutante: "o teste declarado deu erro sob o mutante"). Afirmar a linha de falha fechada de modo que o mutante caia na asserção.
- A4 (recomendado) tests/test_volta_alinhada.py:53 · test_segunda_volta_nao_tem_a_restricao e test_terceira_volta_sem_mexer_em_teste_cumpre_a_restricao (:59) só afirmam ausência de "(R-QA)"; afirmar também o rc e o "resultado:" esperados.

## Sondas
- S1 · test_volta_por_delta.BriefDeVolta.test_volta_quatro_so_com_decisao_do_dono_que_cita_a_branch (brief gerar --volta sobre a 3ª, sem decisão) · espera: 4ª volta gerada (ordem 17:07) · obtido: rc 1, "volta 4 recusada ... no máximo 3 voltas por item sem o dono" (teste verde)

## Verificações
- Testes do diff, à mão no head 46000ed5: `python3 -m unittest tests.test_volta_alinhada tests.test_volta_por_delta` · Ran 120 tests, OK.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-voltas-alinhada.json tests/mutantes/v0481-voltas-alinhada-2.json` · VA-M1..VA-M12 morreram (VA-M7 por erro, A3). `--cobertura --base 34ab6714`: toda guarda mudada coberta; só `tests/pesos-d4.json` fora (dado, sem guarda).
- CI do head 46000ed5 (`gh pr checks 902`): bateria (passos), bateria (verificações longas), instalação e árvore já provada verdes; as 10 partes da suíte pendentes na leitura, por isso sem a linha `ci:`. `bateria (pareceres)` espera este parecer.
- Catraca (log do run 45743992001): pede o rótulo `afrouxa-regra` do dono por duas causas: o teste `test_volta_dois_so_com_decisao_do_dono_que_cita_a_branch` renomeado para `test_volta_quatro_...` e a mudança em `bin/forge-check` (controle, ADR 0008). Os 5 "valor esperado trocado" são as contagens 1→3 e 2→4 que a regra nova exige; conferidos, coerentes com o diff.

## Parecer
Reprovado. O código implementa bem a ordem de 07:31 (restrição da 3ª volta, recusa de teste removido ou enfraquecido pelas medidas da catraca, contagem da volta sem `Volta-de:` pelo parecer reprovado da branch, falha fechada), com testes de comportamento e mutantes mortos. Mas a ordem em vigor é a de 17:07, que tira o teto: A1 e A2 pedem trocar o teto e a recusa da 4ª por "sem teto; da 4ª em diante, o brief de volta junta o tech-lead e o revisor que reprovou", e alinhar R-QA, skill, `jarvis.md` e o fragmento. A restrição da 3ª em diante não conflita com a ordem de 17:07 e fica. A3 e A4 viram cartão depois do merge.
