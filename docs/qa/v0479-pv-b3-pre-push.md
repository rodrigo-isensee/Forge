---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b3-pre-push
commit: 081067f06a28a5bea555e81f69e9cbb35d8c05b2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E57.42 (patch do pre-push, PR-VERDE B3)

Escopo: `docs/engineering/v0479-pv-b3-pre-push.patch` (35 linhas acrescentadas ao `.githooks/pre-push`; o dono aplica). Não aplicado no repositório; conferido em cópia temporária em `$TMPDIR/prova` (clone sem hardlinks, `origin/develop` = 20bbbd8d). Sem suíte local; a bateria é do CI.

## Critério → teste → resultado
| Critério (docs/engineering/v0479-pv-b3-pre-push.md) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Patch aplica limpo sobre a base | `git apply --check`, `git apply`, `bash -n` | n/a | passou (1 arquivo, 35 inserções, sintaxe ok) |
| 1 árvore em dia: rc 0 e resumo `registros rc=` | `.githooks/pre-push` com stdin de envio da ponta | caminho feliz | passou: rc 0, `registros rc=0 em 40 s` |
| 2 módulo novo sem peso recusa | `tests/test_zz_novo.py` sem peso | registro desatualizado | passou: `registro desatualizado: test_zz_novo sem peso`, rc 1 |
| 3 `tests/pesos-d4.json` ilegível: falha fechada | arquivo `{` | saída 2 | passou: "não deu veredito (saída 2)", rc 1 |
| 4 `bin/forge-testes` ausente: aviso e segue | `git rm bin/forge-testes` | ferramenta ausente | passou: aviso, rc 0 |
| 5 prazo estourado recusa | `FORGE_REGISTROS_PRAZO=2` | saída 124 | passou: "saída 124", rc 1 |

## Cenários e resultado real
Os cinco casos do documento deram o resultado dito. Sem rede (sandbox): aviso `não busquei origin/develop`, confere contra a base local e segue, como o documento prevê. Tempo medido de 40 a 49 s, acima da meta de 20 s do desenho (R3); o documento já registra isso e o cartão de corte é do `tech-lead`, não é defeito do patch. Sem `shellcheck` na estação: aviso do hook. Mutação do hook não rodada: o patch não está em vigor, então `bin/forge-mutante` não o alcança; os casos 2 a 5 exercitam as ramificações novas (saída 0, 1, outra, ferramenta ausente).

Método: o primeiro lote dos casos 3 a 5 rodou sem o patch (erro meu ao resetar o commit); foi refeito com o patch commitado, e só a segunda saída vale.
