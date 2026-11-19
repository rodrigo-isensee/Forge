---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-lote
commit: 97e0b6e7d860dde35ae33b39c0265ae3f2fdd7a8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478-fechar-lote

Escopo: diff `82bb9e57..97e0b6e7` (bin/forge-fechar, testes, mutantes, fragmento do changelog). O `forge-fechar` é controle: a limpeza do passo 7 apaga pastas e branches, o 1c decide se a árvore entra na base, e o `--dry-run` agora roda o 1c.

## Gatilhos
Gatilhos: controle de merge e de limpeza (forge-fechar: remoção de worktree, clone e branch local e remota; passo 1c; --dry-run)

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido:

- Limpeza no clone da própria branch (`bin/forge-fechar:646-650`): a árvore de `$ref` só vira "cópia própria" quando o `.git` dela, resolvido com `pwd -P`, é a pasta comum do repositório (`git rev-parse --git-common-dir`). Worktree ligada tem `.git` arquivo em outro caminho e não casa, então continua no caminho antigo. A mudança só tira ações destrutivas: sem `git worktree remove` (`:650`), sem `git branch -D` (`:703`) e sem apagar a remota (`:749`, `:778`). Nada novo é apagado.
- Comandos pendentes impressos (`:612-630`): não são executados. Caminho, pedido e branch passam por `printf '%q'`. O `git branch -D` sugerido (`:627`) só aparece quando `sem_merge=0`, ou seja, quando o sha local já foi conferido como mesclado (`:641`). Com commit sem merge, só a leitura sai (`:619-621`). O clone em `~/.forge-contrib/wt` continua saindo só pelo `limpar_clones` (`:574`) de outra cópia, que segue exigindo clone limpo, sem stash, com tudo na origem e o sha mesclado.
- `-h|--help` (`:103`): o `sed` lê só o próprio script e sai com 0 antes de qualquer log ou ação.
- 1c com busca sempre (`:945-956`): o refspec fixo `+refs/heads/homolog:refs/remotes/origin/homolog` só atualiza a ref de rastreio, sem branch local, checkout nem merge. A origem é o servidor, que vale mais que a ref local velha. Se a busca falha, a decisão volta a ser a de antes (a ref local), agora com aviso e o sha dela. Não abre caminho novo.
- `--dry-run` executa o 1c (`:1221-1228`, `:959-965`): o script vem do diretório do próprio plugin (`:301`) e não da branch revisada. `FORGE_PROMOVER` só o troca com `FORGE_FECHAR_TESTE=1` (`:198-201`). O `--conferir-ref` só lê, sem busca e sem gh, e tem prazo de 300 s. Sem a branch local, ele não roda (`:1227`). O cabeçalho (`:46-47`) e a linha impressa avisam que o `--dry-run` deixou de ser "nada executa".

Testes novos rodados no clone: 26 testes de `tests.test_forge_fechar` e `tests.test_fechar` filtrados por clone, copia, help e 1c, todos OK (26,9 s). Entre eles estão os de clone que não se apaga, clone com commit sem merge, cópia principal fora de wt, `--help`, 1c com homolog velha e com busca que falha, e o dry-run que recusa. A suíte inteira fica no CI do PR: a branch ainda não tem PR nem execução de CI, e o portão do merge é o CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Não estão no PATH (não instalados, `R-CUSTO`): o linter de shell e o varredor de segredos. O linter roda no CI.
