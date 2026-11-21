---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: 4dec77902f90f0db3c7887085ab0f4294d55f2e8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1 Q1, leitor da quarentena (v0478, E61.9), revalidação

Volta por delta. As rodadas anteriores (até `eec2c1c1`, aprovada com A6 corrigido pelo `RecursionError`) ficam no git. Lido: `forge-check parecer delta` de `eec2c1c1..4dec7790`; no domínio só `bin/forge_quarentena.py` (`:1`-`:21` docstring e importação de `hooks/_json_raso.py`, `:48`-`:53` a medida antes do `json.loads` e o `except` sem `RecursionError`); lido também `hooks/_json_raso.py` (inalterado, agora usado pelo leitor). Fora do domínio, conferidos só como prova: `tests/test_forge_quarentena.py` (teste novo do teto) e `tests/mutantes/v0479-quarentena-s1-5.json` (M42 refeito). Requisitos e mitigações como antes (modelo Q0, `docs/security/ameacas/bp1-quarentena.md`).

Gatilhos: autorizacao, ci-cd, controles-do-forge.

Estado dos achados anteriores:
- A1 a A5 corrigidos (rodada `df0251ca`); o delta não toca nessas linhas.
- A6 corrigido de outro jeito, mais forte: `bin/forge_quarentena.py:49` mede o aninhamento com `fundo_demais` (teto 64, passe linear, sem recursão) antes do `json.loads` e devolve `([], ["quarentena ilegível: aninhamento acima do teto"])` (M4.1), o que não depende do `RecursionError` do 3.12 nem da ausência dele no 3.14. A retirada do `RecursionError` do `except` (`:53`) é segura: a medida acompanha a profundidade do `json` em todo prefixo válido (mesmo tratamento de string e escape), e o fechamento a mais que baixa o contador torna o texto inválido antes de qualquer aninhamento (S9). A importação põe `hooks/` no `sys.path` só durante o `from _json_raso import` (`:16`-`:21`, retirada no `finally`), caminho dentro do próprio plugin; sem sombra de módulo de fora.

## Sondas
- S6 · `carregar` de `{"entradas":` + 30000 `[` + 30000 `]` + `}` (60013 bytes) · espera: `([], [motivo])` · obtido: `([], ['quarentena ilegível: aninhamento acima do teto'])`
- S7 · `carregar` de `{"entradas":` + 8000 × `[{"a":` + `1` + 8000 × `}]` + `}` (64014 bytes) · espera: `([], [motivo])` · obtido: `([], ['quarentena ilegível: aninhamento acima do teto'])`
- S8 · mutante M42 (`if False and fundo_demais(texto):`) numa cópia (`git archive HEAD`) e `python3 -m unittest` dos dois testes do M42 · espera: falha · obtido: `FAILED (failures=1, errors=2)`; na mesma cópia, S6 sobe `RecursionError` (sem a medida, o 3.12 quebra)
- S9 · 20000 `]` antes de `{"entradas":` + 20000 `[` + 20000 `]` + `}` (contador negativo) · espera: `([], [motivo])` sem recursão · obtido: `([], ['quarentena ilegível: Expecting value: line 1 column 1 (char 0)'])`
- S10 · `[` dentro de string com `\"` repetido 100 vezes · espera: lido, sem falso positivo · obtido: entrada lida (validação do formato segue com `validar`)

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Teste do módulo rodado no head `4dec7790` (`python3 -m unittest tests.test_forge_quarentena`: 28 testes, OK). Suíte inteira não rodada (roda no CI); CI do head não consultado (credencial do `gh` fora do sandbox): lacuna registrada.
- Só o Python 3.12.3 está na máquina; o 3.14 não foi rodado (lacuna). A medida vem antes do `json.loads` e só usa o próprio passe sobre os caracteres (o leitor passa `str`), então o veredito não depende da versão.
- Sondas locais em pasta temporária, módulo importado isolado (`python3 -I`); nada explorado fora da máquina; nenhuma ferramenta instalada.
