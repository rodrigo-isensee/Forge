---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-brief-gerar
commit: 2008e612de013e287fe544cd1f04dd4332a899f9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0476-brief-gerar (v0474 E3.48, parecer E3.93)

Delta lido: `5fb2c856..2008e612` (12 arquivos; código só em `bin/forge-check` e na lista de `bin/forge-testes`). Pergunta do portão: o que o selo ou a conferência cobravam continua cobrado? Sim: a mudança é só no gerador (`montar_brief`); `conferir_corte` (`bin/forge-check:6781`), o selo, a volta e `conferir_erros_do_destino` (`bin/forge-check:5148`) não mudaram de lógica.

## Gatilhos
Gatilhos: controle do Forge (gerador de brief e linha conferida do erro recorrente)

## Achados
- A1 (recomendado) bin/forge-check:3895 · rótulo encurtado para "Erro recorrente": a volta de brief antigo isenta do "perdeu" toda linha de Decisões que contenha o termo; casar a linha inteira com LINHA_DO_DESTINO em vez do substring.

## Sondas

## Detalhe dos achados
- Fora do escopo só por ids (`bin/forge-check:8733-8734`): reusa `linhas_de_ids_do_fora` (`bin/forge-check:3730`), a forma que a volta já usava; `conferir_corte` resolve cada id por `referencias_do_item` e continua exigindo a marca completa para corte real, a etapa do papel do destino no Entregar e a do `Cobre:` sem corte silencioso. A etapa coberta segue fora da lista (`e != coberta`, mutante `v0474-e348` M1). Perde-se só texto informativo, não cobrança.
- Linha do erro recorrente (`bin/forge-check:5130-5136`): a conferência exige igualdade byte a byte com `linha_do_destino`; o rótulo mais curto alarga o conjunto de linhas cobradas em Decisões (mais estrito, não menos). Brief antigo com o rótulo longo reprova na reconferência: falha fechada. Nenhum pedido nem doc da fábrica usa o termo em texto livre (busca sem resultado), então não há falso positivo hoje.
- A1: em `bin/forge-check:3895`, só no caminho do brief de volta antigo (`referencia_do_brief` ausente), a linha que contenha "Erro recorrente" sai do "perdeu"; o rótulo mais curto alarga essa isenção. Caminho realista estreito: quem compõe a volta antiga apaga uma restrição não-dono que cite o termo; as decisões do dono continuam cobradas pelo laço seguinte. Severidade baixa · correção mínima: isentar só `LINHA_DO_DESTINO.match(linha.strip())` · esforço P · dono: tech-lead.
- `proximo --etapa` no brief (`bin/forge-check:8711-8712`): conferido que a saída por etapa mantém os bloqueios do registro e os últimos vereditos; sem coberta, sai o marcador `<a etapa do Cobre>`, sem consequência de controle.
- `LINHA_DOS_ACHADOS` (`bin/forge-check:8573`): texto fixo, sem dado de entrada; não abre cabeçalho de seção (a linha começa com `- `).
- Mutantes `v0457-aqr2` M1, M2, M3, M5 retirados junto com a função que guardavam (`linha_de_outra_etapa`, removida); M4 realinhado; `v0474-e348` M1 a M6 cobrem a lógica nova.

## Riscos aceitos e ferramentas
Sem risco aceito. Testes rodados no head: `tests.test_brief_tamanho`, `tests.test_erros_no_brief`, `tests.test_etapa_do_brief` (141, OK). A suíte inteira roda no CI do PR (ainda sem PR nem check no head) e é condição do merge. Revisão estática por leitura; varredura de segredos não se aplica (sem configuração nem credencial no delta).
