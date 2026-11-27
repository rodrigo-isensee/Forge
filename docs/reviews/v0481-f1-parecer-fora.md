---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f1-parecer-fora
commit: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E29.5, #925, F1 corte 1, volta 1 por delta)

## Parecer
Aprovado: os dois bloqueantes da 1.ª rodada (A1, A2) estão resolvidos e os dois recomendados (A3, A4) foram atendidos na mesma volta, com teste de comportamento e mutante por guarda.

- Delta lido (H3): `forge-check parecer delta` de e26310c2..edaf7bc0, só no domínio: `bin/forge_pareceres.py`, `docs/indice-forge.md`, `tests/mutantes/v0481-f1-parecer-fora-3.json`, `tests/mutantes/v0481-g2-1-publicar-5.json`, `tests/test_forge_pareceres.py`. Nada fora dele foi relido.
- A1 resolvido: o `de` do M27 passa a `faltam = [s for p in paginas for s in p if isinstance(s, dict)]`, único no arquivo; o M17 acompanha a nova indentação dentro do `try`. Suíte 3.12 e 3.14 parte 4/5 verde no CI.
- A2 resolvido: `scripts/indice-forge.py --conferir` em dia; a linha do `forge_pareceres.py` deixa de dizer "só a escrita". Parte 2/5 verde no CI.
- A3 atendido: `ler` recusa, antes de qualquer chamada ao `gh`, `contas` que não seja set/frozenset de str não vazias (a sonda S1 da 1.ª rodada vira subteste); o teste confere que o `gh` não foi chamado. M18 e M19 morrem.
- A4 atendido: `KeyError`, `TypeError`, `AttributeError` e `ValueError` do laço de `conferir` viram Recusa, como no `publicar`; a `Recusa` vinda do `gh` passa intacta (não está na tupla). Os três casos do teste (creator str, user str, PR sem `number`) chegam por caminhos distintos ao `except`. M20 morre.
- Tamanho (H1): +9 linhas de código no delta, um comportamento (a leitura falha fechada), dentro do teto.
- Commits: 2 no delta, Conventional Commits em português, escopo e etapa.

## Provas
- ci: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb verde
- suíte: edaf7bc08b371efafbd4eeb58dcab39bcb0143eb rc=0 módulos=test_forge_pareceres,test_indice_forge
- check-runs do sha: suíte 3.12 e 3.14 partes 1 a 5, teto de pulados, bateria (passos), bateria (python 3.14), bateria (verificações longas), instalação (python 3.14) e árvore já provada na develop em success; fora `bateria`, `bateria (pareceres)` e `catraca`, que esperam parecer ou rótulo.
- `python3 -m unittest tests.test_forge_pareceres tests.test_indice_forge` no edaf7bc0, com ambiente limpo e flock na trava-teste-b: Ran 88 tests, OK; `scripts/indice-forge.py --conferir`: em dia (/root/.forge-contrib/v0481-tl347-afetados.log).
- `bin/forge-mutante --processos 1 --base e26310c2 <2 specs>`: M17 a M20 e M24 a M30 morreram, rc=0 (/root/.forge-contrib/v0481-tl347-mutantes.log).
