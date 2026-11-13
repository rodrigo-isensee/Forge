---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: abfccb7e24fb7ef005e53080d81d60c3896234cc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.41, conformidade-curinga, volta 5 do furo A11)

Delta revisado: `b283521c..abfccb7e` (3 commits: `15dfdc3a`, `f84306a6`, `abfccb7e`), lido por `forge-check parecer delta` e numa worktree destacada. No domínio: `hooks/conformidade.py` (`COLCHETE_DE_DIGITO`, `sem_caixa` e `origem_so_generica`) e as 12 fixtures `gitcomum-v3-*` novas. A spec de mutantes `-6` (G34 a G39) fica com o QA.

Veredito: **aprovado** (DECISÃO DO DONO de 12/11 18:20, opção A). A volta 5 fecha o A11. Resto com `[` não se libera mais, salvo o colchete só de dígitos e hífen, que o bash e o glob do Python leem igual. Com `?` e `*`, cada letra casa as duas caixas, o que cobre `nocaseglob`. As grafias S10 a S14 da volta 4 e as variações pedidas recusam (rc 2). Os legítimos `HEA?` e `HEAD[0-9]` seguem livres. O delta não abriu caminho novo. Fica um resíduo antigo que o delta não toca (A15, recomendado): no `--git-dir` de uma worktree ligada, `../../config` sai para o `.git` comum, e isso já passava na develop.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de link e de escrita em `.git/`), analisador de comando.

## Achados
- A14 (recomendado) hooks/conformidade.py:1059 · segue (fora do delta, cartão próprio): curinga num componente de pasta ou no nome de outro protegido não é expandido (`ln .g?t/config h`, `cp x .g?t/config`, `cp x .forge/c?nfig.json`)
- A15 (recomendado) hooks/conformidade.py:1049 · já existia (develop c340c322): numa worktree ligada o hook lê o `--git-dir` como <raiz>/.git; `ln "$(git rev-parse --git-dir)"/../../config h` dá rc 0 e o link é o .git/config comum; também hooks/ e `cp -l` por variável (AR-7); cartão

## Sondas

## Detalhe dos achados
Método: o montador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), papel `forge:tech-lead`, projeto em `melhoria/x` e worktree em `melhoria/w`. Cada comando rodou no hook e depois no bash do mesmo repositório temporário. Comparei o inode de `h` com o dos arquivos do `.git`. Foram 61 casos no head `abfccb7e`; os do A15 também rodaram no `9bd83404` e na develop `c340c322`.

**A11 (fechado).** Evidência: `hooks/conformidade.py:1097` recusa o resto com `[` depois de tirar os colchetes de dígitos. `:1103` passa o resto por `sem_caixa` (`:362`) antes do glob. `:1104` busca no `.git` da raiz e no diretório comum sem exigir `is_dir()`. Resultado das sondas:
- Recusam (rc 2) e, no bash, o link seria o `.git/config` ou um arquivo de `.git/hooks/`: `[^x]onfig`, `co[^x]fig`, `[!x]onfig`, `[[:alpha:]]onfig`, `[[:lower:]]onfig`, `[[=c=]]onfig`, `[[.c.]]onfig`, `[c1]onfig`, `[1c]onfig`, `[0-9c]onfig` e `[--z]onfig`.
- Também recusam `[^x]ooks/…` e `hooks/[^x]re-commit.sample`, e, com `nocaseglob`, `CONFI?`, `CONF*G`, `*ONFI?`, `HOOK?/…` e `hooks/PRE-COMMIT.SAMPL?`.
- Recusam por variável (`ln`, `cp -l`, `ln -s`, `cp -s`), por `--git-common-dir` e `--absolute-git-dir`, numa worktree (`[^x]onfig` e `CONFI?` no diretório comum) e com `globstar` (`**/pre-commit.sample`).
- As sondas da volta 3 (S6 a S9) e da volta 4 (S10 a S14) recusam.

Colchete de dígitos: bash e Python leem igual `[0-9]onfig`, `[0-9-]onfig`, `con[0-9]ig`, `[0-9]]onfig`, `conf[0-9]*g`, `c?nfig[0-9]`, `*[0-9]*/config`, `[1-9]*/c*` e, com `nocaseglob`, `[0-9]*ONFIG`. Nenhum cai em arquivo protegido (rc 0 no hook, nada casa no bash). O colchete misto (`[[0-9]onfig`) recusa.

Legítimos livres: `HEA?` e `HEAD[0-9]`. A grafia `[^x]EAD` passou a recusar; é falha fechada aceitável, sem uso no corpus. O `ln "$(git rev-parse --git-dir)"/HEAD h` segue livre, como deve. As grafias extglob recusam pela regra genérica.

O delta não abriu caminho novo. `sem_caixa` só alarga o casamento, ou seja, falha fechada. Sem `is_dir()`, a base inexistente devolve glob vazio, como antes.

**A15 (alta, recomendado; já existia na develop `c340c322` e no `9bd83404`, fora do delta e da dimensão do A11; classe AR-7).** Evidência: `hooks/conformidade.py:1049` troca o `DIR_DO_GIT` por `<raiz>/.git`. Numa worktree ligada, esse caminho é um arquivo, e o `--git-dir` real é `<comum>/worktrees/<nome>`. Assim, `"$(git rev-parse --git-dir)"/../../config` resolve, para o hook, a uma pasta acima da raiz, fora de qualquer regra. No bash, a mesma grafia chega ao `.git/config` comum. Provas: rc 0 no hook, e no bash `h` tem o inode do `.git/config`. O mesmo vale para `../../hooks/pre-commit.sample` e para `d=$(git rev-parse --git-dir); cp -l "$d"/../../config h`. Os três casos também passam no `9bd83404` e na develop.

Caminho de ataque: é o do A11. O agente trabalha numa worktree, que é o modo normal do Forge. Ele cria o link e grava no `.git/config` comum num comando seguinte, por exemplo para mudar `core.hooksPath`. Não bloqueia porque não foi aberto pelo delta e não é a grafia de curinga que esta volta corrige. É o mesmo critério do A13 e do A14.

Correção mínima: com `DIR_DO_GIT` vindo de `--git-dir` numa worktree ligada (`.git` da raiz é arquivo), resolver a sentinela para o `--git-dir` real, ou seja, o `gitdir:` do arquivo `.git`. Também conferir o caminho normalizado contra as regras do diretório comum. O que sai do `--git-dir` com `..` e não se resolve recusa. Fixture: os três casos acima. Esforço P. Dono: tech-lead.

**A14 (recomendado, segue).** Sem mudança no delta. Mantém a correção e o cartão da volta 4.

**Achados antigos (A12, A13, A4 a A10).** Não pioraram no delta.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O portão é o CI do PR (bateria completa). Na máquina rodaram `python3 -m unittest tests.test_hook_git_comum` (1 OK, todas as fixtures `gitcomum-*`) e `tests.test_conformidade_verde` (11 OK). Ferramentas usadas: `git worktree` destacada (head, `9bd83404` e develop), o montador de fixtures e o bash, só em repositórios temporários. `gitleaks`, `semgrep`, `zizmor` e `actionlint` não rodaram: o delta não toca workflow nem segredo, e nada foi instalado (`R-CUSTO`).
