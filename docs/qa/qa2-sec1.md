---
tipo: qa
contrato: 1
pedido: qa2-sec1
branch: melhoria/qa2-sec1
commit: 1093bc1036069b2d5757750b6ad374da75e7c64e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - plano antecipado e testes de abuso durante a implementação (QA2-SEC1)

Links: `docs/pedidos/qa2-sec1.md` (E1, E2, E3), `docs/reviews/qa2-sec1.md` (aprovado, c734276, que só acrescenta o parecer de review sobre 1093bc1). Não há UX nem API; as obrigações são E1, E2 e E3 do pedido, `R-REVIEW` e `R-QA`. Offline (`R-CUSTO`). O conteúdo testado (agents, skills, tests/config.json, changelog.d) é idêntico em 1093bc1 e no HEAD c734276.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Suíte `python3 -m unittest discover -s tests -q` na raiz da worktree | n/a | Passou: 876 testes, OK (170 s); sem falha intermitente, então não há teste instável a registrar |
| CT-02 | `scripts/validar-plugin.sh` | n/a | Passou: marketplace e plugin `Validation passed` (a validação tenta api.anthropic.com e datadog, o sandbox nega; não afeta o resultado) |
| CT-03 | E1: textos de `agents/qa-engineer.md` (passo 2 e Limites) e `skills/qa-testing/SKILL.md` ("Plano antecipado") dizem a mesma regra: plano nasce da especificação sem ler o código, parecer só no commit final depois do review | ordem review, depois QA | Passou: sem contradição com `R-REVIEW` ("todo cartão passa por Code review antes da coluna QA; nenhuma é pulada") nem `R-QA` (parecer em `docs/qa/<pedido>.md`, por entrega); só a escrita do plano e dos testes sai do caminho crítico |
| CT-04 | E2: `agents/security-engineer.md` (item 5), `skills/cyber-security/SKILL.md` (item 5) e `qa-testing` descrevem os casos de abuso igual: com gatilho (`R-SEGURANCA`) o modelo de ameaças os lista (entrada, caminho, resultado esperado), o QA escreve o teste em arquivo seu na implementação, o parecer de segurança segue sobre o commit final, o QA não declara "seguro"; sem gatilho, não se aplica | sem gatilho | Passou: os quatro textos concordam, e a skill `qa-testing` remete ao formato da `cyber-security` |
| CT-05 | E3: `changelog.d/qa2-sec1.md` existe, tipo `### Alterado`, nome igual à branch sem prefixo | n/a | Passou (cobertura do CI de changelog dentro da suíte de 876) |
| CT-06 | 6 invariantes novos em `tests/config.json` falham se o trecho sair | trecho removido | Passou, ver vermelho antes do verde abaixo |
| CT-07 | Guarda contra suíte vazia do teste de invariantes (`minimo(..., 23, ...)` arquivos e `95` trechos) | pasta/lista vazia | Passou: config tem 45 arquivos e 363 trechos, acima dos mínimos |

## Vermelho antes do verde
Cópia limpa de HEAD em `$TMPDIR/vermelho` (`git archive HEAD | tar -x`); em cada rodada apaguei uma frase (trocada por `XXX`) e rodei `python3 -m unittest tests.test_forge.RegrasInviolaveis.test_trechos_obrigatorios`:

| Trecho removido | Arquivo | Resultado |
|---|---|---|
| `sem ler o código` | agents/qa-engineer.md | FAIL (rc 1) |
| `testes dos casos de abuso do modelo de ameaças` | agents/qa-engineer.md | FAIL (rc 1) |
| `## Plano antecipado` | skills/qa-testing/SKILL.md | FAIL (rc 1) |
| `conferir o diff contra a lista de CA-n` | skills/qa-testing/SKILL.md | FAIL (rc 1) |
| `só sobre o commit final e depois do review` | skills/qa-testing/SKILL.md | FAIL (rc 1) |
| `lista os **casos de abuso**` | skills/cyber-security/SKILL.md | FAIL (rc 1) |

Com tudo restaurado na cópia: rc 0, OK. Os 6 invariantes são sensíveis ao trecho que protegem. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Observação
O review registrou uma primeira suíte instável (errors=7 sem nomes). Aqui a suíte rodou uma vez, verde, sem repetição; não houve falha a nomear.

## Achados
