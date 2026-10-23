---
tipo: revisao-devops
contrato: 1
pedido: FIX-SUITE-LOCAL
branch: melhoria/suite-local-verde
commit: 124c521ed00fca3280ea1e88c02f877a9e28aca6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-22
---
# Review de devops: FIX-SUITE-LOCAL

## Parecer
Aprovado. Diff `af79bef..124c521` revisado inteiro. Nenhum arquivo de `.github/`, `Dockerfile*`, `compose*` ou IaC foi tocado.

## Achados
Nenhum bloqueante.

Conferido:
- **Diretiva do shellcheck** (`.githooks/pre-push:242`): `disable=SC2317,SC2329` cobre as duas versões. Na 0.11.0 local, `shellcheck -x .githooks/pre-push` e `templates/projeto/.githooks/pre-push` dão rc 0. Na versão do CI (ubuntu-24.04, pacote da distro, 0.9/0.10, `ci.yml:157-159`) o SC2317 segue suprimido; um código que a versão não conhece na lista de `disable` é ignorado, não é erro. Não pude rodar uma 0.10 (lacuna: só a 0.11.0 está no PATH). Não há outro `SC2317` no repositório.
- **Isolamento do `sitecustomize`** (`tests/apoio_pathlib_312/`): só `tests/test_hooks.py:362-363` (fixtures com `pathlib_312: true`) e `:1046` (um teste) põem a pasta no `PYTHONPATH`, e só no `env` do processo filho do hook. `.githooks/pre-push`, `.github/workflows/*` e `scripts/` não referenciam `PYTHONPATH` nem a pasta; o pre-push e o CI não o carregam. A pasta não tem `test_*.py` nem `__init__.py`, então o `discover -s tests` não a importa. O efeito no CI (Python 3.12) é nulo: reimplementa a semântica da 3.12.
- **Suíte**: `python3 -m unittest tests.test_hooks` na 3.14.4 local: 43 testes, OK (59 s).
- **Custo (`R-CUSTO`)**: zero. Nenhum workflow, runner, cache, artefato ou serviço novo; minutos de CI inalterados.

Recomendado (não bloqueia): o `sitecustomize` substitui `Path.exists/is_dir/is_file` do processo filho inteiro; se uma fixture futura precisar do comportamento 3.14, não deve usar `pathlib_312`.

Ferramentas: `shellcheck` 0.11.0 usado. `actionlint` não necessário (sem mudança em workflow). `docker build` não se aplica.

## Custo e rollback
Sem custo novo. Rollback: reverter os 3 commits (só teste, diretiva e fragmento); nada a migrar.
