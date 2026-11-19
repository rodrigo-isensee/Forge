---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 993b6bb3f3a514753a8f21f0dcceb216f2791d67
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.38, "Só aperta?")

Volta por delta, com a condição do dono (19/11 09:23): o rótulo `afrouxa-regra` só sai se a segurança confirmar por escrito que nada mais passou a ser aceito além das três consultas de só leitura do `gh api`. A rodada anterior é a `3448e7cc` (E3.34, head `deaf3570`) e está no git. Delta lido (`forge-check parecer delta`, `deaf3570..993b6bb3`): `hooks/parecer.py` (`api_depois_de_cd_sem_resolver` e `tira_o_rascunho`, chamada em `:1331`), `docs/hooks.md:43` (D6) e `tests/test_hooks_parecer_matriz.py` (`gerar_sessao_alheia`, `SessaoNaCopiaAlheia`). Os mutantes e o fragmento do changelog ficam fora do domínio. Para a pergunta do dono, refiz a comparação inteira com o hook da `origin/develop` (`c720891e`).

Gatilhos: hook de controle (`hooks/parecer.py`, `hooks/_gh_api.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A11 (recomendado) docs/hooks.md:41 · Limites declarados da D4 seguem abertos (nome por expansão na aritmética e valor avaliado como expressão), aceitos pelo critério da D7; o dono confirma pelo Jarvis. Sem mudança desde o parecer `460a8a00`.

## Sondas

## Só aperta?
**Sim, com a única exceção já conhecida.** Comparei este head com o hook da `origin/develop` e só três entradas passaram a ser aceitas: as três consultas de só leitura do `gh api` (afrouxamento 2). Nenhuma outra entrada que a develop recusava é aceita aqui. O A13 fechou. Pela condição do dono, o rótulo `afrouxa-regra` pode sair.

Montagem: duas árvores por `git archive 993b6bb3`. Numa, os hooks são os deste head. Na outra, a pasta `hooks/` inteira é a da `origin/develop`, sem `hooks/_gh_api.py`. As duas usam os mesmos testes e as mesmas fixtures deste head. Os resultados vão abaixo como "develop → este head".

1. **Fixtures.** As 583 fixtures do `parecer` rodaram nos dois hooks. 546 dão o mesmo código. 37 recusam aqui e davam 0 na develop. **Nenhuma** recusava na develop e passa aqui. Nenhuma fixture da develop mudou nem saiu (`git diff --diff-filter=DMR origin/develop...HEAD -- tests/hooks/` vazio). As fixtures de prazo de produção falham igual nos dois lados porque o roteiro não liga o vigia de produção, e a suíte as roda à parte.
2. **D6, gerador do head mais 21 extras.** São 140 linhas, nas sessões em cópia alheia, fora de cópia de trabalho e no clone. 98 dão o mesmo código. 42 recusam aqui e davam 0 na develop. **Nenhuma** passa a ser aceita.
3. **As seis formas do A13 × as cinco mexidas.** Sessão e pasta da chamada na cópia alheia, `HOME={tmp}`, clone `dono/forge` sem parecer em `{tmp}/proj`. Formas: `gh api -X PUT repos/dono/forge/pulls/1/merge`, `-X POST …/merge`, `-X PUT repos/{owner}/{repo}/pulls/1/merge`, `repos/dono/forge/pulls/1/merge -f merge_method=squash`, `graphql -f query='mutation{markPullRequestReadyForReview(…)}'` e `graphql --input q.json` com `q.json` mutante.
   - Com `export HOME; cd ~/proj` e com `: ${HOME:=/x}; cd ~/proj`: 2 → 2 nas seis. No head `deaf3570`, as seis davam 0.
   - Com `HOME={tmp}; cd ~/proj`, `declare HOME; cd ~/proj` e `export CDPATH; cd proj`: 0 → 2 nas seis. Aqui o hook aperta.
   - Com a sessão fora de cópia de trabalho, o resultado é o mesmo: as duas primeiras mexidas dão 2 → 2 e as outras três dão 0 → 2.
   - Variantes fora do gerador, nas duas sessões e com as cinco mexidas: `--method PUT`, `-XPUT`, `graphql --input=q.json`, `-Fquery=@q.json` e `-f query="$(cat q.json)"`. Nenhuma passa a ser aceita: 2 → 2 ou 0 → 2.
4. **Leituras depois do mesmo `cd`.** Nas duas sessões e com as cinco mexidas, dão 0 → 0: `gh api repos/dono/forge/pulls`, o GET de `…/pulls/1/merge` e `graphql -f query='query{viewer{login}}'`.
   - O `gh api graphql` com `mergePullRequest` e o `-X GET graphql` com a mutação de pronto também dão 0 → 0. Esses casos ficam com o `conformidade` (`GRAPHQL_PERIGOSO`) e com o GET, que não muda nada, nos dois lados.
   - Os controles também não mudam. Sem `cd` (cópia alheia e fora), as seis formas dão 0 → 0: é o limite declarado em "Fora:" do `docs/hooks.md`. Com o `cd` literal ou `cd ~/proj` sem mexida, dão 2 → 2 (R-CONTRIB). Com a sessão no clone, também 2 → 2 (R-CONTRIB).
5. **As três consultas de só leitura (afrouxamento 2).** Reproduzidas no clone, develop → este head:
   - `gh api graphql --input=@q.json` com `q.json` mutante e `@q.json` de leitura: 2 → 0.
   - O mesmo sem `q.json`: 2 → 0.
   - `gh api graphql -F query=x=@y` com `y` de leitura: 2 → 0.
   - Em nenhuma das três o gh manda mutação. Os controles seguem recusando: `--input=@q.json` com `@q.json` mutante dá 2 → 2, e `-F query=x=@y` com `y` mutante também dá 2 → 2.
6. **Teste novo.** `SessaoNaCopiaAlheia` dá OK neste head e 66 subtestes falham com o hook da develop.

A guarda nova só chama `bloquear` ou retorna, e `tira_o_rascunho` é o mesmo trecho que antes ficava dentro de `pronto_por_graphql`. Erro interno com `gh api` cai na falha fechada do `_comum` (ADR 0009, seção 7). Por construção, o delta não abre entrada nova, e as sondas acima confirmam isso.

## Estado dos achados anteriores
- **A13:** fechado em `hooks/parecer.py:1150` e `:1331`, com `gerar_sessao_alheia` e as sondas 3 e 4 acima.
- **A12:** fechado (rodada `3448e7cc`); o delta não o toca.
- **A11:** aberto como recomendado, sem delta.
- **A1 a A10:** fechados; o delta não toca neles.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. As sondas foram fixtures locais em `$TMPDIR/v0478-e338-seg`, fora do repositório, montadas pelo `Fixture` de `tests/test_hooks.py` com a base `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia`. A suíte inteira roda no CI, e o brief não cita CI deste head. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
