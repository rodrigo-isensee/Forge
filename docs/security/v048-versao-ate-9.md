---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-versao-ate-9
commit: c727c89722a5a68b336f7e7e296d02ffa5272cc9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v048 E2.3, #951 (VERSAO-PATCH-ATE-9), 1ª rodada completa

Lido: `b414714c..c727c897` inteiro (`bin/forge-contador`, `bin/forge-changelog`, `tests/test_changelog.py`, `tests/test_forge_contador.py`, `tests/mutantes/v048-versao-ate-9.json`, o fragmento) e, fora do diff, os consumidores do contador e do release: `bin/forge-fechar:1632-1660` (passo V4/V5 da marca) e `:1563-1580` (`anexar_na_marca`), `bin/forge_estado.py:158`.

CI do head c727c897 (run 46084959115): as 5 partes da suíte, instalação, verificações longas, passos, python 3.14, teto de pulados, catraca e árvore provada verdes; `bateria (pareceres)` (e o agregado `bateria`) vermelho só por falta de parecer (`R-REVIEW: PR toca bin/forge-changelog ... sem parecer aprovado de review`), que esta etapa e a E2.2 suprem. Local: `tests.test_changelog` e `tests.test_forge_contador` (119 testes) passam; `forge-mutante` com a spec do pedido: M1 a M4 morrem.

Gatilhos: sensível da catraca (`bin/forge-contador`, classe C), gravação da versão nos manifestos (`bin/forge-changelog release`).

## Conferência
- Recusa sem caminho lateral de gravação: `bin/forge-changelog:190-193` recusa patch acima de 9 antes de abrir `CHANGELOG.md`, antes de `ler_manifestos` e de qualquer `unlink` (a ordem vale também com data inválida: a versão é recusada primeiro). Sonda local: `0.47.10`, `0.47.20`, `0.47.010`, patch de 20 dígitos, e dígitos não ASCII que a classe `\d` aceita (arábico-índico e de largura total) dão saída 1, mensagem com `vem 0.48.0` e os três arquivos (CHANGELOG, `plugin.json`, fragmento) com o mesmo hash de antes.
- `--anexar` (`bin/forge-changelog:181-185`, `anexar`): não muda e não grava manifesto; com versão ausente do CHANGELOG (ex.: `0.47.20`) recusa sem tocar nada, então não abre versão nova por esse lado.
- Marca: `bin/forge-fechar:1633-1650` só grava a versão por `forge-changelog release "$v"`, com `$v` vindo do contador; contador e release concordam (contador nunca emite patch acima de 9, release nunca aceita), então o corte não fica preso entre os dois. Sonda do contador: `0.47.20`, `0.47.9`, `v1.2.15`, `0.47.010` dão `X.(Y+1).0`; `0.47.8` dá `0.47.9`.
- Testes antigos mudados (`tests/test_forge_contador.py:93` e `:108`): continuam guardando o que guardavam (a contagem `2 de 20` sem README nem `.txt`; README com caixa mista fora da contagem); só o número esperado muda, e a fixação `1.4.9` passa a exercer o corte. O incremento comum (`0.48.0 → 0.48.1`, `0.48.8 → 0.48.9`) segue coberto por `test_versao_corta_no_9`; o limite e a existência do corte e da recusa são guardados pelos mutantes M1 a M4.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Fora do delta, pré-existente e sem caminho de ataque (só quem já opera a release o alcança): o release aceita patch com zero à esquerda (`0.47.09`) e versão menor que a atual; vai como cartão, não como achado. Ferramentas: leitura do diff e dos consumidores, sonda local no `$TMPDIR`, testes afetados, `forge-mutante`, `gh pr checks`. Ausentes no ambiente (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor; o delta não toca workflow, dependência nem segredo.
