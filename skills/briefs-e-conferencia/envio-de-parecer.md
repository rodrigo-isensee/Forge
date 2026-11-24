# Envio de parecer: um passo por chamada

Receita dos portões (review, QA, segurança, devops) para gravar e enviar o parecer sem recusa falsa dos hooks nem volta pela neutralidade: Write ou Edit, uma ação por chamada, `git pull --rebase origin <branch>` e nenhum ID curto de mutante. É receita, não regra: a validade do parecer, presa ao domínio, segue no `R-REVIEW`. O Jarvis avisa dela no brief que manda escrever parecer; os agentes de portão a citam pelo caminho.

A pasta do portão: `docs/reviews/` (review), `docs/qa/` (QA), `docs/security/` (segurança), `docs/devops/` (devops).

1. **Escreva o parecer pelo Write ou pelo Edit**, nunca por `cat`, `echo` ou heredoc no Bash, a partir do `_modelo.md` da pasta do portão (no Forge, em `templates/projeto/`); `forge-check docs` valida o frontmatter. Achado até 300 caracteres; regra se cita pelo ID, não copiada.
2. **Uma ação por chamada do Bash**, com o caminho e a branch literais:
   - `git add docs/<pasta do portão>/<pedido>.md` (o seu caminho, explícito; nada de `git add .` nem `-A`);
   - `git commit -m "docs(<portão>): parecer de <pedido>" -m "<linhas de atribuição>"` (vários `-m`, sem heredoc; `<portão>` é `review`, `qa`, `seguranca` ou `devops`);
   - `git push origin <branch>`.
   Na chamada de ação crítica (commit, push, pull), nada de heredoc, `$?`, `$VAR`, `${...}` nem `&&` encadeando outra ação: os hooks leem o comando inteiro e recusam o que não sabem resolver.
3. **Envio recusado por estar atrás do remoto:** numa chamada, `git pull --rebase origin <branch>`; noutra, o `git push origin <branch>` de novo. As cópias de trabalho não têm upstream: sem `origin <branch>`, o pull falha.
4. **Sem ID curto de mutante no parecer.** Cite o mutante pela guarda (`<arquivo>:<linha>` e o que ela barra) ou pelo arquivo de `tests/mutantes/`; o ID curto do JSON, solto no texto, cai na neutralidade (`R-NEUTRO`) e devolve o parecer.
