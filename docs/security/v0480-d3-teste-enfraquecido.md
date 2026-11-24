---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 8daa161194a94fffbeba29e5a1a087aa0a9343fb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E2.4, PR #867, D3 teste afrouxado), volta por delta

Volta por delta sobre o parecer reprovado em `e7a71a8e` (rodada anterior no git, `25091cfd`). Delta lido com `forge-check parecer delta`: `e7a71a8e..8daa1611`; no domínio, `tests/catraca.py` (`:673-681`, `:690`, `:777-786`) e `tests/test_catraca.py` (`:638-667`, `:1063`); fora do domínio, o fragmento do changelog e os JSON de mutantes. O resto da rodada anterior não mudou e não foi relido.

Gatilhos: controle do Forge que analisa entrada (catraca, R-CONFORMIDADE)

## Achados
- A2 (recomendado) tests/catraca.py:792 · Corrigido em parte: o vácuo só de constantes agora barra como teste apagado, mas o mesmo vácuo com um nome (`assertEqual(int(1 + 2), 3)`, `assert int(2) and 4`) ainda passa calado (S4). Liste em `valores_para_conferir` os pares apagado -> renomeado (`:762`), sem barrar.

## Sondas
- S1 · branch aprovada, develop troca `== 4` por `== 5`, merge da develop na branch · espera: [] · obtido: []
- S2 · branch troca `== 4` por `== 5` depois da aprovação · espera: barra · obtido: `T.test_a trocou ou tirou valor esperado depois da versão aprovada`
- S3 · merge da develop (S1) e, depois, a branch troca `), 3,` por `), 7,` · espera: barra · obtido: barra (o filtro não abre brecha quando o merge e a troca da branch caem no mesmo teste)
- S4 · `test_a` trocado por `test_novo` com `assertEqual(int(1 + 2), 3)` e `assert int(2) and 4` · espera: listado ao revisor · obtido: [] e lista vazia

## Estado dos achados anteriores
Sondas de conferência em `scratchpad/sonda_sec_v0481.py` (herda `TestesAfrouxados`); nenhuma prova bloqueante.

- **A1 (bloqueante): corrigido.** `tests/catraca.py:783-785` barra na volta só o teste que também trocou valor contra a base efetiva, exatamente a correção mínima proposta; o teste `tests/test_catraca.py:638` reproduz S1. S2 e S3 provam que a volta continua barrando a troca da própria branch.
- **A2 (recomendado): parcial.** `_vacua` (`:677`) tira da contagem a asserção sem nenhum `ast.Name`; o caso da sonda anterior (S3 do parecer de `e7a71a8e`) agora barra como `foi apagado ou renomeado` (teste `:655`). A heurística se contorna com qualquer nome (S4); a correção proposta (listar o par renomeado ao revisor) cobre a classe inteira sem heurística. Severidade baixa: exige intenção, o diff mostra, e antes do PR também passava. Esforço: P. Dono: autor da branch.

## Conclusão por escrito: o delta só aperta
`_vacua` só reduz a contagem de asserções e de valores esperados das asserções sem nome, aplicada igual na base e no head: remover ou trocar uma asserção real por `assert True` passa a barrar (`perdeu asserção`), e nenhuma asserção real deixa de contar (exige ao menos um nome; `assertTrue()` sem argumento continua contando, teste `:666`). O filtro `da_branch` reduz violações só no caso em que a troca não é da branch (merge da base); S3 mostra que não reduz quando é. `:1063` só acrescenta asserção. Nenhuma outra regra muda.

**Testes:** `python3 -m unittest tests.test_catraca.TestesAfrouxados` no head 8daa1611: 23 testes, OK. Suíte inteira: CI do PR #867 no head 8daa1611 (run 45496406956) com as 10 partes da suíte (3.12 e 3.14) verdes; `catraca` vermelho por `mudança em tests/catraca.py` (pede o rótulo `afrouxa-regra` do dono, esperado para mudança na catraca) e `bateria (pareceres)` vermelho, fora do domínio deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais em repositório temporário (unittest da biblioteca padrão). Varredura de segredos não aplicável (delta só de código de teste, JSON de mutantes e changelog).
