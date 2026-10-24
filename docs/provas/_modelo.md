# Provas do pedido <ID>

Propósito: provas reexecutáveis do pedido, uma por linha; formato, lista permitida e recusas em docs/regras/R-PROVA.md ("Arquivo de provas na branch"). Copie para docs/provas/<pedido>.md e troque as linhas abaixo. Público: autor da entrega, tech-lead e QA. Revisão: <data>.

## Provas

- PQ-1 (cmd): `python3 -m unittest tests.test_exemplo` · espera: rc=0
- PQ-2 (cmd): `git rev-parse --verify HEAD` · espera: rc=0 e linhas=1
