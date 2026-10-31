---
tipo: review
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 44617ead4fee4eab8193b8e07cda121e45f5cf2b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-n-ci (c3), revalidação

## Achados
- A1 (recomendado) tests/test_suite_paralela.py:279 · o caso verde do teste confere só a primeira linha; a presença da medida no verde fica nos testes das linhas 396 a 411. Basta, mas uma asserção ali deixaria o contraste do C-7 num teste só.

## Parecer
Aprovado. Revalidação da rodada que reprovou `4c978e7` (A1 e A2 bloqueantes).

Delta lido: `forge-check delta --parecer docs/reviews/impl-n-ci.md` lista `4c978e7..44617ea`, que traz a develop inteira (já revisada nos PRs dela). Li só o que a c3 acrescenta à develop: `git diff c162bcb 44617ea` em `scripts/suite-paralela.py`, `tests/test_suite_paralela.py` e `changelog.d/impl-n-ci-c3.md`. Já lido: o restante do delta (arquivos da develop), fora do diff da branch.

O que entrega: a segunda metade do E2 do pedido (item 55 d), o veredito protegido (C-6 a C-8, C-10), agora sobre o `montar_resumo` da c2 que está na develop (#408).

- A1 anterior (conflito com a c2): resolvido. A c3 trouxe a develop com a c2 (merge `44617ea`, sem rebase); o diff contra `c162bcb` aplica a proteção às linhas de medida da c2: veredito na primeira linha do resumo, FAILED sai antes de lentas, soma, maior unidade e desequilíbrio com a linha "execução reprovada", "sem duração" listada nos dois casos, `publicar_no_ci` chamado depois do `print(veredito)`, erro ao montar ou gravar vira "resumo indisponível" no stderr sem mudar o código, `fechar_verde` mantém pesos e carimbo só no verde. O `::group::` com os módulos ficou (`scripts/suite-paralela.py:395`).
- A2 anterior (teste de ausência vazio): resolvido. `test_resumo_comeca_pelo_veredito` procura "unidades mais lentas", "soma das unidades", "maior unidade" e "desequilíbrio", textos que o caminho verde de `montar_resumo` escreve (`scripts/suite-paralela.py:438` a `444`) e que os testes do verde afirmam; tirar o retorno antecipado do FAILED faz a asserção falhar. Checklist 11 conferido.

Teste rodado na worktree, em `44617ea`: `python3 -m unittest tests.test_suite_paralela` → `Ran 35 tests`, `OK`.

M14 (agents/tech-lead.md:19): `git diff --numstat --no-renames c162bcb 44617ea` dá `scripts/suite-paralela.py` 28+13 e `tests/test_suite_paralela.py` 80+15, total 136 linhas, abaixo de 150; fragmento de `changelog.d/` e pareceres fora da conta. Não toca `hooks/` nem caminho de `PROTEGIDOS`; um comportamento só (o veredito protegido no resumo do CI). Cumpre, sem linha de exceção.

Ferramentas: o Forge não tem `docs/engineering/praticas.md` com regras por ferramenta; a suíte roda no pre-push e no CI do PR, e a mutação do diff é do autor e do QA. Segurança (E1.3) e devops (E1.6) da c3 são pareceres à parte; não os refaço.
