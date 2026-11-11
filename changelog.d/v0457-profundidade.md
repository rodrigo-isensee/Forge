### Corrigido
- hook conformidade: o comando acima do teto de aninhamento (PROFUNDIDADE, 3 níveis de bash -c, eval, $( entre aspas, crase ou heredoc) é recusado em toda sessão, também fora de projeto e na sessão do Forge; antes passava sem ser lido, e gravar a prova da suíte dentro de 4 níveis de bash -c passava (PROFUNDIDADE-BASH-C, v0457 E17.1)
