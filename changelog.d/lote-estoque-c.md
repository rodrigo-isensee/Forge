### Corrigido
- o aviso de versão nova do doutor sai uma vez por versão, não uma vez por dia: o mesmo par versão em uso/versão nova já avisado fica em silêncio nos dias seguintes (o atraso segue provado no cache), uma versão mais nova ou outra versão em uso volta a avisar, e uma falha ao gravar o aviso do relógio não come o de versão (AVISO-VERSAO-UMA-VEZ)
- o aviso de branch sem proteção no GitHub cita o passo a passo da proteção (`docs/engineering/protecao-de-branch.md` no projeto, `docs/protecao-de-branch.md` no clone do Forge) só quando o arquivo existe na raiz; sem ele, cita só a skill `ci-cd` (N-DOUTOR-F8-CAMINHO)
- O `bin/forge-testes <tests/test_x.py>` sem entrada no mapa roda só esse módulo e avisa, em vez de rodar a suíte inteira em silêncio (FORGE-TESTES-SEM-MAPA).

### Adicionado
- O `bin/forge-testes` avisa cedo, em stderr, quando um módulo de teste monta o caminho de um arquivo de `bin/` que o MAPA não leva a ele (MAPA-TESTES-AVISO-CEDO).
- O `bin/forge-testes` aceita `-k PADRAO` (repetível), repassado ao `unittest -k`, para rodar só parte de um módulo grande (TESTES-DO-ITEM-FILTRO).
- Testes do hook parecer: na branch de trabalho com parecer reprovado, git fetch, merge --ff-only e pull --ff-only do autor da volta passam, e na develop a mesma branch segue barrada (corpus atualiza-*, PARECER-BARRA-FETCH; o hook já liberava, o cartão fecha com a prova)
- testes de comportamento das guardas do forge-fechar (pasta do log, check não catraca, MERGED sem commit de merge) e spec de mutantes lote-fechar2-5

### Alterado
- Hook parecer: as recusas de corpo de heredoc que a chamada pode rodar nomeiam o Write ou Edit no contorno, e o corpo que o hook não lê (como um # que ele não prova ser comentário, num .md gravado com git commit na mesma chamada) recusa com essa causa, sem mandar usar <<'FIM', que já está na linha; nada passa a ser liberado (PARECER-HOOK-DICA-EDIT)
