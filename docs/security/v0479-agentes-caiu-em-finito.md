---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-agentes-caiu-em-finito
commit: c838a467219922cc11c89680dc0aed730bebc0ef
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-agentes-caiu-em-finito

Etapa E53.7 do pedido v0478: revalidação no head c838a467, depois da volta do QA (E53.5). A rodada anterior (E53.3, head 81408618, aprovado) fica no git, commit 050f5ce6.

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/agentes.py`, R-TETO e reserva de disparo), estado de controle lido de arquivo (`agentes.json`).

## Resumo
- **Delta lido** (`forge-check parecer delta`, 81408618..c838a467): no domínio, só `tests/test_agentes_interrompidos.py:261-264`. O teste `test_disparo_com_lapide_ou_autor_enorme_e_recusado_sem_regravar_o_estado` passa a converter um `OverflowError` que escape de `principal` em `self.fail`, em vez de erro de teste: na base o teste falha por asserção, como o QA pediu. Endurece a prova sem mudar o comportamento verificado (código diferente de 0 e arquivo não regravado).
- **Já lido e sem mudança:** `hooks/agentes.py` (`lapides_vigentes`, `autores_vigentes`, `caiu_em_finito`) não é tocado no intervalo; as conclusões da rodada anterior valem para este head. Os outros arquivos do intervalo são os três pareceres (documentação, fora do domínio).
- **Teste rodado no head:** `python3 -m unittest tests.test_agentes_interrompidos`: 29 testes, OK.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief, "sem suíte local"); o CI do PR, obrigatório para o merge, fecha a bateria. Ferramentas: varredor de segredos e SAST fora do PATH (lacuna; o delta é um teste, sem segredo, dependência nem workflow).
