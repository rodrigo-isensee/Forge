---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s3-registro
commit: b3cd1ee41cde185fe7445bb3596c051e2e887f04
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s3-registro (v0478 E39.8, revalidação)

Volta por delta. A rodada anterior (head d03cc57f, A1 recomendado) fica no git em fbac6fd3. Delta lido: `forge-check parecer delta` de d03cc57f a b3cd1ee4; no domínio só `hooks/agentes.py` (`caiu_em_finito` e o laço de `interrompidos_vigentes`) e `tests/test_agentes_interrompidos.py` (3 testes novos). Fora do domínio: fragmento do changelog e os três `tests/mutantes/*.json`. O merge da develop (base 004ce86 para 8a50379) não traz outro arquivo do domínio ao delta.

## Gatilhos
Gatilhos: hook de controle (R-TETO, R-BRIEF), estado de controle em disco.

## Achados

## Sondas

## Detalhe dos achados
A1 (recomendado, rodada anterior): corrigido. `caiu_em` numérico e não finito (inteiro que não cabe em float, inf, nan) lança `EstadoIlegivel` em hooks/agentes.py:647-648; `atualizar_estado` o chama em hooks/agentes.py:1314, dentro do `try` de hooks/agentes.py:1290-1294, que recusa o disparo (`recusar_ilegivel`) sem regravar o arquivo. Com recusa de R-BRIEF, o erro é engolido e o R-BRIEF bloqueia do mesmo jeito (hooks/agentes.py:1296-1299). O `OverflowError` não escapa mais: `caiu_em_finito` o captura (hooks/agentes.py:630-635) e a subtração só roda sobre itens finitos. Sonda refeita: `interrompidos_vigentes({'interrompidos':[{'caiu_em':10**400}]}, time.time(), 3600)` dá `EstadoIlegivel` (antes, `OverflowError`); o mesmo com `-(10**400)`, `inf` e `nan`. Prova de ponta: `test_disparo_com_caiu_em_enorme_e_recusado_sem_regravar_o_estado` (saída não zero e arquivo intacto).

Texto não numérico continuar sumindo basta: `interrompidos` não é lido por nenhuma recusa (só registro e retomada), então o item descartado tira apenas um registro, e quem escreve no `agentes.json` já poderia apagá-lo; não há ganho de ataque. Sonda: `'abc'` e `None` dão `([], [])`. `True` conta como inteiro 1 e vence logo; `10**300` é finito e fica vigente, limitado por `INTERROMPIDOS_MAX`; nenhum dos dois afrouxa trava.

A mesma classe de `OverflowError` segue em `lapides_vigentes` e `autores_vigentes` (anterior à branch, fora do delta); não é afrouxamento desta entrega e fica como sugestão ao autor, não achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado só o teste do módulo tocado, `tests/test_agentes_interrompidos.py` (26 testes, OK); a suíte inteira fica para o CI do PR. Ferramentas ausentes no PATH: varredor de segredos, SAST e auditor de dependências (lacuna; o delta não toca dependência nem segredo).
