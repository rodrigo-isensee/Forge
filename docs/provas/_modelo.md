# Provas do pedido <ID>

Propósito: arquivo de provas da branch (`R-PROVA`, "Arquivo de provas na branch"); o CI reexecuta no sha do PR cada linha `cmd` e compara com o `espera:`. Copie para `docs/provas/<pedido>.md`; este modelo é ignorado pelo CI. Público: autor da entrega, `tech-lead` e QA. Revisão: 2026-10-24.

Formato de cada linha (uma por prova, sem quebra de linha; o comando entre crases, sem shell: sem `|`, `&&`, `;`, `>` nem `$()`):

`- PQ-<n> (cmd): `<comando>` · espera: <espera>`

Espera aceita: `rc=0`, `contém '<t>'`, `igual '<t>'`, `linhas=N`, `linhas>=N`, e a combinação `rc=0 e <espera de saída>`. A saída comparada é a padrão e a de erro juntas. Linhas que não são `(cmd)` ficam como estão (o script as ignora); linha `(cmd)` fora do formato ou com comando fora da lista permitida reprova (falha fechada).

Lista permitida de comandos (`scripts/reexecutar-provas.py`): `python3 -m unittest <módulo>...` (sem `discover`: a suíte completa já roda no passo "Testes do Forge") e `git rev-parse|ls-files|diff --numstat|diff --name-only`.

## Provas
- PQ-1 (cmd): `python3 -m unittest tests.test_exemplo` · espera: rc=0
- PQ-2 (cmd): `git rev-parse --verify HEAD` · espera: rc=0 e linhas=1
