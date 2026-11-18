---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-prepush-pp1
commit: 6c84adb4ea7cda8e9b95de6d2857201afedc2f7e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E14.3, patch PP1 do envio local)

Escopo: `docs/devops/pp1-pre-push.patch`, `docs/devops/pp1-aplicar.md`, `tests/test_pre_push_patch.py`, a linha nova do mapa em `bin/forge-testes` e o fragmento `changelog.d/v0478-prepush-pp1.md`. O `.githooks/pre-push` da branch é idêntico ao da `develop` (4182a6b9, ponta atual): o patch é para o dono aplicar à mão.

## Conferido numa cópia limpa (clone novo da branch no head 6c84adb4, hook igual ao da develop)
- Aplicar, os dois comandos de `pp1-aplicar.md` como estão: `git apply --check` e `git apply` com rc=0; `bash -n` passa; `git diff --stat`: `.githooks/pre-push | 119 ++++-, 116 insertions(+), 3 deletions(-)`; modo `-rwxr-xr-x` mantido.
- Reaplicar: `git apply --check` recusa (`patch failed: .githooks/pre-push:56`, rc=1) sem tocar em nada, como o roteiro diz.
- Testar, o comando de `pp1-aplicar.md` com o hook já remendado: `Ran 180 tests in 202.127s · OK (skipped=1)`; o pulo é a comparação com o original, documentada.
- Envio leve: as duas checagens novas ficam em `checagens_baratas`, sem teste; medido `scripts/indice-fixtures.py --conferir` em 0,40 s (`em dia`) e o filtro de pulos (`PULOS_FILTRO_PY`) em 0,56 s, rc=0 sobre o diff da branch. Só rodam quando o diff toca os arquivos do gatilho; falha da ferramenta é aviso (o CI confere).
- O filtro de pulos usa `catraca.ler` (limpa `GIT_*` do ambiente) e `catraca._forca_das_arvores(...)[1]`, a mesma conta da catraca (`R-VERIFY`); o próprio teste do patch não sobe a contagem de pulos contra a âncora.
- Mapa: `bin/forge-testes --listar -- scripts/indice-fixtures.py` aponta `test_pre_push_patch` entre os dirigidos.
- Suíte inteira: fica no CI do PR (decisão M8); não rerrodada aqui. `shellcheck` não está instalado neste ambiente: o CI confere o hook remendado quando o dono o commitar.

## Achados
- A1 (recomendado) docs/devops/pp1-aplicar.md:11 · a tabela lista os gatilhos do índice como tests/hooks/, tests/config.json e scripts/indice-fixtures.py, mas o patch também dispara com docs/hooks-fixtures.md; incluir o quarto caminho na linha.

## Sondas

## Parecer
Aprovado. O patch aplica limpo sobre o hook da `develop`, os comandos de aplicar e testar do roteiro funcionam como escritos numa cópia limpa, e o envio segue leve (menos de 1 s somado, sem teste). A1 é só texto e não devolve.
