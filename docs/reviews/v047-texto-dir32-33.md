---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-texto-dir32-33
commit: 9fd5d7716a9881fca225ddb5ec27e100bfba5de3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047 (E2.712, diretrizes 32 e 33 e o teto do H6 no texto; revalidação E1.3 do v0474 no head 9fd5d771)

## Achados
- A1 (bloqueante) tests/fixtures/diretrizes-do-dono.json:171 · resolvido em 9fd5d771; diretriz 27 virou fabrica sem estar entregue: KANBAN.md:107 tem RELEASE-EM-1H em "Pronto para fazer" com FALTA (2) PR único, (3) aviso, (5) projetos, (6) medida; e DIR-27-AVISO-MAIN-VERDE aberto. Volte a pendente com o cartão RELEASE-EM-1H.
- A2 (recomendado) tests/test_jarvis_nucleo.py:27 · resolvido em f42808f7; com a 27 pendente são 8 (30 e 31 nasceram depois da P4) e MAX_PENDENTES=7 reprova; subir para 8 afrouxa a trava: destaque no título do PR e motivo no comentário (novas diretrizes, não regressão), ou decisão do dono.
- A3 (recomendado) docs/regras/R-TETO.md:14 · a regra diz "sem número fixo" e não cita o H6 (20 agentes, 12 branches); não contradiz, mas vale citar. Na volta: fica para cartão, o arquivo tem 4 caracteres de folga no teto de test_metricas_texto.

## Sondas

## Revalidação (E1.3, v0474)
Delta lido: `forge-check parecer delta` de ac34647c..9fd5d771, no domínio só `tests/fixtures/diretrizes-do-dono.json` e `tests/test_jarvis_nucleo.py`.
- A1: a 27 volta a `pendente` com `cartao: RELEASE-EM-1H` e os dois trechos saem do fixture; resolve o achado.
- A2: `MAX_PENDENTES` 7 → 8 com o motivo no comentário (26 virou fábrica, 30 e 31 nasceram depois da P4); afrouxa-regra coberto pela DECISÃO DO DONO de 2026-11-16 05:13 (docs/pedidos/v0474.md:40: o Jarvis aplica o rótulo `afrouxa-regra` nos PRs do plano v047). O rótulo no PR fica com o Jarvis.
- A3: fica recomendado, para cartão.
- `test_jarvis_nucleo` (43) e `test_metricas_texto` (2) verdes no head 9fd5d771; suíte inteira no CI do PR.

Aprovado no head 9fd5d771.

## Parecer anterior (ac34647c)
Reprovado por A1. O resto está correto:

- Só acréscimo: no `agents/jarvis.md` a frase antiga segue inteira e o texto novo entra no meio; tech-lead, modelo e `config.json` só ganham linhas; `ritmo-e-corte.md` é novo. Nenhuma invariante nem regra saiu (diff `origin/develop...ac34647c`: 90 inserções, 5 remoções, todas no fixture: `pendente`/`cartao` da 26 e 27 trocados).
- Fidelidade: os textos batem com as diretrizes 32 e 33 de `docs/diretrizes-do-dono.md` e com a ORDEM DO DONO de 17/11 08:06 (teto 20, 12 branches, agente livre termina o aberto).
- Diretriz 26 como fabrica está certa: INTEGRACAO-EM-LOTE em "Pronto" no KANBAN e o trecho existe em `docs/fechamento-integrador.md:96`.
- Diretriz 27: os dois trechos existem (`docs/fechamento-integrador.md:97`), mas cobrem só os pontos (1) e (4) do cartão; daí A1.
- R-NEUTRO: o modelo fala em "branch de integração", sem nome de projeto; classes `Neutralidade`, `NeutralidadeDoNucleo`, `RegrasInviolaveis`, `RegrasComId` e `TextosDoAgenteEDaRegra` verdes (15 testes).
- Teto de métricas: `test_jarvis_nucleo` (43) e `test_metricas_texto` (2) verdes no head; o núcleo do Jarvis cabe no teto, com o detalhe movido para `ritmo-e-corte.md` (diretriz 25).
- Invariantes novas com `invariantes_motivo` e `_trecho` e regra pelo ID; sem guarda de código no diff, sem mutante devido. Suíte inteira: fica no CI do PR.
