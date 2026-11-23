---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ci-anotacao
commit: 3487d89164ca7a88c317a071707d168196fa08f3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E137.11, PR #821, anotação da suíte no CI)

Escopo: o commit `3487d891` sobre a base `0e59c446` (E137.2). Arquivos: `scripts/suite-partes.py` (1 linha de código e 2 de comentário), `tests/test_suite_partes.py` (1 teste), `tests/mutantes/v0480-ci-anotacao.json` (1 mutante) e `changelog.d/v0480-ci-anotacao.md`. O commit `cec59313` posterior traz só o parecer de devops e não entra no código revisado.

## Leitura
- Causa e conserto batem: o discover da divisão importa `tests/test_catraca.py`, que faz `os.environ.pop("GITHUB_ACTIONS")` no import (linha 30); o `main` guardava a referência viva do `os.environ`, então `por_parte` (linhas 407 e 232) via a variável sumida. O `dict(os.environ)` na linha 483 fotografa o ambiente antes de qualquer import de teste; `por_duas_partes` passa a mesma cópia aos filhos, sem mudança de comportamento.
- O único outro leitor do `os.environ` vivo (linha 310, número de processos) não lê `GITHUB_ACTIONS`; fica como está.
- Quando o chamador passa `environ`, nada muda (os testes da casa usam esse caminho).
- Tamanho: 1 linha de código, um comportamento só (H1).
- Teste de comportamento: módulo de brinquedo que tira a variável no import, 5 partes com `GITHUB_ACTIONS=true`; exige 4 verdes com `::notice title=forge-tempos` e 1 vermelha com `::error title=forge-suite parte`. Não lê a fonte; o subprocesso usa o `AMBIENTE` limpo do arquivo.
- Guarda do diff: a linha 483 é a única mudada de controle e tem um mutante declarado (M1), com o teste do ramo de falha.
- Commit em Conventional Commits, em português, com o porquê; fragmento de changelog presente.

## Verificação
- `python3 -m unittest tests.test_suite_partes`: `Ran 50 tests in 26.025s`, `OK`.
- `bin/forge-mutante tests/mutantes/v0480-ci-anotacao.json --processos 1`: `M1 · morreu · scripts/suite-partes.py:483`.
- `bin/forge-mutante --cobertura --base 0e59c446…`: saída 0, sem guarda descoberta.
- Suíte completa: fica no CI do PR #821 (no momento da leitura, o check `catraca` estava pendente); não rerrodada aqui.

## Sondas

## Parecer
Aprovado. Conserto mínimo e correto na causa (referência viva ao ambiente), com teste que falha antes e passa depois e mutante morto. Merge segue os pareceres de QA e segurança da classe C (`forge-check pr` ainda os aponta) e o CI verde.
