---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-sieg-g1-autorizacao
commit: 580b6c34c8cc46ae8270cc42017427d82f64b784
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

## Sondas

## Parecer
Aprovado. Desenho conferido contra as decisões do dono: D2=a (ordem de 17/11 08:06) e D4=c (ordem de 17/11 07:51) gravadas nos itens 7, 11 e na seção de decisões; `Pedido` no item 2 e `F-<Pedido>` no item 1 só apertam (presença tira a concessão de "até o fim deste pedido"), coerentes com a D1 e com o item 7; estado `aceita` sustentado pela revalidação de segurança.

Código: `bin/forge_autorizacao.py` só lê; abre sem seguir link e recusa o que não é arquivo comum, UTF-8 inválido, cabeçalho fora da forma e campo repetido; o `Gravado-por` aceito é o sha256 do `forge-check` carregado; `limite` exige que a `Validade` no `Fuso` e a `Validade-utc` deem o mesmo instante (A6) e corta no teto da D1; `C-` só confirma íntegra, do mesmo gravador e de fala posterior; `R-` e `U-` só apertam e valem sem integridade (lado estreito); qualquer erro de leitura tira toda ativa (`inativa`), e o rc é 1 com erro ou adulterada, sem barrar nada. `SEM_GUARDA_DE_VERSAO` ganha `autorizacao`, coerente com subcomando que não confere repositório. R-NEUTRO: fuso vem do campo, nada fixo de projeto.

Verificadores: `python3 -m unittest tests.test_autorizacao` 8 testes OK; `bin/forge-mutante --processos 1 tests/mutantes/v047-sieg-g1-autorizacao*.json` 55 de 55 mortos; `--cobertura --base 86ac0fcb` deixa só `bin/forge_autorizacao.py:46` (texto de erro, não guarda). Suíte inteira: fica para o CI do PR (sem PR nesta etapa). Os achados A1 a A4 são recomendados e não devolvem (`R-REVIEW`).
