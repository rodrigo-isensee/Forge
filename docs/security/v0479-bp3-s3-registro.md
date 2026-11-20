---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s3-registro
commit: d03cc57f22b83532dccb1a96acb43cb76ed6578a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s3-registro (v0478 E39.8)

Escopo: `git show d03cc57f` sobre a base `004ce869` (hooks/agentes.py, teste e mutantes novos, fragmento do changelog). O registro `agentes.json` é controle do R-TETO; a pergunta do portão é se alguma trava do R-TETO ou do R-BRIEF afrouxa.

## Gatilhos
Gatilhos: hook de controle (R-TETO, R-BRIEF), estado de controle em disco, log de controle.

## Achados
- A1 (recomendado) hooks/agentes.py:634 · interrompidos_vigentes subtrai `caiu_em` fora de try: inteiro enorme no agentes.json dá OverflowError, que sobe ao executar (critico=None) e sai 0, disparo sem reserva. Mesma classe já existe em lapides_vigentes:563 e autores_vigentes:654; não é afrouxamento novo.

## Sondas

## Detalhe dos achados
Conclusão do portão: nenhuma trava afrouxa.
- R-BRIEF: `conferir_brief` segue antes do estado; com recusa, o erro do estado é engolido em hooks/agentes.py:1282 e a recusa sai em seguida. `briefs_da_reserva` (hooks/agentes.py:579) só lê `lidos`, que contém só bytes já hasheados em hooks/agentes.py:1012-1013 (com o limite de briefs), então não lança na reserva (hooks/agentes.py:1217).
- R-TETO: `interrompidos` não é lido por nenhuma recusa (grep: só as funções novas em hooks/agentes.py:574-645 e a montagem em atualizar_estado); a contagem do teto continua sendo `vigentes` sobre `agentes`, que só trocou o filtro de prazo por `dentro_do_prazo` com a mesma expressão (hooks/agentes.py:360-374) e ainda dentro do try por registro. `interrompidos` que não é lista vira estado ilegível (hooks/agentes.py:430-431), que recusa: aperta, não afrouxa. `fechar_por_relancamento` roda depois da reserva e só sobre itens já filtrados como dict, sem caminho de exceção.
- Dado gravado: só `docs/briefs/<nome seguro>.md` (regex em hooks/agentes.py:575, sem `..` nem controle) e o sha256; o item de `interrompidos` copia só campos de forma conhecida, sem PID. Log: `registrar_vencidos` grava id só na forma de agente, senão `-`, e motivo fixo; sem injeção de linha. Teto de 64 itens limita o crescimento; o estado acima de 1 MiB falha fechado.

A1: evidência hooks/agentes.py:634 (sonda local: `interrompidos_vigentes({'interrompidos':[{'caiu_em':10**400}]}, time.time(), 3600)` lança OverflowError; o mesmo com `lapides_vigentes` e `desde` 10**400, na base). Caminho de ataque: quem já escreve no `agentes.json` (pasta do estado) planta o número e cada disparo sai sem reserva; esse agente já poderia esvaziar `agentes`, por isso não há ganho novo e o achado é recomendado, não bloqueante. Severidade baixa. Correção mínima: em `interrompidos_vigentes`, aceitar só `caiu_em` finito (por exemplo, `math.isfinite` sobre `float(...)` em try, descartando o item que falha), e o mesmo em `lapides_vigentes` e `autores_vigentes` se o autor quiser fechar a classe; teste com `10**400`. Esforço P. Dono: autor da branch (forge:software-engineer).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lidos: o diff inteiro do head, `principal`, `atualizar_estado`, `lancar`, `conferir_brief`/`selo_ausente`, `executar` e `falhar_fechado` de hooks/_comum.py. Rodado só o teste novo `tests/test_agentes_interrompidos.py` (23 testes, OK); a suíte inteira fica para o CI do PR (brief sem suíte local). Ferramentas ausentes no PATH: varredor de segredos, SAST e auditor de dependências (lacuna; o diff não toca dependência nem segredo).
