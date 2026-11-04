### Alterado
- Hook parecer: as recusas de corpo de heredoc que a chamada pode rodar nomeiam o Write ou Edit no contorno, e o corpo que o hook não lê (como um # que ele não prova ser comentário, num .md gravado com git commit na mesma chamada) recusa com essa causa, sem mandar usar <<'FIM', que já está na linha; nada passa a ser liberado (PARECER-HOOK-DICA-EDIT)

### Adicionado
- Testes do hook parecer: na branch de trabalho com parecer reprovado, git fetch, merge --ff-only e pull --ff-only do autor da volta passam, e na develop a mesma branch segue barrada (corpus atualiza-*, PARECER-BARRA-FETCH; o hook já liberava, o cartão fecha com a prova)
