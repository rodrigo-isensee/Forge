---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-id-duas-letras
commit: cf59506c11d7ff03caa4418ef9e984e7f5f9ed82
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Code review: ID de regra de duas letras na medida de jargão (E2.351; revisão E2.372)

Escopo: parecer completo (não havia parecer anterior) sobre `git diff 1b88640e...cf59506c`: `hooks/meta.py:144` (classe `regra` de `{3,}` para `{2,}`), o teste `test_regra_de_duas_letras_conta_e_uma_letra_nao` (`tests/test_meta.py:195`), a spec `tests/mutantes/v047-jargao-id-duas-letras.json` e o fragmento de changelog. O revisor não fez a entrega.

## Achados

## Sondas

## Parecer
Aprovado no head cf59506c. Faz o que a etapa pede, nem mais nem menos: `R-QA` (o único ID de duas letras em `docs/regras/`) passa a contar como jargão, e `R-X` e `R-Qa` continuam fora.

Sondas de leitura (não provam bloqueante, ficam aqui): `classes_de_jargao` dá `{'regra': 1}` para `R-QA`, `R-QA.` e `(R-QA)`; `{}` para `R-QA-2` e `R-QAs`; `PR-QA` segue na classe `cartao`, sem contar duas vezes; `R-MAIN e R-QA` dá `{'regra': 2}`.

Verificadores, rodados no clone no head cf59506c:
- `python3 -m unittest tests.test_meta`: 16 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-jargao-id-duas-letras.json`: M1 e M2 morreram (`hooks/meta.py:144`), rc=0.
- `bin/forge-mutante --cobertura --base 1b88640e`: rc=0.

Tamanho (M14): 6 linhas de código e teste, dentro da orientação. A suíte inteira fica para o CI do PR, que ainda não existe (o brief manda não abrir). Neutralidade (`R-NEUTRO`): nada de projeto entra. O único item do Entregar da E2.351 tem commit (cf59506c).

Conferi `docs/engineering/achados-recorrentes.md` (PA-7): AR-1 (os dois sentidos do quantificador têm mutante), AR-4 (o teste chama a função no processo), AR-9 (nenhum texto cita o limite antigo de três letras) e AR-12 (a spec nasce no mesmo commit que muda a linha) não se repetem. Nenhuma linha AR é gravada.
