---
tipo: qa
contrato: 1
pedido: modelos-no-forge
branch: melhoria/modelos-no-forge
commit: d7052be4d5b18552f527023029af762bb2cb58cf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: modelos-no-forge

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: agente que cita `_modelo.md` ausente na raiz traz a cláusula do template | `test_modelos_citados` (cláusula removida do tech-lead em clone: 2 falhas) | cláusula ausente | passou |
| E2: modelo de segurança da raiz igual ao do template | `test_modelo_de_seguranca_da_raiz_igual_ao_do_template` (template com linha extra: falha) | byte a byte | passou |
| `forge-testes` dirigido alcança o teste novo | `bin/forge-testes --listar --base HEAD` com `agents/tech-lead.md` alterado inclui `test_modelos_citados` | mapa CONTEUDO | passou |
| Suíte e plugin | `unittest discover -s tests -q`: 1294 testes OK (394 s); `scripts/validar-plugin.sh`: Validation passed | n/a | passou |

## Cenários e resultado real
- Sondas só em `$TMPDIR` (clone e `git archive` do HEAD), sem rede; a cópia da worktree não foi alterada.
- Vermelho: sem a cláusula, `test_modelo_citado_existe_na_raiz_ou_no_template` e `test_tech_lead_e_qa_trazem_a_clausula` falham; com o template alterado, o teste de igualdade falha; restaurados, 3 OK.
- Dirigido: com `--base origin/develop` a lista vira suíte completa (o diff inclui `bin/forge-testes`, que altera o mapa); com `--base HEAD` lista o `test_modelos_citados`.
- Mutação: sem ferramenta da stack; as sondas acima fazem o papel de mutantes e todos foram mortos.
- Mensagens `deny network-outbound` no sandbox são tentativas de rede do `claude plugin validate`; a validação passou.
