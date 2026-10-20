---
tipo: qa
contrato: 1
pedido: tl-1
branch: melhoria/tl-1
commit: 52d52218fa884e70d23dfb60066f19bc2a884fac
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA: tl-1 (um push por rodada de pareceres)

Sem UX nem API. Diff `e9c81e0...52d5221` (3 agentes e o fragmento `changelog.d/tl-1.md`). Não escrevi o diff. O HEAD da branch (`9b03f48`) só acrescenta o parecer de review.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: regra de push por rodada no mesmo lugar nos três agentes | CT-01: comparar o trecho do diff em tech-lead, qa-engineer e security-engineer | n/a | passou: mesma frase "sai uma vez por rodada (review, segurança e QA do mesmo SHA), quando o último gate termina, não um por parecer" |
| E1: sem contradição com `R-REVIEW` | CT-02: ler `docs/regras/R-REVIEW.md` | n/a | passou: a regra fala de rodada única com o devops e do hook `parecer`, nada sobre quantidade de pushes |
| E1: `forge-check pr` não exige parecer no remoto | CT-03: ler `bin/forge-check` (`parecer_commitado`, `git show HEAD:<rel>`) | n/a | passou: lê o commit local, a regra vale para os três |
| Fragmento de changelog | CT-04: `changelog.d/tl-1.md` existe, seção `### Alterado` | n/a | passou |
| Toda mudança passa pelos testes e pela validação | CT-05: suíte e `scripts/validar-plugin.sh` | suíte não vazia (865 testes) | passou |

## Cenários e resultado real
- `python3 -m unittest discover -s tests -q`: Ran 865 tests in 201.179s, OK.
- `scripts/validar-plugin.sh`: Validation passed (manifesto e plugin). Os negados de rede (api.anthropic.com, datadog) são do sandbox e não afetam o resultado.
- Sem teste novo de regra em código: a mudança é só texto de agente; nenhum teste a protege, e não há mutação aplicável (sem ferramenta de stack).

## Observações (fora do escopo, não bloqueiam)
- `agents/devops-engineer.md:18` ainda diz "no mesmo push da entrega" sem "uma vez por rodada"; já registrado no pedido como cartão DEVOPS-PUSH-PARECER (decisão do Jarvis). Não é contradição: a frase é compatível com a regra nova.
