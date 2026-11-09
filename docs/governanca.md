# Como medir o processo e manter as regras com prazo?

Propósito: explicar as três medidas de governança da fábrica (métricas de fluxo, orçamento de instrução e validade das regras) e como usá-las. Público: quem mantém o Forge e o `agile-coach`. Revisão: 2026-11-08.

Origem: decisão do dono de 08/11 (avaliação externa do processo, 0.43.1): medir o que importa; regra que vale sempre vira código; regras com prazo de validade; o processo para de só crescer. Código em `bin/forge_governanca.py` (subcomandos do `forge-check`) e `tests/test_orcamento_instrucao.py`.

## Métricas de fluxo: `forge-check metricas`

```bash
forge-check --raiz-pedidos ~/.forge-contrib metricas [--pedido ID]... [--desde AAAA-MM-DD] [--ate AAAA-MM-DD] \
    [--por dia|semana] [--fuso -03:00] [--develop origin/develop] [--main origin/main] [--gh] [--json]
```

Só leitura e sem rede (o `gh` só com `--gh`); rc 0, e 2 só com data, hora ou fuso inválido. Lê o `## Histórico` (e as linhas `PERGUNTA AO DONO` e `DECISÃO DO DONO` de `## Decisões do usuário`) de cada pedido, o registro `docs/kanban/conferencias.md` e o git de `--raiz`.

| Medida | Como sai | Natureza |
|---|---|---|
| `pronto` | hora da primeira linha `entrega conferida <sha>` do item | Histórico |
| `develop_h`, `main_h` | horas do `pronto` até o commit da linha de primeiro pai da ref que passou a conter o último sha conferido (o merge que o trouxe); `aberto` se ainda não chegou, com `aberto_h` até agora | medida (git) |
| `voltas` | linhas com "não cumpriu" ou "reprovado" que não falam de push ou suíte | contagem do Histórico |
| `revalidacoes` | linhas com "revalid" | contagem do Histórico |
| `suites`, `falhas` | linhas de push, suíte ou envio com resultado (passou ou rc 0; reprovou, falhou ou rc 1+) | contagem do Histórico |
| `espera_dono_min` | do pedido ao dono ("vai ao dono", "pergunta ao dono", "aguardando o dono", PERGUNTA registrada) até a primeira DECISÃO ou ORDEM DO DONO seguinte (a hora entre parênteses), sem contar sobreposição | estimada |
| `reprovacoes` | reprovações do registro por classe (coluna `classe`) | registro |
| `merito(declarada)` | coluna de mérito do registro | **declarada**: quem anota é o próprio Jarvis; não é medida independente |
| `ci` | execuções e falhas do CI das branches citadas no item (`--gh`) | gh |

O item é o primeiro `E<n>` do parêntese que abre a linha, ou do que segue `entrega conferida <sha>`; linha sem item conta no item `-` (o pedido inteiro). Saem uma linha por item, uma por pedido e uma por período (`--por dia` ou `semana`, pela data do `pronto`), e a linha `fontes`. O `--json` traz os mesmos números e a natureza de cada um em `fontes`. Merge por squash não deixa o sha na develop: o item fica `aberto` (limite conhecido).

**Orçamento de tokens por versão (X2, 0.44.1):** o pedido declara a estimativa nas linhas `Versão: X.Y.Z` e `Tokens previstos: N` (aceita `2.000.000`, `500k`, `3M`). O `metricas` soma o previsto e o gasto medido (`tokens` dos transcritos; sem medida conta 0) por versão, imprime `metricas: orcamento versao <v> previsto=<n> gasto=<n>` e `metricas: alerta: ...` quando o gasto passa do previsto, por pedido e por versão. Só avisa: o rc segue 0.

## Orçamento de instrução: `tests/test_orcamento_instrucao.py`

Mede o que cada agente carrega: `agents/<x>.md`, as skills obrigatórias (as do `skills:` do cabeçalho e as que o texto cita pelo caminho `${CLAUDE_PLUGIN_ROOT}/skills/<nome>/SKILL.md`) e os `docs/regras/R-*.md` citados pelo agente ou por essas skills. Três números: caracteres do arquivo do agente, caracteres do total e marcadores normativos (nunca, sempre, só, proibido, obrigatório, reprova). O teto e o alvo de cada agente ficam em `docs/regras/orcamento.json`; o teste reprova acima do teto, e agente sem orçamento também.

- Teto: a medida de 2026-11-08 depois dos textos da 0.43.1 (nada piora a partir daqui; onde a medida já passou do alvo, o teto fica no alvo). Subir um teto é afrouxar: diga no PR, com o motivo, e leve ao dono.
- Alvo (meta, não trava): jarvis com 12 mil caracteres no arquivo, 45 mil no total e 90 marcadores; conferente com 5 mil, 15 mil e 30. Quando um texto encolher, baixe o teto para a medida nova no mesmo PR.
- Núcleo: `agents/jarvis.md` mais todos os `docs/regras/*.md` em até metade da base da 0.43 (decisão 11 do dono), `nucleo` do mesmo arquivo, lido por `tests/test_jarvis_nucleo.py`; cada trava tem um número só.

## Validade das regras: `forge-check regras`

```bash
forge-check regras [--estrito] [--hoje AAAA-MM-DD] [--json]
```

Cada `docs/regras/R-*.md` leva duas linhas (com ou sem marcador de lista e negrito):

```text
- **Revisar em:** 2027-02-08
- **Medida:** 36 % de reprovação de brief em 1.742 vereditos (03 a 08/11)
```

`Revisar em` é a data em que a retrospectiva mede a regra de novo e decide mantê-la ou removê-la; `Medida` é o número que justifica a regra (sem dígito, sai aviso). Estados: `ok`, `a-vencer` (até 14 dias, sem aviso) e `aviso` (campo ausente, data inválida, regra vencida ou medida sem número). Sem `--estrito` o rc é 0 com aviso; com `--estrito`, rc 1. Sem nenhuma regra, rc 2.
