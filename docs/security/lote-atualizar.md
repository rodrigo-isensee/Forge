---
tipo: revisao-seguranca
contrato: 1
pedido: lote-atualizar
branch: melhoria/lote-atualizar
commit: f1cf78c075ff3f24400ca680944d6dae76d5b493
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: lote-atualizar

Diff `db55859...f1cf78c` (5 commits; `bin/forge-atualizar`, `tests/test_atualizar.py`, `changelog.d/lote-atualizar.md`). Veredito: aprovado. A correção do F4-A9 fecha o defeito (a branch com o merge e a mensagem "Desfiz" ao mesmo tempo); nenhum caminho leva a branch do projeto a um commit errado nem sobrescreve trabalho não commitado.

## Gatilhos
`controles do Forge`: `bin/forge-atualizar` move a branch `forge/upgrade-<nova>` do projeto (`desfazer_mesclagem`, `bin/forge-atualizar:126-131`). O teste do `__pycache__` (`tests/test_atualizar.py:127`) só filtra a cópia de fixture: sem superfície de ataque.

## Achados

## Detalhe dos achados
Conferido por leitura e por sonda local (repositórios e `HOME` em `$TMPDIR/security-engineer-loteatualizar/`, `integrar_develop` carregado em processo, `trazidos` forçado a falhar depois do commit da resolução), mais `tests.test_atualizar` (74 OK) sobre `f1cf78c`:

- **Commit de destino.** `antes` é o `HEAD` lido em `bin/forge-atualizar:110`, logo antes do `merge`; o commit feito em `:151` tem `antes` como primeiro pai, então o `checkout -B` em `:131` só tira o merge. Sem `MERGE_HEAD` e com `HEAD == antes` (por exemplo, a exceção vem depois do `merge --abort` em `:155`), a função não faz nada. Não há caminho para um commit que não seja ancestral.
- **Branch trocada e HEAD destacado.** O script não troca de branch entre `:106` e `:131`. Na sonda, com o HEAD destacado no meio, o `checkout -B` volta para `forge/upgrade-9.9.0` em `antes`, que é o estado certo. Só uma ação feita em paralelo, em outro terminal, faria a branch ter commits novos nesse intervalo; o `-B` os tiraria da branch, mas eles ficam no reflog. Sem atacante nem ganho: informativo.
- **Trabalho não commitado.** O `checkout` roda sem `-f`. Na sonda, uma alteração local em arquivo que não muda foi mantida (`M a.txt`), um arquivo não rastreado também (`?? solto.txt`), e uma alteração em arquivo que o merge trouxe fez o git recusar o checkout, sem perda (`novo.txt` com o conteúdo do dono). Nada é sobrescrito.
- **Mensagem "Desfiz a mesclagem" (recomendação, severidade baixa).** `desfazer_mesclagem` (`bin/forge-atualizar:128-131`) ignora o código de saída do `merge --abort` e do `checkout -B`, e a mensagem em `:122` sai sempre. Na sonda, com o checkout recusado (alteração do dono em arquivo trazido) ou com um `.git/index.lock` presente, a mensagem diz "Desfiz a mesclagem" e a branch continua com o merge. Para isso acontecer, alguém precisa mexer no projeto em paralelo, nos milissegundos entre o commit e a exceção. O conteúdo que fica é o merge que o próprio dono confirmou com "s", então ninguém ganha nada com isso. Não bloqueia. Correção mínima: `desfazer_mesclagem` devolve se voltou (código 0 e `rev-parse HEAD == antes`), e `:122` escolhe a mensagem com base nisso, por exemplo "Não consegui desfazer: a branch do upgrade ficou com a mesclagem; confira com `git log`". Esforço P. Dono: `tech-lead`, num cartão para a 0.30.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura, sonda local em `$TMPDIR` e `python3 -m unittest tests.test_atualizar`. Faltaram no PATH: `gitleaks` e `semgrep` (lacuna registrada). O diff não tem credenciais, rede nem dependência nova.
