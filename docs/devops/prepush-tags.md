---
tipo: revisao-devops
contrato: 1
pedido: prepush-leve
branch: melhoria/prepush-tags
commit: f835f66
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: prepush-leve, parte 1 (PREPUSH-TAGS)

Parecer do próprio autor do hook, que veio de `docs/devops/prepush-leve.md` (7f8166a) e foi refeito para a divisão pedida pelo M14 (achados A1 e A2 do review). O review do `tech-lead` segue exigido (`R-REVIEW`).

## Parecer
Aprovado. Um comportamento só: `tags_ja_no_remoto` em `.githooks/pre-push`. Quando toda ref é `refs/tags/*` e o commit de cada tag já está em `refs/remotes/<remoto>/*`, o push sai com 0 sem teste, trava nem fila, como o PREPUSH-DELETE. A regra vem depois do laço das refs, então a recusa de `develop`, `homolog` e `main` e a de tag movida (`R-VERIFY`) valem antes.

Achados:
- Nenhum bloqueante.
- Falha fechada, coberta em `tests/test_pre_push_tags.py`: commit novo, commit só em outro remoto, tag junto com branch e remoto por URL entram na fila. Tag anotada de commit já no remoto sai sem fila. Com o hook da develop, o teste do caminho novo reprova (prova de vermelho).
- `tests/config.json`: nada muda, e o invariante do hook (`main|homolog|develop`) segue intacto.
- recomendado (A2 da segurança, vai para cartão): as refs `refs/remotes/*` são confiança local, não prova, e o texto disso está em `docs/hooks.md` e no comentário do hook. O CI do PR repete tudo.

Teto M14: 147 linhas de código e teste (`git diff --numstat --no-renames origin/develop...HEAD`): `.githooks/pre-push` 30, `tests/apoio_pre_push.py` 67 e `tests/test_pre_push_tags.py` 50.

Ferramentas: `shellcheck` sem achados. `actionlint` está fora do PATH, mas nenhum workflow mudou.

Provas: `python3 -I -m unittest discover -s tests -p <arq>`, todos com rc=0: `test_pre_push_tags` (3), `test_testes_tocados`, `test_ambiente_git`, `test_pre_push_parecer`, `test_pre_push_parecer_curto`, `test_pre_push_afetados`, `test_pre_push_trava` (3 skips do ambiente), `test_pre_push_shellcheck` e `test_fila_ocupacao`.

## Custo e rollback
Sem minuto de CI nem recurso novo (`R-CUSTO`). Rollback: `git revert` do commit, que devolve o push de tags à fila de sempre.
