---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: e48a2e60a11d97a36ab936fedacb1e93477ff940
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.6, revalidação da trilha CONFORMIDADE-SEGURANCA do `hooks/conformidade.py`, head e48a2e60)

Revalidação (H3, `R-REVIEW`) do parecer aprovado no head 6c0b0f03. Li só o delta de
`forge-check parecer delta docs/reviews/v0479-conformidade-trilha.md`: intervalo `6c0b0f03..e48a2e60`, domínio "código e
testes", `hooks/conformidade.py` (+72/-10), `docs/hooks.md`, `tests/apoio_volta_unica.py`, `tests/fixtures/heredoc-volta-unica.json`,
31 fixtures novas, a troca `oraculo-limite-python-c-libera` → `oraculo-python-c-tech-lead-bloqueia`, os mutantes `-3` a `-9`
e a prova do custo do corpus. Fora desse domínio nada foi relido.

## O que li no delta
- `INDICE_NO_GIT` ganha `stage` e `reset` (A2, A7); `resto_do_subcomando` pula a opção global com valor
  (`GIT_GLOBAIS_COM_VALOR`, A3); `envio_com_substituicao` pega o `xargs git` sem subcomando (A5) e o shell que lê a entrada
  por `shell_que_le_a_entrada` (A4), com a entrada de arquivo (`bash < x.sh`) livre; a recusa vira `TRAVA` (A6). Legível,
  conjuntos literais por custo, comentário com a origem de cada guarda.
- A troca da fixture do oráculo é legítima: a antiga dizia "quem fechar o furo troca o rc esperado", e o A9 fecha o furo.
  O `*` da política casa no texto do interpretador só quando ele cita o caminho; rodar e ler o oráculo seguem livres (sondas abaixo).
- `CONTROLE_NO_TEXTO` (`hooks/conformidade.py:3808`) passa a casar a linha que cita `forge-contrib` e `pedidos`/`briefs` em
  qualquer posição (A1), e `na_pasta_do_controle` (`:3895`) basta `pedidos`/`briefs` com a pasta corrente no controle.
  É aqui o achado A1.
- Os recomendados do parecer anterior: o A2 (S9 no `-6`) foi feito; o A1 (`esperar-estado`) segue como cartão.

## Sondas de caso legítimo (hook do head novo contra o do 6c0b0f03, mesmas fixtures montadas)
Base `cpb-tech-lead-wt-variavel-pedidos-libera` (tech-lead, sessão do Forge, pasta corrente em `~/.forge-contrib/wt/x`) e
`oraculo-python-c-tech-lead-bloqueia` (tech-lead no clone):
- seguem livres nos dois: `python3 -I tests/test_oraculo_x.py`, `python3 -m unittest tests.test_oraculo_x`,
  `python3 -c "print(open('tests/test_oraculo_x.py').read())"`, `sed -n … docs/pedidos/v1.md > $TMPDIR/e.txt` (sem citar
  `forge-contrib`), `grep … docs/pedidos/v1.md ~/.forge-contrib/docs/briefs/b1.md`, `git reset --hard HEAD`,
  `git reset HEAD -- src/app.js`, `git stage src/app.js`, `git diff --name-only | xargs git diff --stat`,
  `ls -d . | xargs -I{} git -C {} status --short`, `bash -n scripts/x.sh && git push origin melhoria/x`,
  `env FOO=1 bash scripts/x.sh && git push …`, `timeout 600 bash -O extglob scripts/x.sh; git push …`,
  `. venv/bin/activate && git push …`, o envio com log e `rc=` da `esperar-estado`, `git --git-dir .git log`,
  `printf 'git status' | bash`, `git pull --rebase origin melhoria/x && git push origin melhoria/x`;
- **passaram a recusar** (rc 0 no 6c0b0f03, rc 2 no e48a2e60): S1, S2 e S3 abaixo. Os três leem o pedido ou o brief e gravam
  num caminho livre por variável. O S1 é o caminho de todo subagente: a pasta corrente volta à raiz entre chamadas, então ele
  começa com `cd ~/.forge-contrib/wt/<x> &&`, e o sandbox manda usar o `$TMPDIR`. O `docs/hooks.md:56` diz que o
  `docs/pedidos/` do clone "segue livre ali, como antes", e o S1 contradiz isso.

## Ferramentas (citadas, não refeitas)
- Testes novos no head e48a2e60: `test_fixtures_do_controle_so_jarvis`, `test_fixtures_da_escrita_no_indice`,
  `test_fixtures_da_substituicao_no_projeto` → `Ran 3 tests in 16.023s OK`.
- `bin/forge-mutante --processos 1 --ids U1 tests/mutantes/v0479-conformidade-trilha-7.json` → `U1 · morreu · hooks/conformidade.py:4041`.
- Suíte inteira: sem PR, sem run de CI na branch (`gh run list` vazio); não rerrodada aqui.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3808 · caso legítimo passou a recusar (S1, S2): `cd ~/.forge-contrib/wt/x &&` mais leitura de docs/pedidos/ com saída em `$TMPDIR` ou variável; contradiz docs/hooks.md:56 ("segue livre, como antes"). Não contar `forge-contrib/wt/<pasta>` sem `..` como pasta mãe; fixtures S1 e S2.
- A2 (recomendado) hooks/conformidade.py:3895 · com a pasta corrente em ~/.forge-contrib fora de wt/, `ls docs/briefs > $TMPDIR/b.txt` recusa (S3): a leitura do brief com saída por variável; declarar como limite em docs/hooks.md com a contraprova literal, ou estreitar.

## Sondas
- S1 · tech-lead, sessão do Forge, cwd ~/.forge-contrib/wt/x: `cd ~/.forge-contrib/wt/x && sed -n 1,5p docs/pedidos/v1.md > $TMPDIR/e.txt` · espera: rc 0 (como no 6c0b0f03) · obtido: rc 2, "R-CONFORMIDADE: `$TMPDIR` com ação crítica: o hook não modela"
- S2 · tech-lead, cwd ~/.forge-contrib/wt/x: `f=~/.forge-contrib/wt/r.txt; grep -c x docs/pedidos/v1.md > $f` · espera: rc 0 (como no 6c0b0f03) · obtido: rc 2, "R-CONFORMIDADE: `$f` com ação crítica: o hook não modela"
- S3 · tech-lead, cwd ~/.forge-contrib: `ls docs/briefs > $TMPDIR/b.txt` · espera: rc 0 (como no 6c0b0f03) · obtido: rc 2, "R-CONFORMIDADE: `$TMPDIR` com ação crítica: o hook não modela"

## Parecer
Reprovado no head e48a2e60. As guardas novas do índice, do envio e do oráculo fazem o que os achados da segurança e do QA
pedem, não recusam nenhum dos casos legítimos que sondei, e o mutante declarado morre. A exceção é o alargamento do
`CONTROLE_NO_TEXTO` (A1 da segurança): ele recusa a leitura do pedido do próprio clone quando a linha começa com o `cd` para a
cópia em `wt/` e grava a saída por variável. Essa construção é a de rotina dos subagentes, e o `docs/hooks.md` promete que ela
segue livre (A1, bloqueante, defeito provado pelas sondas S1 e S2). O A2 (S3) é recomendado: com a pasta corrente no controle,
a recusa ao citar `briefs` está escrita no `docs/hooks.md`, mas falta a contraprova. Na volta, a correção do A1 reabre a
revalidação só do `CONTROLE_NO_TEXTO` e das fixtures novas.
