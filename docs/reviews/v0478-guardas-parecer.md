---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: b989773a2ae7276692081441ff72c05d26d0f8da
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.16 (melhoria/v0478-guardas-parecer), volta 2 do E3.12

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 56bb90b5..b989773a (E3.15: 5c007978, 7b8d8466, cec853c9, b989773a). No domínio: `hooks/parecer.py` (`nomes_dinamicos`, `mexidas_na_linha`, `remotos`, mensagem do REPO_INCERTO), 16 fixtures `incidente-r-copia-alheia-*`, 1 `pasta-*`, specs `v0478-guardas-parecer-{5,6,7}.json` e `hk3-parecer-pasta-{11,12}.json`, `tests/test_hooks.py`, `tests/test_hooks_parecer_repo.py`, `docs/hooks-fixtures.md` (gerado) e o fragmento `changelog.d/`. Nada fora do delta relido.

## Achados
- A3 (bloqueante) hooks/parecer.py:624 · o laço tira só a palavra `command`, não as opções: `command -p . ./env.sh; gh pr ready feature/x` e `command -- . ./env.sh; …` dão 0 na cópia alheia sem parecer (S18, S26), e o bash carrega o GH_REPO nas duas; a docstring promete `source` e `.` depois de `command` (R-REVIEW).
- A4 (recomendado) hooks/parecer.py:953 · (linha da base) a catraca (modo regras, script da develop 2904a68a) acusa R-QA `apagada` das 11 condições movidas para hooks/_gh_api.py e reprova o CI do PR; o `--cobertura` diz `movida`. Isenta não cabe (11 > 8). Saída: o rótulo `afrouxa-regra` do dono ou a catraca corrigida antes na develop.

## Sondas
- S6 · cópia alheia da fixture `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia` (env.sh com `export GH_REPO=dono/forge`), `source env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 2 (R-REVIEW, GH_REPO mexido)
- S7 · mesma montagem, `. ./env.sh && gh pr ready feature/x` · espera: código 2 · obtido: código 2
- S8 · mesma montagem, `builtin . ./env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 2
- S9 · mesma montagem, `if source env.sh; then gh pr ready feature/x; fi`, `{ source env.sh; }; …`, `\source env.sh; …`, `time source …`, `! source …`, `set -a; source …` · espera: código 2 · obtido: código 2 nas seis
- S11 · mesma montagem, `export $(cut -d' ' -f2 env.sh)`, `read "$n"`, `declare -n r=GH_REPO`, `local -n`, `readonly "$n"=…`, `builtin export "$k"=…`, `command -p export GH_REPO=…` antes do gh · espera: código 2 · obtido: código 2 nas sete
- S19 · cópia alheia com `remote.origin.gh-resolved=dono/forge`, `gh pr ready feature/x` · espera: código 2 · obtido: código 2 (sem parecer)
- S20 · cópia alheia com `url.git@github.com:dono/forge.git.insteadOf=<url da cópia>` · espera: código 2 · obtido: código 2 (sem parecer)
- S25 · cópia alheia sem nada antes, `gh pr ready feature/x` (controle) · espera: código 0 · obtido: código 0
- S18 · mesma montagem do S6, `command -p . ./env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 0 (bash: `command -p . ./env.sh; echo $GH_REPO` imprime dono/forge)
- S26 · mesma montagem, `command -- . ./env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 0 (bash idem)
- S27 · catraca da develop (`regra_guardas_dos_hooks`, base 4182a6b9, head b989773a) · espera: sem violação · obtido: 1 violação R-QA, `apagada · hooks/parecer.py:965(base) · corpo` e mais 10

## Conferências
- A2 (meu, E3.12) fechado nas formas do S6 a S11 e S19, S20; aberto só pelo prefixo `command` com opção (A3).
- Mutação dirigida (`bin/forge-mutante tests/mutantes/v0478-guardas-parecer-7.json`, 1 processo): M39, M40, M41 `morreu`, rc=0.
- Cobertura (`bin/forge-mutante --cobertura --base 56bb90b5`): as guardas novas :607 a :613, :624 a :629 e :937 `coberta`; rc=0.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_repo`: 5 testes, OK.
- Leitura (checklist 1 a 4, 7, 9): falha fechada nos remotos ilegíveis com saída dita; `read` com opção desconhecida (`-rp "$x"`) recusa a mais, nunca a menos; commits coerentes.
- Tamanho (H1): cerca de 45 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Reprovado por A3. Sugestão: no laço de :624, depois de `command`, pular as opções (`-p`, `--`, combinações de `-pVv`), com fixture por forma e mutante na guarda. O A4 não é defeito do autor, mas o PR não fica verde sem o rótulo do dono ou a correção da catraca na develop.
