---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-brief-gerar
commit: 2008e612de013e287fe544cd1f04dd4332a899f9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.92, melhoria/v0476-brief-gerar, item E3.48)

Escopo: E3.48, brief gerado compacto, `proximo` só da etapa e formato dos Achados no brief de portão. Diff contra a base 5fb2c856: `bin/forge-check` (+16 −22), `bin/forge-testes` (mapa), `tests/test_brief_tamanho.py` (novo), ajustes de 6 testes, specs `tests/mutantes/v0474-e348.json` (nova) e `v0457-aqr2.json` (M1, M2, M3 e M5 retirados com a guarda que saiu) e o fragmento. Código e teste: 146 linhas, dentro da orientação de 150 (M14). Um comportamento só (texto do `brief gerar`).

O que muda: (1) o Fora do escopo do brief novo usa `linhas_de_ids_do_fora`, a mesma da volta (BRIEF-VOLTA-FORA-COMPACTO); `linha_de_outra_etapa` e `ETAPA_FEITA` saem sem outro uso (grep). O `conferir_corte` já lia ids; `test_o_brief_gerado_e_preenchido_passa_no_corte` e o teste de 600 etapas (15 linhas, abaixo de 10.000 caracteres) provam. (2) `comece por forge-check proximo <p> --etapa <coberta>`; o `--etapa` existe no `proximo` (rodado: 2,5 s com `--etapa E3.92` no v0474). (3) `LINHA_DOS_ACHADOS` só em `ETAPAS_DE_PARECER`, com `TETO_DO_ACHADO` (300) da fonte e o mesmo formato do `_modelo.md`. (4) PQs do autor e a linha do erro recorrente encurtadas; gerador e conferência (`LINHA_DO_DESTINO`, `linha_do_destino`) mudam juntos.

Ferramenta: `forge-mutante` no head 2008e612, 1 processo: v0474-e348 M1 a M6 morreram; v0457-aqr2 M4 morreu. `forge-mutante --cobertura --base 5fb2c856`: guardas 8711 e 8734 cobertas, 8578 e 8579 apagadas; spec v0457-aqr2 editada (alinhada à fonte). Testes do item (`test_brief_tamanho`, `GerarComCumpridas`, `LinhasDoDestino`, `ConferirBrief`): 41 OK. A suíte inteira fica no CI do PR (ainda não aberto).

## Achados
- A1 (recomendado) docs/regras/R-BRIEF.md:16 · a regra ainda manda o "trecho literal" das outras etapas no Fora do escopo; o gerar (e a volta) já escreve só os ids, que o selo aceita. Alinhe o texto da regra ao que a ferramenta faz, num item próprio.
- A2 (recomendado) bin/forge-check:8711 · sem --cobre, o brief sai com `--etapa <a etapa do Cobre>`, que a conferência não cobra; use o marcador PREENCHER, que o selo barra até ser preenchido, e um teste do ramo sem coberta.
- A3 (recomendado) bin/forge-check:5130 · o rótulo encurtado para "Erro recorrente" faz o `conferir_erros_do_destino` reprovar qualquer linha de Decisões com esse trecho, também texto livre do Jarvis; um prefixo mais específico (`- Erro recorrente (`) evita o falso positivo.

## Sondas

## Parecer
Aprovado. O brief fica menor sem perder regra: as etapas continuam todas citadas (pelo id, como na volta), o `proximo` aponta a etapa do Cobre e o portão recebe o formato dos Achados. As guardas mudadas têm mutante que morre e teste do ramo de falha. Os três achados são recomendações e não devolvem (`R-REVIEW`). A catraca decide, no PR, se a troca do Fora do escopo pede `afrouxa-regra`; o review não a refaz.
