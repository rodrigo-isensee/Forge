---
tipo: qa
contrato: 1
pedido: prepush-so-parecer
branch: melhoria/prepush-so-parecer
commit: 862bf19cb7367460eef1c6d1ec0e431e49ea53d5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
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

## Bugs (volta 1; A1 corrigido, ver Volta 2)
Média, A1: o delta usa `git diff --name-only --no-renames`, que lista o arquivo apagado e os dois lados de um rename; ambos casam com `docs/{reviews,security,qa,devops}/*` e o envio vai pelo caminho curto. A decisão D2 do dono e o pedido E1 dizem "só acrescenta". Impacto: um parecer pode ser removido ou movido sem a suíte inteira; o CI repete tudo. Correção: `tech-lead` (hook), dando suíte inteira quando `git diff --diff-filter=D --name-only --no-renames` não for vazio, com teste novo.

## Achados

## Volta 2
Código 862bf19 (HEAD da branch ccf88fc, que só acrescenta pareceres). Suíte: `python3 -m unittest discover -s tests -q`, 1213 testes, OK (322 s); `scripts/validar-plugin.sh`: Validation passed.

Refeito o A1 como usuário: clone em `$TMPDIR` com o hook da branch (`core.hooksPath`), remoto `git init --bare` local, `git push` reais, sem rede. Para não repetir a suíte pesada em cada caso, um `python3` falso no PATH só ecoa o comando que o hook chamou (o hook não foi alterado); cada caso parte de um push-base na mesma branch, que grava a prova da árvore.

| Caso | Delta | Caminho tomado (linha do hook) | Resultado |
|---|---|---|---|
| a | A `docs/reviews/sonda-a.md` | "pre-push: o envio só acrescenta pareceres sobre código já testado; rodando só as classes que leem pareceres" + `-m unittest tests.test_forge.Neutralidade ... NeutralidadeDoNucleo` | passa: caminho curto |
| b | D `docs/reviews/prepush-so-parecer.md` | sem mensagem curta; `-m unittest discover -s tests -q` | passa: suíte inteira |
| c | D + A (rename) | `-m unittest discover -s tests -q` | passa: suíte inteira |
| d | A `docs/reviews/_modelo.md`; A `docs/security/ameacas/s.md`; A `docs/security/aceites/s.md` (três commits) | `discover -s tests -q` nos três | passa: suíte inteira |
| e | A `docs/qa/sonda-e.md` + M `README.md` | `discover -s tests -q` | passa: suíte inteira |

Vermelho antes do verde do A1: na volta 1, os casos b e c saíram pelo caminho curto (registrado acima); agora vão à suíte inteira. Sem teste instável. Pareceres de review e segurança da volta 2: `## Achados` vazio.

Bugs abertos: nenhum.
