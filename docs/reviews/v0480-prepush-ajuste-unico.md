---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-prepush-ajuste-unico
commit: 61997e21f1b1b2164fa943cef707b7c634148ef4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E4.2 e E4.7, code review do PR #871, ajuste único do pre-push)

## Revalidação (E4.7, delta 082f1f9e..61997e21)
- Delta lido: `forge-check parecer delta` deu `revalida: sim` porque `bin/forge-testes` mudou depois do parecer (merges 6a1ffa85 e 61997e21 da `develop`, base bbbe2d8, com o D7 #868, o D4 #869 e o #866).
- Conflito em `bin/forge-testes` (tupla `FORGE_CHECK`): a resolução une os dois lados; entra o `test_criterios` da `develop` (o arquivo existe) e segue fora o `test_prepush_lote_pp1`, cujo arquivo saiu nesta branch. Nenhuma outra linha mudou no arquivo.
- Fora do que veio da `develop`, nada mudou: as linhas `+`/`-` de `git diff a27eab7e 082f1f9e` e de `git diff bbbe2d88 61997e21` são idênticas (diff vazio). `git grep test_prepush_lote_pp1` em `bin/` e `tests/*.py` acha só a nota histórica do `tests/test_prepush_unico.py:8`.
- Prova no head 61997e21: `python3 -m unittest tests.test_testes_tocados` (confere o mapa do `bin/forge-testes`): `Ran 196 tests`, `OK (skipped=1)`. Suíte inteira só no CI do PR.
- Veredito mantido; os achados A1 e A2 seguem recomendados. O texto abaixo é o da primeira rodada (head 13063422).

Base a27eab7e, head 13063422 (PR #871, rascunho). Primeira rodada: não havia parecer anterior na branch. O `.githooks/pre-push` não muda aqui; o PR entrega o patch, o roteiro do dono e os testes.

## O que foi conferido
- **O patch é a soma declarada.** As linhas `+`/`-` de `patches/prepush-unico.patch` (151) contêm todas as 77 do `patches/d2-portao-entrega.patch` da base; as 74 restantes são exatamente as do bloco `diff` de `docs/propostas/prepush-lote-pp1.md` (base) menos a PREPUSH-LEVE-COBERTURA-CATRACA e a PREPUSH-FORGE-AVISO-LISTA-VAZIA, com uma única diferença: a linha `local ...` sem `faltas`, que só a cobertura usava. `controle` segue usado pelo índice e pelos pulos (`patches/prepush-unico.patch:122-142`). Nada de lógica nova além das duas origens já revisadas.
- **Aplica na base:** `git apply --check patches/prepush-unico.patch` no head, rc 0.
- **Afrouxamento autorizado e destacado:** o título do PR traz `[afrouxa-regra: sai o test_prepush_lote_pp1]` e a decisão do dono de 24/11 17:08; a proposta antiga fecha como substituída com o motivo na seção 0. Os mutantes do envio local seguem, portados para `tests/mutantes/v0480-prepush-ajuste-unico*.json`; só saem os da cobertura (fechada sem mudança, decisão 7) e da lista vazia (fora do patch aprovado, segue como cartão).
- **Referências ao módulo que saiu:** `git grep test_prepush_lote_pp1` fora de pareceres e changelog acha só a proposta substituída (A1). `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/test_reval_delta.py` e `tests/pesos-d4.json` foram ajustados juntos; `patches/*` e o `tests/test_prepush_unico.py` caem em "sem mapa", que leva à suíte completa (conservador).
- **`tests/test_pre_push_patch.py`:** a troca de `aplicado` para a marca da cobertura está correta: com o ajuste único no hook, a marca TRAVA-FD já existe e o teste antigo passaria a "conferir só o remendado" sem o PP1; agora ele desfaz o ajuste único na cópia e prova o PP1 sobre o hook de antes.
- **Roteiro do dono** (`patches/prepush-unico-roteiro.md`): conferi as opções de `bin/forge-copia` (`--branch`, `--base`, `--origem`) e do `bin/forge-changelog novo`; a ordem (cópia separada, `core.hooksPath`, apply, teste, fragmento, commit, envio) está certa, o PR do dono traz a linha `teto: excedido, 151 linhas` com motivo (H1), e há critério de reversão com medida (falso positivo ou +3 s no envio leve) e o `git apply -R`. A falha `test_texto_da_trava_sai_limitado_e_sem_controle` (649 > 600) está declarada como pré-existente na `develop` pura dentro do sandbox, com o modo de conferir na máquina do dono.
- **Tamanho (H1):** código fora de teste e documentação, 9 linhas em `bin/forge-testes`; o patch é o hook do dono, cujo teto é tratado no PR dele.
- **Regras:** `R-MAIN`, `R-VERIFY` (nada de `--force`/`--no-verify` no roteiro), `R-NEUTRO` (nada de projeto), `R-CUSTO` (nada pago), `R-CONFORMIDADE` (o hook travado não é tocado; a catraca pede o rótulo do dono no PR dele).

## Provas
- Teste novo e os dois que usam o patch, no head 13063422: `python3 -m unittest tests.test_prepush_unico tests.test_pre_push_d2 tests.test_pre_push_patch`: `Ran 54 tests in 34.133s`, `OK`.
- Suíte inteira só no CI (`R-REVIEW`): as cinco partes da suíte, os tetos de pulados e "árvore já provada na develop" verdes no head 13063422 (run 45487636026). Mutação do diff: rodada pelo autor (V2), não refeita aqui.

## Achados
- A1 (recomendado) docs/propostas/prepush-lote-pp1.md:39 · A seção de teste da proposta substituída ainda manda rodar `tests.test_prepush_lote_pp1`, que saiu (também :375). O aviso do topo cobre, mas quem pular direto à seção roda um módulo inexistente; troque por uma nota que aponte o `test_prepush_unico`.
- A2 (recomendado) tests/test_pre_push_patch.py:35 · `sem_o_ajuste_unico` ignora em silêncio o `apply -R --check` que falha; se o hook derivar, o erro aparece só como falha do `git apply` do PP1. E o PP1 traz a cobertura, fechada sem mudança: abra cartão para aposentar esse teste depois que o dono aplicar.

## Parecer
**Aprovado.** O patch único é, linha a linha, o envio local aprovado mais o D2, aplica limpo na `develop`, e os testes que o provam passam no head; o teste da proposta antiga sai com autorização do dono, destaque no título e os mutantes do que entra portados. Os dois achados são recomendados (cartão depois do merge).
