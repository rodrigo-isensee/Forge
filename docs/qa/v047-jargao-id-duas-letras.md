---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v047-jargao-id-duas-letras
commit: ff6bff0690d9046d570c5d2b5c04824382bcf9b8
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v047-jargao-id-duas-letras (E2.351, parecer E2.374; delta E13.12)

## Achados

## Critério → teste → resultado
Obrigação (E2.351, sem especificação de UX nova): a medida de jargão conta o ID de regra de duas letras (R-QA) e continua sem contar uma letra só.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.351 conta R-QA | `tests.test_meta.JargaoPorClasse.test_regra_de_duas_letras_conta_e_uma_letra_nao` (1ª asserção) | mínimo de duas letras | passou |
| E2.351 R-X e R-Qa não contam | mesmo teste (2ª asserção) | uma letra; minúscula | passou |
| ID de três letras ou mais segue contando | amostra manual R-QAB, R-SEGURANCA | acima do mínimo | passou |

## Cenários e resultado real
- Diff contra a base 1b88640e: `hooks/meta.py` (1 linha, `{3,}` para `{2,}`), `tests/test_meta.py`, spec de mutantes e fragmento de changelog. Escopo confere com E2.351.
- `python3 -m unittest tests.test_meta`: 16 testes, OK. Classe `JargaoPorClasse`: 10 testes, OK.
- Vermelho antes do verde, à mão (o `forge-testes --vermelho 1b88640e` estourou 500 s neste ambiente, rc=124, sem veredito; não vale como vermelho): cópia do head com `hooks/meta.py` da base; o teste novo falha com `AssertionError: {} != {'regra': 1}`; com o head passa.
- Amostra manual no head: `R-QA`→regra 1; `R-QAB`→1; `R-SEGURANCA`→1; `R-X`→{}; `R-Qa`→{}; `R-QA-1`→{}; `R-QA.`→1.
- Mutantes (`forge-mutante tests/mutantes/v047-jargao-id-duas-letras.json`, rc=0): `M1 · morreu · hooks/meta.py:144`, `M2 · morreu · hooks/meta.py:144`.
- Cobertura (`forge-mutante --cobertura --base 1b88640e`): rc=0, nenhuma condição mudada sem mutante (uma linha de guarda mudada, dois mutantes nos dois lados da fronteira).
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha); não rodada aqui.
- Sem bug aberto; PA-7 conferido: AR-1 (lista de mutantes) não se repete, a linha mudada tem mutante.

## Delta cf59506c..ff6bff06 (E13.12, pedido v048)
- ci: ff6bff0690d9046d570c5d2b5c04824382bcf9b8 verde
- Base do ci: run 46166166392 concluído com sucesso: suítes 1 a 5 de 5, instalação, pareceres, passos, verificações longas, catraca; o run do head atual cc21d7e8 difere só em docs/security/.
- O delta é o merge da develop a1971853 (pais ae25187b e a1971853). `git diff a19718532c ff6bff06` contra a base: 7 arquivos (hooks/meta.py 1 linha, tests/test_meta.py +5, spec de mutantes, fragmento de changelog, 3 pareceres). Nada da develop perdido nem alterado fora do esperado; hooks/meta.py:174 é `R-[A-Z]{2,}`.
- `python3 -m unittest tests.test_meta` no head: 56 testes, OK.
- `bin/forge-mutante tests/mutantes/v047-jargao-id-duas-letras.json` (rev=ff6bff0690d9): `M1 · morreu · hooks/meta.py:174`, `M2 · morreu · hooks/meta.py:174`.
- Sem achado; comportamento igual ao aprovado em cf59506c.
