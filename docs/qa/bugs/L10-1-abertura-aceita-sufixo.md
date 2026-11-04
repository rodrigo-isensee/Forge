# L10-1 - a linha de abertura de etapa aceita texto colado em "aberta"
- Severidade: baixa
- Responsável sugerido: forge:tech-lead
- Ambiente: melhoria/lote-l10 @ 4bb60b8 (código effbe5b), bin/forge-check:1832

## Passos para reproduzir
1. Pedido com a etapa E1.4b em `## Etapas` e, no `## Histórico`, a linha do brief anterior e depois `- 2026-11-04 10:00: etapa E1.4b aberta-nao`.
2. `forge-check brief gerar --volta <brief anterior> --ref <branch>`.

## Resultado esperado
Sem prova de abertura (a forma é `etapa <id> aberta` fechando a linha ou seguida de espaço).

## Resultado obtido
A linha `- "E1.4b ..." · etapa de outra delegação; continua no pedido` entra no Fora do escopo: `ETAPA_ABERTA` termina em `aberta\b`, e `\b` casa antes de `-`.

## Evidência
Falha observada ao rodar o cenário no módulo de teste do QA (removido da suíte, não pulado). Exposição pequena: o Histórico é escrito pelo Jarvis, e `abertura prevista`, `abertas` e `etapa` sem data já são recusados.
