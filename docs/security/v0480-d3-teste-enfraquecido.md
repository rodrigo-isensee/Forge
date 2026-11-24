---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d3-teste-enfraquecido
commit: e7a71a8e2f87ef83fc7cb3708396ac05e87ba65d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.24, PR #867, D3 teste afrouxado)

Primeira rodada; sem parecer anterior nesta branch. Lido: `aabc476c..e7a71a8e` inteiro (`tests/catraca.py:662-818`, `:1253`, `:2156`; `tests/test_catraca.py`, classe `TestesAfrouxados`; mutantes e fragmento do changelog).

Gatilhos: controle do Forge que analisa entrada (catraca, R-CONFORMIDADE), leitura de parecer da própria branch como fonte de confiança

## Achados
- A1 (bloqueante) tests/catraca.py:772 · Na volta, a comparação `aprovado..head` inclui o que a develop trouxe por merge: valor esperado trocado num PR já revisado na develop barra a branch aprovada antes, e só o rótulo do dono libera. Falso positivo que treina o rótulo; compare só o que a branch mudou.
- A2 (recomendado) tests/catraca.py:751 · Teste apagado e trocado por um novo com a mesma contagem e as mesmas constantes, mas vácuo (`assertEqual(1 + 2, 3)`, `assert (2 and 4)`), passa calado: nem barra nem entra na lista ao revisor. Liste os pares renomeados em `valores_para_conferir` (`:779`).

## Sondas
- S1 · scratchpad/sonda_sec_merge.py: branch aprovada em X, develop troca `== 4` por `== 5` em tests/test_y.py, `git merge develop` na branch, catraca contra develop · espera: [] · obtido: R-CONFORMIDADE ... T.test_a trocou ou tirou valor esperado depois da versão aprovada

## Detalhe dos achados
**Risco apontado pelo autor (parecer forjado na própria branch).** Reproduzido e sem regressão. `commit_aprovado` (`:797`) lê os pareceres de `docs/` que a própria branch toca; um parecer `aprovado` forjado com `commit:` = head depois da troca faz a comparação da volta não ver nada (sonda: `aprovado` = o forjado, violações `[]`). Mas o estado resultante é o mesmo da primeira entrega sem parecer algum (sonda: troca sem parecer também dá `[]`), que é o comportamento decidido pelo dono; e a lista ao revisor (`valores_para_conferir`, `:776`) compara sempre com a base efetiva, não com o parecer, então o caso forjado continua listado (`['tests/test_y.py::T.test_a']`) para o revisor real conferir no head final. Forjar exige escrever em `docs/{reviews,qa,security,...}/`, que o hook `conformidade` reserva por papel, e o parecer forjado ainda passa pelo `forge-check pareceres` do CI e pelo revisor do head. Sem caminho que dê menos proteção do que antes do PR: não é achado.

**Conclusão por escrito: o item só aperta.** A única linha removida do diff (`tests/test_catraca.py`, lista `pendentes`) ganha `regra_testes_afrouxados`; nenhuma regra existente da catraca muda, `regra_testes_afrouxados` só soma violações em `_violacoes_das_regras` (`:1253`) e `listar_valores_para_conferir` (`:2156`) só imprime, calada com git falho (a falha já vira violação, falha fechada). Antes do PR, valor trocado, asserção movida entre testes e teste apagado com compensação passavam nas somas; agora as perdas duras barram sempre e o valor trocado barra na volta. O A1 não afrouxa: é excesso de barra (disponibilidade), mas bloqueia porque é defeito provado num controle e, recorrente a cada merge da develop (o fluxo do QA prevê o merge da develop na branch), empurra o dono a aplicar `afrouxa-regra` por rotina, o que esvazia o rótulo que libera todas as outras regras.

**A1.** Evidência: `tests/catraca.py:770-772`, `perdas_dos_testes(raiz, aprovado, h)` sem descontar a base; sonda S1. Caminho: não é ataque; qualquer PR que troque valor esperado na develop derruba as branches aprovadas que tocam o mesmo módulo de teste e fazem merge da develop. Severidade: média (controle). Correção mínima: na volta, barrar só se a troca também aparece contra a base efetiva, isto é, `VALOR_TROCADO in perdas(aprovado, h)` e `VALOR_TROCADO in perdas(b, h)` para o mesmo teste (na sonda, `b` = develop já tem `== 5`, e a perda some); teste com o cenário de S1. Esforço: P. Dono: autor da branch (E174.11).

**A2.** Evidência: `tests/catraca.py:726` e `:751`; sonda local (scratchpad `sonda_d3.py`, S3): `test_a` trocado por `test_novo` com `self.assertEqual(1 + 2, 3)` e `assert (2 and 4)` dá `[]` e lista vazia. Caminho: autor que quer o CI verde apaga o teste que falha e põe um vácuo com as mesmas constantes. Severidade: baixa (exige intenção; o diff mostra; antes do PR também passava). Correção mínima: `valores_para_conferir` lista também os pares apagado → renomeado (`confira no parecer: renomeado`), sem barrar. Esforço: P. Dono: autor da branch.

**Testes:** `python3 -m unittest tests.test_catraca.TestesAfrouxados` no head e7a71a8e: 20 testes, OK (25,2 s). Suíte inteira: CI do PR #867 no head e7a71a8e com as 10 partes da suíte (3.12 e 3.14) verdes; `catraca` e `bateria (pareceres)` vermelhos (log não legível daqui: cache do `gh` em sistema de arquivos só de leitura), fora do domínio deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais em repositório temporário (unittest da biblioteca padrão). Varredura de segredos não aplicável (diff só de código de teste e JSON de mutantes).
