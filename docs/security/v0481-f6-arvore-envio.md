---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: d0f41115599f182b8e57b6b7dcd78f529bdad70f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (PR #932, corte do envio do F6, volta 3, E32.43)

Volta por delta: `forge-check parecer delta` de `023b0d68..d0f41115`; no domínio, só `scripts/arvore-testada.py` (`prs_do_ramo_so_para_develop` em `:177-189`, chamada em `prova_do_pr:169`, e `LIMITE_DE_PAGINAS`). Fora do domínio: spec de mutante -8 e `tests/test_arvore_testada.py`. Rodada anterior (023b0d68, reprovado) fica no git.

Gatilhos: pipeline de CI (portão do push na develop), token do workflow, controle que afrouxa regra (R-FLUXO).

## Sondas
- S2 · python3 sonda_s2_lista.py <cópia> (do_ramo com o #77 para develop e o #999 fechado para melhoria/y; run 565 vazio e verde; run 555 do #77 vermelho) · espera: (False, ...) · obtido: (False, "nenhum PR mesclado em aaaaaaa ...")

## Detalhe
**A1 da volta 2 (estado: corrigido).** A correção mínima pedida entrou: `prs_do_ramo_so_para_develop` lista `pulls?head=<dono>:<ramo>&state=all` em até 10 páginas e não prova se algum PR, aberto ou fechado, tiver `base.ref` diferente de `develop`. A S2 anterior dava True porque o fixture dela não montava a lista do ramo (o padrão é só o PR da develop, o estado legítimo); refeita com o PR empilhado na lista, dá False, também com ele na primeira posição.

Verificado sem achado no delta:
- Saída da guarda `type(p) is not dict`: redundante; `campo` devolve None para item que não é dict, e None diferente de "develop" recusa. Sondas com item `None`, item lista, `base.ref` inteiro e `"develop "` dão False.
- Exceção na listagem (TimeoutError na sonda) propaga até `main:252`, que a trata como falta de prova (rc 1), sem detalhe que traga o token.
- Ramo apagado depois do merge: a API real segue listando o PR fechado pelo filtro `head` (conferido no PR #851, ramo já apagado: um item, base develop, state closed).
- PR de fork com o mesmo nome de ramo fica fora do filtro `dono:ramo`, mas o run dele já é recusado por `head_repository.full_name`.
- Mais de 10 páginas cheias não prova. Página vazia na primeira chamada prova por vácuo, mas a lista real sempre traz o próprio PR mesclado (head do mesmo repositório, conferido em `prova_do_pr`): sem caminho de ataque, sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sonda fora do repositório (fixture de `tests/test_arvore_testada.py`, sem rede). Teste afetado rodado: `tests.test_arvore_testada` (33 testes, OK). CI do head `d0f41115`: suíte partes 1 a 5, passos, verificações longas, instalação, `bateria (python 3.14)`, teto de pulados e `árvore já provada na develop` verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhas, à espera dos pareceres desta volta. `zizmor` e `actionlint` fora do PATH: lacuna.
