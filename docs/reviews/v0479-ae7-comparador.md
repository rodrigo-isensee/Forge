---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: bb1bac50822cd077f979063a93430c28a1292977
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.97, AE7.1 `forge-check comparar`, revalidação no head bb1bac50)

Revalidação (H3, R-REVIEW) do parecer aprovado em 61198b20 (E58.58, head caae27c4). Delta lido por
`forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`: intervalo `caae27c4..bb1bac50`, escopo sem o que veio da
develop. O que a develop trouxe foi separado com `git diff c9d69234 HEAD`: `bin/forge-check` e `bin/forge-testes` ficam,
contra a develop, só com o registro do subcomando `comparar` e o `test_comparar` em `FORGE_CHECK`, iguais ao head
caae27c4; o resto desses dois arquivos é da develop e fica fora do domínio. Fora do delta nada foi relido.

## Conferido
- Merge ce904e9c: a única resolução à mão é `tests/pesos-d4.json`, com as duas chaves (`test_comando_pronto` da develop e
  `test_comparar` da branch), em ordem alfabética.
- 43b426e7: `test_reescrita_do_caso_recusado_na_base_nao_conta` monta a base que recusa com hook que reescreve e o head
  que libera; espera `aceite-novo: proibido base=recusa head=allow entrada-reescrita`, ou seja, a reescrita do lado que
  recusa não entra (linha 285). Declarado no CMP60 (`v0478-ae7-comparar-9.json`).
- e90fbd6f: o `de` do CMP102 casa a `RAIZ_FORA` atual (`bin/forge_comparar.py:54`, com `monitors` e `workflows`) e tira
  só `settings.json`.
- bb1bac50: `README.md` citado por `bin/forge_comparar.py` em `CITACOES_CONHECIDAS` com motivo `nome` (só escrito no
  projeto sintético, linha 270, sem leitura de conteúdo); linha do `docs/indice-forge.md` regenerada.
- Testes: `python3 -m unittest tests.test_comparar tests.test_reval_delta tests.test_indice_forge`: 95 OK.
- `bin/forge-testes --registros --base origin/develop`: rc 0 (9 conferências e o peso dos módulos novos).
- Mutantes (V2): `bin/forge-mutante --processos 1 --ids CMP60,CMP102` nas specs 9 e 15: os dois morreram.
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:285 · segue das rodadas anteriores: só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` diferem em cada lado e dão `entrada-reescrita` falso. Erro do lado seguro; normalizar o HOME como `{home}`.
- A15 (recomendado) docs/propostas/v0479-melhorias-anti-erro.md:170 · o C0 da emenda pede `forge-check comparar X X` em `origin/develop` e `origin/main`, que dão rc 2 por falta do corpus; reescrever o oráculo como `fora_da_medida` None em cada ref.

## Parecer
Aprovado no head bb1bac50. O merge da develop só juntou as duas chaves de peso; o teste novo mata o CMP60 e o CMP102
segue a `RAIZ_FORA` atual. A4 e A15 seguem recomendados (R-REVIEW) e viram cartão depois do merge.
