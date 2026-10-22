---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 1b0fb6bf88b73bc81d7a5d4e85164942f119b1b2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: lote-leitura-hook (revalidação 5)

Escopo: a entrega inteira (`git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 1b0fb6bf88b73bc81d7a5d4e85164942f119b1b2`), com revalidação por delta desde o parecer anterior sobre a1a9f84: 2af1983 (A1 da segurança), b45f410 (limites do comando lógico lidos uma vez), 8d59d8f (A2 do review) e 1b0fb6b (refactor de nome). O delta toca controle do Forge (`hooks/_comum.py`, usado pelo `conformidade` e pelo `parecer`) e foi relido inteiro.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega muda a leitura da linha nos hooks `conformidade` e `parecer`, que garantem R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados

## Revalidação do achado anterior (e62b1b6)
- A1 anterior (git push na lista positiva com qualquer opção e com atribuição antes): resolvido pela forma da regra 2.2 a e b da ADR do N-HOOK1. `git_outro_sem_o_corpo` (`hooks/_comum.py:1124`) aceita só as opções da lista fechada de cada subcomando (`hooks/_comum.py:849`); qualquer outra palavra que começa com `-`, inclusive a forma abreviada, tira o comando da lista, e antes do subcomando só `-C <pasta>` e `--no-pager` passam (`--git-dir`, `--config-env`, `--exec-path` e `-c` ficam fora). `programas_e_atribuicoes` (`hooks/_comum.py:1082`) registra as atribuições depois de tirar aspas e barras, então a atribuição entre aspas também conta, e `outro_sem_o_corpo` recusa qualquer atribuição. `env` não está em `ANTES_DO_PROGRAMA` (`hooks/_comum.py:1072`), então vira o programa, fora da lista, e também está em `MUDAM_O_AMBIENTE`, que tira a lista inteira do texto (o `export` anterior também). As fixtures `-bloqueia` novas cobrem `--receive-pack`, `--exec` e `GIT_SSH=` nos dois hooks.
- A2 do review (ganchos de `core.hooksPath`): pela regra 2.2 c. `grava_arquivo` (`hooks/_comum.py:916`) marca o comando lógico com redireção de saída (exceto `/dev/null` e cópia de descritor), `tee`, `uniq`, `-o`/`--output` e `git apply`/`git am`, e então nenhum `git` fica na lista. Como o corpo só chega a arquivo por um dono que é leitor (os outros já fazem do corpo comando), basta cobrir os leitores que gravam, e a lista de `LEITORES_DO_CORPO` (`hooks/_comum.py:1067`) não tem outro leitor que grave por opção fora de `-o`/`--output`. Na dúvida (aspas duplas, destino montado), a regex conta como gravação, o que deixa o hook mais desconfiado.
- A1 do review (custo): `limites_logicos` usa cache e lê os limites uma vez por texto, e `DonosDosHeredocs` guarda o dono por chave. Não muda o que é recusado, só o custo. O orçamento de 3 s e de 150 mil caracteres no `conformidade` continua de pé.
- 1b0fb6b: só troca de nome, sem efeito de segurança.

## Recomendações
- R1 (limite desta revalidação): fiz a revalidação por leitura estática do delta e pela suíte de hooks (`python3 -m unittest tests.test_hooks`: 49 testes OK, com as fixtures novas). Não fiz sondas adversariais novas além das fixtures. As variações de forma (opção abreviada, `-c`, `env`, aspas) estão conferidas na leitura do código acima, não em execução. O gerador por dimensões da ADR do N-HOOK1 (item 5) é a régua que cobre isso de forma sistemática e deve entrar no N-HOOK1, como a ADR já prevê.
- R2: `git push` sem opção ainda lê `remote.<r>.receivepack` e afins da configuração. Hoje essa configuração está protegida e, se a linha grava arquivo, o `git` sai da lista. O endurecimento de `CONFIG_PROTEGIDA` (regra 2.3 da ADR) fica para o N-HOOK1.
- R6 (script gravado e executado na linha seguinte) continua como recomendação, no limite documentado em `docs/hooks.md`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff `a1a9f84..1b0fb6b` e da entrega e a suíte de hooks na worktree. `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não tem segredo, workflow nem dependência. Nada foi instalado, nada saiu da máquina e nada foi gravado além deste parecer.
