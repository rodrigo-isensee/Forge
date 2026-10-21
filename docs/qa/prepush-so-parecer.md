---
tipo: qa
contrato: 1
pedido: prepush-so-parecer
branch: melhoria/prepush-so-parecer
commit: 441ae2727f04a76299723ca79a2c2989117148de
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
aceite_usuario: sim
data: 2026-10-21
---
# QA: pre-push só de parecer (PREPUSH-SO-PARECER, E1.4)

Ambiente: worktree da branch (HEAD d02ebb9, que só acrescenta pareceres sobre o commit 441ae27 testado). Sondas em cópia de 441ae27 com repositório git e remoto falso próprios em `$TMPDIR`, sem rede e sem custo (`R-CUSTO`).

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -q` | 1211 testes, OK (354 s) |
| `scripts/validar-plugin.sh` | Validation passed |
| Teste instável | nenhum observado |
Observação: a cópia de sonda em pasta rasa de `$TMPDIR` (`/tmp/claude-1000/sonda/w`) fez `test_pedido_fora` falhar (`../../x.md` não sai da cópia); em pasta mais funda passou. É profundidade do caminho de sonda, não do hook.

## Obrigação -> sonda -> resultado
| Obrigação (E1, D2, R2) | Sonda | Fronteira protegida | Resultado |
|---|---|---|---|
| Envio só de parecer em `docs/reviews/` sobre árvore testada roda o caminho curto | prova gravada pela suíte inteira; envio de `docs/reviews/sonda-a.md` | só 4 classes | passa: 8 testes em 4,7 s, mensagem do caminho curto |
| Parecer em `docs/security/` com termo de stack é barrado | `docs/security/sonda-b.md` com termo de stack | `NeutralidadeDoNucleo` no atalho | passa: rc 1, a prova não muda |
| Código, `_modelo.md`, `docs/security/ameacas/`, `docs/security/aceites/` rodam a suíte inteira | quatro commits, um por caso | `*/_*` e pastas de controle | passa: sem mensagem do caminho curto, suíte inteira em execução |
| Arquivo fora das quatro pastas, e misto parecer + código, rodam a suíte inteira | `docs/pedidos-sonda.md`; `docs/qa/` + `README.md` | falha fechada | passa |
| Apagar arquivo roda a suíte inteira | `git rm docs/reviews/sonda-a2.md` | só acrescenta | FALHA: caminho curto, rc 0 (A1) |
| Renomear arquivo roda a suíte inteira | `git mv docs/reviews/sonda-a.md ...-a2.md` | só acrescenta | FALHA: caminho curto, rc 0 (A1) |
| A prova grava a árvore do início da suíte | `.verde` igual a `HEAD^{tree}` após a suíte inteira e após o curto; `test_prova_grava_a_arvore_do_inicio_da_suite` | início, não fim | passa |
| Sondas e cópias só em `$TMPDIR`, sem rede | tudo em `$TMPDIR`; remoto é diretório local | `R-CUSTO` | passa |

## Bugs
Média, A1: o delta usa `git diff --name-only --no-renames`, que lista o arquivo apagado e os dois lados de um rename; ambos casam com `docs/{reviews,security,qa,devops}/*` e o envio vai pelo caminho curto. A decisão D2 do dono e o pedido E1 dizem "só acrescenta". Impacto: um parecer pode ser removido ou movido sem a suíte inteira; o CI repete tudo. Correção: `tech-lead` (hook), dando suíte inteira quando `git diff --diff-filter=D --name-only --no-renames` não for vazio, com teste novo.

## Achados
- A1 (bloqueante) .githooks/pre-push:150 · apagar ou renomear arquivo em docs/reviews, security, qa ou devops vai pelo caminho curto, contra o "só acrescenta" de D2 e E1; testado: git rm e git mv rodaram 8 testes e saíram com rc 0.
