---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.3 (melhoria/v0478-guardas-parecer)

## Achados
- A1 (bloqueante) hooks/parecer.py:911 · pasta_do_gh só usa o -R fora de qualquer .git: de dentro de outro repositório não-Forge (até um .git falso), gh pr merge/ready/create --repo dono/forge passa sem parecer (S1-S3; R-REVIEW). Com -R/URL que casa remoto do clone da sessão, confira no clone em qualquer pasta.

## Sondas
- S1 · cwd {tmp}/outro (só .git/HEAD), sessão no clone com remoto dono/forge, gh pr merge --repo dono/forge feature/x --squash, sem parecer · espera: código 2 (R-REVIEW) · obtido: código 0
- S2 · mesma montagem, gh pr ready --repo dono/forge feature/x · espera: código 2 · obtido: código 0
- S3 · mesma montagem, gh pr create --repo dono/forge --head feature/x --base develop -t t -b b · espera: código 2 · obtido: código 0

## Conferências
- Controle: a fixture `incidente-r-merge-fora-sem-parecer-bloqueia` com cwd `{tmp}` (fora de qualquer `.git`) barra (código 2); a S1 muda só o cwd para uma pasta com `.git` de outro repositório.
- Guardas movidas (pedido do autor): `bin/forge-mutante --cobertura --base 4182a6b9` no head d8e9aa8b lista as 12 linhas como `movida · hooks/parecer.py:<L>(base) · hooks/_gh_api.py:<L>`, cada destino `coberta` por mutante declarado; nenhuma `apagada` nem `sem mutante`. A atribuição de linha é por contagem de texto (a 805 da base, `if i + 1 < len(args)`, conta pela cópia que saiu da linha 950; em `parecer.py` o texto cai de 3 para 2 ocorrências), coerente. A leitura de "apagadas" da catraca é falso positivo da mudança de arquivo.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_repo`: 4 testes, OK.
- `_gh_api.py`: leitura igual à de antes, mais estrita em `~`, curinga e chave (recusa em vez de adivinhar), e o campo cortado no `=@`; nada mais importa os nomes que saíram de `parecer.py` (só `conformidade.py` usa `parecer.expande`, que segue reexportado pelo import).
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Reprovado. O segundo cartão (leitura única do `gh api` em `hooks/_gh_api.py`) está correto e coberto, e as 12 guardas foram só movidas. O primeiro fecha o caso em que o gh roda fora de qualquer cópia de trabalho, mas não o mesmo contorno a partir de outro repositório (A1): `copia_de_trabalho(pasta)` decide antes do `-R`, e a pasta que não é projeto do Forge libera. Sugestão: quando há `repo` e o slug casa um remoto do clone da sessão, confira nesse clone seja qual for a pasta; a fixture `incidente-r-ready-no-clone-outro-repo-libera` (outro repositório no `-R`) continua passando. Some uma fixture `incidente-r-*` por sonda (S1 a S3) e um mutante para a guarda nova.
