---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/achado-teto-doc
commit: e0bcb47a7e48d7c825ed139cd2e4f9a801014221
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (ACHADO-TETO-DOC)

Links: não há `docs/ux` neste repositório; o critério vem do cartão (`docs/propostas/backlog/versao-0.34-triagem.md`) e do pedido de QA. Código testado: e0bcb47a7e48d7c825ed139cd2e4f9a801014221 (um commit sobre b45e40a). Entrega só de texto: escopo incremental, suíte completa não rodada. Review lido só pelo número do parecer; segurança não é deste parecer.

## Achados
- A1 (recomendado) agents/tech-lead.md:1 · o cartão cita tech-lead.md e security-engineer.md; a entrega cobre só o security-engineer.md e o changelog declara "parcial", então o cartão segue aberto para o tech-lead.md; não devolve.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1: o security-engineer diz o teto de 300 do achado (cartão, metade security-engineer) | tests.test_achado_teto_doc.AchadoTetoDoc.test_security_engineer_diz_o_teto_de_300_do_achado | frase "até 300 caracteres sem contar o prefixo" no passo 3 do agente | passou; cai na base |
| CA-2: o tech-lead.md diz o teto (cartão, outra metade) | nenhum | n/a | não entregue; declarado parcial (A1) |

## Execução
- `python3 -I -m unittest discover -s tests -p test_achado_teto_doc.py`: 1 OK.
- Leitura: o texto diz uma linha só, até 300 caracteres sem contar o prefixo, que `forge-check docs` e o pre-push barram mais que isso; confere com `bin/forge-check:1471`.
- `python3 -I tests/neutralidade.py` no head: rc 0, sem saída.
- Vermelho antes do verde: arquivos de texto trazidos a b45e40a na worktree qa-achado-teto-doc (`git checkout b45e40a -- <arquivos>`), teste rodado, árvore restaurada ao head e limpa. Falha observada na base, abaixo; no head, o teste passa.
- Base (`agents/security-engineer.md` em b45e40a): `FAILED (failures=1)`, AssertionError: 'até 300 caracteres sem contar o prefixo' not found.
- Bugs abertos: nenhum.
