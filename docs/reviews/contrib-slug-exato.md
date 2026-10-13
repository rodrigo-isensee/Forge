---
tipo: review
contrato: 1
pedido: contrib-slug-exato
branch: melhoria/contrib-slug-exato
commit: d147b09
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: Forge como alvo só pelo slug exato (`R-CONTRIB`)

Corrige o falso positivo apontado na review do #89 (recomendação 1 de `contrib-sessao-forjavel.md`).

- **Mudança:** `parecer.aponta_para_o_forge` deixa de usar `slug in texto` e passa a casar `dono/repo` exato, sem diferenciar maiúsculas, com fronteira (`(?<![\w.-])slug(\.git)?(?![\w.-])`). Início, `/`, `:`, espaço, aspas, `=` e fim são fronteiras; `-`, `.` e letras coladas ao slug não são. `.git` e `/` finais seguem aceitos em https, ssh e `git@`.
- **Vermelho antes:** com as fixtures e sem a correção, falharam `contrib-slug-sufixo-hifen-pr-merge-libera`, `contrib-slug-sufixo-letra-pr-merge-libera` e `contrib-slug-sufixo-hifen-R-libera`. As fixtures de push dos três repositórios foram depois ajustadas para branch alheia, que a substring barrava.
- **Verde depois:** 281 testes e `scripts/validar-plugin.sh` passam.
- **Não afrouxa além do falso positivo:** continuam barrados `-R <dono>/FORGE`, `.../Forge.git`, origin `git@github.com:<dono>/Forge.git`, origin com `/` final e `{owner}/{repo}` com origin no Forge.
- **Atenção do dono:** altera `hooks/parecer.py` (protegido); exige o rótulo `afrouxa-regra`.

## Review independente
Revisor: `forge:tech-lead`, sem participação na autoria. Diff do PR #90 lido por inteiro; head revisado `d147b09`.

- **Testes:** `python3 -m unittest discover -s tests` no checkout do PR: 281 testes, OK.
- **Bloqueia, nenhuma escapou** (slug `rodrigo-isensee/forge`, chamando `aponta_para_o_forge`): https com `.git`, `/`, `/.git/`, `?x` e `#x`; `git@github.com:<slug>.git`; `ssh://git@github.com/<slug>` e com porta; slug sozinho; `-R <slug>`; `--repo=<slug>`; `repos/<slug>/pulls`; aspas simples e duplas; caixa alta e baixa. `{owner}/{repo}` segue coberto pelo ramo do `cwd`/origin, intocado pelo diff, e pela fixture `contrib-slug-placeholders-bloqueia`.
- **Libera:** `<dono>/Forge-site`, `<dono>/ForgeX`, `<dono>/meu-Forge`, a URL `.../Forge-site.git` e `<dono>/Forge.x`.
- **Regex:** `(?<![\w.-])slug(\.git)?(?![\w.-])` sobre texto em minúsculas; `re.escape` no slug, que sai do `plugin.json` (sem termo fixo no código, `R-NEUTRO`). Fronteira à direita só deixa passar `.git`, `/`, `?`, `#`, `:`, espaço, aspas e fim.
- **Sem custo e sem afrouxar além do pedido:** só `hooks/parecer.py` e fixtures; CHANGELOG em `[Não publicado]`.
- **Observação não bloqueante:** `Forge.git` repetido ou `forge.git.bak` colado são tratados como outro repositório, coerente com o GitHub.

Parecer: **aprovado**. Pendência de processo: rótulo `afrouxa-regra` do dono, pois altera `hooks/parecer.py`.
