---
tipo: review
contrato: 1
pedido: rotulo-sobrevive-merge
branch: melhoria/rotulo-sobrevive-merge
commit: acf55f0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review (parecer de autor): rótulo e parecer sobrevivem a merge da base e a commit de parecer

Escopo: `origin/develop..4a4d468` (1 commit): `tests/catraca.py`, `bin/forge-check`, `tests/test_catraca.py`, ADR 0004 (item 3), ADR 0008 (tabela da catraca), `CHANGELOG.md`. Referências: ADR 0008, ADR 0004, R-CONFORMIDADE, R-REVIEW, R-CUSTO.

Este é o parecer do autor. O PR muda `tests/catraca.py` (protegido): falta a review independente e o rótulo `afrouxa-regra` do dono.

## Problema
O rótulo só valia se aplicado depois do último push, e o `commit` do parecer só valia se o diff direto até o head tocasse apenas pareceres e quadro. Um merge da `develop` na branch invalidava os dois. Um commit só de parecer invalidava o rótulo. O conteúdo revisado não mudava em nenhum dos casos.

## Desenho escolhido
1. **Diff efetivo** (`forge-check`: `diff_efetivo`, `mesmo_diff`): é o patch de um commit sobre o seu merge-base com a base, sem os caminhos ignorados e sem as linhas `index` (o hash do blob muda quando a base mexe no arquivo). A comparação é **estrita**: texto, contexto e número de linha. Se a base mexer perto do trecho do PR, o diff muda e o rótulo ou o parecer cai. É uma falha fechada e foi escolhida de propósito. Não usei `git patch-id`: ele ignora espaço em branco, que é semântico em Python e YAML.
2. **Rótulo** (`catraca.py`): a regra antiga continua igual (rótulo depois do último push). Se ela falhar, a catraca tenta a regra nova:
   - `commit_do_rotulo` encontra o head no instante do rótulo. É o head da última execução `pull_request` deste PR criada antes do rótulo, pelo `created_at` do servidor e nunca pela data do commit.
   - Esse head precisa ter outra execução **depois** do rótulo, que é a execução do próprio `labeled`. Sem ela, o head do instante do rótulo pode não ter execução nenhuma (`[skip ci]`, workflow desligado no PR) e a atribuição cairia num head anterior que o dono não viu.
   - Se houver `head_ref_force_pushed`, `head_ref_deleted` ou `head_ref_restored` depois desse head, a regra nova não vale.
   - Com o head encontrado, o diff efetivo dele, fora de `docs/reviews/` e `docs/qa/`, tem de ser idêntico ao do head avaliado.
   - Os dados vêm de `GET /pulls/{n}` (para saber a branch) e de `GET /actions/runs?event=pull_request&branch=...` (filtrado pelo número do PR). As duas consultas são gratuitas e só de leitura (R-CUSTO). Se faltar token, a API falhar, não houver execução ou o commit não existir localmente, a regra nova não vale. Um PR de fork não tem `pull_requests` nas execuções e fica só com a regra antiga.
   - R-CUSTO continua sem exceção pelo rótulo.
3. **Parecer:** `commit_vale(..., base)` e `cmd_pr(..., base)` mantêm a checagem antiga e aceitam também o caso em que o diff efetivo, fora de `LIVRES`, é igual ao do `commit`. O modo `pareceres` passa a base. Sem `--base`, o `forge-check pr` continua estrito como antes, e o hook `parecer` não foi tocado. O veredito continua sendo lido do arquivo de parecer no head, então trocar `aprovado` por `reprovado` continua barrando.

Alternativa descartada: ignorar os commits de merge no diff. Um merge pode resolver conflito com código novo, e isso furaria a regra.

## Testes (vermelho antes, verde depois)
- São 17 casos novos em `tests/test_catraca.py`: `Pareceres` (4), `CommitDoRotulo` (5), `RotuloSobreviveAoConteudo` (6) e `ExecucoesDoPr` (2).
- **Vermelho** sobre o código antigo: 15 dos 17 falharam (9 falhas e 8 erros). Os dois que já passavam são guardas de não regressão: código mudado depois do merge invalida o parecer, e o veredito trocado no parecer continua barrando.
- **Verde:** `python3 -m unittest discover -s tests` deu 267 OK, e `scripts/validar-plugin.sh` passou.
- Os quatro casos pedidos estão cobertos:
  - o merge da base mantém o rótulo e o parecer;
  - um commit só de parecer mantém o rótulo;
  - código mudado depois do rótulo invalida, inclusive `KANBAN.md` e mudança junto com o merge;
  - o veredito trocado é conferido pelo modo `pareceres`.

## Checklist
- O PR faz o que foi pedido e nada além. O hook `parecer` local ficou de fora de propósito.
- Nenhuma checagem existente foi afrouxada: as duas regras novas só somam caminhos de aceitação, e cada uma falha fechada.
- Só biblioteca padrão; sem custo; neutro.
- Os testes não dependem da hora atual: os instantes são fixos.

## Riscos
- **Corrida no instante do rótulo:** se houver um push segundos antes do rótulo e a execução dele ainda não existir, o head atribuído é o anterior. A execução do `labeled` então terá outro SHA, e a regra nova falha fechado.
- **Atribuição depende das execuções:** a confiança é a mesma da regra antiga. Se alguém com permissão de administrador apagar execuções, a atribuição pode mudar.
- **Base que mexe perto do trecho do PR** (por exemplo, a mesma seção do `CHANGELOG.md`) muda o contexto do diff e pede o rótulo de novo. Escolhi o rigor.
- **Hook `parecer` local:** continua estrito depois de um merge da `develop`. Se o dono quiser o mesmo comportamento local, isso fica para outro pedido.

Parecer: **aprovado** (parecer de autor; a review independente vem a seguir).

## Review independente

Segunda leitura (outra instância do `forge:tech-lead`) sobre `origin/develop..90705c1`. Testes no checkout do PR: `python3 -m unittest discover -s tests`, 267 OK. Os desvios foram conferidos chamando `mesmo_diff` do `bin/forge-check` do PR em repositórios descartáveis, um por caso, e a semântica de reexecução no histórico real de execuções do repositório (API do Actions).

### Conferidos sem desvio
- **Conteúdo novo no merge:** merge da base com arquivo novo embutido (`merge --no-commit` + edição), conflito resolvido com linha nova, merge que desfaz uma mudança da base e merge de outra branch que não é a base: todos dão `mesmo_diff = False`. O merge limpo da base dá `True`. No CI o head avaliado é o merge commit sintético do GitHub e a base é o primeiro pai dele, então o diff efetivo é sempre "base atual + patch do PR".
- **Comparação dos diffs:** `chmod` (linhas `old mode`/`new mode` ficam), symlink novo ou trocado (`new file mode 120000` fica), binário (`--binary` traz o conteúdo inteiro), submódulo (`Subproject commit`), `.gitattributes` com `-diff` só no worktree e `docs/reviewsX/` (o pathspec não casa prefixo parcial): todos `False`. Base que mexe no contexto do trecho do PR: `False` (falha fechada, como o parecer de autor declara). `--no-renames`, `--no-textconv` e `--no-ext-diff` fecham renomeação e drivers. Remover só as linhas `index ` não esconde conteúdo: linhas do patch começam com `+`, `-` ou espaço, e as do binário não têm espaço.
- **Arquivos de parecer:** nenhum hook, teste ou workflow executa conteúdo de `docs/reviews/` ou `docs/qa/`. O `forge-check` lê só o frontmatter, o hook `conformidade` controla quem grava e a `Neutralidade` já os ignorava (`tests/config.json`).
- **Head no instante do rótulo:**
  - Uma reexecução preserva o `created_at` original. Execuções do repositório com `run_attempt: 2` mantêm o `created_at` da primeira tentativa, mesmo reexecutadas horas depois. Assim, reexecutar um workflow antigo não forja uma execução depois do rótulo.
  - `workflow_dispatch` e outros eventos ficam fora pelo filtro `event=pull_request`.
  - As execuções de outros workflows `pull_request` são criadas pelo servidor com o head real, então contar todas é correto.
  - Um PR de fork vem com `pull_requests` vazio e fica só com a regra antiga.
  - Corrida entre push e rótulo: a execução do `labeled` sai com o SHA novo, e a regra falha fechado.
  - `[skip ci]`: o head sem execução falha fechado, como o teste cobre.
- **Regressão:** `rotulo_liberado` é equivalente ao anterior. Erro de API, falta de token, falta de execução e commit ausente dão `None` ou `False`. Um timestamp malformado lança exceção fora do `try` e derruba o job, o que também é fechado. R-CUSTO continua sem exceção.
- **Parecer:** sem `--base`, o `forge-check pr` continua estrito (teste `test_sem_base_o_merge_da_base_continua_invalidando`). O veredito trocado continua barrando porque é lido no head. O `commit` passa pela regex hexadecimal antes de chegar ao `git`, então não há injeção de opção. No CI, a catraca e o `forge-check` rodam da base (worktree `$RUNNER_TEMP/base`), e o PR não consegue trocar `mesmo_diff` para se aprovar.

### Desvios
1. `tests/catraca.py` (`PARECERES`) · **recomendado** · Depois do rótulo, qualquer arquivo em `docs/reviews/` ou `docs/qa/` muda sem o dono ver, inclusive o parecer de outro pedido. Isso não executa nada, mas permite reescrever o histórico de outro PR. Sugestão: ignorar só os pareceres dos pedidos desta branch (`pedidos_da_branch`) ou exigir que os arquivos ignorados declarem `branch: <ramo>`.
2. `tests/catraca.py` (`rotulo_vale_pelo_conteudo`) · **recomendado** · O rótulo libera a lista de violações do head atual. Depois de um merge da base, essa lista pode ganhar uma violação que não existia quando o dono rotulou, com o mesmo patch: a base cria um invariante novo sobre um texto que o patch do PR já removia. O conteúdo é o mesmo que o dono viu, mas a violação ele não viu. Sugestão: exigir que as violações atuais estejam contidas nas do head rotulado sobre o merge-base dele, ou listar no resumo as violações novas desde o rótulo.
3. Indireção para `docs/reviews/` · **baixo, não bloqueia** · Um symlink ou código aprovado no instante do rótulo que leia um arquivo de `docs/reviews/` passa a carregar conteúdo novo sem invalidar o rótulo. Isso exige que o dono tenha aprovado a indireção. Se o desvio 1 for adotado, ele fica restrito aos pareceres do próprio pedido.
4. Criação de execuções fora de ordem · **residual, não bloqueia** · Se o GitHub atrasar a criação das execuções de um push e adiantar a de um head anterior para depois do rótulo, a atribuição cai no head anterior. Isso depende de um atraso do servidor e de o dono ter visto o head novo antes de qualquer execução dele. Fica registrado como risco.

### Observação para o merge
Em CI roda o `tests/catraca.py` da base, então este PR é julgado pela regra antiga: o rótulo `afrouxa-regra` precisa ser aplicado pelo dono depois do último push, incluindo este commit de review.

Parecer independente: **aprovado** (nenhum desvio bloqueia; 1 e 2 recomendados para um PR próprio). Frontmatter atualizado para o commit revisado `90705c1`.

Revalidado após merge da develop (só CHANGELOG). Commit revisado atualizado para `acf55f0`; o diff efetivo fora de `docs/reviews/` e `CHANGELOG.md` é idêntico ao revisado em `90705c1`.
