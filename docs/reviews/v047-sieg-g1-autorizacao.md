---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-sieg-g1-autorizacao
commit: 7d8ff8f51af8e12b1b8aed4f12b2bc9f3f78a07e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047 (G1.0 e G1.1 da ADR 0018, E2.666)

Escopo: G1.0 (ADR 0018 aceita com D2=a e D4=c; campo `Pedido` e fechamento `F-<Pedido>`) e G1.1 (`forge-check autorizacao ler`: formato, integridade, validade A6/D1, `C-`/`R-`/`U-`, falha fechada), só leitura. Diff `86ac0fcb...580b6c34`.

## Achados
- A1 (recomendado) docs/adr/README.md:26 · O índice ainda diz "proposta; vale depois do parecer de segurança e das decisões D1 a D3", e a ADR está aceita com D1, D2 e D4 decididas; alinhe o estado no índice.
- A2 (recomendado) bin/forge-check:9548 · A ajuda de `autorizacao` diz "o estado pela validade vem no G1.1b", que já entrou (`bin/forge_autorizacao.py:142`); tire a frase.
- A3 (recomendado) bin/forge_autorizacao.py:111 · Concordo com A12 a A14 da segurança (Id contra o nome, teto de 7 dias por lista dos termos curtos, `Hora-da-fala` futura, `.forge` como link), reproduzidos aqui; fecham antes do G1.3, que consome `U-<Id>` e o estado.
- A4 (recomendado) bin/forge_autorizacao.py:1 · 378 linhas de código e teste (8 em `bin/forge-check`, 190 no módulo, 180 no teste) passam da orientação M14; o corpo do PR traz `teto: excedido, 378 linhas, <motivo>`.
- A5 (bloqueante) bin/forge-testes:105 · `test_autorizacao` roda o `bin/forge-check` e falta em `FORGE_CHECK`; o `test_testes_tocados` da develop reprova, CI do PR 629 vermelho (suíte 5/5, `bateria`). Inclua-o em `FORGE_CHECK`.

## Sondas

## Parecer
Aprovado. Desenho conferido contra as decisões do dono: D2=a (ordem de 17/11 08:06) e D4=c (ordem de 17/11 07:51) gravadas nos itens 7, 11 e na seção de decisões; `Pedido` no item 2 e `F-<Pedido>` no item 1 só apertam (presença tira a concessão de "até o fim deste pedido"), coerentes com a D1 e com o item 7; estado `aceita` sustentado pela revalidação de segurança.

Código: `bin/forge_autorizacao.py` só lê; abre sem seguir link e recusa o que não é arquivo comum, UTF-8 inválido, cabeçalho fora da forma e campo repetido; o `Gravado-por` aceito é o sha256 do `forge-check` carregado; `limite` exige que a `Validade` no `Fuso` e a `Validade-utc` deem o mesmo instante (A6) e corta no teto da D1; `C-` só confirma íntegra, do mesmo gravador e de fala posterior; `R-` e `U-` só apertam e valem sem integridade (lado estreito); qualquer erro de leitura tira toda ativa (`inativa`), e o rc é 1 com erro ou adulterada, sem barrar nada. `SEM_GUARDA_DE_VERSAO` ganha `autorizacao`, coerente com subcomando que não confere repositório. R-NEUTRO: fuso vem do campo, nada fixo de projeto.

Verificadores: `python3 -m unittest tests.test_autorizacao` 8 testes OK; `bin/forge-mutante --processos 1 tests/mutantes/v047-sieg-g1-autorizacao*.json` 55 de 55 mortos; `--cobertura --base 86ac0fcb` deixa só `bin/forge_autorizacao.py:46` (texto de erro, não guarda). Suíte inteira: fica para o CI do PR (sem PR nesta etapa). Os achados A1 a A4 são recomendados e não devolvem (`R-REVIEW`).

## Revalidação (head 7b20d073)
Delta lido com `forge-check parecer delta` (`580b6c34..7b20d073`: `bin/forge-check`, `docs/adr/README.md`, `tests/mutantes/v047-sieg-g1-autorizacao-8.json`, `tests/test_autorizacao.py`). A1 e A2 fechados: índice com a 0018 aceita (D1, D2 e D4 decididas, D3 do dono) e ajuda sem o "G1.1b". Do QA, `setUpModule` carrega o módulo (na base cada teste cai sozinho) e o teste do link confere o texto de `os.strerror(ELOOP)`; M56 (`{e.strerror or e}` para `{e}`) morre, 1 de 1. `python3 -m unittest tests.test_autorizacao` 8 testes OK; `--cobertura --base 580b6c34` sem linha descoberta. A3 e A4 seguem recomendados, sem mudança. Aprovado no novo head.

## Revalidação (head c890fbd6, pedido v0474)
Delta lido com `forge-check parecer delta` (`7b20d073..c890fbd6`, junção da origin/develop b07e6a39, 0.47.3); a ferramenta acusa `bin/forge-check` no domínio. Resolução da junção conferida: `git merge-tree --write-tree c992f567 b07e6a39` dá a mesma árvore do c890fbd6 (junção limpa, sem edição à mão), e o patch da branch fora dos pareceres (`b07e6a39..c890fbd6`) é idêntico, linha a linha, ao de `86ac0fcb..7b20d073`; em `bin/forge-check` seguem só as 8 linhas do G1.1 (`SEM_GUARDA_DE_VERSAO`, subparser e despacho), e `escritor_do_resultado`, `raiz_principal` e `modulo_do_bin` existem na base nova. As demais linhas acusadas vêm da develop. `python3 -m unittest tests.test_autorizacao` 8 testes OK. Bloqueia A5: CI vermelho no head pelo mapa do `forge-testes` (defeito provado, `R-REVIEW`); A3 e A4 seguem recomendados. Reprovado no head c890fbd6; a volta revalida por delta.

## Revalidação (head 2f150f4d, pedido v0474, E1.21)
Delta lido com `forge-check parecer delta` (`c890fbd6..2f150f4d`; no domínio só `bin/forge-testes`, `tests/test_autorizacao.py` e `tests/test_testes_tocados.py`, 1 linha cada). A5 fechado: `test_autorizacao` entra em `FORGE_CHECK`, e `bin/forge-testes --listar bin/forge-check` passa a listá-lo; a docstring de `tests/test_autorizacao.py:1` cita `bin/forge-check` (o que o mapa exige) sem mudar teste, e a contagem em `tests/test_testes_tocados.py:77` vai de 88 para 89 com a origem anotada. `python3 -m unittest tests.test_testes_tocados tests.test_autorizacao`: 170 testes OK (1 pulado). Suíte inteira: fica para o CI do PR 629 no head novo, sem resultado ainda (`gh pr checks 629`: nenhum check). A3 e A4 seguem recomendados. Aprovado no head 2f150f4d.

## Revalidação (head 7d8ff8f5, pedido v0474, E1.33)
Delta lido com `forge-check parecer delta` (`2f150f4d..7d8ff8f5`, junção da develop 6a313b32 com #630 e #632; escopo sem o que veio da base): no domínio só `bin/forge-testes` e `tests/test_testes_tocados.py`. `git show --remerge-diff 7d8ff8f5`: conflito só em `tests/test_testes_tocados.py:77`, resolvido com 90 (89 da develop, com `test_estado_ilegivel`, mais `test_autorizacao` desta branch) e a origem anotada; `bin/forge-testes` juntou sem conflito e o `FORGE_CHECK` traz os dois módulos (`--listar bin/forge-check` lista ambos). `python3 -m unittest tests.test_testes_tocados tests.test_autorizacao`: 170 testes OK (1 pulado). CI do PR 629 no head 7d8ff8f5: suíte 10/10 partes verdes (3.12 e 3.14), `bateria (pareceres)` vermelha só pelo parecer desatualizado (este registro a resolve) e `catraca` pelo rótulo `afrouxa-regra` do dono (R-CONFORMIDADE, `bin/forge-check`), fora do review. A3 e A4 seguem recomendados. Aprovado no head 7d8ff8f5.
