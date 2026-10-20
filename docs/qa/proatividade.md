---
tipo: qa
contrato: 1
pedido: proatividade
branch: melhoria/proatividade
commit: 3a8e376866ccdcd4e49176f3b9531080e217dd95
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# Parecer de QA - proatividade

Diff testado: `e9c81e0..3a8e376` (o HEAD da branch, f84eed7, só acrescenta review e segurança).

## Obrigação -> verificação -> resultado
| Obrigação | Verificação | Fronteira protegida | Resultado |
|---|---|---|---|
| Linha `Melhoria vista:` como última do relatório (`R-DECISAO` a) | `bin/forge-check brief gerar ... --etapa qa`: bloco Relatório traz "Última linha: `Melhoria vista:` ... ou `nenhuma`" numa linha só | n/a | passou |
| Complemento e dois limites do dono literais (`R-DECISAO` c, d) | Texto: custo em dinheiro real "sem exceção" (`R-CUSTO`) e aumento de tokens ou tempo de entrega como decisão do usuário; sem condição ou na dúvida vai ao usuário; custo real não entra na fila | limite de custo e de tokens/tempo | passou |
| Retrospectiva vira cartão (`jarvis.md` item 9, `agile-coach.md` item 3) | `MELHORIA:` gravada no pedido, classificada em cartão, ao usuário ou descartada; pedido só fecha com ela gravada | n/a | passou |
| Jarvis item 6 e autonomia | Item 6 termina com a linha `Melhoria vista:`; autonomia condicionada ao critério de entrada direta; custo, controle, tokens e tempo seguem do usuário | n/a | passou |
| `agile-coach.md` linhas 19 e 21 coerentes com o item 3 | Ambas citam o critério de entrada direta, e o resto vai ao usuário | n/a | passou |
| Extensão aos projetos | `templates/projeto/CLAUDE.md` traz `R-DECISAO` com "melhoria vista entra direto pelo critério da regra"; `R-DECISAO` (e) | n/a | passou |

## Execução
- `python3 -m unittest discover -s tests -q`: Ran 865 tests in 233.092s, OK.
- `scripts/validar-plugin.sh`: Validation passed (as duas validações). Os avisos de rede negada no sandbox são do ambiente.
- Vermelho antes do verde: a mudança é de texto e a proteção é o `tests/config.json`, que o review exercitou; nenhum teste novo escrito por QA.

## Achados
