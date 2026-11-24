---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 23026d32d43b1139c5eac2bf3529a8bd2b47ff2b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E2.8, PR #867, D3 teste afrouxado), volta por delta

Volta por delta sobre o parecer aprovado em `8daa1611` (rodada anterior no git, `793f2440`). Delta lido com `forge-check parecer delta`: `8daa1611..23026d32`; no domínio, só `tests/test_catraca.py:777` (uma linha); fora do domínio, os pareceres de QA, de review e o anterior deste domínio. `tests/catraca.py` e as pastas de controle (`hooks/`, `bin/`, `scripts/`, `.githooks/`, `.github/`) não mudaram; o resto da rodada anterior não foi relido.

Gatilhos: controle do Forge que analisa entrada (catraca, R-CONFORMIDADE)

## Achados
- A2 (recomendado) tests/catraca.py:792 · Sem mudança neste delta: o vácuo só de constantes com um nome (`assertEqual(int(1 + 2), 3)`) ainda passa calado (S4 do parecer de `8daa1611`). Liste em `valores_para_conferir` os pares apagado -> renomeado (`:762`), sem barrar.

## Estado dos achados anteriores
- **A1 (bloqueante): corrigido** em `8daa1611`; o delta não toca `tests/catraca.py`.
- **A2 (recomendado): aberto, inalterado** (o delta não mexe no código da catraca). Severidade baixa, esforço P, dono: autor da branch.

## Conclusão por escrito: o delta só aperta
O teste `test_acrescimos_ajudante_e_arquivo_fora_de_tests_passam` acrescentava `test_d` com `assert 1`, que `_vacua` tira da contagem: o acréscimo não exercitava a contagem de asserções, e os mutantes D3B1 (`tests/catraca.py:750`) e D3B5 (`:709`) sobreviviam (A1 do parecer de QA). Com `assert self` (tem `ast.Name`), a asserção conta, e o teste passa a exigir que um teste novo com asserção real não barre: a garantia sobre a catraca fica mais estrita, sem nenhuma mudança no controle. Nenhuma regra muda; nada afrouxa.

**Testes:** `python3 -m unittest tests.test_catraca.TestesAfrouxados` no head 23026d32: 23 testes, OK. Suíte inteira: CI do PR #867 no head 23026d32 (run 45501111533), em andamento na escrita (partes 1, 2 e 4 em 3.14 e 1 e 4 em 3.12 verdes; as demais pendentes); o merge depende do CI todo verde. `catraca` vermelho por `mudança em tests/catraca.py` (pede o rótulo `afrouxa-regra` do dono, esperado) e `bateria (pareceres)` vermelho por pareceres presos ao head anterior, ambos fora do domínio deste delta. A morte de D3B1 e D3B5 é prova do parecer de QA.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e unittest da biblioteca padrão. Varredura de segredos não aplicável (delta de uma linha de teste).
