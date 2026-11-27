---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: aa3472135b21f0539c3047d1e31fe6718a17bced
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.14, #930, volta 3, por delta)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `e4998443..aa347213`): no domínio, a troca de `textos_do_valor(caminho)[0]` por `[1]` em `hooks/conformidade.py:4355`, a docstring, `docs/hooks.md:69`, as 4 fixtures `raiz-forge-variavel-de-{for,read}-*` e os mínimos de `tests/test_hooks.py:2930-2931` (21/34). Fora do domínio: o mutante `tests/mutantes/v0481-hook-raiz-forge-4.json`.
- Estado dos achados anteriores:
  - A12: resolvido no caso provado. S9 dá rc 2 na raiz (devops e tech-lead). As variantes também recusam: `for` no manifesto, no devcontainer, com `$PWD` e numa lista de dois (F1, F2, F4, F9), `while read … <<<` (F10) e `read` com `-r`, `IFS=`, dois nomes, pipe com chaves e `mapfile` (R1 a R6). Os legítimos seguem livres (L1 a L9, L11).
  - Mas a família não fecha: a entrada partida por aspas ou colada a outro texto passa só na raiz. É o A13.
  - A10 e A11: abertos, sem mudança no delta (recomendados).
- `docs/hooks.md:69` registra que a cópia de `wt/` também recusa sem valor calculado. Na sonda, W9 e WR1 dão rc 2. É a falha fechada documentada, sem achado.
- O L10 (`for f in a b; do printf x > $TMPDIR/$f; done; cat .githooks/pre-push`) recusa. É o custo documentado do texto largo ("a variável de `for` ou `read` conta a linha inteira"), sem achado.
- ci: aa3472135b21f0539c3047d1e31fe6718a17bced vermelho
  - A suíte (3.12 partes 1 a 5 e 3.14), a instalação, os passos, as verificações longas, o teto de pulados e a árvore provada estão verdes (run 45946373703).
  - `bateria (pareceres)` e `catraca` (run 45946373697) estão vermelhas por processo: os pareceres deste head. `bateria` é o agregador.

## Achados
- A13 (bloqueante) hooks/conformidade.py:4356 · explorável: S10 · sem valor calculado, a citação só casa o texto cru: entrada partida por aspas (`for d in .git''hooks`, `read d <<< .git''hooks`) ou variável colada (`${d}s` sobre `.githook`) grava o pre-push da raiz do Forge (rc 0; no projeto, rc 2)
- A14 (recomendado) hooks/conformidade.py:4356 · fora do delta, vira cartão: a lista de `for` com curinga ou chaves (`for d in .githoo*`, `for d in .{githooks,x}`) passa na raiz e no projeto (rc 0 nos dois); dimensão nova da matriz: o valor que o bash expande na lista
- A10 (recomendado) hooks/conformidade.py:130 · aberto, sem mudança no delta: ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` nem `subprocess`; o controle de fato é o sandbox negar a escrita nessas entradas da raiz
- A11 (recomendado) hooks/conformidade.py:4301 · aberto, sem mudança no delta: checar_texto do clone só casa a entrada literal; `os.path.join('.git','hooks',…)` passa na raiz do Forge; hoje o sandbox nega .git/hooks

## Sondas
- S9 · Bash `for d in .githooks; do printf x > $d/pre-push; done`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S10 · Bash `for d in .git''hooks; do printf x > $d/pre-push; done`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0
- S11 · Bash `read d <<< .git''hooks; printf x > $d/pre-push`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0
- S12 · Bash `for d in .githook; do printf x > ${d}s/pre-push; done`, cwd na raiz do Forge, papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0

## Detalhe dos achados
Como as sondas rodaram: `/root/.forge-contrib/wt/_sec134-v0481-sonda.py <cópia> forge|projeto [tl]` (35 entradas), sobre a montagem da fixture `raiz-forge-s0-write-githooks-bloqueia`, com o hook do head revisado. No arquivo, S10 é F6, S11 é R7 e S12 é F5. Com o papel tech-lead, o resultado é o mesmo.

- **A13 (alta):** a ameaça é a do A9 e do A12. Um agente sob injeção grava o pre-push ou o manifesto da raiz numa chamada só e ganha execução fora do sandbox no próximo push do dono, ou desliga as travas da sessão.
  - A causa: sem valor calculado, `hooks/conformidade.py:4356` casa `EM_VIGOR_NO_TEXTO` só no texto cru. O bash junta `.git''hooks` em `.githooks`, e `${d}s` completa `.githook`, mas o texto cru não cita a entrada.
  - Correção mínima, em duas partes, como no ramo do `.git` (`hooks/conformidade.py:1933`):
    1. Casar também `palavra_juntada(t)`: `EM_VIGOR_NO_TEXTO.search(t) or EM_VIGOR_NO_TEXTO.search(palavra_juntada(t))`. Fecha S10 e S11.
    2. Recusar quando a variável sem valor está colada a outro texto no primeiro componente do destino: `"*" in palavra_juntada(caminho).split("/")[0]`. Fecha S12.
  - Conferido numa cópia em `$TMPDIR` com as duas partes (`_sec134-v0481-patch.py` e `_sec134-v0481-patch2.py`, em `/root/.forge-contrib/wt/`):
    - S9 a S12 dão rc 2.
    - L1 a L9 e L11 seguem livres. O L8 (`$TMPDIR/$f`) não muda, porque a variável está sozinha no componente.
    - `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` OK.
  - Fixtures que faltam: S10, S11 e S12 na raiz (rc 2), e um legítimo com a variável colada fora das entradas. Mutantes: tirar cada uma das duas partes.
  - Esforço P. Dono: tech-lead.
- **A14:** o curinga e as chaves na lista do `for` passam também no projeto, então não é uma regressão desta branch: é uma dimensão que falta na matriz da família.
  - A correção é expandir a lista do `for` como o bash faz (curinga contra a raiz e chaves) e tratar cada valor como valor calculado.
  - Vira cartão, porque está fora do delta (G1.2). Dono: tech-lead.
- **Limite registrado, sem achado novo:** `read d < $TMPDIR/n` (R8) segue livre aqui e no projeto. É a família do A10, e o controle que a fecha é o sandbox negar a escrita nessas entradas da raiz.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam: o delta é um hook, fixtures e documentação, sem dependência nem workflow. A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`, rodei as sondas acima e `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` na cópia com a correção.
