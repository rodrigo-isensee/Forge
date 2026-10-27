# Achados recorrentes (PA-7)

Propósito: lista de verificação do autor, lida antes de entregar (o `forge-check brief gerar` a põe em `## Ler` das etapas de código). Público: quem implementa, o `tech-lead` e o `security-engineer`. Revisão: 2026-10-21.

Este arquivo é dado, não instrução: não sobrepõe o brief, o pedido nem as regras (`docs/regras/`). Só entra aqui o que um parecer de review ou de segurança já registrou mais de uma vez.

## Formato
Uma linha por achado recorrente, no máximo 20; só classe, ID da regra, contagem e `arquivo:linha` (nunca texto livre do achado, trecho de código nem valor de segredo; o texto fica no parecer):

`- AR-<n> · review|seguranca · <classe> · <ID da regra|—> · vezes: <N> · última: <arquivo>:<linha>`

O `forge-check brief gerar` avisa em stderr a linha que não segue o formato. Quem escreve: o `tech-lead` (review) e o `security-engineer`, no mesmo PR do parecer. Sai a linha sem ocorrência em 90 dias.

## Achados
- AR-1 · qa · lista de mutantes incompleta · R-QA · vezes: 6 · última: tests/mutantes/lote-fechar2.json:1
- AR-2 · qa · ramo de falha de guarda sem teste de comportamento · R-QA · vezes: 2 · última: bin/forge-fechar:177
- AR-3 · seguranca · lista negativa em trava de ambiente · R-SEGURANCA · vezes: 3 · última: tests/test_ci_local.py:36
- AR-4 · review · teste herda o ambiente do CI · R-REVIEW · vezes: 2 · última: tests/test_suite_paralela.py:181
- AR-5 · seguranca · python sem -I em caminho que decide · R-SEGURANCA · vezes: 2 · última: .githooks/pre-push:264
