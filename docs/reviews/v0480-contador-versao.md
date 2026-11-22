---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 1593c1a1ee1547c1c208c2293291f88fdd550a8c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E103.13, CONTADOR-DA-VERSAO, revalidação da volta de CI)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0480-contador-versao.md`, intervalo 362b45ad..1593c1a1, sem o que veio da develop; no domínio: `bin/forge-contador`, `docs/indice-forge.md`, `skills/fluxo-do-pedido/SKILL.md`, `tests/mutantes/v0480-contador-versao.json`, `tests/pesos-d4.json`, `tests/test_forge_contador.py`. Parecer anterior: 41fbbc83 (aprovado no head 362b45ad).

Ferramentas citadas, sem refazer: CI do PR #787 no head 1593c1a1 com a suíte, a catraca, a instalação e a bateria (passos) verdes; a bateria (pareceres) espera estes pareceres. Teste do item rodado: `tests.test_forge_contador`, 24 testes, OK.

## Pergunta do autor: `Path(n).name.lower() != "readme.md"` contorna a guarda TEXTO?
No código, não. A guarda de `tests/test_reval_delta.py` existe para que o código não trate um caminho de TEXTO como normativo; aqui a leitura é só de nome (motivo `nome`, nada de `LE_CONTEUDO`), o arquivo fica dentro de `changelog.d/`, que a própria guarda tolera, e a forma é a mesma que o consumidor real usa (`bin/forge-changelog:68` e `:320`). Com isso, o contador passa a contar o mesmo que a release junta. Antes, um `readme.md` em minúsculas entrava na conta do contador e ficava fora da release. A troca fica. Registrar em `CITACOES_CONHECIDAS` não é preciso para esta linha.

O custo apareceu no teste: para não citar `README.md`, o teste trocou o caso real (`changelog.d/README.md`, o arquivo que existe no repositório) por `readme.md`, e o `.lower()` novo ficou sem cobertura (A1).

## Achados
- A1 (bloqueante) tests/test_forge_contador.py:90 · `.lower()` de bin/forge-contador:54 sem teste nem mutante: o mutante sem ele sobrevive (S1) e conta o `changelog.d/README.md` real (S2). Correção em "Detalhe de A1".
- A2 (recomendado) tests/test_reval_delta.py:189 · fora do delta, vira cartão: `caminho in linha` diferencia caixa, então citações em minúsculas passam sem a lista (já é o caso de `bin/forge-changelog:68` e `:320`). Dono: security-engineer, com o arquiteto.

## Detalhe de A1
Os dois casos do teste agora só usam `readme.md`. Correção: um caso com caixa mista, como `changelog.d/Readme.md` (que não cita o caminho de TEXTO), mais o mutante `M8` em `tests/mutantes/v0480-contador-versao.json`, de `Path(n).name.lower() != "readme.md"` para `Path(n).name != "readme.md"`. A outra saída é manter `README.md` no teste e registrar `("tests/test_forge_contador.py", "README.md"): (n, "nome")` em `CITACOES_CONHECIDAS`; essa mexe na lista da guarda e pede o parecer de segurança.

## Sondas
- S1 · cópia do head 1593c1a1 com bin/forge-contador:54 sem `.lower()`; `tests.test_forge_contador` · espera: falha · obtido: 24 testes, OK (o mutante sobrevive)
- S2 · `forge-contador` original e o mutante de S1 na worktree do head · espera: mesma conta · obtido: original `0.47.15: 7 de 20`, mutante `0.47.15: 8 de 20`

## Parecer
Reprovado no head 1593c1a1, só por A1. O resto do delta passa: o índice foi regerado, a skill ficou mais curta sem perder o invariante, e M7 e `pesos-d4.json` estão consistentes. Na volta, o delta precisa só do caso novo e do mutante M8.
