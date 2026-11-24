---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 8b3124465d4c1a3c0b31e100731a5b9935d8a223
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (pedido que se arquiva sozinho, #874, E9.12, volta por delta)

Gatilhos: bin/forge-check (controle do Forge, R-CONFORMIDADE), escrita automática em docs/pedidos/ pelo `brief gerar`.

Delta lido (`forge-check parecer delta`, ec38cbc4..8b312446): no domínio só bin/forge-check (comentário de `ETAPA_ARQUIVADA` em 8058, `ENTREGUE_DA_ETAPA` em 8061, `etapa_entregue_na_linha` em 8064-8073); fora do domínio, lidos como prova: tests/test_brief_tamanho.py (três testes novos), mutantes M22 e M40 a M48, changelog.d. Já lido nas rodadas anteriores (no git): o resto da entrega, sem mudança.

Só aperta ou neutro, por escrito: **sim**.
- Aperta: `etapa_entregue_na_linha` (bin/forge-check:8073) passa de `search` com `(?<!não )\bentregue\b` em qualquer ponto do trecho para `ENTREGUE_DA_ETAPA.match` (8061): `entregue` logo depois do id, com `)` e um `(papel)` opcionais no meio, e sem letra nem `?` colados depois. O conjunto que fecha é subconjunto do anterior: a sonda S1 compara as duas formas em 20 linhas de borda e nenhuma fecha só na nova.
- Neutro: o comentário de `ETAPA_ARQUIVADA` (8058) troca o papel de stack por um papel neutro (R-NEUTRO); o código não muda.

Achados anteriores: A4 (recomendado) corrigido; as nove linhas da sonda dele não fecham mais (`test_negacao_futuro_e_texto_livre_de_entregue_nao_fecham`, `test_entregue_com_interrogacao_nao_fecha`), a forma real segue fechando (`test_forma_estrita_de_entregue_fecha`) e M22, M40 a M48 matam a volta de cada forma.

Resíduo aceito como neutro, sem achado: o parêntese do papel aceita texto livre, então `E1.1 (ainda não) entregue` ainda fecha, e o que vem depois de `entregue ` (`entregue ? não`, `entregue, não`) não é lido. O parêntese é o lugar do papel nas linhas do Histórico, essas formas não aparecem em nenhum pedido de /root/.forge-contrib/docs/pedidos (grep sem ocorrência) e já fechavam antes; restringir o parêntese a nome de papel (`[\w:-]+`) fecharia isso se o autor quiser.

Suíte: CI do head 8b312446 na fila (a catraca espera este parecer, R-CONFORMIDADE); rodado aqui tests.test_brief_tamanho (23 testes, OK) e a sonda S1, em arquivo de rascunho que carrega bin/forge-check e compara a regra nova com a anterior.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sonda local (biblioteca padrão); gitleaks, Semgrep e zizmor não se aplicam ao delta (sem segredo, sem workflow).
