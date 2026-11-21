---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: 4dec77902f90f0db3c7887085ab0f4294d55f2e8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E61.8, BP1 Q1 formato e leitor puro da quarentena)

## Achados
- A2 (recomendado) changelog.d/v0479-bp1-q1-leitor.md:2 · a docstring já não cita a proposta, mas o fragmento segue citando `docs/propostas/v0479-bp1-quarentena.md`, ausente desta branch e da `develop` (f96ede5); link quebrado se esta entrar antes. Vira cartão depois do merge.
- A3 (recomendado) tests/mutantes/v0479-quarentena-s1-5.json:16 · M42 segue na spec de outro pedido (`v0479-quarentena-s1`), e não numa `v0479-bp1-q1-leitor-<n>.json`; `--cobertura` acusa "spec editada". Vira cartão depois do merge.

## Parecer
Aprovado no head 4dec7790. Revalidação pelo delta: li só `forge-check parecer delta docs/reviews/v0479-bp1-q1-leitor.md`, intervalo eec2c1c1..4dec7790, sem o que veio da `develop`; domínio: `bin/forge_quarentena.py`, `changelog.d/v0479-bp1-q1-leitor.md`, `docs/indice-forge.md`, `tests/mutantes/v0479-quarentena-s1-5.json`, `tests/pesos-d4.json`, `tests/test_forge_quarentena.py`.

1. Leitor: `carregar` mede o aninhamento com `fundo_demais` de `hooks/_json_raso.py` (já na `develop`, 89a4e02b) antes do `json.loads` (bin/forge_quarentena.py:49) e devolve "quarentena ilegível" acima de 64 níveis. Com o teto, o `RecursionError` deixa de ser alcançável, e tirá-lo do `except` é coerente; o erro de decodificação segue no `ValueError`. Falha fechada igual no 3.12 e no 3.14, sem depender do contador do `json`. Reuso do teto único (import, não cópia), sem mecanismo novo.
2. Import por `sys.path.insert`/`pop` em `try/finally`: o caminho sai do `sys.path` mesmo se o import falhar; `json`, `re` e `os` já carregados antes, sem sombra de módulo de `hooks/`.
3. Teste do ramo de falha `Carregar.test_aninhamento_medido_pelo_leitor_no_teto_de_json_raso` (tests/test_forge_quarentena.py:74): 64 níveis passam ao formato e 65 são "ilegível"; comportamento, fronteira exata.
4. `python3 -m unittest tests.test_forge_quarentena`: 28 testes OK. `bin/forge-mutante --processos 1 --ids M42 tests/mutantes/v0479-quarentena-s1-5.json`: M42 morreu (bin/forge_quarentena.py:49). `--cobertura --base eec2c1c1`: a guarda do delta está coberta por M42; o resto da saída é do merge da `develop` e o "spec editada" é o A3.
5. Índice (`docs/indice-forge.md`) e pesos (`tests/pesos-d4.json`) só acrescentam linhas das unidades novas; `test_forge_quarentena: 0.0` segue o padrão de outros módulos rápidos.
6. Tamanho: cerca de +10/-2 de código no delta, dentro do teto H1, um comportamento só. Suíte inteira fica no CI do PR (não rerrodada aqui). Commit único, Conventional Commits em português.
