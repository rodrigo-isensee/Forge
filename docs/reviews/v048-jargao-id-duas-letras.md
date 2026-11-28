---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-jargao-id-duas-letras
commit: 51c259f8419594b6b077cc42ae7e15f67106627f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Code review: jargão com ID de regra de duas letras, branch limpa (E13.27)

Escopo: o commit único `51c259f8` sobre a develop `9479650b` (o Base-sha do brief, que é o merge-base), refeito em branch limpa (E13.25) no lugar do #966, cujos três portões aprovaram o mesmo patch no head `ff6bff06`. O revisor não fez a entrega.

## Sondas

## Parecer
Aprovado no head 51c259f8. É o mesmo patch já aprovado no #966, e não entrou mais nada.

- O diff `origin/develop...51c259f8` tem só 4 arquivos (34 linhas a mais, 1 a menos): `hooks/meta.py` (1 linha), `tests/test_meta.py` (5 linhas), `tests/mutantes/v048-jargao-id-duas-letras.json` e `changelog.d/v048-jargao-id-duas-letras.md`. Os pareceres da v047 não vieram junto.
- Comparação com a branch antiga: o diff de `hooks/`, `tests/` e `changelog.d/` em `origin/develop...origin/melhoria/v047-jargao-id-duas-letras`, contra o da branch nova, fica igual depois de trocar o prefixo `v047`/`v048` e tirar as linhas `index`. Ficam só o nome do arquivo de mutantes, o do fragmento e o campo `pedido` da spec (`v048-jargao-id-duas-letras`, que segue o padrão das outras specs `v048-*`). O texto do fragmento continua igual ao aprovado (cita `v047 E2.351`, a etapa de origem).
- `hooks/meta.py:174` no head: `"regra": re.compile(r"(?<![\w-])R-[A-Z]{2,}(?![\w-])")`.
- Guarda mudada: só a linha 174, que tem dois mutantes declarados (M1 `{3,}`, M2 `{1,}`), ambos apontando para o teste de comportamento `test_regra_de_duas_letras_conta_e_uma_letra_nao` (o caso positivo `R-QA` e os negativos `R-X` e `R-Qa`).

Verificadores, rodados no meu clone no head 51c259f8:
- `python3 -m unittest tests.test_meta`: 56 testes, OK.
- `bin/forge-mutante tests/mutantes/v048-jargao-id-duas-letras.json`: M1 e M2 morreram (`hooks/meta.py:174`).
- ci: 51c259f8419594b6b077cc42ae7e15f67106627f verde

CI do PR #968 (rascunho) no 51c259f8: verde fora de `bateria (pareceres)`, `bateria` e `catraca`, que esperam o parecer ou o rótulo.

Tamanho (H1): 1 linha de código, dentro do teto. Neutralidade (`R-NEUTRO`): nada de projeto no diff. Não abro cartão novo.
