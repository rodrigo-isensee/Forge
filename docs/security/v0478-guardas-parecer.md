---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: deaf35704182bc20c1bcc2e630f044480e1ddb06
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.34, "Só aperta?")

Volta por delta, com a condição do dono (19/11 09:23): o rótulo `afrouxa-regra` só sai se a brecha da pasta pessoal (A12) estiver fechada e se nada mais passar a ser aceito além das três consultas de só leitura do `gh api` (afrouxamento 2 do parecer `7ffe10ef`). Rodada anterior: `7ffe10ef` (E3.32, no head `946926e9`), no git. Delta lido (`forge-check parecer delta`, `946926e9..deaf3570`): `hooks/parecer.py` (`pasta_do_gh` recusa com `resolvida` falso), `docs/hooks.md` (linha D6) e `tests/test_hooks_parecer_matriz.py` (`SessaoNaCopiaAlheia`). Para a pergunta, refiz a comparação inteira com o hook da `origin/develop` (`c720891e`; o `hooks/` dela é o mesmo da base `4182a6b9`).

Gatilhos: hook de controle (`hooks/parecer.py`, `hooks/_gh_api.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A11 (recomendado) docs/hooks.md:41 · Limites declarados da D4 seguem abertos (nome por expansão na aritmética e valor avaliado como expressão), aceitos pelo critério da D7; o dono confirma pelo Jarvis. Sem mudança desde o parecer `460a8a00`.
- A13 (recomendado) hooks/parecer.py:1306 · A guarda do A12 cobre só o `gh pr`. Numa sessão em cópia alheia, `export HOME; cd ~/proj && gh api -X PUT repos/dono/forge/pulls/1/merge` e o `markPullRequestReadyForReview` por graphql recusavam na develop e passam aqui: o ramo `api` usa a pasta da chamada quando o `cd` não resolve.

## Sondas

## Só aperta?
**Não.** A brecha da pasta pessoal fechou no `gh pr`, mas ela continua aberta no `gh api` mutante: além das três consultas de só leitura, outras entradas que a develop recusava passam a ser aceitas (A13). Pela condição do dono, o rótulo `afrouxa-regra` fica.

Prova de que o A12 fechou (sessão e pasta da chamada na cópia alheia, `HOME={tmp}`, clone em `{tmp}/proj` com `feature/x` sem parecer; develop → este head): `export HOME; cd ~/proj && gh pr ready feature/x` 2 → 2; `: ${HOME:=/x}; cd ~/proj && gh pr ready feature/x` 2 → 2; `export HOME; cd ~/proj && gh pr merge feature/x` 2 → 2; `export HOME; cd ~/proj && gh pr create --base develop --head feature/x` 2 → 2. Este head também recusa formas que já passavam na develop: `HOME=/q; cd ~/proj && gh pr ready feature/x` 0 → 2, `declare HOME; cd ~/proj && gh pr merge feature/x` 0 → 2, `export CDPATH; cd proj && gh pr ready feature/x` 0 → 2. O legítimo `gh pr ready feature/x` na cópia alheia, sem `cd`, dá 0 → 0. `SessaoNaCopiaAlheia`: OK neste head e 4 falhas com o hook da develop.

Comparação das fixtures, refeita no head `deaf3570`: as 583 do `parecer` rodaram contra os dois hooks (a develop rodou da cópia por `git archive` com o `hooks/parecer.py` da `origin/develop` e sem `hooks/_gh_api.py`). 546 dão o mesmo código nos dois. 37 recusam aqui e davam 0 na develop. **Nenhuma** recusava na develop e libera aqui. Nenhuma fixture da develop mudou nem saiu (`git diff --diff-filter=DMR origin/develop...HEAD -- tests/hooks/` vazio). As 6 fixtures de prazo de produção falham igual nos dois lados porque o roteiro de sondas não liga o vigia de produção, e a suíte as roda à parte.

As três consultas de só leitura (afrouxamento 2), reproduzidas no clone (develop → este head): `gh api graphql --input=@q.json` com `q.json` mutante e `@q.json` de leitura, 2 → 0; o mesmo sem `q.json`, 2 → 0; `gh api graphql -F query=x=@y` com `y` de leitura, 2 → 0. Em nenhuma das três o gh manda mutação. `--input=@q.json` com `@q.json` mutante dá 2 → 2, e `-F query=x=@y` com `y` mutante também dá 2 → 2.

O que mais passou a ser aceito (A13). Mesma montagem da cópia alheia, develop → este head:
- `export HOME; cd ~/proj && gh api -X PUT repos/dono/forge/pulls/1/merge`: 2 → 0
- `: ${HOME:=/x}; cd ~/proj && gh api -X PUT repos/dono/forge/pulls/1/merge`: 2 → 0
- `export HOME; cd ~/proj && gh api -X POST repos/dono/forge/pulls/1/merge`: 2 → 0
- `export HOME; cd ~/proj && gh api -X PUT repos/{owner}/{repo}/pulls/1/merge`: 2 → 0
- `export HOME; cd ~/proj && gh api graphql -f query='mutation{markPullRequestReadyForReview(…)}'`: 2 → 0
- `export HOME; cd ~/proj && gh api graphql --input q.json` com `q.json` mutante: 2 → 0

As fixtures não cobrem esse cruzamento (`cd` sem resolver + `gh api` + sessão em cópia alheia), e por isso a comparação por fixtures não o mostra. Com a sessão no clone, `export HOME; cd ~/proj && gh api -X PUT …/merge` dá 2 nos dois.

## Detalhe dos achados
**A13 (baixa, recomendado).** Evidência: `hooks/parecer.py:1291` (`raiz_gh = pasta or hook.cwd()`) e `:1306` a `:1309`. O ramo `api` passa a `raiz_gh` direto para `merge_por_api`, `arquivo_trocado_na_linha` e `pronto_por_graphql`, sem o `pasta_do_gh` que recebeu a guarda do A12 (`:1065`). O mesmo mecanismo do A12: as mexidas novas de `HOME` e `CDPATH` deixam o `cd` sem resolver, a pasta da chamada é uma cópia alheia que não é projeto, e as três funções saem sem conferir. Caminho de ataque: o agente, numa sessão aberta num repositório que não é projeto do Forge, mescla ou tira do rascunho um PR do Forge pela API depois de `cd ~/clone` com uma mexida de `HOME` antes. Não dá capacidade nova: na develop, da mesma sessão, já davam 0 `gh api -X PUT repos/dono/forge/pulls/1/merge` sem `cd` (o endpoint traz o repositório), `HOME=/q; cd ~/proj && gh api -X PUT repos/dono/forge/pulls/1/merge`, `declare HOME; cd ~/proj && gh api -X PUT …/merge`, `export CDPATH; cd proj && gh api -X PUT …/merge` e o graphql sem `cd` (o id do PR é global). O `gh api` fora da cópia é limite declarado (`docs/hooks.md`, "Fora:"). Por isso fica como recomendado, mas a resposta à pergunta do dono é não. Correção mínima: no ramo `api` (`:1306`), com `pasta` None e a sessão numa cópia alheia sem clone (a condição de `:1064`), recusar o que `merge_por_api` e `pronto_por_graphql` recusariam num clone: endpoint de merge com método mutante e `gh api graphql`. Fixtures das quatro mexidas (`export HOME`, `${HOME:=v}`, `HOME=`, `declare HOME`) e de `export CDPATH`, cruzadas com `-X PUT`, `-X POST`, `{owner}/{repo}`, `-f query=` e `--input`, mais o legítimo `gh api repos/dono/forge/pulls` (GET) depois do mesmo `cd`. Esforço P. Dono: o autor do pedido. Fechado o A13, a resposta passa a sim; a prova se refaz com as sondas acima.

## Estado dos achados anteriores
- **A12:** fechado no `gh pr` (`hooks/parecer.py:1065`, `SessaoNaCopiaAlheia`); a parte do `gh api` vira o A13.
- **A11:** aberto como recomendado, sem delta.
- **A1 a A10:** fechados; o delta não toca neles.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. As sondas foram fixtures locais fora do repositório, montadas pelo `Fixture` de `tests/test_hooks.py` com a base `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia`. A suíte inteira roda no CI, e o brief não cita CI deste head. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
