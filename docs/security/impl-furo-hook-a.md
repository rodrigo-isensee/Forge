---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a5
commit: ecf99c3e60cb11ea3f52ab029327e967619d7053
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a5

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-2`). Diff lido: `234dbe0..ecf99c3`, incluindo a volta 1 (`cf5b850`, `caae6a6`). Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.6. Não sou o autor.

## Item entregue e M14
- **Item:** E5, A5 ROTULO-VARIAVEL: `aplica_afrouxa_regra` com o rótulo por variável, substituição, `xargs`, alias e escape JSON.
- **M14 (decisão M14, `agents/tech-lead.md:19` na develop):** contam `hooks/conformidade.py` (25+9) e `tests/test_hooks.py` (5): 39 linhas, abaixo de 150. As fixtures de `tests/hooks/`, `tests/mutantes/`, `docs/hooks.md`, `changelog.d/` e os pareceres ficam fora. Uma classe de comportamento em `hooks/` (o rótulo que o hook não vê exige o dono), com corpus próprio (19 fixtures `rotulo-variavel-*`). **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o hook `conformidade` no portão R-CONTRIB (o rótulo `afrouxa-regra` só pela conta do dono).

## Achados
- A1 (recomendado) hooks/conformidade.py:1366 · chaves e glob do bash no rótulo saem 0 fora da conta do dono: `--add-label={afrouxa-regra,bug}` (rótulo literal na linha), `--add-label=afrouxa-regr{a,a}`, `afrouxa-regr?` (com o arquivo criado antes), `gh api … -flabels[]=afrouxa-regr{a,a}`. Cartão.

## Detalhe dos achados
Sondas: cada uma monta a fixture `rotulo-variavel-por-variavel-bloqueia` (sessão do Forge, conta `outra-pessoa`) pelo `Fixture`/`rodar` da própria worktree e roda o hook real. A expansão do bash foi conferida com `printf` local. Nada rodou contra repositório real, rede ou produção.

**O que a branch fecha:** as 15 fixtures `-bloqueia` do lote (variável, `${A}regra`, `$( )`, aspas ANSI, comentário em expansão, opção sem valor, `xargs` com `echo`, `printf`, `cat` e com valor, `gh alias`, `alias` do shell, escape JSON, escape malformado e `--input`) saem 2. As contraprovas (`--add-label bug`, variável noutro argumento, escape inofensivo e rótulo literal diferente) saem 0. Também saem 2 `-lafrouxa-regra` colado no `pr create` e `AFROUXA-REGRA` em maiúsculas. O A1 da volta anterior (`xargs` sem rótulo na linha) está fechado em `hooks/conformidade.py:1366-1367`, pelo `por_xargs` sozinho. Rodei `test_fixtures_do_lote_furo_hook_a` no HEAD revisado, com `OK`.

**A1, recomendado.** Evidência: `hooks/conformidade.py:1366` compara o valor do rótulo com o literal e só falha fechado com `$` ou crase no valor. A expansão de chaves e o glob do bash mudam o valor depois do hook. Sondas com saída 0 na conta `outra-pessoa`, cada uma conferida pela expansão do bash:
- `gh pr edit 1 --add-label={afrouxa-regra,bug}` vira `--add-label=afrouxa-regra --add-label=bug`, com o texto do rótulo literal na linha;
- `gh pr edit 1 --add-label=afrouxa-regr{a,a}`;
- `gh pr edit 1 {--add-label=afrouxa-regra,--add-label=bug}`;
- `gh pr create -t x -b y --label={afrouxa-regra,bug}`;
- `gh pr edit 1 --remove-label=afrouxa-regr{a,a}`;
- `gh api repos/o/r/issues/1/labels -flabels[]=afrouxa-regr{a,a}` e `--raw-field=labels[]=afrouxa-regr{a,a}`;
- `gh pr edit 1 --add-label=afrouxa-regr?`, `afrouxa-regr[a]` e `afrouxa-regr*`, que só aplicam o rótulo se antes se criar um arquivo `afrouxa-regra` na pasta.

Na base `234dbe0`, `--add-label={afrouxa-regra,bug}` também sai 0: a branch não abre isso. Mas é a mesma família que ela fecha (o valor que o shell muda depois do hook). Caminho: só deliberado. Uma sessão com outra conta do `gh`, por injeção, monta o rótulo com chaves ou glob. Nesta máquina os agentes usam a conta do dono, então o controle só pesa para sessões de outra conta. A mesma intenção também passa por um interpretador que monta o texto (N6, limite aceito). Por isso não bloqueia. Severidade baixa. Correção mínima (cartão):
1. Em `gh pr|issue edit|create`, `CITA_ROTULO` sobre o texto da linha inteira conta como "pode aplicar", o que fecha a forma com o rótulo literal e falha fechado pelo texto, como o resto do R-CONTRIB.
2. Toda palavra com `{` seguido de `,` ou `..` antes do `}`, ou com `*`, `?` ou `[` fora de aspas, num `gh pr|issue edit|create` ou num `gh api` de rótulo, também conta como "pode aplicar". O falso positivo atinge só contas que não são do dono, e o contorno é escrever o valor literal ou entre aspas (§2.7(d) do desenho).

Fixtures `-bloqueia` com as sondas acima e contraprova `gh pr edit 1 --add-label bug` · 0. Esforço P. Dono: tech-lead.

Dimensão nova para a matriz do modelo (§8, Mecanismo): **expansão de chaves e glob do bash** em linha sem a rede da ADR 0011 (fora do projeto ou sem marcador). Ela aparece também nas branches a2, a3 e a4. Proponho um cartão único para as quatro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais pelo harness de fixtures, `printf` local para a expansão e execução das fixtures do lote. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `bandit` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow).
