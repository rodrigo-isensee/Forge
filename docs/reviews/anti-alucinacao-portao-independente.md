---
tipo: review
contrato: 1
pedido: anti-alucinacao-portao
branch: melhoria/anti-alucinacao-portao
commit: c365315
parecer: aprovado
revisor: forge:tech-lead (independente)
data: 2026-10-15
---
# Review independente: portão do parecer no Forge (fatia 3 do anti-alucinação)

Escopo: `git diff origin/melhoria/anti-alucinacao-regras..c365315` (00b3042, 0f389dd, 6f71cf5 e o parecer de autor). Os commits seguintes (d599a4d, 5e3ff0e) só trazem o parecer de segurança, que não altera código. Referências: a linha "| 3 |" da seção 11 da proposta anti-alucinação (PQ-1 a PQ-4), as decisões do dono (P1 = B, P2 = A, P3 = A, §14 = B), o parecer de autor `docs/reviews/anti-alucinacao-portao.md` e o de segurança `docs/security/anti-alucinacao-portao.md` (aprovado, `commit: c365315`). Revisor diferente do autor (`R-REVIEW`).

**Parecer: aprovado.** Nada bloqueia. Ficam três recomendações de texto e uma orientação para as fatias 4 e 5. Os achados A1 a A4 da segurança são citados aqui sem ser refeitos. **O PR precisa do rótulo `afrouxa-regra`**, porque toca `hooks/parecer.py`, `hooks/_comum.py` e `tests/catraca.py`, que estão em `PROTEGIDOS`. A mudança endurece a guarda e não remove nenhum invariante.

## Provas (PQ da linha "| 3 |")
Comandos rodados por mim na branch, com HEAD 5e3ff0e (o mesmo código de c365315):
- **PQ-1:** as fixtures `forge-clone-pr-create-reprovado-bloqueia` (`codigo: 2`, "R-REVIEW: sem parecer aprovado, abra com gh pr create --draft; docs/reviews/p1-1.md") e `forge-clone-pr-merge-reprovado-bloqueia` (`codigo: 2`, "R-REVIEW: docs/reviews/p1-1.md") passam em `tests.test_hooks.Hooks.test_fixtures`, que deu "Ran 2 tests in 76.045s / OK" junto com `test_raiz_de_estado_no_clone_do_forge`. A segurança mediu o antes e o depois (S1, de rc 0 para rc 2).
- **PQ-2:** `forge-clone-pr-create-draft-sem-parecer-libera` (`codigo: 0`) e `forge-clone-pr-ready-sem-parecer-bloqueia` (`codigo: 2`, "R-REVIEW: PR sai do rascunho só com parecer: nenhum parecer") passam na mesma execução.
- **PQ-3:** `tests.test_catraca.Pareceres` deu "Ran 12 tests in 0.690s / OK". Entre eles está `test_um_pedido_reprovado_barra_mesmo_com_outro_aprovado`, que cobre as duas ordens alfabéticas (`a-ok`/`b-ruim` e `b-ok`/`a-ruim`). A catraca não é vazia: `tests/catraca.py --modo pareceres --base-ref homolog` sobre esta branch dá rc=1 ("sem parecer aprovado de review e QA (docs/qa: ...)"), porque o QA ainda não existe. Com `--base-ref develop`, dá rc=0 tanto com base `origin/develop` quanto com base `origin/melhoria/anti-alucinacao-regras`.
- **PQ-4:** `python3 -m unittest tests.test_hooks -v` deu "Ran 13 tests in 68.885s / OK", incluindo as 59 fixtures de `parecer` que já existiam. As fixtures novas de projeto `pr-draft-em-projeto-sem-parecer-bloqueia` (`codigo: 2`) e `pr-ready-em-projeto-libera` (`codigo: 0`) provam que `--draft` não dispensa o parecer no projeto e que `gh pr ready` não é conferido lá. A única fixture alterada (`pr-merge-no-forge-a-partir-do-clone-libera`) mudou só a `descricao`: o cenário, que já tinha parecer aprovado, agora passa porque o hook confere e aprova, e não porque ignora o clone. A segurança (S8) chegou ao mesmo resultado por sonda.

## `raiz_de_estado`: legibilidade e manutenção
- **Composição clara.** `copia_de_trabalho` (a primeira pasta com `.git`) → `raiz_do_projeto` (essa pasta, se tiver `.forge/versao`) → `raiz_de_estado` (o projeto ou, na falta dele, o clone do Forge). São funções de 1 a 4 linhas, que só olham o disco, sem git no caminho comum. O projeto vem antes do manifesto, e a docstring registra a invariante que importa para quem for reaproveitar a função: ela só pode **acrescentar** guarda.
- **O nome diz mais do que ela faz hoje.** No `parecer`, `raiz_de_estado` decide **onde o hook age**, sem gravar estado nenhum. O estado em si vai para `Hook.run()`, isto é, `copia_principal()`: numa worktree, a raiz é a da worktree e o estado fica na cópia principal. A docstring explica isso e o teste confirma (`hook.copia_principal().resolve() == clone.resolve()`). Não proponho renomear agora, porque as fatias 4, 5 e a retomada vão gravar estado por ela e o nome passará a ser exato. Recomendo, nessas fatias, que **todo estado passe por `Hook.run()`** e nunca por `raiz_de_estado(...) / ".forge"`, para que as worktrees continuem somando no mesmo estado.
- **`Hook.projeto(..., clone_do_forge=True)` acopla duas coisas:** aceitar o clone e ignorar `hooks_desligados` lá. Para o `parecer`, o acoplamento está certo. As fatias 4 e 5, porém, herdam o "não se desliga no clone" só por passar `clone_do_forge=True`. Isso deve ser uma decisão explícita de cada fatia, registrada no parecer dela, e não um efeito colateral. O caso inverso (clone convertido em projeto religa o `hooks_desligados`) é o A1 da segurança e fica fora deste escopo.
- **Rastro de erro:** `registrar_erro` ainda procura a raiz por `raiz_do_projeto` (A3 da segurança). Quando as fatias seguintes usarem `raiz_de_estado`, convém trocar ali também, para que o `erros.log` citado na mensagem de bloqueio exista no clone.
- **Custo:** `raiz_de_estado` lê o `plugin.json` a cada chamada, fora de projeto. É desprezível no caminho comum: o autor mediu 24 a 44 ms para `gh pr create`. As fatias 4 e 5 vão chamá-la em mais eventos. Se aparecer latência, o próximo passo é guardar o resultado no `Hook`, não em variável global.

## Demais pontos do código
- `bandeira` resolve `--draft`, `-d`, `--draft=<valor>`, valor de opção (`--title -d`) e "vale a última", como o `gh`. A forma desconhecida (`-dw`) conta como desligada, o que só pode endurecer o portão. As listas `CREATE_COM_VALOR` e `READY_COM_VALOR` são dado e não lógica, e ficam fáceis de atualizar.
- `pronto_de_pr` reaproveita `branch_do_pr`, `base_do_pr` e `verificar`, sem duplicar regra. A `dica` em `verificar` é opcional e não muda a mensagem nos projetos.
- No clone, `pull_request` passa a barrar `--head` de branch não buscada (antes liberava). Isso é correto, porque no clone não há outra guarda local, e a mensagem ensina o `git fetch` ou o `--draft`.
- `tests/catraca.py`: o `return []` de dentro do laço aprovava a branch inteira pelo primeiro pedido limpo. Agora o laço acumula as violações e só aprova com `pedidos and not achados`. Sem pedido, a função continua reprovando. É o menor conserto possível.

## Coerência entre `docs/hooks.md`, `agents/tech-lead.md` e o CHANGELOG
As três fontes concordam no essencial: no Forge, o PR nasce com `--draft`, e `gh pr create` sem rascunho ou `gh pr ready` exigem review e QA aprovados. Nos projetos, nada muda. O `hooks_desligados` não vale no clone, e a falha fechada vale lá também. O marcador `pr ready` aparece no `CRITICO` do `parecer` e no do `conformidade`, como `docs/hooks.md` afirma. O limite do `gh api graphql` está em "Limites" (é o A2 da segurança).

Recomendações (severidade: recomendado, nenhuma bloqueia):
1. `docs/hooks.md:21`, `CHANGELOG.md:10`, `hooks/_comum.py:75` e `hooks/parecer.py:11` dizem "as worktrees de `~/.forge-contrib/wt/`", mas o código vale para **qualquer** worktree de um clone, inclusive fora de `wt/`, como a sonda S6 da segurança mostrou. Isso não afrouxa nada, mas o texto subestima o alcance. Sugestão: "as worktrees do clone (por convenção em `~/.forge-contrib/wt/`)".
2. `agents/tech-lead.md`: "só então `gh pr ready <branch>`" está certo. Vale acrescentar que, com o parecer reprovado, o PR **continua em rascunho**, e que o `gh pr ready --undo` existe para voltar ao rascunho quando um novo commit invalida o parecer.
3. O CHANGELOG põe a fatia em "Corrigido", o que é coerente, porque fecha o vetor do #120. A frase "que as fatias seguintes e a retomada reaproveitam" anuncia trabalho futuro. Ela é aceitável como contexto, mas deve sair ou ser confirmada na release, se alguma fatia não usar a função.

## Efeito nas fatias 4 e 5 e na retomada
- A raiz única evita que cada hook novo reinvente a detecção do clone, que é o maior ganho de manutenção da fatia.
- Duas condições para o reaproveitamento continuar seguro: (a) gravar estado só por `Hook.run()`; (b) decidir de forma explícita, por hook, se `hooks_desligados` vale no clone.
- A retomada que rodar fora de sessão (sem `CLAUDE_PROJECT_DIR`) recebe a raiz pela pasta corrente, e a de uma worktree é a própria worktree. O teste `test_raiz_de_estado_no_clone_do_forge` já cobre a cópia principal, a worktree, o projeto, a pasta alheia e a pasta sem git, e serve de base para os testes dessas fatias.

## Checklist (leitura)
1. Escopo: o da linha "| 3 |", nem mais nem menos. Os hooks `decisao`, `brief` e `prova`, a retomada e o S8 não foram tocados.
2. Regras: `R-NEUTRO` (sem nome de projeto nem stack; o slug das fixtures é o do próprio Forge), `R-CUSTO` (sem rede nem IA), ADR 0003 e ADR 0009 (seção 7) preservadas.
3. a 4. Legibilidade e tratamento de erros: ver acima. Nenhum `except` novo.
5. Segurança: parecer próprio, aprovado em c365315. Os cartões A1 e A2 ficam fora deste escopo.
6. Desempenho: medido pelo autor e comentado acima.
7. Testes: 19 fixtures novas, 1 com a descrição atualizada, 2 testes novos na catraca e 1 de unidade. O teste da catraca falha sem a correção, segundo o autor e a lógica do `return []` antigo.
9. Commits: três por tema, em Conventional Commits e em português.
10. Mecanismo novo: não há. A fatia estende o portão existente, e o "por que o existente não basta" é o #120 (o hook não agia no clone).
11. Testes de ausência: as fixtures `-libera` de projeto seguem procurando os mesmos textos. A pasta `tests/hooks/parecer/` tem 78 fixtures.

## Pendências
- QA (`R-QA`) e o rótulo `afrouxa-regra`, do dono, antes de o PR sair do rascunho.
- Os cartões A1 e A2 da segurança e as recomendações 1 e 2 acima: para o autor, nesta fatia ou na próxima.
