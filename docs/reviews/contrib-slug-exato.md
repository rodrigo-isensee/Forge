---
tipo: review
contrato: 1
pedido: contrib-slug-exato
branch: melhoria/contrib-slug-exato
commit: 9c0b341
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
