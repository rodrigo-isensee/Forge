---
tipo: qa
contrato: 1
pedido: release-0.20.0
branch: melhoria/release-0.20.0
commit: b52c9451432eaa29f6d76590bb9d4b722a5d3464
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-17
---
# QA - release 0.20.0

Sem UX nem API. Diff `ecf553d...b52c945` (6 arquivos, 9 inserções, 8 remoções). O commit seguinte (65c7fbe) só traz o parecer de review, também `aprovado` com `commit: b52c9451432eaa29f6d76590bb9d4b722a5d3464`. Não escrevi o diff.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| O-1 | Versão 0.20.0 nos manifestos | `git diff ecf553d...b52c945 -- .claude-plugin dev` e `grep '"version"'` nos dois plugin.json | as duas versões iguais | passou: só a linha da versão mudou, 0.19.0 -> 0.20.0 |
| O-2 | CHANGELOG.md com `[0.20.0]` e os três itens, texto igual aos fragmentos | diff do CHANGELOG contra `git show ecf553d:changelog.d/*.md` | `[Não publicado]` vazio | passou: AQ, CONF-TABELA-ROTULO e S-15 idênticos |
| O-3 | `changelog.d/` vazio | `ls -A changelog.d` | pasta vazia | passou |
| O-4 | Nada além disso | `git diff --stat`: 2 plugin.json, CHANGELOG, 3 fragmentos apagados | n/a | passou |
| O-5 | Suíte completa verde | `python3 -m unittest discover -s tests` | n/a | passou: 785 testes, OK, 125 s (nenhuma outra suíte rodando) |
| O-6 | Plugin válido | `scripts/validar-plugin.sh` | n/a | passou (marketplace, forge e forge-dev) |

Vermelho antes do verde e mutação: não se aplicam (sem teste novo nem código).
Observação: o sandbox negou rede para api.anthropic.com e datadog durante os comandos; sem efeito nos resultados.
