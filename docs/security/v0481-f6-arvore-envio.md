---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: 023b0d68c5f67c64236363d17e5d17f2fdaea770
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (PR #932, corte do envio do F6, volta 2, E32.39)

Volta por delta: `forge-check parecer delta` de `dcd4003c..023b0d68`; no domínio, só `scripts/arvore-testada.py` (`prova_do_pr` passa o `numero`; `bateria_do_run_do_pr:190-192` descarta o run cujo `pull_requests` traga outro número, outra base ou tipo que não seja lista). Fora do domínio: specs de mutante -5 e -7 e `tests/test_arvore_testada.py`. Rodada anterior (79bdb8de, reprovado) fica no git.

Gatilhos: pipeline de CI (portão do push na develop), token do workflow, controle que afrouxa regra (R-FLUXO).

## Achados
- A1 (bloqueante) scripts/arvore-testada.py:190 · Parcial: o run de outro PR do mesmo ramo para outra base é recusado só enquanto esse PR está aberto. Mesclado ou fechado, a API esvazia o pull_requests, o run passa e, sendo o mais novo, prova o merge na develop com o run do PR da develop vermelho (S2). Falta a parte (2) da correção.

## Sondas
- S1 · python3 sonda_s1.py <cópia> (run 565 com pull_requests=[{number 999, base melhoria/y}] e bateria success; run 555 do PR #77 com bateria failure) · espera: (False, ...) · obtido: (False, "nenhum PR mesclado em aaaaaaa tem head de mesma árvore, ...")
- S2 · python3 sonda_s2.py <cópia> (o mesmo, com o PR empilhado já mesclado: run 565 com pull_requests=[] e bateria success; run 555 com bateria failure) · espera: (False, ...) · obtido: (True, "árvore 1111111 igual à do head 3333333 do PR #77, run 565, job bateria")

## Detalhe dos achados
**A1 (estado: parcialmente corrigido; continua bloqueante).** A parte (1) da correção mínima da rodada anterior entrou e fecha o caso do PR empilhado aberto (S1 agora dá False). A parte (2) não entrou: a lista vazia segue valendo para qualquer run do mesmo head e ramo (`:190-192`), e ela é exatamente o estado do run de um PR já mesclado ou fechado, de qualquer base. O próprio código registra isso na docstring (`:178`: "vazia só depois do merge").

Caminho: quem tem escrita abre `melhoria/x -> melhoria/y` no mesmo head do PR da develop; o run desse PR fica verde sobre `merge(head, melhoria/y)`; fecha ou mescla esse PR (o `pull_requests` do run some); o PR da develop é mesclado e o `arvore-envio` pega o run mais novo, verde, de outra base, e corta a suíte do push sem nunca ter testado a árvore mesclada na develop. A ordem é a natural de um PR empilhado, não exige forja.

Correção mínima (P, dono `devops-engineer`; teste `qa-engineer`): listar os PRs do ramo, `repos/<repo>/pulls?head=<dono>:<ramo>&state=all&per_page=100`, e não provar se algum, aberto ou fechado, tiver `base.ref` diferente de `develop` (ou tiver número diferente do `numero` com o mesmo `head.sha`); falha fechada se a listagem falhar ou vier sem `base.ref`. Caso de abuso para o teste: o da S2 (run mais novo verde com `pull_requests=[]` de PR do mesmo ramo para `melhoria/y`, já fechado; run do PR da develop vermelho), espera `(False, ...)`.

Verificado sem achado no delta: tipo errado no `pull_requests` (não lista) recusa; item sem `number` ou `base.ref` recusa (`campo` devolve None); o `numero` vem do PR lido pela API, não do run.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sondas S1 e S2 fora do repositório (fixture de `tests/test_arvore_testada.py`, sem rede). Teste afetado rodado: `tests.test_arvore_testada` (32 testes, OK). CI do head `023b0d68`: suíte partes 1 a 5, passos, verificações longas, instalação, `bateria (python 3.14)` e `árvore já provada na develop` verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhas pelo que falta da integração (pareceres). `zizmor` e `actionlint` fora do PATH: lacuna.
