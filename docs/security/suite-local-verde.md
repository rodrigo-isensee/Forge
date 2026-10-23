---
tipo: revisao-seguranca
contrato: 1
pedido: FIX-SUITE-LOCAL
branch: melhoria/suite-local-verde
commit: 124c521ed00fca3280ea1e88c02f877a9e28aca6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: FIX-SUITE-LOCAL

Escopo: `git diff af79bef3e1525e54de0f7b7fc6024e841a6dff85..124c521` (3 commits): `.githooks/pre-push`, `tests/apoio_pathlib_312/sitecustomize.py`, `tests/test_hooks.py`, as fixtures `tests/hooks/conformidade/contrib-falha-fechada-pela-raiz-cwd-{home,wt}-bloqueia.json` e `changelog.d/suite-local-verde.md`. Nenhum arquivo de `hooks/` mudou (`git diff --stat af79bef..124c521 -- hooks/` vazio).

## Gatilhos
Controles do Forge: o pre-push (portão de envio) e os testes de falha fechada do hook `conformidade` (ADR 0009, seções 6.6 e 7).

## Achados

## Detalhe dos achados
**O teste de falha fechada continua provando a falha fechada.** O `sitecustomize` (`tests/apoio_pathlib_312/sitecustomize.py:13-41`) devolve a `Path.exists`, `is_dir` e `is_file` a semântica da 3.12: ignora só ENOENT, ENOTDIR, EBADF e ELOOP (e `ValueError`), igual ao `_ignore_error` da 3.12, e relança o resto (EACCES, ENAMETOOLONG). Com ele, o hook recebe o `OSError` na decisão do papel e as asserções seguem as mesmas: código 2 e "erro interno" no stderr (`tests/test_hooks.py:1050-1055`; nas fixtures, `esperado.codigo: 2`, `stderr` e `erros_log`). Nenhuma asserção foi afrouxada nem removida. O teste não passa vazio: sem o módulo, na 3.14.4 local, os três casos falham (`0 != 2` no papel `aq`; `0 != 2` na fixture `cwd-home`; R-CONTRIB no lugar de "erro interno" na `cwd-wt`), e com ele passam (`Ran 2 tests ... OK`).

**O `sitecustomize` não chega aos hooks reais.** Ele só entra no processo pelo `PYTHONPATH` montado pelo teste (`tests/test_hooks.py:362-363`, só para fixture com `"pathlib_312": true`, e `:1046`). O `hooks/hooks.json` roda `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<hook>.py`, cujo `sys.path[0]` é `hooks/`; nada em `hooks/`, `bin/`, `scripts/`, `.githooks/`, `.github/` ou `templates/` cita `apoio_pathlib_312`, `sitecustomize` ou `PYTHONPATH`. Quem controla o `PYTHONPATH` do Claude Code já executa código arbitrário; o módulo não cria caminho novo.

**Pre-push** (`.githooks/pre-push:242`): a diretiva passa a `SC2317,SC2329`, restrita à função `parar()` (linha 243); não silencia nada fora dela. `shellcheck 0.11.0` limpo no arquivo.

**Recomendação (informativa, fora do escopo, não bloqueia).** Na 3.14 em produção, a via de falha fechada que estes testes exercitam (o `OSError` de `Path.exists`) não dispara mais: o hook trata o caminho como inexistente. Analisei os dois casos e não há caminho de ataque realista: com pasta sem permissão, quem a criou também não consegue escrever nela (o caminho cai no repositório de fora, e a decisão é a da política: `docs/propostas/` é do `aq`); com nome longo demais, o `cd` real também falha, o shell fica em `~`, que não é repositório, e o push não sai (no caso `cwd-wt`, o hook ainda barra por R-CONTRIB). Sugestão ao `devops-engineer`, sem custo (`R-CUSTO`): incluir a 3.14 na matriz do CI, para o comportamento de produção na versão nova ficar coberto além da semântica da 3.12 restaurada pelo teste. Esforço P.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck 0.11.0`, Python 3.14.4 (testes com e sem o módulo, numa cópia descartada da pasta `tests/`), leitura estática. Faltaram no PATH: `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `osv-scanner` (o diff não toca workflow nem dependência; sem segredo no diff, conferido por leitura).
