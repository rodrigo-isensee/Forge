---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d3-teste-enfraquecido
commit: e7a71a8e2f87ef83fc7cb3708396ac05e87ba65d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E174.22 (D3, catraca recusa teste afrouxado; PR #867)

Diff revisado: `aabc476c..e7a71a8e` (6 commits; `tests/catraca.py` +159, `tests/test_catraca.py` +205, 7 arquivos em `tests/mutantes/`, fragmento em `changelog.d/`). Primeiro parecer da branch. H1: `tests/` fica fora da contagem; dentro do teto.

## Ferramenta (citada, sem refazer)
- CI do PR no head e7a71a8e: as 10 partes da suíte (3.12 e 3.14), passos, verificações longas, instalação e teto de pulados verdes. `catraca` vermelha só por `R-CONFORMIDADE: mudança em tests/catraca.py` (pede o rótulo do dono, coberto pela DECISÃO DO DONO de 24/11 17:24); `bateria (pareceres)` vermelha pela falta dos pareceres.
- Mutação: 46 mutantes em `tests/mutantes/v0480-d3-teste-enfraquecido{,-2..-7}.json`, todos mortos, e `forge-mutante --cobertura --base aabc476c` sem linha descoberta, pelo PR do autor; não refeito.
- Teste do item rodado aqui: `python3 -m unittest tests.test_catraca.TestesAfrouxados`: 20 testes, OK.

## Leitura
- Atende a decisão do dono de 24/11 17:24: asserção a menos, pulo, esvaziado e apagado barram sempre; valor trocado na primeira entrega só é listado (saída e resumo, código de saída inalterado); renomeado de mesmas asserções passa.
- O `TestesNoCi` passa a vigiar `regra_testes_afrouxados` contra import e exec; o `forge_check()` de `commit_aprovado` carrega o `bin/forge-check` ao lado da catraca (no CI, o da base), sem código do head.

## Achados
- A1 (bloqueante) tests/catraca.py:772 · a volta compara aprovado..head inteiro: o valor trocado por outro PR da develop, que entra por merge depois da aprovação (R-FLUXO), barra esta branch e pede rótulo (S1). Sugestão: só barrar o teste que também aparece em perdas_dos_testes(b, h) com valor trocado; teste espelho da S1.
- A2 (recomendado) tests/catraca.py:716 · asserção trocada por tautologia (assert dobro(2) == 4 vira assert True) conta como valor trocado e só é listada na primeira entrega (S2), embora seja asserção removida na prática; cartão para contar asserção de constante pura como perda.

## Sondas
- S1 · sonda_d3.py test_s1: branch aprovada no head, develop troca == 4 por == 5 em tests/test_y.py, git merge develop, violacoes_das_regras(develop, HEAD) · espera: [] · obtido: 1 violação "T.test_a trocou ou tirou valor esperado depois da versão aprovada"
- S2 · sonda_d3.py test_s2: assert dobro(2) == 4 vira assert True · espera: perdeu asserção · obtido: nenhuma violação; valores_para_conferir lista tests/test_y.py::T.test_a

## Parecer
Reprovado por A1: no fluxo normal (pareceres aprovados, depois a develop entra na branch na hora do merge), qualquer valor esperado que a develop tenha mudado desde a aprovação vira violação desta regra e exige o rótulo do dono; é um falso positivo com gatilho certo (a `tests/test_catraca.py` muda a cada poucos PRs). Correção pequena em `regra_testes_afrouxados`: cruzar o achado da volta com o da base efetiva, para que só conte o que a própria branch trocou. A2 vira cartão depois do merge.
