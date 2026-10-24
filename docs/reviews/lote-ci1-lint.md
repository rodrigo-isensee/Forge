---
tipo: review
contrato: 1
pedido: lote-ci1-lint
branch: melhoria/lote-ci1-lint
commit: b59891dd4b621fc6f5b0bdce44a192d1c5ed33a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-ci1-lint

Pedido LOTE-CI1-LINT (E1, CI-ORDEM-LINT), revisado no pedido LOTE-CI1-LINT-REV (E1.1). Diff `3c66b881...b59891dd`, um commit (`b59891d`).

## Achados
- A1 (recomendado) tests/test_ci_local.py:178 · a lista executam_codigo é nominal: um passo novo que execute código da branch e entre antes do lint não é pego; trocar por "todo passo com run depois do zizmor, exceto gate e Testes que leem pareceres"
- A2 (recomendado) .github/workflows/ci.yml:161 · fora do escopo, cartão para o security-engineer: bin/forge-changelog e scripts/verificar-contribuicao.sh, da branch, rodam antes do passo que chama a catraca da base com python3 do PATH (mesma classe do X2, alvo a catraca)

## O que foi lido
- `.github/workflows/ci.yml`, job `bateria`, ordem nova dos passos (linhas 86 a 241 no head).
- `tests/test_ci_local.py:166-182`, teste novo.
- `changelog.d/lote-ci1-lint.md`.
- `docs/engineering/achados-recorrentes.md` (PA-7): sem linha registrada; nada a conferir.

## Verificações
- **Nenhum controle saiu:** as linhas do `ci.yml` ordenadas na base e no head só diferem pelo comentário novo (`diff <(sort base) <(sort head)` = 1 linha `+`, o comentário `CI-ORDEM-LINT`). É mudança de posição pura: os três passos (baixa, actionlint, zizmor) mantêm `if`, versão fixa, checksum e argumentos.
- **Nada da branch antes do lint no caminho pesado:** antes do download ficam só `actions/checkout`, o `Gate` (shell inline do próprio workflow, que o actionlint e o zizmor analisam, com `git` e `gh`, sem script da branch), `Testes que leem pareceres` (só com `pesada != 'true'`, caminho em que o lint não roda) e `setup-python`/`setup-node` (actions fixadas por sha). O primeiro passo que roda código da branch (`Claude Code CLI`, depois `claude plugin validate .`, `bin/forge-changelog`, `scripts/conferir-release.py`, `scripts/verificar-contribuicao.sh`, a suíte, o shellcheck e o e2e) vem depois do zizmor.
- **Semântica de falha:** os passos seguintes continuam com `!cancelled()`, então o lint vermelho não esconde o resultado dos outros, como antes.
- **O teste prova a ordem:** passa no head (`Ran 1 test ... OK`) e falha com o `ci.yml` da base (`AssertionError: 17 not less than 5 : Claude Code CLI`), conferido trocando só o arquivo na worktree de review e voltando com `git checkout`. Os nomes são buscados com desempacotamento `(i,) =`, então um passo renomeado ou duplicado quebra o teste em vez de passar calado. `tests.test_ci_local` inteiro: OK.
- **Teto M14:** 61 linhas (`ci.yml` 22+21, `tests/test_ci_local.py` 18+0); nenhum arquivo em `hooks/` nem em `PROTEGIDOS`.
- **Ferramentas:** actionlint e zizmor não estão instalados nesta estação; quem roda é o CI, no próprio PR. Não refaço o lint aqui; a saída entra na leitura dos checks no fechamento.
- **Commit e changelog:** Conventional Commits em português, com a classe e as variantes no corpo; fragmento `changelog.d/lote-ci1-lint.md` em `### Corrigido`. Sem `R-NEUTRO` nem `R-CUSTO` em jogo (download das mesmas releases públicas, já fixadas).

## Parecer
Aprovado. A mudança faz o que o cartão pede, nem mais nem menos: o download do actionlint e do zizmor e os dois lints passam a rodar antes de todo passo que executa código da branch no job `bateria`, sem perder nenhum controle, e o teste novo prova a ordem (falha antes, passa depois).

- A1 · `tests/test_ci_local.py:178` · a lista de passos é nominal; um passo novo com código da branch inserido antes do lint passaria · inverter a asserção para "todo passo com `run` exceto o gate e os testes de parecer vem depois do zizmor" · recomendado.
- A2 · `.github/workflows/ci.yml:161` · fora do escopo deste cartão: código da branch (`bin/forge-changelog`, `scripts/verificar-contribuicao.sh`) roda antes do passo da catraca, que usa o script da base mas com o `python3` do `PATH`; é a mesma classe do X2 com outro alvo · vira cartão para o `security-engineer`, que dá o parecer próprio (E2.1) · recomendado.
