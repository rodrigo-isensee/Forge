### Corrigido
- hook de conformidade: o dono de cada heredoc é lido em duas partes (o texto de fora uma vez), em tempo linear, e a chamada com corpo de heredoc ainda por conferir quando o prazo vence é recusada (antes liberada, 128 s com 3000 donos distintos); a recusa por regra não muda (HEREDOC-DONOS)
