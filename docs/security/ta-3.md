---
tipo: revisao-seguranca
contrato: 1
pedido: ta-3
branch: melhoria/ta-3-testes-tocados
commit: 604b2a90c509915c39becadbd5f56cb47cbd195e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: ta-3

Escopo: `git diff 6ebd2016939293d451f3584a2d3ae3e6fde381bf...98bd38a`, 4 arquivos (`bin/forge-testes`, `tests/test_testes_tocados.py`, `docs/economia-de-tokens.md`, `changelog.d/ta-3-testes-tocados.md`). Ameaças consideradas: o dirigido entrar num portão e reduzir a suíte que protege a `main`; a falha fechada ser contornada; caminho ou nome de arquivo do diff virar comando de shell ou módulo arbitrário no `unittest`; o log gravar segredo ou entrar no git.

## Gatilhos
`R-SEGURANCA`: script novo que decide quando a suíte roda (controle de qualidade do fluxo, decisão do dono "A, desde que para main rode tudo.").

## Resumo
**Aprovado.** Nenhum portão usa o script; a suíte completa segue em pre-push, CI e no caminho para a `main`. Não há execução por shell nem módulo arbitrário. O log não contém segredo e fica fora do git. Um achado baixo: a falha fechada pode ser contornada sem querer por um **renomeio** (B-TA3-1). Como os portões rodam a suíte inteira, isso não tem consequência de segurança e não bloqueia. Uma recomendação baixa para o teste de "não é portão" (B-TA3-2) e uma observação informativa (I-TA3-1). Testes do autor: `python3 -m unittest tests.test_testes_tocados`, 21 testes, OK.

## Verificações
1. **Nenhum portão usa o dirigido.** `grep -rn forge-testes .githooks .github hooks bin scripts tests/config.json` só encontra o próprio `bin/forge-testes`. `bin/forge-check` (inclusive `forge-check pr`) não o cita. `.githooks/pre-push` segue com `python3 -m unittest discover -s tests` (coberto por `tests/test_testes_tocados.py:186-188`). O docstring do script (`bin/forge-testes:16-17`) e a regra 5 (`docs/economia-de-tokens.md:10`) dizem isso.
2. **Falha fechada.** Caminho sem regra → completa (`bin/forge-testes:88-89`). `tests/config.json` e o próprio script → completa (`:58`, `:81-82`). Módulo mapeado sem arquivo → completa (`:91-93`). Erro do git (base inexistente, merge-base falho) → completa (`:119-122`). Caminho com acento ou caractere especial sai entre aspas do `git` (`core.quotePath`), não casa com nenhuma regra e cai na completa (testado num repositório de brinquedo). Exceção: renomeio (B-TA3-1).
3. **Sem injeção.** Todo `subprocess.run` usa lista e não usa `shell=True` (`:63`, `:137`). O nome do módulo só sai de `tests/(test_[a-z0-9_]+)\.py` com `fullmatch` (`:38`, `:59`, `:86`) ou de tuplas fixas do mapa. Antes de rodar, ele tem de existir como arquivo em `tests/` (`:91`). Um nome de arquivo no diff não injeta `.`, `/` nem opção no `unittest`. O `--base` é argumento do próprio autor na própria máquina, então não há fronteira de confiança.
4. **Log.** A linha tem data UTC, modo, módulos (validados acima), duração e código de saída (`:97-101`). Não leva caminho, base, ambiente nem saída dos testes, então não grava segredo. Fica em `.forge/run/testes.log`, e `/.forge` está no `.gitignore:20` (coberto por `tests/test_testes_tocados.py:195-196`).

## Achados

### B-TA3-1 (baixa): renomeio esconde o caminho de origem e contorna a falha fechada
- **Evidência:** `bin/forge-testes:72`, `git("diff", "--name-only", ancora)`. Com `diff.renames` ligado (padrão do git desde a 2.9), um renomeio lista só o caminho **novo**. Reproduzido no git 2.55: `git mv .githooks/pre-push docs/pre-push.md` gera só `docs/pre-push.md` e `planejar(["docs/pre-push.md"])` dá `dirigido` (conteúdo). O mesmo vale para `tests/config.json` → `docs/config.json`, `.github/...` → `docs/...` e para o `bin/forge-testes` renomeado para um caminho mapeado. Isso contraria o docstring (`:11-12`, "qualquer caminho sem entrada no mapa ... fazem rodar a suíte completa").
- **Caminho de ataque:** nenhum realista. Quem renomeia é o próprio autor, e o efeito é só um sinal local incompleto. O pre-push e o CI rodam a suíte inteira e pegam a quebra. Por isso é baixa e não bloqueia.
- **Correção mínima:** `git("diff", "--name-only", "--no-renames", ancora)` (a origem aparece como apagada e cai na completa, se não tiver mapa), mais um teste em `Execucao` com `git mv` de um caminho sem mapa para `docs/`. Esforço P.
- **Dono:** autor (`tech-lead` do E1).

### B-TA3-2 (baixa, recomendação): o teste de "não é portão" não olha o `bin/forge-check`
- **Evidência:** `tests/test_testes_tocados.py:177` varre `.githooks`, `.github`, `hooks` e `scripts/ci-local`, mas não `bin/forge-check` (o `forge-check pr` é portão). Hoje ele não cita o script (verificação 1). A lacuna é só de regressão futura.
- **Correção mínima:** incluir `RAIZ / "bin" / "forge-check"` em `alvos`. Esforço P. **Dono:** autor (`tech-lead` do E1).

### I-TA3-1 (informativa): o log segue link simbólico
- **Evidência:** `bin/forge-testes:98-100` abre `.forge/run/testes.log` em modo de acréscimo, sem checar link.
- **Caminho de ataque:** exigiria uma branch maliciosa versionar (com `git add -f`) um link em `.forge/run/`. Quem roda o script dessa branch já executa o código dela, então não há ganho. Fica só o registro, sem ação.

## Revalidação após a volta do autor
Escopo: `git diff 98bd38a..604b2a9 -- bin/ tests/ docs/ changelog.d/` (`bin/forge-testes`, `tests/test_testes_tocados.py`). **Aprovado** no HEAD `604b2a9`.
- **B-TA3-1 corrigido:** `bin/forge-testes:92` usa `git diff --name-only --no-renames`, então o caminho antigo de um renomeio entra no plano. Testes: `test_arquivo_protegido_renomeado_cai_na_completa` (`tests/config.json` → `docs/` cai na completa) e `test_arquivo_mapeado_renomeado_inclui_os_modulos_do_caminho_antigo` (`tests/test_testes_tocados.py:220-242`).
- **B-TA3-2 corrigido:** `tests/test_testes_tocados.py:254-255` inclui `bin/forge-check` nos alvos de `test_nenhum_portao_cita_o_script`.
- **Falha fechada sem desvio novo:** `planejar` (`bin/forge-testes:96-117`) mantém a mesma ordem: `ALTERA_O_MAPA` → completa; sem regra → completa; módulo sem arquivo → completa; erro do git → completa (`:143-144`). O mapa só ganhou módulos e regras mais finas para caminhos que já eram dirigidos (`stacks/`, `.claude-plugin/`, `migrations/`, `templates/`, `docs/`, `README`/`CONTRIBUTING`). Nenhum caminho que caía na completa passou a dirigido. `IMPORTADO_POR` (`:76`) só acrescenta módulos. O nome do módulo continua vindo de `fullmatch` ou de tuplas fixas, e o `subprocess` continua por lista.
- **Nenhum portão chama o script:** `grep -rn forge-testes .githooks .github hooks bin scripts tests/config.json` só encontra o próprio script. A volta não toca `.githooks`, `.github`, `hooks` nem `scripts`, e `.githooks/pre-push:36` segue com `unittest discover -s tests`.
- **Testes:** `python3 -m unittest tests.test_testes_tocados -q`: 27 testes, OK.
- I-TA3-1 continua só registrado, sem ação.

## Lacunas de ferramenta
`gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (nada foi instalado, `R-CUSTO`). A revisão foi manual. O diff não toca workflow, dependência nem segredo.

## Riscos aceitos
Nenhum.
