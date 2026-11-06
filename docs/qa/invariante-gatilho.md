---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/invariante-gatilho
commit: 5fffee68faa49810653da9dceb8c5c8dd69aaf44
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (INVARIANTE-GATILHO)

Links: não há `docs/ux` neste repositório; o critério vem do cartão (`docs/propostas/backlog/versao-0.34-triagem.md`) e do pedido de QA. Código testado: 5fffee68faa49810653da9dceb8c5c8dd69aaf44 (um commit sobre b45e40a). Entrega só de texto: escopo incremental, suíte completa não rodada. Review lido só pelo número do parecer; segurança não é deste parecer.

## Achados
- Nenhum.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1: o modelo de pedido nasce com a etapa do security-engineer, inclusive para invariante novo em `tests/config.json` | tests.test_invariante_gatilho.InvarianteGatilho.test_modelo_de_pedido_nasce_com_a_etapa_de_seguranca_para_invariante_novo | exatamente uma linha `E1.3 (security-engineer)` (`assertEqual` 1, nem zero nem duas) | passou; cai na base |

## Execução
- `python3 -I -m unittest discover -s tests -p test_invariante_gatilho.py`: 1 OK.
- `test_modelos_projeto` (6), `test_clareza` (7) e `test_erros_no_brief` (42), que leem os modelos: OK.
- Leitura: a linha usa o formato `E1.x (papel): texto` do modelo e diz como apagá-la quando não há gatilho ("sem gatilho de segurança" no plano). Entrega o cartão.
- `python3 -I tests/neutralidade.py` no head: rc 0, sem saída.
- Vermelho antes do verde: arquivos de texto trazidos a b45e40a na worktree qa-invariante-gatilho (`git checkout b45e40a -- <arquivos>`), teste rodado, árvore restaurada ao head e limpa. Falha observada na base, abaixo; no head, o teste passa.
- Base (`templates/projeto/docs/pedidos/_modelo.md` em b45e40a): `FAILED (failures=1)`, AssertionError: 0 != 1 (nenhuma linha E1.3 do security-engineer).
- Bugs abertos: nenhum.
