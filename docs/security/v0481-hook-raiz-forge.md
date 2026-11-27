---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: e4998443f6eea0ef08c43dbbb9b35627f13582b0
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.10, #930, volta 2, por delta)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `10c1b834..e4998443`): no domínio, `GuardaDaProva.destino_opaco` (`hooks/conformidade.py:4342-4361`), `docs/hooks.md:69` e as 6 fixtures novas `raiz-forge-*` (S7, S8, substituição com resto, variável sem valor com resto, e S7 e S8 na cópia de `wt/`). Fora do domínio: os mutantes RD7 e RD8 e o fragmento do changelog.
- Estado dos achados da rodada anterior:
  - A9: resolvido no caso provado. S7 e S8 dão rc 2 na raiz (devops e tech-lead com a raiz em `melhoria/z`) e rc 0 na cópia de `wt/` (L3). As variantes também recusam: resto colado sem barra (V1), `cp` no devcontainer (V2), `$PWD` (V3), `export` com `tee` (V5), `${D:-…}` (V6), `rm` (V7), `$(printf %s …)` (V8), crase (V9). V1, V2 e V8 recusam aqui e passam no projeto. O legítimo `printf x > $TMPDIR/y; cat .githooks/pre-push` (L1) segue livre, e também L2, L4 e L5.
  - Mas a escolha só dos textos precisos abre a variável que nasce de `for`: A12.
  - A10 e A11: abertos, sem mudança no delta (recomendados; corrigidos antes do merge ou levados ao dono como cartão).
- Nota de redação ao tech-lead (fora da segurança): em `docs/hooks.md:69` faltam vírgula ou "e" entre os exemplos `` `F=.githooks/pre-push; printf x > $F` `` e `` `D=.githooks; …` ``.
- ci: e4998443f6eea0ef08c43dbbb9b35627f13582b0 vermelho
  - A suíte (3.12 e 3.14, partes 1 a 5), a instalação, os passos, as verificações longas e o teto de pulados estão verdes (run 45943925466).
  - `bateria (pareceres)` e `catraca` (run 45943925467) estão vermelhas por processo: os pareceres deste head e o rótulo. `bateria` é o agregador.

## Achados
- A12 (bloqueante) hooks/conformidade.py:4354 · explorável: S9 · com resto e sem valor calculado, só os textos precisos contam; a variável de `for` cai fora: `for d in .githooks; do printf x > $d/pre-push; done` grava o pre-push da raiz do Forge (rc 0; no projeto, rc 2)
- A10 (recomendado) hooks/conformidade.py:130 · aberto, sem mudança no delta: ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` nem `subprocess`; o controle de fato é o sandbox negar a escrita nessas entradas da raiz
- A11 (recomendado) hooks/conformidade.py:4301 · aberto, sem mudança no delta: checar_texto do clone só casa a entrada literal; `os.path.join('.git','hooks',…)` passa na raiz do Forge; hoje o sandbox nega .git/hooks

## Sondas
- S7 · Bash `D=.githooks; printf x > $D/pre-push`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2 · obtido: rc 2 (resolvido)
- S8 · Bash `D=.claude-plugin; printf '{}' > $D/plugin.json`, cwd na raiz do Forge, papel tech-lead, raiz em melhoria/z · espera: rc 2 · obtido: rc 2 (resolvido)
- S9 · Bash `for d in .githooks; do printf x > $d/pre-push; done`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2, como no projeto · obtido: rc 0

## Detalhe dos achados
Como as sondas rodaram: `/root/.forge-contrib/wt/_sec133-v0481-sonda.py <cópia> forge|projeto [tl]` (20 entradas), sobre a montagem da fixture `raiz-forge-s0-write-githooks-bloqueia`, com o hook do head revisado. No arquivo, S9 é a entrada V12.

- **A12 (alta):** a ameaça é a do A9. Um agente sob injeção grava o pre-push ou o manifesto da raiz numa chamada só e ganha execução fora do sandbox no próximo push do dono, ou desliga as travas da sessão.
  - A causa: `hooks/conformidade.py:4354` usa `textos_do_valor(caminho)[0]` (os precisos). A variável que nasce de `for d in …` ou de `read d` só entra nos largos (`[1]`, que somam a linha).
  - Correção mínima: trocar `[0]` por `[1]` nessa linha. Conferido numa cópia em `$TMPDIR` com a troca: S9 dá rc 2; S7, S8 e os legítimos L1 a L5 não mudam; `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` OK. O L1 segue livre porque `$TMPDIR` não nasce na linha, então não há largo.
  - Fixture que falta: S9 na raiz (rc 2) e na cópia de `wt/` (rc 0). Mutante: a troca de volta para `[0]`.
  - Esforço P. Dono: tech-lead.
- **Limite registrado, sem achado novo:** o valor lido de um arquivo gravado numa chamada anterior passa aqui e no projeto (rc 0 nos dois): `D=$(cat $TMPDIR/n); printf x > $D/pre-push` (V10), `$(cat $TMPDIR/n)/pre-push` (V11) e `read d < $TMPDIR/n` (V13). É a família do A10 (o hook não sabe o que um comando produz), e o controle que a fecha é o mesmo: o sandbox negar a escrita em `.githooks/`, `.devcontainer/`, `.devcontainer.json` e `.claude-plugin/` da raiz. Fechá-la no hook recusaria todo destino `$TMPDIR/…`.
- **A10 e A11:** a análise e a correção estão na rodada anterior (no git, commit do parecer de `10c1b834`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam: o delta é um hook e fixtures, sem dependência nem workflow. A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`: as sondas acima e `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` na cópia com a troca.
