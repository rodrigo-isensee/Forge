---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: abfccb7e24fb7ef005e53080d81d60c3896234cc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.40, revalidação por delta da volta 5 do curinga na origem de link vinda de rev-parse)

Delta lido: `b283521c..abfccb7e` (3 commits: 15dfdc3a, f84306a6, abfccb7e), numa worktree destacada do revisor no head abfccb7e. Instância que não fez a correção. A volta 5 fecha os achados do parecer da volta 4 (E20.36, commit 9bd83404, reprovado).

## Achados

## Achados da volta 4
- A1 da volta 4 (bloqueante), fechado: `hooks/conformidade.py:1097` recusa o resto com `[` que não seja colchete só de dígitos e hífen; `[^x]`, `[[:alpha:]]`, `[[=c=]]` e `[[.c.]]` têm fixture que recusa.
- A2 da volta 4 (recomendado), fechado: `docs/engineering/achados-recorrentes.md:27` grava o AR-13 no formato do arquivo.

## Sondas
- S1 · shopt -s extglob (nova linha) ln "$(git rev-parse --git-dir)"/@(config) h · espera: código 2 · obtido: código 2 (pela regra genérica `.git/`, falha fechada)
- S2 · shopt -s extglob (nova linha) ln "$(git rev-parse --git-dir)"/?(config) h · espera: código 2 · obtido: código 2 (regra genérica)
- S3 · shopt -s extglob (nova linha) cp -s "$(git rev-parse --git-dir)"/+(hooks)/pre-push h · espera: código 2 · obtido: código 2 (regra genérica)
- S4 · ln "$(git rev-parse --git-dir)"/[0-9-]onfig h · espera: código 0 (o bash não expande para nome protegido) · obtido: código 0

## Parecer
Aprovado. Fecha os dois achados da volta 4 e o delta não abre nada.

A exceção do colchete de dígitos é segura. `\[[0-9-]+\]` só tira colchete sem `!`, `^`, `]` nem `[:`, que o bash e o `fnmatch` leem igual (dígito, faixa de dígitos e hífen literal; faixa invertida casa nada nos dois). Nenhum nome protegido (`config`, `hooks/`, `forge/`) tem dígito no lugar do colchete. O hífen de `pre-push` cabe em `[-]`, mas o prefixo `hooks` já cai na regra específica antes. Colchete aninhado (`[[0-9]onfig`) deixa um `[` depois da troca e recusa. O desvio do brief (abrir a exceção pelo par `forge-suite-Xverde.[0-9]` do `test_conformidade_verde`) é aceitável: o verde segue passando e a fixture `gitcomum-v3-colchete-digito-letra-bloqueia` prova que o dígito não libera a letra junto.

`sem_caixa` troca só as letras (`[^\W\d_]`) por `[xX]`, o que cobre o `nocaseglob`. Os dígitos e o colchete que sobra ficam como estão. `filter(None, …)` sem o `is_dir()` mantém o `.git` da raiz e o diretório comum: o glob sobre um caminho inexistente devolve lista vazia, e `topo and …` evita o erro sem cópia de git (fixture `fora-do-git-libera`). A spec `-6` declara G34 a G39, um mutante por linha de guarda mudada. A G38 (`${d}`) cobre a linha de `valores`, que tem fixture nova (`variavel-chaves-libera`). O índice das fixtures foi regenerado (2420) e o fragmento do changelog é desta branch.

As sondas S1 a S3 mostram que o extglob, que o glob do Python também não lê, não abre porta: a origem com `(` não chega a se liberar. Elas foram fixtures temporárias, apagadas depois.

O parecer antigo da mesma brecha (`docs/reviews/v046-conformidade-caminho-git.md`) já está aprovado na branch e fica como está, como o brief manda.

Testes rodados um por vez (R-TETO, só os do brief), da raiz da worktree: `python3 -m unittest tests.test_hook_git_comum` · 1 teste, OK, 8,6 s; `python3 -m unittest tests.test_conformidade_verde` · 11 testes, OK, 19,2 s.
