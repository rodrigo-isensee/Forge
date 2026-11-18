---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: c41f7fe58808dfae86c046611c39ee4de9825098
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.8, revalidação)

Volta por delta. Rodada anterior: `commit d8e9aa8b`, no git (E3.4). Delta lido (`forge-check parecer delta`, `d8e9aa8b..c41f7fe5`): no domínio, `hooks/parecer.py` (`remotos`, `sessao_ou`, `pasta_do_gh`, `graphql_no_clone`, `arquivo_trocado_na_linha`, `acompanhado` em `conferir_linha`/`conferir`), 15 fixtures novas `incidente-r-copia-alheia-*` e `graphql-*` e `tests/test_hooks_parecer_repo.py`. Fora do domínio, não relido: changelog, `docs/hooks-fixtures.md` e `tests/mutantes/*`.

## Gatilhos
Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A5 (bloqueante) hooks/parecer.py:932 · Na cópia alheia, GH_REPO exportado na linha (`export GH_REPO=dono/forge; gh pr ready feature/x`, `&&`, `declare -x`, `set -a`) não conta como repositório indicado: o PR do Forge sai do rascunho sem parecer (S6 a S9). Mesmo cartão e caminho do A1.

## Sondas
- S6 · cwd={tmp}/alheio (remoto outro/coisa), sessão no clone dono/forge, sem parecer: `export GH_REPO=dono/forge; gh pr ready feature/x` · espera: código 2 (R-REVIEW) · obtido: código 0
- S7 · cwd={tmp}/alheio: `export GH_REPO=dono/forge && gh pr merge feature/x` · espera: código 2 · obtido: código 0
- S8 · cwd={tmp}/alheio: `declare -x GH_REPO=dono/forge; gh pr ready feature/x` · espera: código 2 · obtido: código 0
- S9 · cwd={tmp}/alheio: `GH_REPO=dono/forge; export GH_REPO; gh pr ready feature/x` · espera: código 2 · obtido: código 0

## Estado dos achados anteriores
- **A1 (bloqueante): fechado nas formas da rodada.** S1 a S5 refeitas no head: todas dão 2 (S1 a S3 e S5 com R-REVIEW sem parecer; S4 com R-CONTRIB, PR só por número). Também dão 2 `--repo=`, `-R` colado, `env GH_REPO=`, `-R https://github.com/...`, `-R github.com/...` e `-R Dono/Forge`. A forma exportada do GH_REPO continua aberta e vira o A5.
- **A2 (recomendado): fechado.** Cópia sem manifesto com remoto do clone (`origin` ssh, `origin` https, ou só no `upstream`): `gh pr ready feature/x` dá 2.
- **A3 (recomendado): fechado.** `markPullRequestReadyForReview` com cwd `{tmp}` e na cópia alheia dá 2. A consulta de leitura na cópia alheia passa (0).
- **A4 (recomendado): fechado.** `cp`, `--field=`, `>` com `--input`, `ln -sf`, substituição, crase e pipeline na mesma linha do `gh api graphql` com arquivo dão 2. Só `cd` antes passa (0).
- Corpus de legítimos conferido: cópia alheia sem -R e sem remoto do clone (0), `gh pr view -R` (0), `gh pr ready --undo -R` e `gh pr create --draft -R` (0, nenhum dos dois tira do rascunho).

## Detalhe dos achados
**A5 (alta, bloqueante).** Evidência: `hooks/parecer.py:932` e `hooks/parecer.py:389`. O repositório do `gh pr` vem do `-R`, do `--repo` ou do prefixo `GH_REPO=` do próprio comando. O GH_REPO exportado antes na linha não entra em `repo`, e `GH_REPO` não está em `SENSIVEIS` (`hooks/parecer.py:112`). Na cópia alheia, `pedido` fica None e os remotos não batem, então a função devolve `pasta` (a cópia alheia), `hook.projeto` dá None e o hook libera. O gh lê o GH_REPO do ambiente e age no repositório do Forge. Fora de cópia de trabalho a mesma linha já dá 2, pela falha fechada de `pasta_do_gh` (sonda feita no head; na develop 4182a6b9 dava 0). O efeito é o do incidente: o agente recebe a recusa, roda `git init "$TMPDIR/x"` e, na chamada seguinte, `cd "$TMPDIR/x" && export GH_REPO=<dono>/<forge>; gh pr ready <branch>`. O PR sai do rascunho sem parecer, e `gh pr merge` passa da mesma forma (S7). Já valia em d8e9aa8b e na develop. Faltou na matriz da rodada anterior, que listava só "`GH_REPO=` na linha": a dimensão **origem do alvo** ganha a linha "GH_REPO exportado na linha (`export`, `declare -x`, `typeset -x`, `set -a` com atribuição, atribuição solta seguida de `export GH_REPO`)".

Correção mínima: inclua `GH_REPO` em `SENSIVEIS` (assim `mexidas_na_linha` já pega `export`, `declare`, `set -a` e a atribuição). Em `pasta_do_gh`, trate `GH_REPO` em `mexidas` como repositório indicado e desconhecido: confira no clone da sessão só se o valor puder ser lido com certeza, senão recuse (`bloquear`). A sonda com GH_REPO no ambiente da sessão também dá 0 na cópia alheia. Ninguém o põe lá pela linha, mas pela mesma correção, considere `os.environ.get("GH_REPO")` quando não houver `-R`. Fixtures novas: S6 a S9 com recusa e a variante fora de cópia de trabalho. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As sondas rodaram com o lançador da suíte (`tests/test_hooks.py`: `Fixture.montar`, `rodar`), por um script local fora do repositório. Base: a fixture `incidente-r-copia-alheia-ready-r-bloqueia.json`, variando o cwd, o comando e os remotos. Rodaram no head, em d8e9aa8b e na develop 4182a6b9 (`git archive`). Teste rodado: `python3 -m unittest tests.test_hooks_parecer_repo` (OK, 5 testes). A suíte inteira roda no CI, e este head não tem CI (o brief diz "sem suíte local"). Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
