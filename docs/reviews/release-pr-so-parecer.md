---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/release-pr-so-parecer
commit: 2665b9a193f1f1ebefcf7699782281325a1267d3
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: release-pr-so-parecer (`forge-changelog conferir` aceita PR só de pareceres)

## Achados
- A1 (bloqueante) bin/forge-changelog:217 · o diff de `mudou` não tem `--no-renames`: mover código para pasta de parecer (`git mv bin/forge-x docs/reviews/forge-x.md`) lista só o nome novo e passa sem fragmento; na develop reprova. Pôr `--no-renames`, como o gate do ci.yml, e testar o caso
- A2 (recomendado) tests/test_changelog.py:414 · faltam casos no teste: renomeação de código para dentro de `docs/reviews/` (o A1) e arquivo em pasta `_*` (`docs/qa/_x/a.md`), para fixar o limite da regra

## Parecer
Reprovado por um defeito provado (A1), regressão sobre a develop.

- Lista de caminhos (`e_parecer`, `bin/forge-changelog:191`): recusa `_*` pelo nome do arquivo, `docs/security/ameacas/` e `docs/security/aceites/`, igual à regra do gate do `ci.yml:107-108`; `docs/ux/` fica fora (mais estrito que o CI, aceitável). Arquivo fora das quatro pastas cai no caminho antigo e exige fragmento.
- O furo é a leitura de `mudou` (`bin/forge-changelog:217`): `git diff --name-only` sem `--no-renames` detecta renomeação e lista só o destino. Prova, num repositório de teste com `bin/forge-x` de 40 linhas movido para `docs/reviews/forge-x.md`: o `forge-changelog` da develop (b45e40a) sai com rc 1 ("Registre a mudança num fragmento novo"); o desta branch sai com rc 0 ("ok: PR só de parecer"). Ou seja, um PR que tira código da fábrica passa sem registro. O próprio gate que a docstring cita usa `--no-renames` (`ci.yml:105`), e `fragmentos_alterados` também (`:199`). Correção mínima: `--no-renames` na linha 217, mais um teste com `git mv` de `agents/a.md` para `docs/reviews/`.
- M14: `git diff --numstat --no-renames b45e40a...2665b9a`: `bin/forge-changelog` 9+0, `tests/test_changelog.py` 31+0 = 40 linhas, abaixo de 150; um comportamento.
- Teste reprova sem a mudança: com o teste da branch sobre o `forge-changelog` da develop, `test_pr_so_de_pareceres_passa_sem_fragmento` falha; os dois testes de guarda (modelo/ameacas/aceites e parecer com outro arquivo) passam antes e depois, como guardas devem.
- `python3 -I -m unittest discover -s tests -p test_changelog.py`: 49 testes, OK (1 pulado).
- Fragmento `changelog.d/release-pr-so-parecer.md` presente. Commit em Conventional Commits. A mudança afrouxa um gate (`conferir`): o PR pede o rótulo `afrouxa-regra` do dono.
