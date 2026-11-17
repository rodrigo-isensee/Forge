### Adicionado
- SIEG-G4: regra única de idioma ao dono na skill falar-com-o-dono (toda-mensagem.md): toda mensagem, inclusive as notas entre chamadas de ferramenta e as que vêm depois de compactação, sai no idioma do dono (`idioma_do_dono`; sem a chave, português); a medida é o `outro_idioma` do hook meta.
- JARVIS-SO-PORTUGUES: eval do jarvis em tests/evals/test_erros_por_papel.py (MensagemEmOutroIdioma): mensagem final ao dono em inglês é acusada pela medida `outro_idioma`; a nota entre chamadas de ferramenta, que o hook meta ainda não mede, fica como backlog (`expectedFailure`).
