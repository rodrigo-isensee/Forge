---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-forge-check
commit: 99f474bbcb8619c69a07887081bb703fdd389c34
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 META85 (bin/forge-check), E34.4 e revalidação E34.8

A rodada 1 (E34.4, head 6853e0ee) fica no git. Esta é a revalidação no head 99f474bb.

## Revalidação (E34.8)
Delta lido: `forge-check parecer delta docs/security/v0479-meta85-forge-check.md`, intervalo `6853e0ee..99f474bb`. No domínio, só
`bin/forge-check` (`cmd_pr` :2014-2028, `parecer_que_aprova` :2033, `livres_do_pedido` :2038, `veredito_do_parecer` :2043-2058,
`parecer_delta` :3575, `revalida_do_parecer` :3592-3601). Fora do domínio: os testes `test_meta85_*` e as specs de mutante 3, 5 e 6.
Já lido na rodada 1 e não relido: o resto do intervalo `eca1d21b..6853e0ee`.

Estado dos achados anteriores: A1 resolvido no 2927e738 (o `revalida:` sai do mesmo `veredito_do_parecer` do `pr`, com o aceite do
usuário e o AQ-5); o resíduo de base segue como recomendado (abaixo).

## Achados
- A1 (recomendado) bin/forge-check:3575 · Resolvido no 2927e738 (riscos-aceitos sem aceite e AQ-5 dão `revalida: sim`). Resíduo não sondado: o `revalida` usa `ref_da_base(raiz, base)` e o `pr` recebe base None no caminho de :1570; só informativo, fail-closed.

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-check`: `cmd_pr` decide o portão de merge); rótulo `afrouxa-regra` pedido.

## Confirmação para o rótulo `afrouxa-regra` (head 99f474bb)
A mudança **só aperta**: o `forge-check pr` não aceita nenhum parecer que antes recusava. Conferido ramo a ramo contra o `cmd_pr` do
6853e0ee:
1. **`riscos-aceitos` sem aceite** (:2046-2048): mesma condição (`aceite_do_usuario(raiz, pedido, commit, ref)`, mesma `ref`), mesma
   mensagem, mesmo campo `parecer:`. Recusa igual.
2. **Valor fora de `aprovado`/`riscos-aceitos`** (:2050): `parecer_que_aprova` é o mesmo teste de pertinência. Recusa igual.
3. **`commit:` ausente ou fora do formato** (:2052): antes, `campos.get("commit") and COMMIT.match(...)` falso não gerava linha; agora
   `COMMIT.match(campos.get("commit") or "")` (o regex `^[0-9a-f]{7,40}$`, :186, nunca casa a cadeia vazia) devolve None, sem linha.
   Equivalente; a forma do `commit:` segue barrada pela validação do frontmatter (`viol`), que não mudou.
4. **Ramo `paralelo` (AQ-5)** (:2054-2055): saiu do corpo do `cmd_pr`, não do portão. `veredito_do_parecer` devolve
   `("commit", paralelo)` antes do `commit_vale`, como antes; no `cmd_pr` cai no `elif motivo` (:2019); o prefixo `desatualizado` não
   casa com a mensagem do AQ-5 (que começa pelo sha), então não há reescrita E16 nem sufixo do delta, e sai `commit: {paralelo} ({rid})`,
   texto idêntico ao antigo. O `continue` antigo era o último comando do corpo do laço, sem outro efeito. Recusa igual.
5. **`commit_vale`** (:2056): mesmos argumentos (`ref or "HEAD"`, `base`, os livres agora em `livres_do_pedido` com a mesma tupla,
   `FRAGMENTOS`, `dominio=tipo`, `dominio_mais`, `dispensados`). `dispensados` sai da mesma `testes_do_qa` sob a mesma condição útil
   (review, parecer que aprova, `commit:` válido); o cálculo a mais no `riscos-aceitos` sem aceite não é usado (retorno antecipado em 1).
   A pós-formatação E16 e o sufixo do delta ficaram iguais.
6. **`revalida:`** segue só informativo (nenhum portão o lê) e agora vem da mesma função do `pr`; diverge, no máximo, pela base (resíduo
   do A1), o que só pode pedir uma rodada a mais.
Nenhum caminho novo devolve None onde antes havia linha de recusa.

## Detalhe dos achados
**A1.** Correção conferida no código (:3596-3601) e pelos testes `test_riscos_aceitos_sem_aceite_do_usuario_revalida_como_o_pr` e
`test_riscos_aceitos_com_aceite_do_usuario_segue_valendo` (tests/test_meta85_revalida.py:55, :60), que reproduzem a sonda S1 da
rodada 1. Resíduo: a base do `revalida` (`ref_da_base`) e a do `pr` (None no caminho de :1570) podem diferir; sem caminho de ataque
(a linha não é portão); severidade baixa. Correção mínima, se quiserem: passar ao `revalida` a mesma base que o `pr` usaria. Dono:
autor do item (E34.1).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados no head 99f474bb: `python3 -m unittest tests.test_meta85_revalida tests.test_meta85_item_arquivos
tests.test_meta85_entrega` (25 testes, OK); a suíte inteira fica com o CI do PR (sem suíte local, pelo brief). Sem segredo no delta
(revisão manual; só código Python).
