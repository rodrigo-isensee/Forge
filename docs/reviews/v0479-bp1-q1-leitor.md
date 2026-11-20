---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q1-leitor
commit: d0619ab2ca768b802cc9731ea5792c56447da461
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.44, BP1 Q1 formato e leitor puro da quarentena)

## Achados
- A1 (bloqueante) bin/forge_quarentena.py:56 · `desde` no futuro não é recusado e `ativas` só confere `hoje <= prazo`: entrada com desde 2030-01-01 e prazo 2030-01-08 passa em `validar` e fica ativa hoje, por mais de 3 anos (S1). Fura o prazo de 7 dias da D3 (07:47 de 20/11). Sugestão: erro se `desde > hoje`, com teste e mutante.
- A2 (recomendado) bin/forge_quarentena.py:1 · a docstring e o fragmento `changelog.d/v0479-bp1-q1-leitor.md` citam `docs/propostas/v0479-bp1-quarentena.md`, que não está nesta branch nem na `develop` (só em `melhoria/v0479-estabilidade-bp`, f20d8cd1); o link fica quebrado se esta entrar antes.

## Sondas
- S1 · validar e ativas com {desde: 2030-01-01, prazo: 2030-01-08, autorizacao: A-1} e hoje 2026-11-21 · espera: erro de prazo ou entrada fora de ativas · obtido: validar [] e ativas com 1 entrada

## Parecer
Reprovado pelo A1. Diff 004ce869..d0619ab2: 96 linhas de código em `bin/forge_quarentena.py`, dentro do teto H1, um comportamento só; o resto é teste, spec de mutantes, `tests/quarentena.json` vazio e o fragmento.

1. Leitura: módulo pequeno, só biblioteca padrão, data sempre injetada (nenhuma leitura de relógio; `test_o_leitor_nao_tem_padrao_de_data`), falha fechada em `ativas` e `vencidas` quando `validar` acusa qualquer erro. Nomes e funções claros.
2. A1: o desenho define `desde` como a data de entrada (seção 3, tabela do formato) e as ativas como "até o `prazo`, inclusive"; sem `desde <= hoje`, o teto de 7 dias (D3) e a prorrogação única viram letra morta, porque a entrada vale desde já até um prazo arbitrário. Conserto curto em `validar` (ou em `_erros_da_entrada` com `hoje`), com teste do ramo de falha e mutante declarado na spec.
3. Testes: `python3 -m unittest tests.test_forge_quarentena` 20 testes OK no head. Mutantes do diff (`bin/forge-mutante --processos 1` nas três specs): 17 de 17 morreram (Q7 e Q13 por erro do teste declarado, aceito pela ferramenta). `--cobertura --base 004ce869`: toda guarda listada coberta; `tests/quarentena.json` aparece sem cobertura, é dado, não guarda.
4. Suíte inteira: fica no CI do PR (não rerrodada aqui).
5. Commits: dois, Conventional Commits em português, coerentes (código e testes; mutantes).
