---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-sieg-g1-autorizacao
commit: f42850b5519efe09548f913a63c9969c31bf4298
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 ADR 0018, autorização do dono gravada (E2.502, revalidação no head f42850b5)

Gatilhos: hook, autorização, CI (`R-SEGURANCA`). Revalidação por delta do parecer reprovado do head a87f0a6f (`forge-check parecer delta`: o domínio mudou só em `docs/adr/0018-autorizacao-do-dono-gravada.md`; sem código nem teste, nada a rodar). Fora daqui: D2, D3 e D4, pendentes com o dono.

## Resumo
- A1 resolvido: o corpo é a mensagem inteira (itens 2 e 3, sem `--palavras`); ato, alvo e validade saem do texto todo; só nasce `ativa` com vocabulário positivo fechado, e negação, condição, ato duplo ou conflito de validade vão a `pendente-confirmacao`. As marcas de negação ficam como lista de teste, não como regra (AR-3).
- A2 a A7 entraram como requisito (tabela abaixo); A8 virou D4 (do dono, fora desta revalidação; até a resposta vale a opção a, a mais estreita).
- D1 do dono aplicada (item 6, Critério de parada `inativa`): 48 h sem prazo, "hoje" ou "até amanhã"; prazo escrito até 7 dias, "até o fim deste pedido" incluído, parando no primeiro entre o fechamento gravado e o teto. É coerente entre os itens 5, 6, 7 e o critério. A forma de aplicá-la deixa três pontos abertos, todos recomendados (A9 a A11), nenhum bloqueante.
- Aprovado: o desenho só aperta, sem caminho novo, e o bloqueante saiu. O item segue dependendo das decisões D2 a D4 do dono (a ADR continua proposta).

## Achados
- A9 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:25 · Fuso lido de `/etc/localtime`: neste ambiente é Etc/UTC e o dono está em -03. UTC legível mas errado não cai em "sem fuso legível": data escrita e "esta noite" erram o dia. Trate UTC ou sem região como não legível nesses termos (uso único).
- A10 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:15 · "Até o fim deste pedido" precisa de campo `Pedido` na concessão (o item 2 não tem): sem ele a ferramenta não sabe qual fechamento conferir. Grave o id declarado, mostre-o em `ler` e confira pedido aberto; só encurta.
- A11 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:42 · A mitigação da D1 (a mensagem da manhã lista as autorizações ativas e quando vencem) está só no registro da D1; não está no item 12 nem na G1.6. Ponha na G1.6 (`agents/jarvis.md`, `falar-com-o-dono`) usando `autorizacao ler`.

## Sondas

## Revalidação de A1 a A8
| Achado | Estado no f42850b5 | Onde |
|---|---|---|
| A1 bloqueante | resolvido: mensagem inteira, vocabulário positivo, pendência pelo texto todo, `C-<Id>` só com `Id` e palavras de `PALAVRAS` | itens 2, 3, 5; Alternativas |
| A2 | resolvido: marcador colado (`PR 5`, `PR5`, `#5`), versão `X.Y.Z`, alvo só na frase do ato | item 5 |
| A3 | resolvido: três grafias inteiras, `quem: []`, teste `escrita-direta` em Write, Edit e Bash | G1.2 |
| A4 | resolvido: `U-<Id>` com `x` como cadeado; teste com dois hooks juntos | item 9, G1.3 |
| A5 | resolvido: texto fixo "forma conferida; origem só na camada local" na catraca e no job | itens 10 e 11, G1.4, G1.5 |
| A6 | incorporado, com a ressalva A9 | item 6 |
| A7 | incorporado: matriz com gerador, corpus de legítimos e orçamento antes da G1.3; remoção do rótulo decidida (só `exigir_dono`) | item 9, G1.3 |
| A8 | virou D4, do dono | Decisões em aberto |

## Detalhe dos achados
**D1, onde a forma de aplicar pode abrir brecha.** Nada contesta a decisão. (i) O teto é tempo absoluto e o fuso não o move; "sem termo", "hoje" e "até amanhã" valem 48 h mesmo sem fuso; fora do mapa e sem prazo legível, `uso-unico`. Sem brecha. (ii) "Até o fim deste pedido": o fechamento é gravado pelo agente, mas só encurta (vale o primeiro entre fechamento e 7 dias), então não amplia; falta só o campo que diz qual pedido (A10). (iii) Pedido aberto por 7 dias com D4 pendente deixa o `ate:` cobrir PR e não conteúdo por até 7 dias; é a D4, não a D1, e a opção a) (head visto) vale até a resposta. (iv) A confirmação não renova a validade: conta a `Hora-da-fala` (item 7), o lado estreito.

**A9.** Evidência: item 6 (linha 25) lê o fuso de `/etc/localtime`, "nunca de `TZ`". Neste ambiente `/etc/localtime -> /usr/share/zoneinfo/Etc/UTC`, e `date` mostra -03. Caminho: o dono escreve "até 18/11 12:00" ou "esta noite"; a ferramenta converte com UTC e o fim cai até 3 h além do dito, e "esta noite" pode pular um dia quando a fala em UTC já virou o dia (21:00 local). Severidade: baixa (o teto de 48 h ou 7 dias limita; o fuso vai em `Fuso` e em `ler`). Correção mínima: fuso `Etc/UTC`, `UTC` ou sem nome de região conta como não legível para data, hora, dia da semana e "esta noite" (valem `uso-unico`, e o Jarvis pergunta); o resto da regra fica. Esforço P. Dono: tech-lead (G1.1).

**A10.** Evidência: item 2 (linha 15) sem campo do pedido; item 6 depende do "fechamento gravado do pedido". Caminho: sem identificar o pedido, a conferência do item 7 não tem o que ler e cai no teto de 7 dias (o que o dono permitiu) ou num pedido escolhido sem registro. Correção mínima: campo `Pedido` (id declarado por `--pedido`, mostrado em `ler` e na confirmação); concessão que nasce com o pedido já fechado vale `uso-unico`. Esforço P. Dono: software-architect (ADR), tech-lead (G1.2).

**A11.** Evidência: o registro da D1 (linha 48) e a G1.6 (linha 42), que cita `R-CONTRIB`, `R-DECISAO`, `R-MAIN`, a skill e `agents/jarvis.md` sem a lista matinal. Caminho: 48 h sem prazo é mais largo que o "hoje" falado; sem a lista, a autorização esquecida segue ativa sem o dono ver. Correção: uma linha na G1.6 e no item 12 (lista das ativas com vencimento no fuso e em UTC). Esforço P. Dono: tech-lead.

## Itens conferidos sem achado
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 e AR-2 (mutantes nos ramos de falha) estão na G1.3; AR-3 não se aplica (vocabulário positivo, marcas só em teste); AR-5 (`python3 -I` nos subcomandos) na G1.2; AR-7 (raiz principal do clone) coberto pelas três grafias; AR-11 (leitura do `gh api` como a do `gh`) no item 9.
- Só aperta: o `exigir_dono`, a catraca por conteúdo e a trava `R-MAIN` ficam; "Afrouxa? Não" confere.
- Coerência da D1: item 6, item 7, linha 48 e o critério `inativa` dizem o mesmo (48 h sem prazo escrito, 7 dias com).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: nenhuma varredura aplicável (documento). Suíte: não roda (sem código; nenhum teste foi tocado); CI do PR não consultado. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` fora do PATH.
