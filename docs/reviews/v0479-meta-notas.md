---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta-notas
commit: 7132ac151a5dd9b9fc4026ffdba7b2c182965bdb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E25.2, revalidado na E25.7, melhoria/v0479-meta-notas)

Escopo: E25.1, o hook `meta` mede o idioma das notas entre chamadas de ferramenta da rodada (`notas_da_rodada`, `notas_em_outro_idioma`), o campo `notas_em_outro_idioma` no `mensagens.jsonl` e `outro_idioma` passando a incluí-las. Diff `0c47762a..87015983`: 40 linhas de código em `hooks/meta.py` (dentro do H1), um comportamento.

## Achados
- A1 (recomendado) hooks/meta.py:277 · Rodada só fecha na fala do dono: Stop seguido de aviso `<task-notification>` ou continuação do próprio S4 recontam a nota já medida e a final anterior (sonda: 2 notas na 2a medida). Infla `outro_idioma` e o critério de reversão; parar também na final anterior.
- A2 (recomendado) hooks/meta.py:271 · O filtro por substring `"tool_result"` pula também a linha do assistente cuja entrada de ferramenta traz esse texto literal (ex.: `grep "tool_result"`); a nota dela some da medida. Falso negativo raro; filtrar por `"type":"tool_result"`.

## Sondas

## Parecer
Aprovado. Faz o que a E25.1 pede: a fronteira da rodada usa a fonte única `vigia.texto_do_dono`, subagente (`isSidechain`) e a mensagem final ficam fora, a leitura tem teto em `TETO_DA_MEDIDA` e o resultado de ferramenta não é decodificado (custo provado no teste). O `expectedFailure` do eval `MensagemEmOutroIdioma` saiu e o caso passa (`tests/evals/test_erros_por_papel.py`), como pede a regra do erro por papel. Changelog traz custo medido e critério de reversão. A linha nova só leva contagem, nunca o texto (parecer de segurança no mesmo head, `docs/security/v0479-meta-notas.md`).

Ferramentas, no SHA revisado: `python3 -m unittest tests.test_meta tests.evals.test_erros_por_papel.MensagemEmOutroIdioma` com 46 testes OK; `bin/forge-mutante tests/mutantes/v0478-meta-notas.json tests/mutantes/v0478-meta-notas-2.json` com todos os mutantes mortos (M1 a M14; M11 a M14 por erro do teste declarado, o que conta como morto). A spec M6 do SIEG-G4 segue a linha nova (AR-12). Suíte inteira: fica no CI do PR (`R-REVIEW`).

A1 e A2 não bloqueiam (`R-REVIEW`): A1 é inflação da medida, sem efeito em decisão do Stop, e a janela "desde a última fala do dono" é a do pedido; vale como item seguinte antes de usar a contagem no critério de reversão.

## Revalidação (E25.7, head 7132ac15)
Delta lido só por `forge-check parecer delta docs/reviews/v0479-meta-notas.md`, intervalo `87015983..7132ac15`: no domínio, uma linha em `tests/test_meta.py:350`, o helper `medir` lê `notas_em_outro_idioma` e `outro_idioma` com `.get` (A1 do QA). Sem mudança em `hooks/meta.py`. Rodado: `python3 -m unittest test_meta.NotasEntreFerramentas` (em `tests/`) com 11 testes OK no head; com o `hooks/meta.py` da base `0c47762a`, os 7 testes do helper falham por asserção (FAIL), não mais por `KeyError`, como o commit declara. A1 e A2 seguem recomendados, já no cartão META-NOTAS-RECONTA. Aprovado mantido.
