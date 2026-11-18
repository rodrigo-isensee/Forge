---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.4)

Escopo: `4182a6b9..d8e9aa8b` (`hooks/parecer.py`, `hooks/_gh_api.py` novo, fixtures `incidente-r-*` e `leitura-api-*`, mutantes, `bin/forge-testes`). Duas guardas de controle: INCIDENTE-HOOK-PARECER-CONTORNADO (`pasta_do_gh`) e GH-API-LEITURA-UNICA (`textos_do_gh_api`).

## Gatilhos
Gatilhos: hook de controle (`hooks/parecer.py`, `hooks/_gh_api.py`) que guarda o portão de parecer de todos os projetos e do Forge; `bin/forge-testes` (mapa de testes).

## Achados
- A1 (bloqueante) hooks/parecer.py:911 · Brecha do -R só fecha fora de repositório git: numa cópia de trabalho alheia (fora do clone e de projeto), `gh pr ready/merge/create` com -R, --repo, GH_REPO= ou URL do PR ainda passa sem parecer (S1 a S5); o cartão pede ler o repositório do -R e conferir nele.
- A2 (recomendado) hooks/parecer.py:911 · Cópia de trabalho sem o manifesto do Forge e com remoto do Forge: `gh pr ready <branch>` sem -R passa sem parecer (o gh age no PR do Forge). Já existia na develop 4182a6b9; mesma dimensão do A1 (alvo vindo do remoto da cópia).
- A3 (recomendado) hooks/parecer.py:973 · `gh api graphql` com markPullRequestReadyForReview rodado fora do clone (ex.: cwd no $TMPDIR) libera, e o `conformidade` também libera na sessão do Forge; o graphql não depende da pasta. Já existia na develop; vira cartão próprio.
- A4 (recomendado) hooks/_gh_api.py:56 · TOCTOU na mesma linha: `cp m q && gh api graphql -F query=@q` (ou `--field=query=@q`, `>`, `ln -sf`) troca o arquivo depois da leitura do hook e libera. Já valia para -F na develop; o --field só passa a igualar o -F.

## Sondas
- S1 · cwd={tmp}/alheio (git init, remoto outro/coisa), sessão no clone com remoto dono/forge, sem parecer: `gh pr ready -R dono/forge feature/x` · espera: código 2 (R-REVIEW, sem parecer) · obtido: código 0
- S2 · cwd={tmp}: `cd {tmp}/alheio && gh pr ready --repo dono/forge feature/x` · espera: código 2 · obtido: código 0
- S3 · cwd={tmp}/alheio: `GH_REPO=dono/forge gh pr merge feature/x` · espera: código 2 · obtido: código 0
- S4 · cwd={tmp}/alheio: `gh pr merge https://github.com/dono/forge/pull/5` · espera: código 2 · obtido: código 0
- S5 · cwd={tmp}/alheio: `gh pr create -R dono/forge --base develop --head feature/x` · espera: código 2 · obtido: código 0

## Detalhe dos achados

**O que fecha (conferido).** Fora de repositório git, o incidente de 12/11 fecha: `gh pr ready -R dono/forge feature/x` com cwd `{tmp}` dava 0 na develop 4182a6b9 e dá 2 no head (sonda feita nos dois). A leitura do `gh api` recusa: `--field=query=@~/q.graphql` (til), `--field=query=@q*.graphql` (curinga), `--field=query=@f` com `f` FIFO (recusa sem esperar o escritor, `ler_regular` com `O_NONBLOCK` e `fstat`), `cd "$D" && gh api graphql --field=query=@q.graphql` (pasta não resolvida) e `--input=@q.graphql` (lê `@q.graphql`, ausente); todas dão 2. O legítimo passa: `-F query=@q.graphql` e `--field=query=@q.graphql` com consulta de leitura dão 0, e com a mutação no arquivo dão 2. `tests.test_hooks_parecer_repo` (o teste de abuso novo) roda verde: 4 testes, OK.

**`--field=campo=@arq`, a única coisa que libera mais.** Não abre caminho novo. O hook corta no primeiro `=@`; o gh corta a chave no primeiro `=` e só lê arquivo quando o valor começa com `@`. Quando o gh lê arquivo, o primeiro `=` vem logo antes do `@`, então os dois leem o mesmo nome. Nos casos em que o gh não lê arquivo (`-F a=b=@c`, `-f`/`--raw-field c=@a`, `--field=@q` sem chave, que o gh rejeita), o hook lê a mais e só fica mais estrito. Antes, `--field=query=@q` recusava só porque procurava o arquivo `query=@q`, que não existe, e não por uma guarda. A forma equivalente `-F query=@q` já liberava do mesmo jeito. O único risco que sobra vale para as duas formas e já existia antes (A4).

**A1 (alta, bloqueante).** Evidência: `hooks/parecer.py:911`. Em `pasta_do_gh`, `if copia_de_trabalho(pasta) is not None: return pasta` devolve a cópia alheia, e depois `hook.projeto(...)` dá None, então `pull_request`, `pronto_de_pr` e `merge_de_pr` liberam. O -R, o GH_REPO e a URL trocam o alvo do gh seja qual for a pasta, e é isso que o cartão INCIDENTE-HOOK-PARECER-CONTORNADO pede conferir. Caminho de ataque: o agente recebe a recusa de `gh pr ready`, roda `git init "$TMPDIR/x"` numa chamada e, na seguinte, `cd "$TMPDIR/x" && gh pr ready -R <dono>/<forge> <branch>`. O PR sai do rascunho sem parecer, que é o mesmo efeito do incidente com um passo a mais (S1 a S5; a develop dava 0 no S1 também). Correção mínima: em `pasta_do_gh`, devolva a cópia só quando `slug(repo)` for None ou quando `hook.projeto(pasta, clone_do_forge=True)` não for None. Nos outros casos (cópia alheia com -R, `--repo`, `--repo=`, `GH_REPO=` ou URL), siga o caminho já escrito: clone da sessão com remoto do slug, ou `bloquear`. A fixture `incidente-r-ready-no-clone-outro-repo-libera` continua passando, porque a pasta é o clone. Fixtures novas: S1 a S5 com recusa, cópia alheia com -R de repositório que a sessão não tem com recusa, e cópia alheia sem -R liberando. Esforço P. Dono: tech-lead.

Matriz da família (dimensão nova, para o modelo `docs/security/hk3-parecer-ameacas.md`): **pasta do gh** {fora de cópia de trabalho, cópia alheia, clone do Forge, projeto ativo, projeto com `hooks_desligados`} × **origem do alvo** {-R, `-R=`, `--repo`, `--repo=`, `GH_REPO=` na linha, URL do PR, remoto da cópia} × **subcomando** {`create`, `create --draft`, `ready`, `ready --undo`, `merge`}. O head cobre só a primeira linha da pasta.

**A2 (média, recomendado).** Evidência: `hooks/parecer.py:911`. Cópia com `.git` e remoto `git@github.com:dono/forge.git`, sem `.claude-plugin/plugin.json`: `gh pr ready feature/x` dá 0 no head e na develop. O caminho de ataque é o do A1, sem -R (`git init` e `git remote add`). Correção mínima: no mesmo ramo da cópia alheia do A1, compare também os slugs dos remotos da cópia com os do clone da sessão. Com remoto igual, confira no clone. Esforço P. Dono: tech-lead. Fica recomendado porque o cartão fala do -R. Sai junto com o A1 se o dono quiser.

**A3 (média, recomendado).** Evidência: `hooks/parecer.py:973`. `pronto_por_graphql` só age se a pasta for o clone do Forge, mas `gh api graphql` não usa a pasta. Com cwd `{tmp}`, a mutação `markPullRequestReadyForReview` dá 0 no `parecer` e no `conformidade` (sondado nos dois hooks, sessão no clone). Já existia na develop. Correção mínima: pasta fora de cópia de trabalho ou cópia alheia com sessão no clone do Forge vale o clone da sessão, como faz o `pasta_do_gh`. Esforço P. Dono: tech-lead, num cartão novo (fora do escopo da E3).

**A4 (baixa, recomendado).** Evidência: `hooks/_gh_api.py:56`. O hook lê o arquivo antes da linha rodar. Uma escrita no mesmo arquivo antes do gh (`cp`, `mv`, `>`, `tee`, `ln -sf`) passa: `cp m.txt q.graphql && gh api graphql -F query=@q.graphql` dá 0 no head e na develop. Correção mínima: considere ilegível o arquivo de `-F`/`--input` que a mesma linha escreve antes do `gh api` (destino de redireção ou último argumento de `cp`, `mv`, `ln`, `tee`, `install`, `dd of=`, `sed -i`), ou o arquivo de qualquer linha que tenha escrita a caminho não resolvido. Esforço M. Dono: tech-lead, cartão novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As sondas rodaram com o próprio lançador da suíte (`tests/test_hooks.py`: `Fixture.montar` e `rodar`), no head e numa cópia da develop 4182a6b9 (`git archive`), por um script local fora do repositório. Teste rodado: `python3 -m unittest tests.test_hooks_parecer_repo` (OK, 4 testes). A suíte inteira roda no CI e não há PR nem CI deste head (o brief diz "sem suíte local"). Lacuna: `gitleaks` e `semgrep` não estão no PATH. A mudança não traz segredo nem dependência.
