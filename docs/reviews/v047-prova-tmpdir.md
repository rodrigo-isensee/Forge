---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-prova-tmpdir
commit: 3fc4724df0bfd01b97e7502826318fe091ed5af9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (prova-tmpdir, E2.316)

Revisão completa (E2.355), instância que não fez a entrega, sobre o diff `1b88640e...a1eb19ef`: `bin/forge-check` (+27), `tests/test_forge_run.py` (+74), `tests/mutantes/v047-prova-tmpdir.json`, `changelog.d/v047-prova-tmpdir.md`. Tamanho (M14): 101 linhas de código e teste, um comportamento só.

## Achados

## Sondas

## Parecer
Aprovado (`R-REVIEW`).

- **Escopo (E2.316):** `rodar_prova` passa a repassar só `TMPDIR`, e só quando `tmpdir_da_prova` o aceita: caminho absoluto, pasta (após `realpath`), do próprio usuário, com escrita e acesso, fora da worktree e da pasta do `.git` comum. Nenhuma outra variável nova; o ambiente da prova segue montado do zero. Nem mais, nem menos que o pedido.
- **Falha segura:** toda dúvida devolve `None` (a prova roda sem `TMPDIR`, como antes). `git rev-parse` falho reduz a exclusão à worktree; `--separate-git-dir` exclui a pasta-mãe do git-dir, o que é conservador. Link simbólico resolvido antes das guardas; o valor passado é o resolvido.
- **Testes:** cada guarda tem teste do ramo de falha por comportamento (nenhum lê a fonte); a prova filha roda com `-I`. `python3 -m unittest tests.test_forge_run` no head a1eb19ef: OK.
- **Mutantes (AR-1, AR-12):** `bin/forge-mutante --processos 1 --base 1b88640e tests/mutantes/v047-prova-tmpdir.json`: PT-M1 a PT-M8 morreram; `--cobertura --base 1b88640e`: todas as linhas de guarda do diff cobertas por mutante declarado. Spec no head revisado, sem linha defasada.
- **Achados recorrentes (PA-7):** conferidos AR-1 a AR-14; nenhum alcança o diff (AR-4: o ambiente da prova é montado do zero; o `git` de teste é o já existente no módulo, fora do diff).
- **Suíte inteira:** fica no CI do PR (sem PR nesta etapa); não rerrodada aqui.

## Revalidação (E2.491)
Delta lido (`forge-check parecer delta`, `a1eb19ef..3fc4724d`): só o merge da develop `86ac0fcb` (`juncao_limpa` E2.302, `voltas --tempo`, `custo --media-por-agente`, mutantes e testes de outros itens), tudo vindo da base. O diff próprio contra a develop segue igual ao revisado: `bin/forge-check` +27, `tests/test_forge_run.py` +74, mutantes e fragmento; nenhuma linha do item mudou. `python3 -m unittest tests.test_forge_run` no head 3fc4724d: OK. AR-1 a AR-14 conferidos de novo: nenhum alcança o delta. Aprovado no head 3fc4724d.
