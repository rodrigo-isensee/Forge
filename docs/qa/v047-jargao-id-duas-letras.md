---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-id-duas-letras
commit: cf59506c11d7ff03caa4418ef9e984e7f5f9ed82
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-jargao-id-duas-letras (E2.351, parecer E2.374)

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
