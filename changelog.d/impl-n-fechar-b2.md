### Alterado
- forge-fechar (N-FECHAR-b, B1 a B5): a parada do passo 4 imprime o comando para ler o log do check e diz se pedir o rótulo ajuda; a espera do rótulo vale para a execução da Catraca vista antes dele (a nova reprovada para na hora, a velha cancelada espera a nova, sem reexecutar nada); o parecer é conferido no sha lido antes do passo 1 (forge-check pr --ref <sha>), relido e igual ao remoto; as leituras do PR vão pelo número (lido do aberto ou da URL do create) e MERGED só vale com o head conferido, a base alvo e commit de merge; PR de fork para; o merge segue por nome de branch com --match-head-commit

### Corrigido
- forge-fechar: tmp2b e dorme_pid nascem vazios no topo do script; valor herdado do ambiente não vira alvo do rm -rf nem do kill do fim (R2 do parecer de segurança do lote a)
