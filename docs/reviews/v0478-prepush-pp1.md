---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-prepush-pp1
commit: 3d4a84ffecfeaf5ae35c2107706eafdaff2f37b6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E14.3 e revalidação E14.7, patch PP1 do envio local)

Escopo: `docs/devops/pp1-pre-push.patch`, `docs/devops/pp1-aplicar.md`, `tests/test_pre_push_patch.py`, a linha nova do mapa em `bin/forge-testes` e o fragmento `changelog.d/v0478-prepush-pp1.md`. O `.githooks/pre-push` da branch é idêntico ao da `develop` (4182a6b9, ponta atual): o patch é para o dono aplicar à mão.

## Conferido numa cópia limpa (clone novo da branch no head 6c84adb4, hook igual ao da develop)
- Aplicar, os dois comandos de `pp1-aplicar.md` como estão: `git apply --check` e `git apply` com rc=0; `bash -n` passa; `git diff --stat`: `.githooks/pre-push | 119 ++++-, 116 insertions(+), 3 deletions(-)`; modo `-rwxr-xr-x` mantido.
- Reaplicar: `git apply --check` recusa (`patch failed: .githooks/pre-push:56`, rc=1) sem tocar em nada, como o roteiro diz.
- Testar, o comando de `pp1-aplicar.md` com o hook já remendado: `Ran 180 tests in 202.127s · OK (skipped=1)`; o pulo é a comparação com o original, documentada.
- Envio leve: as duas checagens novas ficam em `checagens_baratas`, sem teste; medido `scripts/indice-fixtures.py --conferir` em 0,40 s (`em dia`) e o filtro de pulos (`PULOS_FILTRO_PY`) em 0,56 s, rc=0 sobre o diff da branch. Só rodam quando o diff toca os arquivos do gatilho; falha da ferramenta é aviso (o CI confere).
- O filtro de pulos usa `catraca.ler` (limpa `GIT_*` do ambiente) e `catraca._forca_das_arvores(...)[1]`, a mesma conta da catraca (`R-VERIFY`); o próprio teste do patch não sobe a contagem de pulos contra a âncora.
- Mapa: `bin/forge-testes --listar -- scripts/indice-fixtures.py` aponta `test_pre_push_patch` entre os dirigidos.
- Suíte inteira: fica no CI do PR (decisão M8); não rerrodada aqui. `shellcheck` não está instalado neste ambiente: o CI confere o hook remendado quando o dono o commitar.

## Revalidação E14.7 (head 3d4a84ff, delta desde 6c84adb4)
Lido só `forge-check parecer delta docs/reviews/v0478-prepush-pp1.md`: intervalo 6c84adb4..3d4a84ff, no domínio `changelog.d/v0478-prepush-pp1.md`, `docs/devops/pp1-aplicar.md`, `docs/devops/pp1-pre-push.patch`, `tests/mutantes/v0478-prepush-pp1.json` e `tests/test_pre_push_patch.py`.
- A1 resolvido: `docs/devops/pp1-aplicar.md:11` lista `docs/hooks-fixtures.md` entre os gatilhos, igual ao `case` do patch (`tests/hooks/*|scripts/indice-fixtures.py|docs/hooks-fixtures.md|tests/config.json`).
- Patch: `$((10#$intervalo))` lido uma vez em `intervalo_dec`, que segue para a espera; `[ ! -L bin/forge-check ]` junto das guardas vizinhas. Mutantes declarados M3, M11, M12 e M15 (`bin/forge-mutante --processos 1 tests/mutantes/v0478-prepush-pp1.json`): os quatro morreram. Os quatro testes novos dos ramos de falha: `Ran 4 tests · OK`.
- Roteiro novo de `pp1-aplicar.md`, numa cópia limpa da `develop` (4182a6b9, hook igual ao da branch): `git show 0a986ebe:docs/devops/pp1-pre-push.patch` rc=0 e idêntico ao patch do head (`cmp`); `git apply --stat` lista só `.githooks/pre-push | 122, 119 insertions(+), 3 deletions(-)`; `--check` e `apply` rc=0; `bash -n` passa; modo `-rwxr-xr-x` mantido; reaplicar recusa (`patch failed: .githooks/pre-push:56`, rc=1). Com os arquivos da branch trazidos, o comando de teste do roteiro: `Ran 185 tests in 174.697s · OK (skipped=1)` (o pulo é a comparação com o original).
- Suíte inteira: fica no CI do PR (M8); não rerrodada.

## Parecer
Aprovado no head 3d4a84ff. O A1 foi corrigido, o patch novo aplica limpo sobre a `develop` pelo roteiro como escrito, e as guardas mudadas têm mutante declarado que morre.
