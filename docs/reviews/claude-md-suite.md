---
tipo: review
contrato: 1
pedido: claude-md-suite
branch: melhoria/claude-md-suite
commit: f4c287477103000a24f99269925240edd0f1f819
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: claude-md-suite

## Achados

## Parecer
Aprovado. Delta lido: `git diff 8c07b44..f4c2874`, um commit (`docs(claude-md): ...`) que troca duas linhas do `.claude/CLAUDE.md` e acrescenta o fragmento `changelog.d/claude-md-suite.md`.

- Linhas 16 e 34 do `.claude/CLAUDE.md` (na numeração do arquivo do diff: 16 na lista de regras, 34 no bloco "Como testar localmente"): o comando `python3 -m unittest discover -s tests -v` virou `.githooks/pre-push --suite`; o resto de cada linha ficou igual. Escopo do pedido cumprido, nada além.
- Conferido na `origin/develop`: `.githooks/pre-push` tem o modo `--suite` (só com exatamente esse argumento, linha 104); ele roda `scripts/suite-paralela.py` e, sem esse script, `python3 -m unittest discover -s tests -q`, ou seja, a suíte inteira, sem refs e sem prova anotada. O comando citado existe e faz o que o texto diz.
- Fragmento de changelog presente e no formato (`### Alterado`); a versão não sobe aqui (ADR 0006).
- `R-NEUTRO`, `R-CUSTO` e regras invioláveis: preservadas; nenhuma invariante afrouxada.
- M14: cumpre. Linhas contadas de código e teste: 0 (as alterações são `.md` e fragmento de changelog, fora da contagem); `git diff --numstat origin/develop...HEAD` mostra 2+2 em `.claude/CLAUDE.md` e 2 no fragmento. Um comportamento só.
- Sem gatilho de segurança (texto de documentação). Sem pendência de regra "ferramenta" sem comando.
