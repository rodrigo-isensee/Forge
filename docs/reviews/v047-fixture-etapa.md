---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-etapa
commit: 8bbbc3c173926a4b3b401afa181e9f886c43ed25
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (E2.96, classe T, item E2.75 FIXTURE-ETAPA-FORA-VOCABULARIO)

Diff `bf475209..8bbbc3c1`: `tests/test_selo_e_entrega.py` +12 e o fragmento `changelog.d/v047-fixture-etapa.md`. 12 linhas de teste, dentro da orientação de tamanho (M14). Sem guarda de código mudada (só teste), sem mutante declarado exigido.

## Achados
- A1 (recomendado) tests/test_selo_e_entrega.py:721 · a trava cobre só o dict ETAPA; as chamadas com etapa literal (791, 792, 906, 1000, 1008) escapam. Conferir em selar_portao que a etapa está em set(fc.ETAPA_DO_PORTAO.values()) cobriria todos os chamadores numa linha.

## Sondas

## Parecer
Aprovado. A trava vale o PR: o defeito (fixture com `Etapa:` fora do vocabulário mascarando a regressão A4 da E23.36) já foi corrigido na base (#517), e o teste novo impede a volta pelos dois lados por custo quase nulo (12 linhas, roda em milissegundos).

Teste novo rodado (`python3 -I tests/test_selo_e_entrega.py VocabularioDaEtapaDoPortao`): OK no head. Mutantes rodados numa cópia, todos mortos:
- fixture `"devops": "devops"` (a volta do defeito): FAILED (failures=1);
- fixture sem a pasta `security`: FAILED (failures=1), a igualdade de conjuntos funciona como mínimo de itens (checklist 11);
- produção `ETAPA_DO_PORTAO["revisao-devops"] = "devops"`: FAILED (failures=1), a trava também pega deriva do vocabulário.

Suíte inteira: fica no CI do PR (brief sem PR nesta etapa); não rerrodada aqui. Commit em Conventional Commits, mensagem clara. `docs/engineering/achados-recorrentes.md`: nenhuma classe ligada a este diff.
