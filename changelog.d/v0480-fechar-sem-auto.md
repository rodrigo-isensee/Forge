### Alterado
- forge-fechar: FECHAR-NUNCA-AUTO (decisão do dono de 24/11): o merge exige todo check-run do head concluído e verde, não só os obrigatórios (pendente espera, falha para), e o script se recusa a rodar, também no --dry-run e no --limpar, quando o próprio arquivo difere do bin/forge-fechar da origin/develop; teste varre todo `gh pr merge` de bin/ e scripts/ atrás de --auto (E171.1)
