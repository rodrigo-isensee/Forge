---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-prepush-ajuste-unico
commit: 13063422d1fcf3ecb8a657ee83f573af5c139085
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E4.4), PR #871, ajuste único do pre-push

Escopo: o diff `a27eab7e..13063422` (20 arquivos). O `.githooks/pre-push` em vigor, `hooks/` e `.github/` não mudam neste PR (`git diff --quiet` vazio nos três): o hook só muda quando o dono aplicar `patches/prepush-unico.patch` pelo roteiro.

## Gatilhos
Gatilhos: controle de envio (pre-push, por patch para o dono), teste que sai (catraca R-CONFORMIDADE), afrouxa-regra autorizado.

## O que aperta, o que é neutro e o que afrouxa
**Aperta (quando o dono aplicar o patch; nada muda antes):**
- PRE-PUSH-TEXTO-TRAVA-FD (`patches/prepush-unico.patch:9`): o texto da trava sai do fd 9 já conferido, não do caminho (fecha a troca por link depois da conferência). Prova: `tests/test_prepush_unico.py:119` (TextoDaTravaPorFd).
- FILA-INTERVALO-ZERO (`patches/prepush-unico.patch:190`): 0 recusado e leitura em base 10. Prova: `tests/test_prepush_unico.py:162`.
- PREPUSH-INDICE-E-PULOS (`patches/prepush-unico.patch:24`): índice das fixtures e skip novo em tests/ barram no envio leve. Prova: `tests/test_prepush_unico.py:218`.
- PORTAO-D2 (`patches/prepush-unico.patch:51`, `:171`): índice do Forge, teto H1 e texto do PR aberto. Prova: `tests/test_pre_push_d2.py`. O `d2_so_avisa` (`:92`) só alivia o envio só de parecer (docs/{reviews,qa,security,devops}) e falha fechado em ref nova ou sha remoto ausente (delta vazio barra).

**Neutro:**
- Equivalência linha a linha, conferida por mim: toda linha `+/-` do `patches/d2-portao-entrega.patch` (aprovado em `docs/security/v0480-d2-portao-entrega.md`, 5cac2919) está no patch único; toda linha do bloco `diff` da proposta PP1 (aprovada em `docs/security/v0479-prepush-lote-pp1.md`, ce1dc90c) também, menos as das partes que saem (abaixo). A única linha nova é a fusão do `local` de `checagens_baratas` (`controle` somado). Nenhuma checagem do D2 nem das três partes do envio local ficou mais branda.
- Mutantes do D2 só reapontados para o patch novo; M12 e M13 ganham contexto para casar uma só ocorrência (o patch único tem dois `if [ "$rc" -eq 1 ]`), o que deixa o mutante mais preciso. M1 a M8 do envio local seguem em `tests/mutantes/v0480-prepush-ajuste-unico*.json`.
- `tests/test_pre_push_patch.py:31` e `:35`: o PP1 passa a ser provado sobre o hook sem o ajuste único (desfeito na cópia); não toca o hook em vigor.
- `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/test_reval_delta.py`, `tests/pesos-d4.json`: só o nome do módulo de teste trocado no mapa.
- `patches/prepush-unico-roteiro.md`: sem `--no-verify`, `--force` nem `--admin`; envio para branch `melhoria/*`, nunca para develop, homolog ou main; critério de reversão escrito.

**Afrouxa (autorizado: DECISÃO DO DONO 2026-11-24 17:08, pedido v0478):**
- Sai `tests/test_prepush_lote_pp1.py` com as classes CoberturaDaCatraca (8 testes) e ListaVazia (6), e saem os mutantes `tests/mutantes/v0479-prepush-lote-pp1{,-2,-3}.json` das duas partes (AVISO-LISTA-VAZIA M5 a M8, COBERTURA-CATRACA M9 a M20). A catraca do head mediu: testes 6707 para 6694 (-13 = -14 + 1 novo) e asserções 16850 para 16817; bate com essas duas classes, nenhum outro teste some.
- Efeito real: nenhum desses dois consertos estava no hook em vigor, então nenhum envio que hoje é barrado passa a passar. O que se perde é a prova pronta de duas propostas não aplicadas: a COBERTURA-CATRACA fechou sem mudança (decisão 7 de 24/11; o CI barra a falta de mutante) e a AVISO-LISTA-VAZIA (só aviso, nunca barrava) fica sem patch testado e volta a cartão do dono (`docs/propostas/prepush-lote-pp1.md:5`).
- O PR traz `[afrouxa-regra: ...]` no título; a catraca do head está vermelha esperando o rótulo do dono depois do último envio, como manda a regra.

## Detalhe dos achados
Sem achado. Ferramentas e verificação:
- Rodei `python3 -m unittest tests.test_prepush_unico tests.test_pre_push_d2 tests.test_pre_push_patch` no head: 54 testes, OK. `git apply --check patches/prepush-unico.patch` aplica no hook da base.
- CI do head 13063422: as 10 partes da suíte (3.12 e 3.14) verdes; vermelhos só a catraca (testes que saem, pede o rótulo) e a bateria de pareceres (pareceres pendentes), os dois esperados.

## Riscos aceitos e ferramentas
Risco aceito pelo dono: a saída do teste e dos mutantes das duas partes fora do ajuste (decisão de 2026-11-24 17:08). Faltaram no PATH: gitleaks, shellcheck e zizmor (não instalo; o CI roda o shellcheck). O diff não tem segredo nem workflow.
