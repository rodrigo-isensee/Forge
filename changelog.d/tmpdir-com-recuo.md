### Corrigido
- O texto que manda criar ou usar pasta temporária (`briefs-e-conferencia`, `esperar-estado`, `agile-coach`) usa `${TMPDIR:-/tmp}` no lugar de `$TMPDIR`: com `TMPDIR` vazio no ambiente do agente, o caminho caía na raiz do sistema (E3 TMPDIR-DO-AGENTE, versao-067).
