---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: eec2c1c14cc4de4c1af0d39e3bac4d808ce88b90
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E61.4, BP1 Q1 formato e leitor puro da quarentena)

## Achados
- A2 (recomendado) bin/forge_quarentena.py:1 · a docstring e o fragmento `changelog.d/v0479-bp1-q1-leitor.md` citam `docs/propostas/v0479-bp1-quarentena.md`, que segue fora desta branch e da `develop`; o link fica quebrado se esta entrar antes. Vira cartão depois do merge.
- A3 (recomendado) tests/mutantes/v0479-quarentena-s1-5.json:16 · M42 foi declarado na spec de outro pedido (`v0479-quarentena-s1`, já na `develop`), e não numa spec `v0479-bp1-q1-leitor-<n>.json` deste item; `--cobertura` acusa "spec editada". Vira cartão depois do merge.

## Parecer
Aprovado no head eec2c1c1. Revalidação pelo delta: li só `forge-check parecer delta docs/reviews/v0479-bp1-q1-leitor.md`, intervalo df0251ca..bc0a9b43 (bc0a9b43 só acrescenta o parecer da segurança), domínio: `bin/forge_quarentena.py`, `changelog.d/v0479-bp1-q1-leitor.md`, `tests/mutantes/v0479-quarentena-s1-5.json`, `tests/test_forge_quarentena.py`.

1. A6 da segurança (JSON aninhado fundo derrubava o leitor com `RecursionError`) fechado: `RecursionError` entra no `except` de `carregar` (bin/forge_quarentena.py:43) e vale como "quarentena ilegível", falha fechada coerente com o resto do leitor. Mudança de uma linha de guarda, mais a docstring e o fragmento do changelog.
2. Teste do ramo de falha `Carregar.test_json_aninhado_fundo_devolve_erro_sem_quebrar` (tests/test_forge_quarentena.py:64): 30000 colchetes abaixo do `TETO_BYTES`, na raiz e dentro de `entradas`; comportamento, não leitura da fonte.
3. `python3 -m unittest tests.test_forge_quarentena`: 27 testes OK. `bin/forge-mutante --processos 1 --ids M42 tests/mutantes/v0479-quarentena-s1-5.json`: M42 morreu (bin/forge_quarentena.py:43). `--cobertura --base df0251ca`: sem guarda descoberta (rc=0). `--conferir --base df0251ca`: trechos no lugar.
4. Tamanho: +2/-1 de código no delta, dentro do teto H1, um comportamento só.
5. Suíte inteira: fica no CI do PR (não rerrodada aqui).
6. Commit da correção: um, Conventional Commits em português, coerente.
