---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: eec2c1c14cc4de4c1af0d39e3bac4d808ce88b90
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: BP1 Q1, leitor da quarentena (v0478, E61.2), revalidação

Volta por delta. As rodadas anteriores (reprovada em `d0619ab2`, aprovada com A6 recomendado em `df0251ca`) ficam no git. Lido: `forge-check parecer delta` de `df0251ca..eec2c1c1`; no domínio só `bin/forge_quarentena.py` (`:6`-`:7` docstring e `:43` o `except`); fora do domínio, conferidos só como prova da correção: `tests/test_forge_quarentena.py` (teste novo) e `tests/mutantes/v0479-quarentena-s1-5.json` (M42). Requisitos e mitigações como antes (modelo Q0, `docs/security/ameacas/bp1-quarentena.md`).

Gatilhos: autorizacao, ci-cd, controles-do-forge.

Estado dos achados anteriores:
- A1 a A5 corrigidos (rodada `df0251ca`); o delta não toca nessas linhas.
- A6 corrigido: `bin/forge_quarentena.py:43` inclui `RecursionError` na tupla do `except`, e `carregar` devolve `([], ["quarentena ilegível: ..."])` (M4.1); teste `Carregar.test_json_aninhado_fundo_devolve_erro_sem_quebrar` (raiz e dentro de `entradas`, abaixo do teto); mutante M42 retira o `RecursionError` e o teste cai (2 erros); S6 refeita e estendida a objetos e mistura.

## Sondas
- S6 · `carregar` de `{"entradas":` + 30000 `[` + 30000 `]` + `}` (60013 bytes) · espera: `([], [motivo])` · obtido: `([], ['quarentena ilegível: maximum recursion depth exceeded ...'])`
- S7 · `carregar` de `{"entradas":` + 8000 × `[{"a":` + `1` + 8000 × `}]` + `}` (64014 bytes, passa pelo `object_pairs_hook`) · espera: `([], [motivo])` · obtido: `([], ['quarentena ilegível: maximum recursion depth exceeded ...'])`
- S8 · mutante M42 aplicado numa cópia (`git archive HEAD`) e `python3 -m unittest tests.test_forge_quarentena.Carregar.test_json_aninhado_fundo_devolve_erro_sem_quebrar` · espera: falha · obtido: `FAILED (errors=2)`

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Teste do módulo rodado no head `eec2c1c1` (`python3 -m unittest tests.test_forge_quarentena`: 27 testes, OK). Suíte inteira não rodada (roda no CI); CI do head não consultado (credencial do `gh` fora do sandbox): lacuna registrada.
- Sondas locais em pasta temporária, módulo importado isolado (`python3 -I`); nada explorado fora da máquina; nenhuma ferramenta instalada.
