---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/prepush-so-docs
commit: 0ba1a876f9176c74d9dae97ca208805c3f652e43
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: prepush-so-docs (E18 PREPUSH-SO-DOCS, versao-033)

Escopo: o diff `928e61b..0ba1a87` (2 commits): `templates/projeto/.githooks/pre-push`, `tests/test_prepush_so_docs.py`, `bin/forge-testes` (mapa) e `changelog.d/prepush-so-docs.md`. Conferido contra a seção E18 de `docs/security/ameacas/versao-033.md` (limite Q7 = A, controles C-1 a C-5, mudanças proibidas T-1 a T-4).

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: o pre-push que o modelo de projeto instala em todo projeto. A entrega afrouxa o controle (pula o `pre-push.local` em envio só de documentação), dentro do limite decidido pelo dono (Q7 = A).

## Achados
- A1 (recomendado) templates/projeto/.githooks/pre-push:48 · o diff não fixa --ignore-submodules=none: com diff.ignoreSubmodules=all (config ou GIT_CONFIG_PARAMETERS), a troca de um gitlink fora de docs/ some da lista e o envio com docs/a.md pula o pre-push.local (sonda local); acrescentar a opção e um teste
- A2 (recomendado) tests/test_prepush_so_docs.py:1 · a matriz E18 lista mudança de modo, symlink e submódulo (gitlink) e nenhum teste os cobre; acrescentar ao menos o gitlink fora de docs/ (roda tudo, inclusive com diff.ignoreSubmodules=all)

## Detalhe dos achados
**Conferência dos controles (sem defeito):**
- C-1: `:48` lista os arquivos dos commits enviados (`git diff --name-only -z --no-renames <remote_sha> <local_sha>`), não da árvore (`test_diff_usa_os_commits_e_nao_a_arvore`); o laço `:43-55` exige que toda ref se qualifique (`test_duas_refs_uma_docs_outra_codigo_roda`). Como `:10-25` já barrou o não fast-forward antes, o diff de dois pontos é o conjunto líquido do que sobe.
- C-2 (falha fechada): branch nova (`:46`), apagar ref (`:45`, mais estrito que o modelo: qualquer apagamento no envio roda tudo), tag (`:47`), falha do git (`:48`, `|| return 1`), lista vazia (`:54`), stdin sem ref (`:41`) e falha do `mktemp` (`:42`) rodam tudo. Objeto remoto ausente sai antes, em `:13-16`. Cada caso tem teste.
- C-3: `:52` usa `case` sensível a caixa, `.github/*` antes de `docs/*|*.md` (mais estrito que o literal: `.github/x.md` roda tudo, que é o que o brief pede); `docsx/`, `a.MD`, `a.md.ts`, `docs` como arquivo e `Docs/` rodam tudo (testados). `--no-renames` mais `-z` dão o nome antigo no renome e nomes com espaço ou quebra de linha sem citação.
- C-4: o `unset GIT_DIR ...` (`:34`) vem antes do primeiro git novo; o `pre-push.local` é chamado como antes (`:66`), e o pulo imprime a linha prevista (`:64`).
- C-5: os casos pedidos estão em `tests/test_prepush_so_docs.py`; rodei `tests.test_prepush_so_docs`, `tests.test_ambiente_git` e `tests.test_testes_tocados`: 130 testes, OK.
- T-1: não há variável, opção nem arquivo que pule (`test_sem_variavel_que_pule`; leitura de `:36-68`). T-2: o critério é o literal. T-3: `:10-29` (R-VERIFY e `main`) só ganhou a linha `:6`, que acumula a ref sem decidir nada, e `.githooks/pre-push` do Forge não está no diff. T-4: nenhum workflow tocado.

**A1.** Evidência: `templates/projeto/.githooks/pre-push:48`; sonda em repositório descartável: com `diff.ignoreSubmodules=all`, no config do repositório ou por `GIT_CONFIG_PARAMETERS`, `git diff --name-only` entre dois commits omite o gitlink `lib` e lista só `docs/a.md`. Caminho de ataque: quem envia (o próprio dev ou um agente) com essa configuração manda a troca de um submódulo junto de documentação e o lint e o typecheck locais não rodam. Ganho pequeno: o hook local não segura quem controla a própria máquina, o lint raramente cobre o submódulo e o CI do projeto roda tudo. Severidade: baixa. Correção mínima: `--ignore-submodules=none` no `git diff` de `:48` e um teste. Esforço: P. Dono: tech-lead (implementação do item).

**A2.** Evidência: a matriz E18 traz a dimensão Mudança (modo, symlink, gitlink) e `tests/test_prepush_so_docs.py` não a cobre. Sem caminho de ataque próprio além do A1; é lacuna de cobertura. Severidade: informativa. Correção mínima: teste do gitlink fora de `docs/` (padrão e com `diff.ignoreSubmodules=all`). Esforço: P. Dono: tech-lead ou qa-engineer.

## Riscos aceitos e ferramentas
Risco residual aceito pelo dono na decisão Q7 = A (2026-11-03): código dentro de `docs/` (e qualquer `*.md`) pula o lint local; o CI do projeto pega. Nenhum risco novo pedido a aceite.

Ferramentas: leitura do diff, os testes do item e sondas locais em `$TMPDIR`. Lacunas no PATH: `shellcheck`, `gitleaks`, `semgrep`, `zizmor` e `actionlint` (não instalados; o shellcheck roda na bateria do CI). Nada pago (`R-CUSTO`).
