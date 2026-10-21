---
tipo: qa
contrato: 1
pedido: pergunta-tokens-tempo
branch: melhoria/pergunta-tokens-tempo
commit: df1b1b450f1296c27a50d41fccbe6cbabe499cbe
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - pergunta-tokens-tempo

Sem UX nem API. Código `df1b1b4`; review (`5229ca8`) e segurança (`12d2892`) aprovados, os commits depois do código só trazem esses pareceres. Não escrevi o diff.

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| E1 | Cada opção traz Afrouxa o processo?, tempo e tokens (faixa e média) em skill, `R-DECISAO` e jarvis.md | `tests/test_clareza.py::test_pergunta_traz_afrouxa_tempo_e_tokens_por_opcao` + simulação de 3 perguntas | opção sem um dos campos; mínimo de 2 opções | passou |
| E2 | Vale para Forge e projetos (chega pela release) | texto em skill, regra e agente do plugin; fragmento `changelog.d/pergunta-tokens-tempo.md` | n/a | passou |
| E3 | Teste impede o padrão de sumir | mutação em cópia ($TMPDIR): tirar `Tokens:` da opção C | opção com campo faltando | morto |

## Simulação (três perguntas pelo texto novo)
Perguntas montadas em $TMPDIR pelo item 4 da skill, por `R-DECISAO` e pelo jarvis.md: cada opção ficou com Afrouxa o processo?, Tempo (faixa e média) e Tokens (faixa e média, marca `medido`/`estimado`, ou `não medido` sem número). A saída "decidam vocês" (item 6, jarvis.md, exemplo) e as exceções (custo, acesso, exceção a regra, ato irreversível) não aparecem no diff: seguem iguais.

## Vermelho antes do verde e mutação
- Com a skill da `develop` na cópia: `python3 -m unittest tests.test_clareza -q` falha (`FAILED (failures=1)`).
- Com a skill atual sem `Tokens:` na opção C: falha (`'Tokens:' not found in '> C) ...'`).

## Execução
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`: 1312 testes, 1 erro (`test_atualizar.test_sigint_entre_o_remove_e_o_add_devolve_a_marketplace_original`, IndexError). Arquivo fora do diff; `tests.test_atualizar` sozinho: 57 OK. Instável sob carga/sandbox, não bloqueante; fica para registro.
- `scripts/validar-plugin.sh`: Validation passed.

## Achados
