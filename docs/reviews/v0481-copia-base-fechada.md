---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-base-fechada
commit: 483a5614b7941fc5ff299ea15ef3305f0a85cce2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.34), forge-copia diz o sha em que criou a branch (#896)

Diff revisado: `b224ee09..483a5614` (1 commit). `bin/forge-copia` tem 3 linhas novas: uma na docstring (COPIA-SHA) e duas de código. O resto são `tests/test_forge_copia.py` (3 testes), `tests/mutantes/v0481-copia-base-fechada.json` (M1, M2) e o fragmento `changelog.d/v0481-copia-base-fechada.md`. Não há parecer de review anterior nesta branch. Fica dentro do teto H1.

## Parecer
**Aprovado.** O diff faz o que o E14.33 pede, sem mais. Depois do `switch` que deu certo, o clone imprime em stderr `criei <branch> em <sha> (de <ref>)` e segue para o `instalar`/`return 0` de antes.

Nenhuma guarda mudou. O diff de `bin/` não tem `if`, `||`, `&&`, `return` de erro nem `raise`. As duas linhas novas ficam depois de todas as recusas e da falha fechada do `ponto_de_partida`/`switch` (`rmtree` e sai 1), e essas recusas e falhas não mudaram. Tudo o que barra hoje continua barrando. Se o `rev-parse HEAD` falhar, sai só um sha vazio na mensagem, o código de saída não muda e a cópia já está criada e certa.

A ref dita é a ref de fato usada. `ponto` é `refs/remotes/origin/<branch>` (vira `origin/<branch>`) ou a candidata da base que resolveu (`develop` ou `origin/develop`). Na base, `removeprefix` não faz nada. Com `--revisao`, ela é sempre o head remoto.

Testes:
- `test_branch_do_remoto_com_base_curta_nasce_no_head_dela_e_diz_o_sha`: o clone parte da main com `--base develop`, a branch já está no remoto e o teste confere o HEAD e a mensagem. Cobre o defeito do E14.33.
- `test_clone_pela_base_diz_o_sha_dela`: confere o sha de `origin/develop`.
- `test_base_curta_que_nao_resolve_falha_fechado_sem_clone`: confere rc 1, que o clone não fica e que a mensagem de criação não sai.

Ferramentas, citadas e não refeitas:
- No clone em `483a5614`, `python3 -m unittest tests.test_forge_copia` com ambiente limpo deu 88 testes OK.
- `bin/forge-mutante tests/mutantes/v0481-copia-base-fechada.json` em `483a5614`: M1 morreu (`bin/forge-copia:337`, sha da árvore no lugar do commit) e M2 morreu (`:338`, `a.base` no lugar da ref de fato).
- A suíte inteira roda no CI do PR #896 (linha abaixo). O `bateria (pareceres)` vermelho é a falta dos pareceres de agora, não o código.

Clone de revisão criado com o `bin/forge-copia` da develop (`b224ee09`, `--revisao`). O HEAD dele é `483a5614`, igual a `origin/melhoria/v0481-copia-base-fechada`.

- ci: 483a5614b7941fc5ff299ea15ef3305f0a85cce2 verde
