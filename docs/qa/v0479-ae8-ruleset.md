---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae8-ruleset
commit: c2f75cacdf29be4eea6ffb8bd96a263f89399021
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E58.5 (AE8.1, ruleset sem bypass)

Diff contra a base 5ccac0bf: só documentação (`docs/protecao-de-branch.md`, o modelo `templates/projeto/docs/engineering/protecao-de-branch.md` e o fragmento de changelog). Sem código de controle, então sem mutantes nem vermelho-antes-do-verde (nenhum teste novo).

## Achados
- A1 (recomendado) docs/protecao-de-branch.md:66 · "mais de 4 h, em dois episódios" (também no modelo) não tem decisão do dono localizável em `## Decisões` do pedido; registrar a origem do limite ou marcá-lo como proposta.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E58.2: passo a passo para tirar o bypass | leitura contra o diff; `test_doutor_protecao_gh` (15 testes) | lista de bypass vazia no `portoes`; Always não vira "só PR" | passou |
| Conferência só de leitura (`bypass_actors`, `enforcement`, `current_user_can_bypass`) | leitura; campo ausente = "não verificado" | campo ausente | passou |
| Saída da develop vermelha pela BP2, sem bypass | referência `ritmo-e-corte.md` linha 23 existe ("Conserto da integração vermelha", D2) | n/a | passou |
| Modelo de projeto neutro (`R-NEUTRO`) | `test_modelos_projeto` (20), `test_textos_034` (9), `test_qa_doutor_f8` (7) | termos de projeto | passou |

## Cenários e resultado real
Testes dos arquivos tocados, com `python3 -I -m unittest discover -s tests -p <arquivo>`: os quatro módulos acima verdes (51 testes, 0 falha). Sem suíte local. Os nomes citados (`portoes`, `main-do-dono`) conferem com as seções existentes do mesmo arquivo.

## Revalidação (volta única, head c2f75cac)
`forge-check parecer delta` lista só docs (`protecao-de-branch.md`, o modelo e o fragmento de changelog); sem código de controle, sem mutantes nem teste novo. Conferido: a leitura passa a achar os rulesets por `rules/branches/<branch>` (GET, só leitura), confere `exclude` além de `include`, separa o quadro de 15/11 da data dos merges e cita `checks-obrigatorios-develop-main`; o modelo de projeto continua neutro. Os mesmos quatro módulos, rodados de novo com `python3 -I -m unittest discover -s tests -p <arquivo>`: 51 testes, 0 falha. Sem suíte local. O A1 anterior (limite de 4 h sem decisão localizável) segue em aberto como recomendado e vira cartão depois do merge.
